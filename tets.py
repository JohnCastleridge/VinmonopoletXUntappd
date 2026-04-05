'''
# 1. Opprett oppslagstabellene først
m_cur.execute("CREATE TABLE IF NOT EXISTS countries (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)")
m_cur.execute("CREATE TABLE IF NOT EXISTS vmp_styles (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)")
m_cur.execute("CREATE TABLE IF NOT EXISTS unt_styles (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)")
m_cur.execute("CREATE TABLE IF NOT EXISTS vmp_breweries (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)")
m_cur.execute("CREATE TABLE IF NOT EXISTS unt_breweries (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)")

# 2. Opprett hovedtabellen med oppdaterte Foreign Keys
m_cur.execute("""
    CREATE TABLE IF NOT EXISTS beer_catalog (
        vmp_product_id INTEGER PRIMARY KEY, -- Varenummer på Vinmonopolet (Unik ID)
        unt_beer_id INTEGER,                -- Untappd BID

        name_vmp TEXT,                      -- Ølets navn slik det står på Polet
        name_unt TEXT,                      -- Ølets navn slik det står på Untappd

        -- Foreign Keys for bryggerier
        brewery_vmp_id INTEGER,             -- Peker til vmp_breweries
        brewery_unt_id INTEGER,             -- Peker til unt_breweries
        unt_collab_brewery_id INTEGER,      -- Peker også til unt_breweries (samarbeidsbryggeri)

        -- Kategorisering
        vmp_type TEXT,                      -- Hovedtype fra Polet ('øl', 'mjød', eller 'cider')
        vmp_style_id INTEGER,               -- Peker til vmp_styles
        unt_style_id INTEGER,               -- Peker til unt_styles

        -- Tekniske data
        abv_vmp REAL,                       -- Alkoholprosent (Vinmonopolet)
        abv_unt REAL,                       -- Alkoholprosent (Untappd)
        ibu REAL,                           -- Bitterhet (fra Untappd)

        -- Rating og popularitet
        unt_rating_score REAL,              -- Gjennomsnittlig rating (fra Untappd)
        unt_rating_count INTEGER,           -- Antall ratings (fra Untappd)

        -- Salgsinfo fra Polet
        vmp_vintage TEXT,                   -- Årgang fra Polet
        vmp_country_id INTEGER,             -- Peker til countries
        vmp_price REAL,                     -- Pris i NOK
        vmp_volume REAL,                    -- Volum i liter
        vmp_selection TEXT,                 -- Utvalg (f.eks. 'Basisutvalget')
        vmp_image_url TEXT,                 -- Lenke til bilde hos Vinmonopolet
        vmp_is_discontinued BOOLEAN,        -- Utgått på Polet? (0 eller 1)
        unt_is_checked_in BOOLEAN,          -- Har du sjekket inn ølet? (0 eller 1)

        match_confidence REAL,              -- Score (f.eks. 0.0 - 1.0) på koblingen

        -- Beskrivelser og detaljer
        description_vmp TEXT,               -- Generell beskrivelse fra Vinmonopolet
        description_unt TEXT,               -- Generell beskrivelse fra Untappd
        vmp_aroma TEXT,                     -- Lukt/aroma (fra Polet)
        vmp_taste TEXT,                     -- Smaksbeskrivelse (fra Polet)
        vmp_color TEXT,                     -- Fargebeskrivelse (fra Polet)
        vmp_packaging TEXT,                 -- Emballasjetype (f.eks. 'Glass', 'Boks')
        vmp_allergens TEXT,                 -- Allergener (fra Polet)
        vmp_method TEXT,                    -- Produksjonsmetode (fra Polet)

        -- Definerer relasjonene (Foreign Keys)
        FOREIGN KEY(brewery_vmp_id) REFERENCES vmp_breweries(id),
        FOREIGN KEY(brewery_unt_id) REFERENCES unt_breweries(id),
        FOREIGN KEY(unt_collab_brewery_id) REFERENCES unt_breweries(id),
        FOREIGN KEY(vmp_style_id) REFERENCES vmp_styles(id),
        FOREIGN KEY(unt_style_id) REFERENCES unt_styles(id),
        FOREIGN KEY(vmp_country_id) REFERENCES countries(id)
    )
""")
'''
