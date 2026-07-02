"""
update_catalog.py – Oppdaterer vmp_all_products mot Vinmonopolet-APIet.

Logikk:
  1. Sett ALL needs_sync = 0 (frisk start)
  2. Hent alle produkter fra VMP-APIet side for side
  3. For hvert produkt:
       - Ny  (finnes ikke i DB)         → INSERT med needs_sync = 1
       - Endret dato/tid               → UPDATE, sett needs_sync = 1
       - Ikke klassifisert (is_beer=NULL) → sett needs_sync = 1
       - Uendret øl/ikke-øl            → sett needs_sync = 0 (allerede satt i steg 1)
  4. Produkter som finnes i DB men IKKE fra APIet er fjernet fra VMP:
       → sett is_discontinued = 1 i vmp_products (hvis de er øl),
         og needs_sync = 0 (de trenger ikke ny VMP-skraping)
"""

import sqlite3
import time
import requests
from datetime import datetime

# ---------------------------------------------------------------------------
# Konfigurasjon
# ---------------------------------------------------------------------------
DB_PATH    = "vmp_untappd_new.db"
API_KEY    = "0803107360064be187d02eb284f7e146"
API_URL    = "https://apis.vinmonopolet.no/products/v0/details-normal"
MAX_RESULTS = 1000        # maks per API-kall (VMP-grense)
DELAY       = 1.2         # sekunder mellom sider (maks 60 kall/min)
MAX_RETRIES = 5


def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


# ---------------------------------------------------------------------------
# API-henting med retry
# ---------------------------------------------------------------------------
def fetch_page(session: requests.Session, start: int) -> list | None:
    """Henter én side fra VMP-APIet. Returnerer liste med produkter, eller None ved feil."""
    url = f"{API_URL}?maxResults={MAX_RESULTS}&start={start}"
    headers = {"Ocp-Apim-Subscription-Key": API_KEY}

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = session.get(url, headers=headers, timeout=15)
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 429:
                wait = 10 * attempt
                log(f"  Rate limit (429) – venter {wait}s (forsøk {attempt}/{MAX_RETRIES})")
                time.sleep(wait)
            else:
                log(f"  HTTP {resp.status_code} – prøver igjen ({attempt}/{MAX_RETRIES})")
                time.sleep(3)
        except requests.exceptions.RequestException as exc:
            log(f"  Nettverksfeil: {exc} – prøver igjen ({attempt}/{MAX_RETRIES})")
            time.sleep(5)

    log("  Klarte ikke å hente side etter maks forsøk.")
    return None


# ---------------------------------------------------------------------------
# Hoved-funksjon
# ---------------------------------------------------------------------------
def update_catalog(db_path: str = DB_PATH) -> None:
    log("=== Starter oppdatering av vmp_all_products ===")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # -------------------------------------------------------------------
    # STEG 1: Reset – sett alle til needs_sync = 0
    # -------------------------------------------------------------------
    log("Steg 1: Setter needs_sync = 0 for alle eksisterende produkter...")
    cur.execute("UPDATE vmp_all_products SET needs_sync = 0")
    conn.commit()
    log(f"  {cur.rowcount} rader nullstilt")

    # Hent eksisterende produkter inn i minnet for rask oppslag
    cur.execute(
        "SELECT product_id_vmp, last_changed_date, last_changed_time, is_beer "
        "FROM vmp_all_products"
    )
    existing: dict[int, tuple] = {
        row["product_id_vmp"]: (
            row["last_changed_date"],
            row["last_changed_time"],
            row["is_beer"],
        )
        for row in cur.fetchall()
    }
    log(f"  {len(existing)} produkter lastet inn fra DB")

    # -------------------------------------------------------------------
    # STEG 2 & 3: Hent fra API og oppdater DB
    # -------------------------------------------------------------------
    log("Steg 2: Henter produkter fra Vinmonopolet-APIet...")

    session = requests.Session()
    start           = 0
    totalt_hentet   = 0
    ny_count        = 0
    oppdatert_count = 0
    uendret_count   = 0
    api_ids: set[int] = set()   # alle ID-er vi ser fra APIet

    while True:
        log(f"  Henter posisjon {start}...")
        data = fetch_page(session, start)

        if data is None:
            log("Avbryter pga. API-feil.")
            break

        if len(data) == 0:
            log("  Tom side – alle produkter hentet.")
            break

        totalt_hentet += len(data)

        inserts = []
        updates_changed = []   # (date, time, id) – endret dato/tid
        updates_unclassified = []  # (id,) – is_beer IS NULL

        for item in data:
            basic        = item.get("basic", {})
            last_changed = item.get("lastChanged", {})

            p_id   = basic.get("productId")
            name   = basic.get("productShortName")
            d_date = last_changed.get("date")
            d_time = last_changed.get("time")

            if p_id is None:
                continue

            p_id = int(p_id)
            api_ids.add(p_id)

            if p_id not in existing:
                # Nytt produkt
                inserts.append((p_id, name, d_date, d_time))
                ny_count += 1
            else:
                old_date, old_time, is_beer = existing[p_id]

                if is_beer is None:
                    # Ikke klassifisert → needs_sync = 1, oppdater navn og dato
                    updates_unclassified.append((name, d_date, d_time, p_id))
                    oppdatert_count += 1
                elif old_date != d_date or old_time != d_time:
                    # Dato/tid er endret → needs_sync = 1
                    updates_changed.append((name, d_date, d_time, p_id))
                    oppdatert_count += 1
                else:
                    # Uendret og klassifisert
                    uendret_count += 1

        # Batch-skriv til DB
        if inserts:
            cur.executemany(
                """
                INSERT INTO vmp_all_products
                    (product_id_vmp, name_raw, last_changed_date, last_changed_time,
                     is_beer, needs_sync)
                VALUES (?, ?, ?, ?, NULL, 1)
                """,
                inserts,
            )

        if updates_changed:
            cur.executemany(
                """
                UPDATE vmp_all_products
                SET name_raw           = ?,
                    last_changed_date  = ?,
                    last_changed_time  = ?,
                    needs_sync         = CASE WHEN is_beer = 1 OR is_beer IS NULL THEN 1 ELSE 0 END
                WHERE product_id_vmp = ?
                """,
                updates_changed,
            )

        if updates_unclassified:
            cur.executemany(
                """
                UPDATE vmp_all_products
                SET name_raw           = ?,
                    last_changed_date  = ?,
                    last_changed_time  = ?,
                    needs_sync         = 1
                WHERE product_id_vmp = ?
                """,
                updates_unclassified,
            )

        conn.commit()

        if len(data) < MAX_RESULTS:
            log("  Siste side nådd.")
            break

        start += MAX_RESULTS
        time.sleep(DELAY)

    # -------------------------------------------------------------------
    # STEG 4: Marker produkter som er fjernet fra VMP (utgått)
    # -------------------------------------------------------------------
    log("Steg 4: Sjekker for produkter fjernet fra VMP...")

    cur.execute(
        "SELECT product_id_vmp, is_beer FROM vmp_all_products"
    )
    all_db_ids = {row["product_id_vmp"]: row["is_beer"] for row in cur.fetchall()}

    fjernet_ids = [pid for pid in all_db_ids if pid not in api_ids]

    if fjernet_ids:
        # Merk som is_discontinued i vmp_products (kun de som er øl)
        beer_fjernet = [
            (str(pid),) for pid in fjernet_ids if all_db_ids[pid] == 1
        ]
        if beer_fjernet:
            cur.executemany(
                "UPDATE vmp_products SET is_discontinued = 1 WHERE product_id_vmp = ?",
                beer_fjernet,
            )

        # needs_sync = 0 for fjernede (trenger ikke skrapes)
        placeholders = ",".join("?" * len(fjernet_ids))
        cur.execute(
            f"UPDATE vmp_all_products SET needs_sync = 0 WHERE product_id_vmp IN ({placeholders})",
            fjernet_ids,
        )
        conn.commit()
        log(f"  {len(fjernet_ids)} produkter ikke lenger i API ({len(beer_fjernet)} øl markert som utgått)")
    else:
        log("  Ingen produkter fjernet fra VMP.")

    # -------------------------------------------------------------------
    # Oppsummering
    # -------------------------------------------------------------------
    cur.execute("SELECT COUNT(*) FROM vmp_all_products WHERE needs_sync = 1")
    trenger_sync = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM vmp_all_products WHERE needs_sync = 1 AND is_beer = 1")
    trenger_sync_ol = cur.fetchone()[0]

    conn.close()

    log("=== Ferdig! ===")
    log(f"  Totalt hentet fra API  : {totalt_hentet}")
    log(f"  Nye produkter          : {ny_count}")
    log(f"  Oppdaterte produkter   : {oppdatert_count}")
    log(f"  Uendrede produkter     : {uendret_count}")
    log(f"  Trenger sync (alle)    : {trenger_sync}")
    log(f"  Trenger sync (øl)      : {trenger_sync_ol}")


if __name__ == "__main__":
    update_catalog()
