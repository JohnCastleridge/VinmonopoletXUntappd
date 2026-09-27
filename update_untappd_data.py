import sqlite3
import requests
import json
import time
import sys
import argparse

DB_PATH = "vmp_untappd_new.db"

# Algolia API informasjon (Untappds offentlige søkemotor)
ALGOLIA_APP_ID = "9WBO4RQ3HO"
ALGOLIA_API_KEY = "1d347324d67ec472bb7132c66aead485"
ALGOLIA_URL = "https://9wbo4rq3ho-dsn.algolia.net/1/indexes/*/queries"


def get_beer_by_id(bid):
    """
    Spør Algolia om data for én spesifikk Untappd-ID (bid).
    Dette returnerer eksakt det ølet uten at vi trenger å søke på navn.
    """
    headers = {
        "X-Algolia-Application-Id": ALGOLIA_APP_ID,
        "X-Algolia-API-Key": ALGOLIA_API_KEY,
    }
    data = {"requests": [{"indexName": "beer", "params": f"filters=bid={bid}"}]}
    try:
        resp = requests.post(ALGOLIA_URL, headers=headers, json=data, timeout=10)
        if resp.status_code == 200:
            res = resp.json()
            if "results" in res and len(res["results"]) > 0:
                hits = res["results"][0].get("hits", [])
                if hits:
                    return hits[0]
    except Exception as e:
        # Hvis nettverket faller ut et lite sekund, ignorerer vi det og går videre
        pass
    return None


def main():
    parser = argparse.ArgumentParser(description="Oppdater Untappd-data for eksisterende øl.")
    parser.add_argument("--limit", type=int, default=None, help="Maks antall øl som skal oppdateres i denne kjøringen.")
    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH, timeout=60)
    c = conn.cursor()

    # Hent alle unike Untappd øl vi har lagret
    c.execute("SELECT bid, beer_name FROM unt_beers ORDER BY last_synced_unt ASC NULLS FIRST")
    beers = c.fetchall()
    
    if args.limit:
        beers = beers[:args.limit]

    total = len(beers)
    if args.limit and total == args.limit:
        print(f"Hentet de {total} ølene som har ventet lengst på oppdatering...")
    else:
        print(f"Fant {total} Untappd-øl i databasen. Starter oppdatering av ferske data...")
    print("Dette kan ta litt tid (ca. 3 øl i sekundet for å unngå IP-blokkering).\\n")

    updated_count = 0

    for i, (bid, name) in enumerate(beers, 1):
        hit = get_beer_by_id(bid)
        if hit:
            # Hent ut de ferske tallene
            rating_score = hit.get("rating_score") or 0.0
            rating_count = hit.get("rating_count") or 0
            popularity = hit.get("popularity") or 0

            in_production = hit.get("in_production")
            if in_production is None:
                in_production = 1  # Antar i produksjon hvis feltet helt mangler

            has_community_award = 1 if hit.get("has_community_award") else 0
            awards_json = json.dumps(hit.get("community_awards", []))
            index_date = hit.get("index_date", "")

            # Smekk tallene rett inn i databasen for denne eksakte IDen
            c.execute(
                """
                UPDATE unt_beers 
                SET rating_score = ?,
                    rating_count = ?,
                    popularity = ?,
                    in_production = ?,
                    has_community_award = ?,
                    community_awards = ?,
                    index_date = ?,
                    last_synced_unt = CURRENT_TIMESTAMP
                WHERE bid = ?
            """,
                (
                    rating_score,
                    rating_count,
                    popularity,
                    in_production,
                    has_community_award,
                    awards_json,
                    index_date,
                    bid,
                ),
            )

            updated_count += 1

        # Enkel terminal-oppdatering på samme linje slik at den ikke fyller hele skjermen
        safe_name = (name[:35] + "..") if len(name) > 35 else name
        sys.stdout.write(f"\\rOppdatert {i}/{total} [{safe_name:<37}]")
        sys.stdout.flush()

        # Lagre til disk for hvert øl for å slippe databaselåsen (veldig viktig når vi sover i 0.3 sekunder)
        conn.commit()

        # VELDIG VIKTIG PAUSE for å unngå å bli blokkert av Algolia (rate limits)
        time.sleep(0.3)

    conn.commit()
    conn.close()
    print()

    # 2. Print statusmeldingen på en ny, ren linje (med riktig singel \n for ekstra mellomrom etterpå)
    print(f"Ferdig! Hentet ferske ratinger og data for {updated_count} øl.\n")


if __name__ == "__main__":
    main()
