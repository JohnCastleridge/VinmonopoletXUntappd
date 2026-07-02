"""
sync_vmp.py – Itererer over vmp_all_products og oppdaterer alle som har needs_sync = 1.

Dette skriptet er ment for regelmessig kjøring (f.eks. via cron eller Task Scheduler) 
etter at update_catalog.py har markert hvilke produkter som trenger oppdatering.

Bruker scrape_vmp_product() fra vmp_scraper.py.
Respekterer VMP-rate-limit (~60 kall/min → 1.2s delay).
"""

import sqlite3
import time
from vmp_scraper import scrape_vmp_product

# ---------------------------------------------------------------------------
# Konfigurasjon
# ---------------------------------------------------------------------------
DB_PATH = "vmp_untappd_new.db"
DELAY   = 2.5   # sekunder mellom hvert kall

# ---------------------------------------------------------------------------
# Hent liste over produkter som skal oppdateres
# ---------------------------------------------------------------------------
def get_pending_ids(db_path: str) -> list[int]:
    """
    Returnerer en liste med product_id_vmp for alle produkter hvor needs_sync = 1.
    """
    conn = sqlite3.connect(db_path)
    cur  = conn.cursor()

    cur.execute("""
        SELECT product_id_vmp
        FROM vmp_all_products
        WHERE needs_sync = 1
    """)
    
    rows = cur.fetchall()
    conn.close()

    # Sorterer listen for forutsigbar rekkefølge
    return sorted([row[0] for row in rows])


# ---------------------------------------------------------------------------
# Hoved-løkke
# ---------------------------------------------------------------------------
def sync_all(db_path: str = DB_PATH) -> None:
    pending = get_pending_ids(db_path)
    total   = len(pending)

    if total == 0:
        print("Ingen produkter trenger oppdatering (needs_sync = 0 for alle).")
        return

    print(f"Fant {total} produkter med needs_sync = 1 som skal oppdateres.")
    print("-" * 50)

    ok_count   = 0
    fail_count = 0

    for i, pid in enumerate(pending, start=1):
        print(f"[{i}/{total}] Oppdaterer ID={pid}...")
        success = scrape_vmp_product(pid, db_path)

        if success:
            ok_count += 1
        else:
            fail_count += 1

        # Vent etter hvert kall, unntatt det aller siste
        if i < total:
            time.sleep(DELAY)

    print("-" * 50)
    print(f"Ferdig! OK: {ok_count}  Feil: {fail_count}  Totalt: {total}")


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    sync_all()
