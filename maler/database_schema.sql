-- =========================================
-- UNT-bryggerier:
--   - ID, navn, land, type
--   - Ratingdata
--   - Lenker (UNT, nettside, bilde)
-- =========================================
CREATE TABLE unt_breweries (
    -- Identifikatorer
    brewery_id INTEGER PRIMARY KEY,        -- Ekstern Untappd ID for bryggeri (Nå Primary Key)

    -- Navn
    brewery_name TEXT,                     -- Bryggerinavn
    brewery_url TEXT,                      -- URL til bryggeriside på Untappd

    -- Lenker
    brewery_label TEXT,                    -- Bilde/logo-URL
    
    -- Lokasjon
    lat REAL,                              -- GPS Breddegrad
    lng REAL                               -- GPS Lengdegrad
);


-- =========================================
-- Kobling øl ↔ bryggerier (UNT):
--   - Hvilket øl (Untappd)
--   - Hvilket bryggeri
-- =========================================
CREATE TABLE unt_beer_brewery_links (
    -- Nøkler mot øl og bryggeri
    bid INTEGER,                           -- Referanse til unt_beers.bid
    brewery_id INTEGER,                    -- Referanse til unt_breweries.brewery_id

    PRIMARY KEY (bid, brewery_id),

    FOREIGN KEY (bid) REFERENCES unt_beers(bid),
    FOREIGN KEY (brewery_id) REFERENCES unt_breweries(brewery_id)
);


-- =========================================
-- Ølstiler (UNT):
--   - ID
--   - Stilnavn og beskrivelse
-- =========================================
CREATE TABLE unt_styles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Intern stil-ID
    name TEXT UNIQUE,                      -- Stilnavn: 'IPA', 'Stout', ...
    description TEXT                       -- Stilbeskrivelse
);


-- =========================================
-- Øl (UNT):
--   - ID, stil
--   - Navn og beskrivelse
--   - Tekniske data
--   - Ratingdata
--   - Lenker (Untappd, nettside, bilde)
--   - Sist synk mot Untappd
-- =========================================
CREATE TABLE unt_beers (
    -- Identifikatorer og stil
    bid INTEGER PRIMARY KEY,               -- Ekstern Untappd ID for øl (Nå Primary Key)

    -- Navn og stil
    beer_name TEXT,                        -- Ølnavn
    beer_style TEXT,                       -- Ølstilen (f.eks. "Stout - Imperial...")
    style_id INTEGER REFERENCES unt_styles(id), -- Referanse til stil-tabellen

    -- Tekniske data
    beer_abv REAL,                         -- Alkoholprosent
    beer_ibu INTEGER,                      -- Bitterhet (IBU)
    is_beer INTEGER,                       -- 1 hvis det er øl, 0 hvis sider/mjød etc

    -- Rating og Metadata
    rating_score REAL,                     -- Ølets gjennomsnittlige rating
    rating_count INTEGER,                  -- Antall ratinger
    popularity INTEGER,                    -- Untappds popularitetsscore
    in_production INTEGER,                 -- 1 hvis ølet fortsatt brygges, 0 hvis utgått
    has_community_award INTEGER,           -- 1 hvis ølet har vunnet priser på Untappd
    community_awards TEXT,                 -- JSON-liste over priser
    index_date TEXT,                       -- Dato ølet sist ble oppdatert på Untappd

    -- Lenker og URL
    beer_url TEXT,                         -- Full URL til ølet på Untappd
    beer_label TEXT,                       -- URL til miniatyrbilde for øletikett

    -- Sist synk mot Untappd
    last_synced_unt TEXT DEFAULT (CURRENT_TIMESTAMP)
);


-- =========================================
-- Produsenter (VMP):
--   - ID
--   - Navn og land
--   - Kobling til Untappd bryggeri
-- =========================================
CREATE TABLE vmp_producers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Produsent-ID
    name TEXT UNIQUE,                      -- Produsentnavn
    country TEXT,                          -- Land
    unt_brewery_id INTEGER REFERENCES unt_breweries(brewery_id) -- Kobling
);


-- =========================================
-- Kategorier (VMP):
--   - ID
--   - Hovedkategori og underkategori
-- =========================================
CREATE TABLE vmp_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Kategori-ID
    category_main TEXT,                    -- Hovedkategori: 'Øl', ...
    category_sub TEXT                      -- Underkategori: 'IPA', ...
);


-- =========================================
-- Produkter (VMP):
--   - VMP-ID og kobling til Untappd
--   - Produsent og kategori
--   - Navn, årgang, pris, volum, ABV
--   - Sortiment og emballasje
--   - Smaksprofil
--   - Allergener og lenker
--   - Status (utgått eller ikke)
-- =========================================
CREATE TABLE vmp_products (
    -- ID og kobling til Untappd
    product_id_vmp TEXT PRIMARY KEY,       -- VMP-produktnummer
    bid INTEGER,                           -- Referanse til unt_beers.bid
    match_confidence REAL,                 -- Match-score VMP ↔ Untappd

    -- Produsent og kategori
    producer_id INTEGER,                   -- vmp_producers.id
    category_id INTEGER,                   -- vmp_categories.id

    -- Navn, årgang, pris, volum, ABV
    name TEXT,                             -- Produktnavn
    vintage TEXT,                          -- Årgang
    price REAL,                            -- Pris (NOK)
    volume_ml INTEGER,                     -- Volum i ml
    abv REAL,                              -- Alkoholprosent

    -- Sortiment og emballasje
    selection TEXT,                        -- Utvalg (Basis, BU, osv.)
    packaging TEXT,                        -- Emballasje (flaske, boks, ...)

    -- Smaksprofil
    aroma TEXT,                            -- Aroma-beskrivelse
    taste TEXT,                            -- Smaksbeskrivelse
    color TEXT,                            -- Fargebeskrivelse
    method TEXT,                           -- Produksjonsmetode

    -- Allergener og lenker
    allergens TEXT,                        -- Allergener
    url_vmp TEXT,                          -- Produkt-URL hos VMP
    url_image TEXT,                        -- Produktbilde-URL

    -- Status
    is_discontinued INTEGER DEFAULT 0,     -- 0 = aktiv, 1 = utgått

    FOREIGN KEY (bid) REFERENCES unt_beers(bid),
    FOREIGN KEY (producer_id) REFERENCES vmp_producers(id),
    FOREIGN KEY (category_id) REFERENCES vmp_categories(id)
);


-- =========================================
-- Alle produkter (rådump fra VMP API):
--   - VMP-produkt-ID og navn (rådata)
--   - Siste endringsdato/tid
--   - Flag for om det er øl
--   - Flag for om det trenger sync mot hovedtabellene
-- =========================================
CREATE TABLE vmp_all_products (
    -- ID og navn (rådata fra VMP)
    product_id_vmp INTEGER PRIMARY KEY,    -- VMP-produktnummer (heltall)
    name_raw TEXT,                         -- Produktnavn slik det kommer fra VMP

    -- Endringstidspunkt
    last_changed_date TEXT,                -- Dato for siste endring
    last_changed_time TEXT,                -- Tid for siste endring

    -- Flag for filtrering og sync
    is_beer INTEGER DEFAULT NULL,          -- 1 = øl, 0 = ikke øl, NULL = ikke klassifisert
    needs_sync INTEGER DEFAULT 1           -- 1 = må synkes, 0 = ferdig synk
);


-- =========================================
-- Indekser (VMP og UNT):
--   - Pris
--   - Kobling Untappd ↔ VMP
--   - Match-score
-- =========================================

CREATE INDEX idx_vmp_price
    ON vmp_products(price);

CREATE INDEX idx_vmp_unt_beer_fk
    ON vmp_products(bid);

CREATE INDEX idx_vmp_match_confidence
    ON vmp_products(match_confidence);
