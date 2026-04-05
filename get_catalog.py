import requests
import time
import sqlite3
import json

API_KEY = "0803107360064be187d02eb284f7e146"
MAX_RESULTS = 1000
start = 0

db_navn = "vinmonopolet.db"
conn = sqlite3.connect(db_navn)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    productId TEXT PRIMARY KEY,
    shortName TEXT,
    longName TEXT,
    category TEXT,
    volume REAL,
    alcohol REAL,
    price REAL,
    raw_json TEXT
)
""")
conn.commit()

print(f"Starter massenedlasting av Vinmonopolet (med krasj-sikring)...")
print("-" * 50)

totalt_hentet = 0

while True:
    url = f"https://apis.vinmonopolet.no/products/v0/details-normal?maxResults={MAX_RESULTS}&start={start}"
    headers = {"Ocp-Apim-Subscription-Key": API_KEY}

    # --- NYTT: Vi prøver opptil 5 ganger hvis nettet feiler ---
    suksess = False
    for forsok in range(5):
        try:
            # timeout=10 betyr at Python gir opp og går til "except" hvis serveren bruker mer enn 10 sekunder
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                suksess = True
                break  # Gå ut av forsøk-løkken, vi fikk dataene!
            elif response.status_code == 429:
                print(
                    "Advarsel: Vi sjekker for fort (Rate limit). Venter 10 sekunder..."
                )
                time.sleep(10)
            else:
                print(f"Fikk HTTP kode {response.status_code}. Prøver på nytt...")
                time.sleep(3)

        except requests.exceptions.RequestException as e:
            print(
                f"Nettverksfeil/Timeout. Prøver igjen om 5 sekunder... (Forsøk {forsok + 1}/5)"
            )
            time.sleep(5)

    # Hvis vi prøvde 5 ganger uten hell, avbryter vi for å ikke sitte fast evig
    if not suksess:
        print("Klarte ikke å hente data etter 5 forsøk. Avbryter scriptet.")
        break
    # -----------------------------------------------------------

    data = response.json()
    antall_i_denne_bolken = len(data)

    if antall_i_denne_bolken == 0:
        print("\nKatalogen er ferdig nedlastet!")
        break

    totalt_hentet += antall_i_denne_bolken
    print(
        f"Henter posisjon {start} til {start + antall_i_denne_bolken - 1}... (Totalt lagret: {totalt_hentet})"
    )

    produkter_til_db = []
    for item in data:
        basic = item.get("basic", {})
        classification = item.get("classification", {})

        prices = item.get("prices", [])
        price = prices[0].get("salesPrice") if prices else None

        product_id = basic.get("productId")
        short_name = basic.get("productShortName")
        long_name = basic.get("productLongName")
        category = classification.get("mainProductTypeName")
        volume = basic.get("volume")
        alcohol = basic.get("alcoholContent")
        raw_json = json.dumps(item)

        if product_id:
            produkter_til_db.append(
                (
                    product_id,
                    short_name,
                    long_name,
                    category,
                    volume,
                    alcohol,
                    price,
                    raw_json,
                )
            )

    cursor.executemany(
        """
    INSERT OR REPLACE INTO products (productId, shortName, longName, category, volume, alcohol, price, raw_json)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
        produkter_til_db,
    )

    conn.commit()

    start += MAX_RESULTS
    time.sleep(1.2)  # Ventetiden for å holde oss under maks kall pr minutt

conn.close()
print("-" * 50)
print(f"Suksess! Databasen er klar og inneholder alt.")
