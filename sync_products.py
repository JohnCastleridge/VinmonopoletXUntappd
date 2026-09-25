"""
sync_products.py - Iterer over vmp_all_products og oppdater alle som:
  1. needs_sync = 1
  2. Er øl (is_beer = 1 ELLER is_beer IS NULL) og mangler category_id i vmp_products

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
DELAY = 12  # sekunder mellom hvert kall


# ---------------------------------------------------------------------------
# Hent liste over produkter som skal oppdateres
# ---------------------------------------------------------------------------
def get_pending_ids(db_path: str) -> list[tuple[int, str]]:
    """
    Returnerer liste av (product_id_vmp, årsak) for alle produkter som trenger skraping.
    Årsak er enten 'needs_sync' eller 'no_category'.
    """
    conn = sqlite3.connect(db_path, timeout=60)
    cur = conn.cursor()

    # 1. Alle med needs_sync = 1
    cur.execute("""
        SELECT product_id_vmp, 'needs_sync' as reason
        FROM vmp_all_products
        WHERE needs_sync = 1
    """)
    rows = cur.fetchall()
    pending = {pid: reason for pid, reason in rows}

    # 2. Produkter i vmp_products med category_id IS NULL
    #    (allerede i vmp_products men uten kategori – sider/mjød fra migrering)
    cur.execute("""
        SELECT CAST(p.product_id_vmp AS INTEGER), 'no_category' as reason
        FROM vmp_products p
        WHERE p.category_id IS NULL
    """)
    for pid, reason in cur.fetchall():
        if pid not in pending:  # ikke dobbelttell
            pending[pid] = reason

    conn.close()

    # Sorter for forutsigbar rekkefølge
    return sorted(pending.items())


# ---------------------------------------------------------------------------
# Hoved-løkke
# ---------------------------------------------------------------------------
def sync_all(db_path: str = DB_PATH) -> None:
    pending = get_pending_ids(db_path)
    total = len(pending)

    if total == 0:
        print("Ingen produkter trenger oppdatering.")
        return

    print(f"Fant {total} produkter som skal oppdateres.")
    needs_sync_count = sum(1 for _, r in pending if r == "needs_sync")
    no_category_count = sum(1 for _, r in pending if r == "no_category")
    print(f"  needs_sync   : {needs_sync_count}")
    print(f"  no_category  : {no_category_count}")
    print("-" * 50)

    ok_count = 0
    fail_count = 0

    for i, (pid, reason) in enumerate(pending, start=1):
        print(f"[{i}/{total}] ID={pid} ({reason})")
        success = scrape_vmp_product(pid, db_path)

        if success == -1:
            print("  -> Fikk HTTP 429 Too Many Requests!")
            print("  -> Setter skriptet på pause i 10 minutter (600 sekunder)...")
            time.sleep(600)
            print("  -> Våkner opp fra pausen, prøver samme produkt på nytt...")
            continue  # Går tilbake til starten av while-løkken for å prøve igjen
        elif success:
            ok_count += 1
        else:
            fail_count += 1

        # Ikke vent etter siste kall
        if i < total:
            time.sleep(DELAY)

    print("-" * 50)
    print(f"Ferdig! OK: {ok_count}  Feil: {fail_count}  Totalt: {total}")


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    sync_all()
