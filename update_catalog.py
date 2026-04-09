import requests
import time
import sqlite3

API_KEY = "0803107360064be187d02eb284f7e146"
MAX_RESULTS = 1000
start = 0

db_navn = "beers.db"
conn = sqlite3.connect(db_navn)
cursor = conn.cursor()

# Vi antar at tabellen allerede er opprettet av rebuild_database.py eller fix_database.py
cursor.execute("""
CREATE TABLE IF NOT EXISTS vmp_all_products (
    id_vmp INTEGER PRIMARY KEY,
    name_vmp TEXT,
    last_changed_date TEXT,
    last_changed_time TEXT
)
""")


print(f"Starter massenedlasting av Vinmonopolet (til {db_navn} - vmp_all_products)...")
print("-" * 50)

totalt_hentet = 0

while True:
    url = f"https://apis.vinmonopolet.no/products/v0/details-normal?maxResults={MAX_RESULTS}&start={start}"
    headers = {"Ocp-Apim-Subscription-Key": API_KEY}

    suksess = False
    for forsok in range(5):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                suksess = True
                break
            elif response.status_code == 429:
                print("Advarsel: Rate limit. Venter 10 sekunder...")
                time.sleep(10)
            else:
                print(f"Fikk HTTP kode {response.status_code}. Prøver på nytt...")
                time.sleep(3)
        except requests.exceptions.RequestException:
            time.sleep(5)

    if not suksess:
        print("Klarte ikke å hente data. Avbryter.")
        break

    data = response.json()
    antall_i_denne_bolken = len(data)

    if antall_i_denne_bolken == 0:
        break

    totalt_hentet += antall_i_denne_bolken
    print(f"Henter posisjon {start}... (Totalt: {totalt_hentet})")

    produkter_til_db = []
    for item in data:
        basic = item.get("basic", {})
        p_id = basic.get("productId")
        name = basic.get("productShortName")

        lastChanged = item.get("lastChanged", {})
        date_str = lastChanged.get("date")
        time_str = lastChanged.get("time")

        # if beer["is_beer"] == False: # hvis det ikke er en øl, oppdaterer vi uansett
        #    produkter_til_db.append((p_id, name, date_str, time_str))
        #
        #
        # if newtime > oldtime: # hvis den har blitt endret siden sist
        #    vmp_scrape_suc = scrape_vmp(p_id) # vmp_scrape skal scrape vmp siden for info og returnere False hvis scarpingen feiler
        #    if vmp_scrape_suc: # sjekker om det er en øl og om vmp_scrape er suksessfull,
        #
        #       if beer["unt_id"] is Null:
        #           unt_id = find_id_unt(p_id) # åpteter beers.db med "id_unt" og "match_confidence" og returnerer nye id_unt
        #       else:
        #           unt_id = beer["unt_id"]
        #
        #
        #       unt_scrape_suc = scrape_unt(unt_id) #
        #
        #    if beer["is_beer"] == False or (unt_scrape_suc and vmp_scrape_suc):
        #    # oppdaterer vmp_all_products med ny dato, hvis den klarte å opptatere databasen eller hvis det ikke er en øl
        #       produkter_til_db.append((p_id, name, date_str, time_str))

    cursor.executemany(
        """
        INSERT INTO vmp_all_products (id_vmp, name_vmp, last_changed_date, last_changed_time) 
        VALUES (?, ?, ?, ?)
        ON CONFLICT(id_vmp) DO UPDATE SET 
            name_vmp=excluded.name_vmp,
            last_changed_date=excluded.last_changed_date,
            last_changed_time=excluded.last_changed_time
    """,
        produkter_til_db,
    )

    conn.commit()

    if antall_i_denne_bolken < MAX_RESULTS:
        break

    start += MAX_RESULTS
    time.sleep(1.2)

conn.close()
print("-" * 50)
print(f"Suksess! Katalogen i {db_navn} er oppdatert.")
