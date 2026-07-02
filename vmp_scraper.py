"""
vmp_scraper.py – Skraper ett VMP-produkt og upsert-er det i databasen.

Eksponert funksjon:
    scrape_vmp_product(vmp_id, db_path) -> bool

Bruker JSON-blokken som ligger i <main id="page"> <script type="application/json">
på produktsiden til vinmonopolet.no – ingen ekstern API-nøkkel nødvendig.

Tabeller som oppdateres:
    vmp_products      – ett produkt (INSERT OR REPLACE)
    vmp_producers     – produsent, oprettes ved behov
    vmp_categories    – kategori-par, oprettes ved behov
    vmp_all_products  – is_beer og needs_sync oppdateres
"""

import json
import re
import sqlite3
import time
import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Konfigurasjon
# ---------------------------------------------------------------------------
DB_PATH    = "vmp_untappd_new.db"
BASE_URL   = "https://www.vinmonopolet.no"
HEADERS    = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "no-NO,no;q=0.9",
}

# Kategorier VMP bruker som tilsvarer "øl-lignende" produkter
BEER_CATEGORIES = {"Øl", "Sider", "Mjød"}


# ---------------------------------------------------------------------------
# Hjelper: hent og parse JSON fra produktsiden
# ---------------------------------------------------------------------------
def _fetch_product_json(vmp_id: int | str) -> dict | None:
    """
    Henter produktsiden og returnerer product-dict fra den innebygde JSON-blokken
    i <main id="page"> <script type="application/json">.
    Returnerer None ved feil eller hvis produktet ikke finnes.
    """
    url = f"{BASE_URL}/p/{vmp_id}"

    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            
            if resp.status_code == 429:
                wait_time = 10 * attempt
                print(f"  [vmp_scraper] HTTP 429 for {vmp_id}. Venter {wait_time}s og prøver igjen ({attempt}/{max_retries})...")
                time.sleep(wait_time)
                continue
                
            break
        except requests.exceptions.RequestException as exc:
            if attempt == max_retries:
                print(f"  [vmp_scraper] Nettverksfeil for {vmp_id}: {exc}")
                return None
            time.sleep(2)

    if resp.status_code == 429:
        print(f"  [vmp_scraper] Ga opp etter {max_retries} forsøk (HTTP 429).")
        # Returnerer -1 for å signalisere rate limit
        return -1

    if resp.status_code == 404:
        print(f"  [vmp_scraper] 404 – produkt {vmp_id} finnes ikke.")
        return None
    if resp.status_code != 200:
        print(f"  [vmp_scraper] HTTP {resp.status_code} for {vmp_id}.")
        return None

    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "html.parser")

    # JSON-blokken vi vil ha ligger i <main id="page">
    main_tag = soup.find("main", id="page")
    if not main_tag:
        print(f"  [vmp_scraper] Fant ikke <main id='page'> for {vmp_id}.")
        return None

    script_tag = main_tag.find("script", type="application/json")
    if not script_tag or not script_tag.string:
        print(f"  [vmp_scraper] Fant ikke JSON-blokk for {vmp_id}.")
        return None

    try:
        data = json.loads(script_tag.string)
    except json.JSONDecodeError as exc:
        print(f"  [vmp_scraper] JSON-feil for {vmp_id}: {exc}")
        return None

    return data.get("product")


# ---------------------------------------------------------------------------
# Hjelper: parse ABV fra traits-listen
# ---------------------------------------------------------------------------
def _parse_abv(traits: list) -> float | None:
    for t in traits:
        if t.get("name") == "Alkohol":
            raw = t.get("formattedValue", "")        # f.eks. "9%"
            match = re.search(r"[\d]+(?:[.,][\d]+)?", raw)
            if match:
                return float(match.group(0).replace(",", "."))
    return None


# ---------------------------------------------------------------------------
# Hjelper: upsert produsent, returner producer_id
# ---------------------------------------------------------------------------
def _upsert_producer(cur: sqlite3.Cursor, name: str, country: str | None) -> int:
    cur.execute(
        "INSERT OR IGNORE INTO vmp_producers (name, country) VALUES (?, ?)",
        (name, country),
    )
    cur.execute("SELECT id FROM vmp_producers WHERE name = ?", (name,))
    return cur.fetchone()[0]


# ---------------------------------------------------------------------------
# Hjelper: upsert kategori-par, returner category_id
# ---------------------------------------------------------------------------
def _upsert_category(
    cur: sqlite3.Cursor, category_main: str | None, category_sub: str | None
) -> int:
    # Sjekk om paret allerede finnes
    cur.execute(
        """
        SELECT id FROM vmp_categories
        WHERE (category_main IS ? OR (category_main IS NULL AND ? IS NULL))
          AND (category_sub  IS ? OR (category_sub  IS NULL AND ? IS NULL))
        """,
        (category_main, category_main, category_sub, category_sub),
    )
    row = cur.fetchone()
    if row:
        return row[0]

    cur.execute(
        "INSERT INTO vmp_categories (category_main, category_sub) VALUES (?, ?)",
        (category_main, category_sub),
    )
    return cur.lastrowid


# ---------------------------------------------------------------------------
# Hoved-funksjon
# ---------------------------------------------------------------------------
def scrape_vmp_product(vmp_id: int | str, db_path: str = DB_PATH) -> bool:
    """
    Skraper ett VMP-produkt og upsert-er det i databasen.

    Oppdaterer:
        - vmp_products  (INSERT OR REPLACE)
        - vmp_producers (INSERT OR IGNORE)
        - vmp_categories (INSERT hvis nytt kategori-par)
        - vmp_all_products (is_beer, needs_sync = 0)

    Returnerer True ved suksess, False ved feil.
    """
    vmp_id = str(vmp_id)

    p = _fetch_product_json(vmp_id)
    if p == -1:
        # Rate limit (HTTP 429) - vi vil ikke markere som utgått, bare returnere False
        return False
        
    if p is None:
        # Produktet finnes ikke / nettverksfeil – mark as discontinued
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(
            "UPDATE vmp_all_products SET is_beer = 0, needs_sync = 0 "
            "WHERE product_id_vmp = ?",
            (int(vmp_id),),
        )
        cur.execute(
            "UPDATE vmp_products SET is_discontinued = 1 WHERE product_id_vmp = ?",
            (vmp_id,),
        )
        conn.commit()
        conn.close()
        return False

    # -------------------------------------------------------------------
    # Trekk ut alle felt fra JSON
    # -------------------------------------------------------------------
    name            = p.get("name")
    status          = p.get("status", "aktiv")          # "aktiv" / "utgått"
    is_discontinued = 0 if status == "aktiv" else 1

    main_cat     = p.get("main_category", {}).get("name")       # "Øl"
    sub_cat      = p.get("main_sub_category", {}).get("name")   # "Klosterstil"
    producer_name= p.get("main_producer", {}).get("name")
    country      = p.get("main_country", {}).get("name")
    vintage      = p.get("year") or None

    price_val    = p.get("price", {}).get("value")
    volume_cl    = p.get("volume", {}).get("value")             # i cl
    volume_ml    = int(round(volume_cl * 10)) if volume_cl else None

    selection    = p.get("product_selection")
    packaging    = p.get("packageType")
    aroma        = p.get("smell")
    taste        = p.get("taste")
    color        = p.get("color")
    method       = p.get("method")
    allergens    = p.get("allergens")

    traits       = p.get("content", {}).get("traits", [])
    abv          = _parse_abv(traits)

    # Produktbilde – foretrekk superZoom-format
    images = p.get("images", [])
    url_image = None
    for fmt in ("superZoom", "zoom", "product"):
        for img in images:
            if img.get("format") == fmt:
                url_image = img.get("url")
                break
        if url_image:
            break
    if not url_image and images:
        url_image = images[0].get("url")

    # Relativ URL → absolutt
    rel_url  = p.get("url", "")
    url_vmp  = f"{BASE_URL}{rel_url}" if rel_url else f"{BASE_URL}/p/{vmp_id}"

    # Er dette et ølprodukt? (Øl, Sider, Mjød telles som "øl" i denne konteksten)
    is_beer = 1 if main_cat in BEER_CATEGORIES else 0

    # -------------------------------------------------------------------
    # Skriv til database
    # -------------------------------------------------------------------
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = OFF")
    cur = conn.cursor()

    try:
        # Produsent
        producer_id = None
        if producer_name:
            producer_id = _upsert_producer(cur, producer_name, country)

        # Kategori
        category_id = _upsert_category(cur, main_cat, sub_cat)

        # vmp_products – upsert (INSERT OR REPLACE bevarer beer_id_unt og match_confidence)
        cur.execute(
            """
            INSERT INTO vmp_products
                (product_id_vmp, beer_id_unt, match_confidence,
                 producer_id, category_id, name, vintage, price,
                 volume_ml, abv, selection, packaging, aroma, taste,
                 color, method, allergens, url_vmp, url_image,
                 is_discontinued)
            VALUES (?, NULL, NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(product_id_vmp) DO UPDATE SET
                producer_id    = excluded.producer_id,
                category_id    = excluded.category_id,
                name           = excluded.name,
                vintage        = excluded.vintage,
                price          = excluded.price,
                volume_ml      = excluded.volume_ml,
                abv            = excluded.abv,
                selection      = excluded.selection,
                packaging      = excluded.packaging,
                aroma          = excluded.aroma,
                taste          = excluded.taste,
                color          = excluded.color,
                method         = excluded.method,
                allergens      = excluded.allergens,
                url_vmp        = excluded.url_vmp,
                url_image      = excluded.url_image,
                is_discontinued= excluded.is_discontinued
            """,
            (
                vmp_id, producer_id, category_id,
                name, vintage, price_val,
                volume_ml, abv, selection, packaging,
                aroma, taste, color, method, allergens,
                url_vmp, url_image, is_discontinued,
            ),
        )

        # vmp_all_products – oppdater klassifisering og sync-status
        cur.execute(
            """
            INSERT INTO vmp_all_products
                (product_id_vmp, name_raw, is_beer, needs_sync)
            VALUES (?, ?, ?, 0)
            ON CONFLICT(product_id_vmp) DO UPDATE SET
                name_raw   = excluded.name_raw,
                is_beer    = excluded.is_beer,
                needs_sync = 0
            """,
            (int(vmp_id), name, is_beer),
        )

        conn.commit()
        print(
            f"  [vmp_scraper] OK: {vmp_id} – {name!r} "
            f"({main_cat} / {sub_cat}, {abv}% ABV, {price_val} kr)"
        )
        return True

    except Exception as exc:
        conn.rollback()
        print(f"  [vmp_scraper] DB-feil for {vmp_id}: {exc}")
        return False

    finally:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.close()


# ---------------------------------------------------------------------------
# Kjør direkte for testing
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    test_ids = sys.argv[1:] if len(sys.argv) > 1 else ["3246802", "202501", "1476601"]

    for vid in test_ids:
        print(f"\nSkraper {vid}...")
        scrape_vmp_product(vid)
        time.sleep(1.5)
