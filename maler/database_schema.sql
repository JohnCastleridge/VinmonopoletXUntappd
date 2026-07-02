-- =========================================
-- UNT-bryggerier:
--   - ID, navn, land, type
--   - Ratingdata
--   - Lenker (UNT, nettside, bilde)
-- =========================================
CREATE TABLE unt_breweries (
    -- Identifikatorer
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Intern bryggeri-ID
    brewery_id_unt INTEGER UNIQUE,         -- Ekstern Untappd ID for bryggeri

    -- Navn/land
    name TEXT,                             -- Bryggerinavn
    country TEXT,                          -- Land

    -- Type bryggeri
    brewery_type TEXT,                     -- 'Brewery', 'Cidery', 'Meadery', 'Contract', ...

    -- Ratingdata
    rating_score REAL,                     -- Gjennomsnittlig rating
    rating_count INTEGER,                  -- Antall ratinger

    -- Lenker
    url_unt TEXT,                          -- URL til bryggeriside på Untappd
    url_website TEXT,                      -- Bryggeriets egen nettside
    url_image TEXT                         -- Bilde/logo-URL
);


-- =========================================
-- Kobling øl ↔ bryggerier (UNT):
--   - Hvilket øl (Untappd)
--   - Hvilket bryggeri
--   - Rolle
-- =========================================
CREATE TABLE unt_beer_brewery_links (
    -- Nøkler mot øl og bryggeri
    beer_id_unt INTEGER,                   -- Referanse til unt_beers.beer_id_unt
    brewery_id INTEGER,                    -- Referanse til unt_breweries.id

    -- Rolle
    role TEXT,                             -- 'primary', 'collab', 'contract', ...

    PRIMARY KEY (beer_id_unt, brewery_id, role),

    FOREIGN KEY (beer_id_unt) REFERENCES unt_beers(beer_id_unt),
    FOREIGN KEY (brewery_id) REFERENCES unt_breweries(id)
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
    beer_id_unt INTEGER PRIMARY KEY,       -- Ekstern Untappd ID for øl
    style_id INTEGER,                      -- Referanse til unt_styles.id

    -- Navn og beskrivelse
    name TEXT,                             -- Ølnavn
    description TEXT,                      -- Beskrivelse / smaksnotat

    -- Tekniske data
    abv REAL,                              -- Alkoholprosent
    ibu INTEGER,                           -- Bitterhet (IBU)

    -- Ratingdata
    rating_score REAL,                     -- Rating
    rating_score_weighted REAL,            -- Vektet rating
    rating_count INTEGER,                  -- Antall ratinger

    -- Lenker
    url_unt TEXT,                          -- URL til ølside på Untappd
    url_website TEXT,                      -- Ølets/seriens egen nettside
    url_image TEXT,                        -- Bilde-URL for ølet

    -- Sist synk mot Untappd
    last_synced_unt TEXT DEFAULT (CURRENT_TIMESTAMP),

    FOREIGN KEY (style_id) REFERENCES unt_styles(id)
);


-- =========================================
-- Produsenter (VMP):
--   - ID
--   - Navn og land
-- =========================================
CREATE TABLE vmp_producers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Produsent-ID
    name TEXT UNIQUE,                      -- Produsentnavn
    country TEXT                           -- Land
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
    beer_id_unt INTEGER,                   -- Referanse til unt_beers.beer_id_unt
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

    FOREIGN KEY (beer_id_unt) REFERENCES unt_beers(beer_id_unt),
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
--   - Rating
--   - Kobling Untappd ↔ VMP
--   - Match-score
-- =========================================

CREATE INDEX idx_vmp_price
    ON vmp_products(price);

CREATE INDEX idx_unt_rating_weighted
    ON unt_beers(rating_score_weighted);

CREATE INDEX idx_vmp_unt_beer_fk
    ON vmp_products(beer_id_unt);

CREATE INDEX idx_vmp_match_confidence
    ON vmp_products(match_confidence);
