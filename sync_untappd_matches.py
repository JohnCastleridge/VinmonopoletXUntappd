"""
sync_untappd_matches.py - Synchronizes beer matching between Vinmonopolet products and Untappd data.
Iterates through products in the database and calls the Untappd scraper to find matches.
"""
import sqlite3
from unt_scraper import match_vmp_to_untappd

DB_PATH = "vmp_untappd_new.db"

import time

def sync_all_untappd_matches():
    print("Starter synkronisering av Untappd-matcher for alle øl...")
    
    conn = sqlite3.connect(DB_PATH, timeout=60)
    cur = conn.cursor()
    
    # Hent alle VMP-produkter som er under kategorien "Øl" (og Mjød/Sider hvis ønskelig, men vi starter med Øl)
    # Filtrer evt på de som mangler match_confidence, eller iterer over alt. 
    cur.execute('''
        SELECT p.product_id_vmp
        FROM vmp_products p
        LEFT JOIN vmp_categories c ON p.category_id = c.id
        LEFT JOIN unt_beers u ON p.bid = u.bid
        WHERE c.category_main IN ('Øl', 'Mjød', 'Sider')
    ''')
    
    beers = cur.fetchall()
    conn.close()
    
    total = len(beers)
    print(f"Fant {total} produkter som skal sjekkes mot Untappd.")
    
    for i, row in enumerate(beers, 1):
        vmp_id = row[0]
        print(f"\n[{i}/{total}] Behandler VMP ID {vmp_id}...")
        
        try:
            match_vmp_to_untappd(vmp_id)
            time.sleep(0.5) # Vær snill med Algolia
        except Exception as e:
            print(f"Feil under matching av {vmp_id}: {e}")
            if "blokkerte" in str(e) or "429" in str(e):
                print("\nAvbryter synkronisering for å unngå permanent utestengelse.")
                break

if __name__ == "__main__":
    sync_all_untappd_matches()
