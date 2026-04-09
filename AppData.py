import sqlite3
import requests
from bs4 import BeautifulSoup
import json
import re
import time


# --- HJELPEFUNKSJON FOR Å RENSE TALL ---
def rens_tall(tekst):
    """Henter ut tall fra tekst, bytter komma med punkt, og returnerer float."""
    if not tekst or tekst == "Ukjent":
        return 0.0
    # Finner første tall (inkludert eventuelt komma/punktum)
    match = re.search(r"[\d]+(?:[.,][\d]+)?", str(tekst))
    if match:
        return float(match.group(0).replace(",", "."))
    return 0.0


# --- SKRAPEREN (Oppdatert med tallvask) ---
def hent_og_vask_produkt(product_id):
    url = f"https://www.vinmonopolet.no/p/{product_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.encoding = "utf-8"
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        main_tag = soup.find("main", id="page")
        if not main_tag:
            return None

        json_script = main_tag.find("script", type="application/json")
        if json_script and json_script.string:
            produkt = json.loads(json_script.string).get("product", {})
            kategori = produkt.get("main_category", {}).get("name", "")

            # STOPP hvis det ikke er relevant!
            if kategori not in ["Øl", "Sider", "Mjød"]:
                return None

            # --- VASKING AV TALL OG TEKST ---
            abv_rå = next(
                (
                    t.get("formattedValue")
                    for t in produkt.get("content", {}).get("traits", [])
                    if t.get("name") == "Alkohol"
                ),
                "0",
            )
            bilde = (
                produkt.get("images", [{}])[0].get("url", "Ukjent")
                if produkt.get("images")
                else "Ukjent"
            )

            return {
                "id": int(product_id),  # GJORT OM TIL INT
                "navn": produkt.get("name", "Ukjent"),
                "varetype": kategori,
                "undertype": produkt.get("main_sub_category", {}).get("name", "Ukjent"),
                "produsent": produkt.get("main_producer", {}).get("name", "Ukjent"),
                "land_distrikt": f"{produkt.get('main_country', {}).get('name', '')}, {produkt.get('district', {}).get('name', '')}".strip(
                    ", "
                ),
                "abv": rens_tall(abv_rå),  # GJORT OM TIL FLOAT
                "pris": float(
                    produkt.get("price", {}).get("value", 0.0)
                ),  # ALLEREDE FLOAT
                "volum": rens_tall(
                    produkt.get("volume", {}).get("formattedValue", "0")
                ),  # GJORT OM TIL FLOAT
                "utvalg": produkt.get("product_selection", "Ukjent"),
                "bilde_url": bilde,
            }
    except Exception as e:
        print(f"Feil med {product_id}: {e}")
        return None


def kjor_vaskemaskin_pipeline():
    # 1. Koble til den NYE databasen (der vi lagrer vasket data)
    ny_db = sqlite3.connect("Untappd.db")
    ny_cursor = ny_db.cursor()

    # Oppretter tabellen med riktige datatyper (REAL for float, INTEGER for int)
    ny_cursor.execute("""
        CREATE TABLE IF NOT EXISTS ol_data (
            id INTEGER PRIMARY KEY,
            navn TEXT,
            varetype TEXT,
            undertype TEXT,
            produsent TEXT,
            land TEXT,
            abv REAL,
            pris REAL,
            volum REAL,
            utvalg TEXT,
            bilde_url TEXT
        )
    """)

    # 2. Koble til KILDE-databasen
    katalog_db = sqlite3.connect("catalog.db")
    katalog_cursor = katalog_db.cursor()

    # --- NYTT: Legg til SQL-spørringen som filtrerer dataene ---
    # Bytt ut 'date' med den kolonnen du vil sjekke, og '2023-10-25' med verdien du ser etter.
    kriterium = "2023-10-25"
    katalog_cursor.execute("SELECT id FROM products WHERE date = ?", (kriterium,))

    # Henter ut alle ID-ene som matchet spørringen over
    ider_til_sjekk = [rad[0] for rad in katalog_cursor.fetchall()]
    katalog_db.close()

    # 3. Gå gjennom IDene og vask data
    for p_id in ider_til_sjekk:
        print(f"Sjekker ID {p_id}...")
        data = hent_og_vask_produkt(p_id)  # Bruker funksjonen fra forrige svar

        if data:
            print(f"🍺 Fant: {data['navn']} - {data['abv']}% - {data['pris']}kr")

            ny_cursor.execute(
                """
                INSERT INTO ol_data (id, navn, varetype, undertype, produsent, land, abv, pris, volum, utvalg, bilde_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    navn=excluded.navn,
                    abv=excluded.abv,
                    pris=excluded.pris,
                    volum=excluded.volum
            """,
                (
                    data["id"],
                    data["navn"],
                    data["varetype"],
                    data["undertype"],
                    data["produsent"],
                    data["land_distrikt"],
                    data["abv"],
                    data["pris"],
                    data["volum"],
                    data["utvalg"],
                    data["bilde_url"],
                ),
            )
            ny_db.commit()
            time.sleep(0.5)  # Pause for å unngå blokkering
        else:
            print(f"⏭️ ID {p_id} er ikke en relevant drikke.")

    ny_db.close()
    print("\n✅ Testkjøring ferdig! Sjekk Untappd.db for resultater.")


# Kjør pipelinen!
kjor_vaskemaskin_pipeline()
