"""
sync_untappd_matches.py - Synchronizes beer matching between Vinmonopolet products and Untappd data.
Iterates through products in the database and calls the Untappd scraper to find matches.
"""
import sqlite3
import argparse
import time
from unt_scraper import match_vmp_to_untappd

DB_PATH = "vmp_untappd_new.db"

def sync_all_untappd_matches():
    parser = argparse.ArgumentParser(description="Finn Untappd-matcher for Vinmonopolet-produkter.")
    parser.add_argument("--limit", type=int, default=None, help="Maks antall produkter å sjekke i denne kjøringen.")
    parser.add_argument("--max-confidence", type=float, default=75.0, help="Sjekk bare produkter med confidence UNDER denne verdien (Standard: 75.0)")
    parser.add_argument("--force-all", action="store_true", help="Ignorer confidence-sjekk og sjekk alle produkter uansett.")
    args = parser.parse_args()

    print("Starter synkronisering av Untappd-matcher...")
    
    conn = sqlite3.connect(DB_PATH, timeout=60)
    cur = conn.cursor()
    
    if args.force_all:
        query = '''
            SELECT p.product_id_vmp, p.match_confidence, p.name
            FROM vmp_products p
            LEFT JOIN vmp_categories c ON p.category_id = c.id
            WHERE c.category_main IN ('Øl', 'Mjød', 'Sider')
            ORDER BY p.match_confidence ASC NULLS FIRST
        '''
        params = ()
    else:
        query = '''
            SELECT p.product_id_vmp, p.match_confidence, p.name
            FROM vmp_products p
            LEFT JOIN vmp_categories c ON p.category_id = c.id
            WHERE c.category_main IN ('Øl', 'Mjød', 'Sider')
            AND (p.bid IS NULL OR p.match_confidence < ?)
            ORDER BY p.match_confidence ASC NULLS FIRST
        '''
        params = (args.max_confidence,)
        
    cur.execute(query, params)
    beers = cur.fetchall()
    conn.close()

    if args.limit:
        beers = beers[:args.limit]
    
    total = len(beers)
    if total == 0:
        print(f"Fant ingen produkter som trenger matching med gjeldende kriterier (< {args.max_confidence}%).")
        return

    print(f"Fant {total} produkter som skal sjekkes mot Untappd.")
    if not args.force_all:
        print(f"(Filtrert: Sjekker kun match under {args.max_confidence}%)")
    
    for i, row in enumerate(beers, 1):
        vmp_id = row[0]
        conf = row[1] if row[1] is not None else 0.0
        name = row[2]
        
        # Kort av navnet for fin utskrift
        safe_name = (name[:30] + '..') if name and len(name) > 30 else (name or "Ukjent")
        
        print(f"\n[{i}/{total}] VMP ID {vmp_id} | Tidligere score: {conf}% | {safe_name}")
        
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
