import sqlite3

# Dette er malen for hvordan beers.db skal se ut etter omstrukturering.
db_navn = "beers.db"
conn = sqlite3.connect(db_navn)
cur = conn.cursor()

print(f"Sjekker/oppretter databasestrukturen i '{db_navn}'...")

# 1. Oppslagstabeller (Lookup tables)
cur.execute("CREATE TABLE IF NOT EXISTS countries (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)")
cur.execute("CREATE TABLE IF NOT EXISTS styles_vmp (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)")
cur.execute("CREATE TABLE IF NOT EXISTS styles_unt (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)")
cur.execute("CREATE TABLE IF NOT EXISTS breweries_vmp (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)")
cur.execute("CREATE TABLE IF NOT EXISTS breweries_unt (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)")

# 2. Hovedtabellen for den komplette Vinmonopolet-katalogen
cur.execute("""
    CREATE TABLE IF NOT EXISTS vmp_all_products (
        id_vmp INTEGER PRIMARY KEY,
        name_vmp TEXT,
        last_changed_date TEXT,
        last_changed_time TEXT,
        is_beer INTEGER DEFAULT NULL  -- 1 = Øl, 0 = Ignorert, NULL = Ukjent
    )
""")

# 3. Hovedtabellen for øl-katalogen (Beer Catalog)
cur.execute("""
    CREATE TABLE IF NOT EXISTS beer_catalog (
        id_vmp INTEGER PRIMARY KEY,          -- Varenummer på Vinmonopolet
        id_unt INTEGER,                      -- Untappd Beer ID (BID)

        name_vmp TEXT,                       -- Navn fra Polet
        name_unt TEXT,                       -- Navn fra Untappd

        -- Foreign Keys for bryggerier
        brewery_vmp_id INTEGER,              -- Peker til breweries_vmp
        brewery_unt_id INTEGER,              -- Peker til breweries_unt
        collab_brewery_unt_id INTEGER,       -- Samarbeidsbryggeri (Untappd)

        -- Kategorisering
        type_vmp TEXT,                       -- Hovedtype fra Polet ('Øl', 'Mjød', 'Sider')
        style_vmp_id INTEGER,                -- Peker til styles_vmp
        style_unt_id INTEGER,                -- Peker til styles_unt

        -- Tekniske data
        abv_vmp REAL,                        -- Alkoholprosent (VMP)
        abv_unt REAL,                        -- Alkoholprosent (Untappd)
        ibu_unt REAL,                        -- Bitterhet (Untappd)

        -- Rating og popularitet
        rating_score_unt REAL,               -- Gjennomsnittlig rating (Untappd)
        rating_count_unt INTEGER,            -- Antall ratings (Untappd)

        -- Salgsinfo fra Polet
        vintage_vmp TEXT,                    -- Årgang
        country_vmp_id INTEGER,              -- Peker til countries
        price_vmp REAL,                      -- Pris i NOK
        volume_vmp REAL,                     -- Volum i liter
        selection_vmp TEXT,                  -- Utvalg (f.eks. 'Basisutvalget')
        image_url_vmp TEXT,                  -- Bilde-URL
        is_discontinued_vmp BOOLEAN,         -- Utgått? (0 eller 1)

        match_confidence REAL,               -- Score på koblingen mellom VMP og Untappd

        -- Beskrivelser og detaljer fra Polet
        description_unt TEXT,                -- Beskrivelse fra Untappd
        aroma_vmp TEXT,                      -- Lukt
        taste_vmp TEXT,                      -- Smak
        color_vmp TEXT,                      -- Farge
        packaging_vmp TEXT,                  -- Emballasje
        allergens_vmp TEXT,                  -- Allergener
        method_vmp TEXT,                     -- Produksjonsmetode

        FOREIGN KEY(brewery_vmp_id) REFERENCES breweries_vmp(id),
        FOREIGN KEY(brewery_unt_id) REFERENCES breweries_unt(id),
        FOREIGN KEY(collab_brewery_unt_id) REFERENCES breweries_unt(id),
        FOREIGN KEY(style_vmp_id) REFERENCES styles_vmp(id),
        FOREIGN KEY(style_unt_id) REFERENCES styles_unt(id),
        FOREIGN KEY(country_vmp_id) REFERENCES countries(id)
    )
""")

conn.commit()
conn.close()

print(f"Suksess! '{db_navn}' er oppdatert i henhold til ny mal.")
