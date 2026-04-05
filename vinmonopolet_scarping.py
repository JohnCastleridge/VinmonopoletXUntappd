import sqlite3
import requests
from bs4 import BeautifulSoup
import json
import re
import time

# --- KONFIGURASJON ---
KILDE_DB = "VinmonopoletKatalog.db"
MAL_DB = "Untappd.db"
PAUSE_SEKUNDER = 1.2


def rens_tall(tekst):
    if not tekst or tekst == "Ukjent":
        return 0.0
    match = re.search(r"[\d]+(?:[.,][\d]+)?", str(tekst))
    return float(match.group(0).replace(",", ".")) if match else 0.0


def hent_vasket_data(p_id):
    url = f"https://www.vinmonopolet.no/p/{p_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.encoding = "utf-8"
        if r.status_code != 200:
            return None

        soup = BeautifulSoup(r.text, "html.parser")
        main_tag = soup.find("main", id="page")
        json_script = main_tag.find("script", type="application/json")
        produkt = json.loads(json_script.string).get("product", {})

        kategori = produkt.get("main_category", {}).get("name", "")
        # Vi lagrer kun det som er relevant for Untappd
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

        return {
            "id": int(p_id),
            "navn": produkt.get("name", "Ukjent"),
            "varetype": kategori,
            "undertype": produkt.get("main_sub_category", {}).get("name", "Ukjent"),
            "produsent": produkt.get("main_producer", {}).get("name", "Ukjent"),
            "land": produkt.get("main_country", {}).get("name", "Ukjent"),
            "abv": rens_tall(abv_raw),
            "pris": float(produkt.get("price", {}).get("value", 0.0)),
            "volum": rens_tall(produkt.get("volume", {}).get("formattedValue", "0")),
            "utvalg": produkt.get("product_selection", "Ukjent"),
            "bilde_url": produkt.get("images", [{}])[0].get("url", ""),
        }
    except Exception:
        return None


def kjor_full_skraping():
    # 1. Sett opp databaser
    kilde_conn = sqlite3.connect(KILDE_DB)
    mal_conn = sqlite3.connect(MAL_DB)

    k_cur = kilde_conn.cursor()
    m_cur = mal_conn.cursor()

    m_cur.execute("""
        CREATE TABLE IF NOT EXISTS ol_data (
            id INTEGER PRIMARY KEY, navn TEXT, varetype TEXT, undertype TEXT,
            produsent TEXT, land TEXT, abv REAL, pris REAL, volum REAL,
            utvalg TEXT, bilde_url TEXT
        )
    """)

    # Lag en tabell for å huske IDer som IKKE var relevante (så vi slipper å sjekke rødvin på nytt)
    m_cur.execute("CREATE TABLE IF NOT EXISTS ignorerte_ider (id INTEGER PRIMARY KEY)")
    mal_conn.commit()

    # 2. Finn ut hva vi allerede har gjort
    m_cur.execute("SELECT id FROM ol_data")
    ferdige_ider = {rad[0] for rad in m_cur.fetchall()}

    m_cur.execute("SELECT id FROM ignorerte_ider")
    ignorerte_ider = {rad[0] for rad in m_cur.fetchall()}

    ferdig_sett = ferdige_ider.union(ignorerte_ider)

    # 3. Hent alle IDer fra katalogen
    k_cur.execute("SELECT id FROM products ORDER BY id DESC")
    alle_ider = [rad[0] for rad in k_cur.fetchall()]

    ider_som_gjenstar = [p_id for p_id in alle_ider if p_id not in ferdig_sett]

    totalt = len(alle_ider)
    allerede_prosessert = len(ferdig_sett)
    skal_sjekkes = len(ider_som_gjenstar)

    print(f"--- STATUS ---")
    print(f"Totalt i katalog: {totalt}")
    print(f"Allerede sjekket: {allerede_prosessert}")
    print(f"Gjenstår nå:     {skal_sjekkes}")
    print(f"---------------\n")

    # 4. Hovedløkke
    try:
        for i, p_id in enumerate(ider_som_gjenstar):
            data = hent_vasket_data(p_id)

            if data == "IKKE_RELEVANT":
                m_cur.execute("INSERT INTO ignorerte_ider (id) VALUES (?)", (p_id,))
            elif data:
                m_cur.execute(
                    """
                    INSERT INTO ol_data VALUES (?,?,?,?,?,?,?,?,?,?,?)
                    ON CONFLICT(id) DO UPDATE SET navn=excluded.navn, pris=excluded.pris, abv=excluded.abv
                """,
                    (
                        data["id"],
                        data["navn"],
                        data["varetype"],
                        data["undertype"],
                        data["produsent"],
                        data["land"],
                        data["abv"],
                        data["pris"],
                        data["volum"],
                        data["utvalg"],
                        data["bilde_url"],
                    ),
                )
                print(f"[{i + 1}/{skal_sjekkes}] 🍺 Lagret: {data['navn']}")
                print(f"Allerede sjekket: {allerede_prosessert}")
                print(f"Gjenstår nå:     {skal_sjekkes}")
            else:
                print(
                    f"[{i + 1}/{skal_sjekkes}] ⚠️ Kunne ikke hente ID {p_id} (hoppet over)"
                )

            # Lagre progresjon for hver 10. vare
            if i % 10 == 0:
                mal_conn.commit()

            time.sleep(PAUSE_SEKUNDER)

    except KeyboardInterrupt:
        print("\n\n🛑 Avbrutt av bruker. Lagrer fremdrift...")
    finally:
        mal_conn.commit()
        kilde_conn.close()
        mal_conn.close()
        print("✅ Prosessen er avsluttet. Du kan trygt starte koden på nytt senere.")


if __name__ == "__main__":
    kjor_full_skraping()
