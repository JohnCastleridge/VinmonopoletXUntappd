import sqlite3
import requests
from bs4 import BeautifulSoup
import json
import re
import time

# --- KONFIGURASJON ---
KILDE_DB = "catalog.db"
BEERS_DB = "beers.db"
PAUSE_SEKUNDER = 1.2


def rens_tall(tekst):
    if not tekst or tekst == "Ukjent":
        return 0.0
    match = re.search(r"[\d]+(?:[.,][\d]+)?", str(tekst))
    return float(match.group(0).replace(",", ".")) if match else 0.0


def convert_to_liters(volume_data):
    """Konverterer volumobjekt fra VMP til liter (float)."""
    if not volume_data:
        return 0.0
    val = float(volume_data.get("value", 0.0))
    fmt = volume_data.get("formattedValue", "").lower()
    if "cl" in fmt:
        return val / 100.0
    if "ml" in fmt:
        return val / 1000.0
    return val


def get_or_create_id(cursor, table, name):
    """Henter ID fra en oppslagstabell, eller oppretter hvis den ikke finnes."""
    if not name or name == "Ukjent":
        return None
    cursor.execute(f"SELECT id FROM {table} WHERE name = ?", (name,))
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute(f"INSERT INTO {table} (name) VALUES (?)", (name,))
    return cursor.lastrowid


def scrape_vmp_to_beers_db(p_id, db_path=BEERS_DB):
    """Skraper data for en vmp_id og lagrer/oppdaterer i beer_catalog i beers.db."""
    url = f"https://www.vinmonopolet.no/p/{p_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.encoding = "utf-8"
        if r.status_code != 200:
            print(f"⚠️ Kunne ikke hente {p_id} (HTTP {r.status_code})")
            return None

        soup = BeautifulSoup(r.text, "html.parser")
        main_tag = soup.find("main", id="page")
        if not main_tag:
            return None

        json_script = main_tag.find("script", type="application/json")
        if not json_script:
            return None

        produkt = json.loads(json_script.string).get("product", {})
        kategori = produkt.get("main_category", {}).get("name", "")

        # Sjekk relevans
        if kategori not in ["Øl", "Sider", "Mjød"]:
            return "IKKE_RELEVANT"

        abv_raw = next(
            (
                t.get("formattedValue")
                for t in produkt.get("content", {}).get("traits", [])
                if t.get("name") == "Alkohol"
            ),
            "0",
        )

        # Hent data
        data = {
            "id_vmp": int(p_id),
            "name_vmp": produkt.get("name", "Ukjent"),
            "brewery_name": produkt.get("main_producer", {}).get("name", "Ukjent"),
            "type_vmp": kategori,
            "style_name": produkt.get("main_sub_category", {}).get("name", "Ukjent"),
            "abv_vmp": rens_tall(abv_raw),
            "vintage_vmp": produkt.get("year", ""),
            "country_name": produkt.get("main_country", {}).get("name", "Ukjent"),
            "price_vmp": float(produkt.get("price", {}).get("value", 0.0)),
            "volume_vmp": convert_to_liters(produkt.get("volume", {})),
            "selection_vmp": produkt.get("product_selection", "Ukjent"),
            "image_url_vmp": produkt.get("images", [{}])[0].get("url", ""),
            "is_discontinued_vmp": int(
                produkt.get("expired", False) or produkt.get("status") == "utgått"
            ),
            "aroma_vmp": produkt.get("smell", ""),
            "taste_vmp": produkt.get("taste", ""),
            "color_vmp": produkt.get("color", ""),
            "packaging_vmp": produkt.get("packageType", ""),
            "allergens_vmp": produkt.get("allergens", ""),
            "method_vmp": produkt.get("method", ""),
        }

        # Lagre i databasen
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # Hent fremmednøkler
        brewery_id = get_or_create_id(cur, "breweries_vmp", data["brewery_name"])
        style_id = get_or_create_id(cur, "styles_vmp", data["style_name"])
        country_id = get_or_create_id(cur, "countries", data["country_name"])

        cur.execute(
            """
            INSERT INTO beer_catalog (
                id_vmp, name_vmp, brewery_vmp_id, type_vmp, style_vmp_id,
                abv_vmp, vintage_vmp, country_vmp_id, price_vmp, volume_vmp,
                selection_vmp, image_url_vmp, is_discontinued_vmp, aroma_vmp,
                taste_vmp, color_vmp, packaging_vmp, allergens_vmp, method_vmp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id_vmp) DO UPDATE SET
                name_vmp=excluded.name_vmp,
                brewery_vmp_id=excluded.brewery_vmp_id,
                type_vmp=excluded.type_vmp,
                style_vmp_id=excluded.style_vmp_id,
                abv_vmp=excluded.abv_vmp,
                vintage_vmp=excluded.vintage_vmp,
                country_vmp_id=excluded.country_vmp_id,
                price_vmp=excluded.price_vmp,
                volume_vmp=excluded.volume_vmp,
                selection_vmp=excluded.selection_vmp,
                image_url_vmp=excluded.image_url_vmp,
                is_discontinued_vmp=excluded.is_discontinued_vmp,
                aroma_vmp=excluded.aroma_vmp,
                taste_vmp=excluded.taste_vmp,
                color_vmp=excluded.color_vmp,
                packaging_vmp=excluded.packaging_vmp,
                allergens_vmp=excluded.allergens_vmp,
                method_vmp=excluded.method_vmp
        """,
            (
                data["id_vmp"],
                data["name_vmp"],
                brewery_id,
                data["type_vmp"],
                style_id,
                data["abv_vmp"],
                data["vintage_vmp"],
                country_id,
                data["price_vmp"],
                data["volume_vmp"],
                data["selection_vmp"],
                data["image_url_vmp"],
                data["is_discontinued_vmp"],
                data["aroma_vmp"],
                data["taste_vmp"],
                data["color_vmp"],
                data["packaging_vmp"],
                data["allergens_vmp"],
                data["method_vmp"],
            ),
        )

        conn.commit()
        conn.close()
        return data

    except Exception as e:
        print(f"❌ Feil ved skraping av {p_id}: {e}")
        return None


def kjor_oppdatering():
    """Går gjennom alle produkter i beers.db og henter utfyllende data fra Polet."""
    # 1. Koble til databasen
    conn = sqlite3.connect(BEERS_DB)
    cur = conn.cursor()

    # 2. Hent kun IDer som mangler detaljer (sjekker om aroma_vmp er tom eller NULL)
    cur.execute("""
        SELECT id_vmp, name_vmp 
        FROM beer_catalog 
        WHERE aroma_vmp IS NULL OR aroma_vmp = ''
    """)
    produkter = cur.fetchall()
    
    totalt = len(produkter)
    if totalt == 0:
        print("✅ Alle produkter i beers.db har allerede detaljer. Ingenting å gjøre.")
        conn.close()
        return

    print(f"--- STATUS ---")
    print(f"Produkter som mangler detaljer: {totalt}")
    print(f"Starter oppdatering av detaljer...\n")

    # 3. Hovedløkke
    try:
        for i, (p_id, navn) in enumerate(produkter):
            print(f"[{i + 1}/{totalt}] 🔍 Henter detaljer for: {navn} ({p_id})...", end="\r")
            data = scrape_vmp_to_beers_db(p_id)

            if data:
                # Vi logger ikke suksess hver gang for å holde terminalen ren, 
                # med mindre det er noe spesielt.
                pass
            else:
                print(f"\n⚠️ Kunne ikke oppdatere ID {p_id}")

            time.sleep(PAUSE_SEKUNDER)

    except KeyboardInterrupt:
        print("\n\n🛑 Avbrutt av bruker.")
    finally:
        conn.close()
        print("\n✅ Oppdatering er ferdig.")


if __name__ == "__main__":
    kjor_oppdatering()
