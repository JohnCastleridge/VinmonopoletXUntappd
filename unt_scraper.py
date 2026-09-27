"""
unt_scraper.py - Handles integration with the Untappd API/search.
Provides functions for searching Untappd, fetching beer details, and matching Vinmonopolet products against Untappd data.
"""
import sqlite3
import requests
import urllib.parse
import difflib
import re

# Algolia credentials for Untappd Search (Public API for search)
ALGOLIA_APP_ID = "9WBO4RQ3HO"
ALGOLIA_API_KEY = "1d347324d67ec472bb7132c66aead485"
ALGOLIA_URL = "https://9wbo4rq3ho-dsn.algolia.net/1/indexes/*/queries"

DB_PATH = "vmp_untappd_new.db"

def search_untappd(query: str, hits_per_page=15) -> list:
    """
    Søker på Untappd via deres Algolia Search API.
    """
    headers = {
        "X-Algolia-Application-Id": ALGOLIA_APP_ID,
        "X-Algolia-API-Key": ALGOLIA_API_KEY,
    }
    
    # URL-encode spørringen for å unngå feil med spesialtegn
    encoded_query = urllib.parse.quote(query)
    data = {
        "requests": [
            {
                "indexName": "beer",
                "params": f"query={encoded_query}&hitsPerPage={hits_per_page}"
            }
        ]
    }
    import time
    time.sleep(0.3) # Sørg for at VI ALLTID tar en liten pause før HVERT ENESTE søk
    
    try:
        resp = requests.post(ALGOLIA_URL, headers=headers, json=data, timeout=10)
        if resp.status_code == 200:
            hits = resp.json()["results"][0]["hits"]
            # EKSLUDER HJEMMEBRYGG: Vinmonopolet selger aldri hjemmebrygg
            hits = [h for h in hits if h.get("homebrew") != 1]
            return hits
        elif resp.status_code in (429, 403):
            raise Exception(f"Algolia blokkerte søket (Status: {resp.status_code}) - Mulig rate limit!")
        else:
            print(f"Advarsel: Fikk statuskode {resp.status_code} fra Algolia.")
    except Exception as e:
        print(f"Algolia search error: {e}")
        # Vi vil kaste feilen videre hvis vi blir blokkert, slik at vi ikke lagrer 0% på alt
        if "blokkerte" in str(e) or "429" in str(e):
            raise
        
    return []

def clean_vmp_name_for_search(name: str) -> str:
    """Fjerner vanlige ølstiler fra navnet for å gjøre søket bredere på Untappd."""
    styles_to_remove = [
        r'\bipa\b', r'\bindia pale ale\b', r'\bneipa\b', r'\bdipa\b', r'\btipa\b',
        r'\bdouble ipa\b', r'\btriple ipa\b', r'\bhazy ipa\b', r'\bsession ipa\b',
        r'\bwest coast ipa\b', r'\bwest coast\b', r'\beast coast ipa\b', r'\bnew england ipa\b', r'\bnew england pale ale\b',
        r'\bpale ale\b', r'\bale\b', r'\bstout\b', r'\bporter\b', r'\bbaltic porter\b',
        r'\bimperial stout\b', r'\bpastry stout\b', r'\bsour\b', r'\bfruited sour\b',
        r'\bsour ale\b', r'\bpilsner\b', r'\bpils\b', r'\blager\b', r'\bhefeweizen\b',
        r'\bweissbier\b', r'\bwheat\b', r'\bbock\b', r'\bbarley wine\b', r'\bsaison\b',
        r'\blambic\b', r'\bgeuze\b', r'\bberliner weisse\b', r'\bgose\b', r'\bcider\b',
        r'\bsider\b', r'\bmead\b', r'\bmjød\b', r'\bblond\b', r'\bblonde\b', r'\bquadrupel\b',
        r'\btripel\b', r'\bdubbel\b', r'\bamber\b', r'\bbarleywine\b', r'\bimperial\b',
        r'\bdouble\b', r'\bsmoothie\b', r'\bx\b', r'\bcollab\b', r'\bcollaboration\b',
        r'\bindiaøl\b', r'\bdobbel\b', r'\btrippel\b', r'\bhveteøl\b', r'\bklosterøl\b',
        r'\bthe\b', r'\ba\b', r'\ban\b', r'\band\b', r'\bof\b', r'\bden\b', r'\bdet\b', r'\bde\b',
        r'\bba\b', r'\bbarrel aged\b', r'\bbourbon ba\b', r'\bbourbon barrel aged\b'
    ]
    
    # Sorterer på lengde, slik at "hazy ipa" fjernes før "ipa" (ellers står "hazy " igjen)
    styles_to_remove.sort(key=len, reverse=True)
    
    clean_name = name.lower()
    for pattern in styles_to_remove:
        clean_name = re.sub(pattern, '', clean_name)
    
    # Fjern doble mellomrom og spesialtegn som kan ødelegge
    clean_name = re.sub(r'[^a-z0-9æøåäöü\s]', ' ', clean_name)
    return re.sub(r'\s+', ' ', clean_name).strip()

def calculate_confidence(vmp_name: str, vmp_brewery: str, vmp_abv: float, unt_beer: dict, linked_brewery_id: int = None) -> float:
    """
    Regner ut en "Match Confidence" (0-100%) ved å sammenligne data fra Polet med Untappd.
    """
    unt_name = unt_beer.get("beer_name", "")
    unt_brewery = unt_beer.get("brewery_name", "")
    unt_abv = unt_beer.get("beer_abv") or 0.0
    
    # Hjelpefunksjon for å beregne likhet mellom to strenger
    def text_match_score(a: str, b: str) -> float:
        if not a or not b: return 0.0
        
        # Fallback difflib (bokstav for bokstav, bra for skrivefeil)
        diff = difflib.SequenceMatcher(None, a, b).ratio()
        
        # Hvis de er kliss like
        if a == b: return 1.0
            
        # Hvor mange ord fra den korteste strengen finnes i den lengste?
        words_a = set(re.findall(r'\w+', a))
        words_b = set(re.findall(r'\w+', b))
        
        if words_a and words_b:
            if len(words_a) <= len(words_b):
                overlap = len(words_a.intersection(words_b)) / len(words_a)
                extra_words = len(words_b) - len(words_a)
            else:
                overlap = len(words_b.intersection(words_a)) / len(words_b)
                extra_words = len(words_a) - len(words_b)
                
            # Maks 95% score på subset-match.
            # Vi trekker bittelitt (0.5 prosentpoeng) for hvert "overflødig" ord. 
            # Dette fungerer som tie-breaker slik at navnet med minst "fluff" vinner!
            subset_score = (overlap * 0.95) - (extra_words * 0.005)
            diff = max(diff, subset_score)
            
        return diff

    # 1. Bryggeri-match
    vmp_brewery_clean = vmp_brewery.lower().replace("bryggeri", "").replace("brewery", "").strip()
    unt_brewery_clean = unt_brewery.lower().replace("bryggeri", "").replace("brewery", "").strip()
    
    if linked_brewery_id and unt_beer.get("brewery_id") == linked_brewery_id:
        brewery_score = 1.0
    else:
        brewery_score = text_match_score(vmp_brewery_clean, unt_brewery_clean)
        
        # SJEKK FOR SUB-BRANDS / COLLABS:
        # Hvis Untappd-bryggeriet sitt første hovedord finnes inni det fulle VMP-navnet (f.eks "Bryggerhuset" inni "Aass Bryggerhuset...")
        unt_brewery_words = unt_brewery_clean.split()
        if unt_brewery_words and len(unt_brewery_words[0]) > 4 and unt_brewery_words[0] in vmp_name.lower():
            brewery_score = max(brewery_score, 0.85)
        # Samme motsatt vei
        if vmp_brewery_clean and len(vmp_brewery_clean) > 4 and vmp_brewery_clean in unt_brewery_clean:
            brewery_score = max(brewery_score, 0.85)
        
    # 2. Navne-match
    # Fjerner bryggerinavnet fra ølnavnet hvis det er bakt inn (typisk på Vinmonopolet)
    clean_vmp_name = vmp_name.lower().replace(vmp_brewery_clean, "").strip()
    clean_unt_name = unt_name.lower().replace(unt_brewery_clean, "").strip()
    
    name_score = text_match_score(clean_vmp_name, clean_unt_name)
    
    # Basis-score: Hvis navnet er nesten identisk, stoler vi mer på navnet enn bryggeriet
    if name_score >= 0.85:
        base_score = (brewery_score * 0.2) + (name_score * 0.8)
    else:
        base_score = (brewery_score * 0.5) + (name_score * 0.5)
    
    # 3. Fleksibel ABV-straff
    if unt_abv == 0.0 or vmp_abv == 0.0:
        # Hvis en av sidene mangler ABV helt, gir vi ingen straff
        abv_penalty = 0.0
    else:
        abv_diff = abs(vmp_abv - unt_abv)
        if abv_diff <= 0.2:
            abv_penalty = 0.0       # Perfekt match
        elif abv_diff <= 0.6:
            abv_penalty = 0.10      # Liten forskjell, trekk 10%
        elif abv_diff <= 1.2:
            abv_penalty = 0.25      # Medium forskjell, trekk 25%
        elif abv_diff <= 2.5:
            abv_penalty = 0.50      # Stor forskjell, trekk 50%
        else:
            abv_penalty = 0.80      # Helt ulikt, trekk 80% (trolig feil øl)
            
        # SIKKERHETSNETT:
        # Hvis navnet og bryggeriet er en ekstremt god match (> 85% tekstlikhet), 
        # er det mest sannsynlig riktig øl, men feil i registreringen av årgang/ABV.
        # Da capper vi straffen til maks 20% slik at ølet fortsatt vil matche.
        if name_score >= 0.85 and brewery_score >= 0.80:
            abv_penalty = min(abv_penalty, 0.20)
            
    confidence = (base_score - abv_penalty) * 100
    return max(0.0, confidence)

def match_vmp_to_untappd(vmp_id: int | str, db_path: str = DB_PATH, dry_run: bool = False) -> dict | None:
    """
    Tar inn et vmp_id, slår det opp i lokal database, søker på Untappd,
    og returnerer beste match med en confidence-score.
    """
    conn = sqlite3.connect(db_path, timeout=60)
    cur = conn.cursor()
    cur.execute('''
        SELECT p.name, pr.name as brewery, p.abv, p.vintage, pr.id as producer_id, ub.brewery_name, pr.unt_brewery_id
        FROM vmp_products p
        LEFT JOIN vmp_producers pr ON p.producer_id = pr.id
        LEFT JOIN unt_breweries ub ON pr.unt_brewery_id = ub.brewery_id
        WHERE p.product_id_vmp = ?
    ''', (int(vmp_id),))
    row = cur.fetchone()
    conn.close()
    
    if not row:
        print(f"Fant ikke VMP-ID {vmp_id} i databasen.")
        return None
        
    vmp_name, vmp_brewery, vmp_abv, vmp_vintage, producer_id, unt_brewery_name, linked_unt_brewery_id = row
    if not vmp_brewery: vmp_brewery = ""
    if not vmp_abv: vmp_abv = 0.0
    
    hits = []
    
    # Hjelpefunksjon for å unngå dupliserte ord (f.eks. "Nøgne Ø Nøgne Ø #100")
    def build_query(*parts):
        combined = " ".join(p for p in parts if p)
        seen = set()
        unique_words = []
        for w in combined.split():
            if w.lower() not in seen:
                seen.add(w.lower())
                unique_words.append(w)
        return " ".join(unique_words)

    candidates = []
    global_best_match = None
    global_best_score = -1.0
    
    def try_search(query, desc):
        nonlocal global_best_match, global_best_score, candidates
        print(desc + f" '{query}'")
        res = search_untappd(query)
        if not res:
            return False
            
        candidates.extend(res)
        found_good = False
        for hit in res:
            score = calculate_confidence(vmp_name, vmp_brewery, vmp_abv, hit, linked_unt_brewery_id)
            if score > global_best_score:
                global_best_score = score
                global_best_match = hit
                if score >= 75.0:
                    found_good = True
        return found_good

    # 1. Prøv Untappd-bryggerinavn
    done = False
    if unt_brewery_name:
        query = build_query(unt_brewery_name, vmp_name, vmp_vintage)
        done = try_search(query, "Søker med eksisterende bryggerikobling:")
        
    # 2. VMP-bryggerinavn
    if not done:
        query = build_query(vmp_brewery, vmp_name, vmp_vintage)
        done = try_search(query, "Søker med VMP-bryggeri:")
        
    cleaned_name = clean_vmp_name_for_search(vmp_name)
    
    # 3. Renset navn
    if not done and cleaned_name and cleaned_name != vmp_name.lower():
        query = build_query(vmp_brewery, cleaned_name, vmp_vintage)
        done = try_search(query, "Prøver uten ølstil:")
            
    # 4. Kun renset navn (uten bryggeri)
    if not done:
        query = build_query(cleaned_name, vmp_vintage)
        done = try_search(query, "Prøver kun renset navn:")
        
    # 4.5. Uten årgang
    if not done and vmp_vintage:
        print(f"Prøver uten årgang {vmp_vintage}...")
        query = build_query(unt_brewery_name or vmp_brewery, cleaned_name)
        done = try_search(query, " -> Med bryggeri:")
        if not done:
            query = build_query(cleaned_name)
            done = try_search(query, " -> Uten bryggeri:")
            
    # 5. DESPERAT FALLBACK
    if not done:
        words = cleaned_name.split()
        if len(words) > 2:
            print("Desperat søk: Prøver å fjerne ord fra slutten (ett og ett)...")
            for i in range(len(words)-1, 1, -1):
                test_query = " ".join(words[:i])
                if try_search(test_query, f" -> Fjerner ord fra slutten:"):
                    done = True
                    break

        if not done and len(words) >= 3:
            print("Desperat søk 2: Prøver å fjerne enkeltord fra midten for å finne skjulte treff...")
            for i in range(len(words)-1, -1, -1):
                test_query = " ".join(words[:i] + words[i+1:])
                if try_search(test_query, f" -> Fjerner ordet '{words[i]}':"):
                    done = True
                    break
                    
    if not candidates:
        print("Ingen treff på Untappd i det hele tatt.")
        return None
        
    print(f"\nFant {len(candidates)} potensielle kandidater (viser kun de unike i testmodus):")
    # For visning: vi bruker et set for å ikke printe samme øl flere ganger
    seen_bids = set()
    for hit in candidates:
        bid = hit.get('bid')
        if bid not in seen_bids:
            seen_bids.add(bid)
            score = calculate_confidence(vmp_name, vmp_brewery, vmp_abv, hit, linked_unt_brewery_id)
            print(f" - {hit.get('brewery_name')} - {hit.get('beer_name')} (Score: {score:.1f}%)")
            
    best_match = global_best_match
    best_score = global_best_score
            
    print("\n" + "="*50)
    print("BESTE MATCH:")
    print("="*50)
    print(f"VMP: {vmp_brewery} - {vmp_name} ({vmp_abv}%)")
    
    if best_match:
        print(f"UNT: {best_match.get('brewery_name')} - {best_match.get('beer_name')} ({best_match.get('beer_abv')}%)")
        print(f"Match Confidence: {best_score:.1f}%")
        unt_url = f"https://untappd.com/b/{best_match.get('beer_slug')}/{best_match.get('bid')}"
        print(f"Untappd URL: {unt_url}")
        
    if dry_run:
        print("\n[DRY RUN] Lagrer ikke resultatet i databasen. Test ferdig.")
        return {"match": best_match, "confidence": best_score}
        
    # Lagre i databasen uansett resultat
    conn = sqlite3.connect(db_path, timeout=60)
    cur = conn.cursor()
    
    if best_match:
        
        beer_id = best_match.get("bid")
        brewery_id = best_match.get("brewery_id")
        
        beer_url = f"https://untappd.com/b/{best_match.get('beer_slug')}/{beer_id}"
        brewery_slug = best_match.get('brewery_slug')
        brewery_url = f"https://untappd.com/brewery/{brewery_slug}" if brewery_slug else f"https://untappd.com/brewery/{brewery_id}"
        
        # 1. Oppdater / Insert bryggeri i unt_breweries
        geoloc = best_match.get("_geoloc", {})
        cur.execute('''
            INSERT INTO unt_breweries (brewery_id, brewery_name, brewery_url, brewery_label, lat, lng)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(brewery_id) DO UPDATE SET
                brewery_name=excluded.brewery_name,
                brewery_url=excluded.brewery_url,
                brewery_label=excluded.brewery_label,
                lat=excluded.lat,
                lng=excluded.lng
        ''', (
            brewery_id, 
            best_match.get("brewery_name"), 
            brewery_url,
            best_match.get("brewery_label"),
            geoloc.get("lat"),
            geoloc.get("lng")
        ))
        
        # Fiks for ugyldig default bilde fra Untappd
        unt_image = best_match.get("beer_label_hd") or best_match.get("beer_label")
        if unt_image in ("https://assets.untappd.com/", "https://assets.untappd.com/site/assets/images/temp/badge-beer-default.png"):
            unt_image = None
            
        # 2. Oppdater / Insert øl i unt_beers
        import json
        awards = json.dumps(best_match.get("community_awards", []))
        
        # Håndter style (unt_styles table)
        beer_style_str = best_match.get("type_name")
        style_id = None
        if beer_style_str:
            cur.execute("INSERT OR IGNORE INTO unt_styles (name) VALUES (?)", (beer_style_str,))
            cur.execute("SELECT id FROM unt_styles WHERE name = ?", (beer_style_str,))
            res = cur.fetchone()
            style_id = res[0] if res else None
        
        cur.execute('''
            INSERT INTO unt_beers (
                bid, beer_name, beer_style, style_id, beer_abv, beer_ibu, beer_url, beer_label, rating_score, rating_count,
                is_beer, popularity, in_production, has_community_award, community_awards, index_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(bid) DO UPDATE SET
                beer_name=excluded.beer_name,
                beer_style=excluded.beer_style,
                style_id=excluded.style_id,
                beer_abv=excluded.beer_abv,
                beer_ibu=excluded.beer_ibu,
                beer_url=excluded.beer_url,
                beer_label=excluded.beer_label,
                rating_score=excluded.rating_score,
                rating_count=excluded.rating_count,
                is_beer=excluded.is_beer,
                popularity=excluded.popularity,
                in_production=excluded.in_production,
                has_community_award=excluded.has_community_award,
                community_awards=excluded.community_awards,
                index_date=excluded.index_date,
                last_synced_unt=CURRENT_TIMESTAMP
        ''', (
            beer_id, 
            best_match.get("beer_name"),
            best_match.get("type_name"), # Algolia kaller dette 'type_name'
            style_id,
            best_match.get("beer_abv"),
            best_match.get("beer_ibu") or 0,
            beer_url,
            unt_image,
            best_match.get("rating_score"), 
            best_match.get("rating_count"),
            best_match.get("parent_style_is_beer", 1),
            best_match.get("popularity", 0),
            best_match.get("in_production", 1),
            1 if best_match.get("has_community_award") else 0,
            awards,
            best_match.get("index_date")
        ))
        
        # 3. Oppdater / Insert kobling i unt_beer_brewery_links
        cur.execute('''
            INSERT OR IGNORE INTO unt_beer_brewery_links (bid, brewery_id)
            VALUES (?, ?)
        ''', (beer_id, brewery_id))
        
        # 4. Oppdater vmp_products med referansen
        cur.execute('''
            UPDATE vmp_products 
            SET bid = ?, match_confidence = ?
            WHERE product_id_vmp = ?
        ''', (beer_id, best_score, int(vmp_id)))
        
        # 5. Lagre bryggerikobling hvis matchen er veldig trygg
        if producer_id and best_score >= 80.0:
            cur.execute('''
                UPDATE vmp_producers
                SET unt_brewery_id = ?
                WHERE id = ? AND unt_brewery_id IS NULL
            ''', (brewery_id, producer_id))
        
    else:
        # Lagre 0 i confidence og fjern evt. link hvis ingen match ble funnet
        cur.execute('''
            UPDATE vmp_products 
            SET bid = NULL, match_confidence = 0.0
            WHERE product_id_vmp = ?
        ''', (int(vmp_id),))

    conn.commit()
    conn.close()
    
    return {"match": best_match, "confidence": best_score}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Match et VMP-produkt mot Untappd.")
    parser.add_argument("vmp_id", nargs="?", default=14243801, help="VMP ID på ølet")
    parser.add_argument("--test", action="store_true", help="Kjør i testmodus uten å lagre til databasen")
    args = parser.parse_args()
    
    if args.vmp_id == 14243801:
        print("Ingen VMP ID gitt, tester med 14243801 (Kinn Svartekunst)...")
    else:
        print(f"Kjører match for VMP ID {args.vmp_id}...")
        
    match_vmp_to_untappd(args.vmp_id, dry_run=args.test)
