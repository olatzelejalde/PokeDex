-- 1. MOTA
CREATE TABLE IF NOT EXISTS mota (
    izena TEXT PRIMARY KEY,
    indarra TEXT
);

-- 2. ESPEZIEA
CREATE TABLE IF NOT EXISTS espeziea (
    id INTEGER PRIMARY KEY,
    izena TEXT NOT NULL,
    mota1 TEXT NOT NULL,
    mota2 TEXT,
    osasuna INTEGER NOT NULL,
    atakea INTEGER NOT NULL,
    defentsa INTEGER NOT NULL,
    atake_berezia INTEGER NOT NULL,
    defentsa_berezia INTEGER NOT NULL,
    abiadura INTEGER NOT NULL,
    irudia TEXT NOT NULL,
    deskribapena TEXT,
    FOREIGN KEY(mota1) REFERENCES mota(izena),
    FOREIGN KEY(mota2) REFERENCES mota(izena)
);

-- 3. POKEMON
CREATE TABLE IF NOT EXISTS pokemon (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    espezie_izena TEXT NOT NULL,
    izena TEXT NOT NULL,
    FOREIGN KEY(espezie_izena) REFERENCES espeziea(izena)
);

-- 4. MUGIMENDUAK
CREATE TABLE IF NOT EXISTS mugimendua (
    izena TEXT PRIMARY KEY,
    mota TEXT NOT NULL,
    indarra INTEGER,
    zehaztasuna INTEGER,
    eragina TEXT,
    FOREIGN KEY(mota) REFERENCES mota(izena)
);

-- 5. ESPEZIEAK MUGIMENDUAK
CREATE TABLE IF NOT EXISTS jakin_dezake (
    espezie_izena TEXT NOT NULL,
    mugimendu_izena TEXT NOT NULL,
    PRIMARY KEY (espezie_izena, mugimendu_izena),
    FOREIGN KEY(espezie_izena) REFERENCES espeziea(izena),
    FOREIGN KEY(mugimendu_izena) REFERENCES mugimendua(izena)
);

-- 6. ERABILTZAILEA
CREATE TABLE IF NOT EXISTS erabiltzailea (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    izena TEXT NOT NULL,
    abizena TEXT NOT NULL,
    erabilIzena TEXT UNIQUE NOT NULL,
    pasahitza TEXT NOT NULL,
    telegramKontua TEXT,
    rola TEXT DEFAULT 'erabiltzailea'
);

-- 7. INTSIGNIA: Plataforman lortu daitezkeen intsigniak
CREATE TABLE IF NOT EXISTS intsignia (
    izena TEXT PRIMARY KEY,        -- Intsigniaren izena
    deskripzioa TEXT NOT NULL,     -- Intsigniaren azalpena, hover-eko tooltip edo informazio moduan erabiliko da
    helburua INTEGER NOT NULL      -- Intsignia lortzeko behar den ekintzen kopurua
);

-- 8. ERABILTZAILEAK INTSIGNIAK: Erabiltzaile bakoitzak duen jarraipena
CREATE TABLE IF NOT EXISTS erabiltzaileak_intsigniak (
    erabiltzaile_id INTEGER NOT NULL,       -- Erabiltzailearen ID, erabiltzailea taulatik dator
    intsignia_izena TEXT NOT NULL,         -- Intsigniaren izena, intsignia taulatik dator
    jarraipena INTEGER DEFAULT 0,          -- Zenbat ekintza burutu ditu erabiltzaileak intsignia lortzeko
    eguna_ordua TEXT DEFAULT CURRENT_TIMESTAMP, -- Azken aldiz eguneratutako data/ordua
    PRIMARY KEY (erabiltzaile_id, intsignia_izena), -- Erabiltzaile bakoitzak intsignia bakoitza bakarrik izan dezake
    FOREIGN KEY(erabiltzaile_id) REFERENCES erabiltzailea(id),  -- Lotura erabiltzailea taularekin
    FOREIGN KEY(intsignia_izena) REFERENCES intsignia(izena)    -- Lotura intsignia taularekin
);

-- 9. TALDEA
CREATE TABLE IF NOT EXISTS taldea (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    izena TEXT NOT NULL,
    erabiltzaile_id INTEGER NOT NULL,
    FOREIGN KEY(erabiltzaile_id) REFERENCES erabiltzailea(id)
);

-- 10. TALDEAK POKEMONAK (muchos a muchos)
CREATE TABLE IF NOT EXISTS ditu (
    taldea_id INTEGER NOT NULL,
    pokemon_id INTEGER NOT NULL,
    PRIMARY KEY (taldea_id, pokemon_id),
    FOREIGN KEY(taldea_id) REFERENCES taldea(id),
    FOREIGN KEY(pokemon_id) REFERENCES pokemon(id)
);

-- 11. JAKIN DEZAKE
CREATE TABLE IF NOT EXISTS daki (
    pokemon_id INTEGER NOT NULL,
    mugimendu_izena TEXT NOT NULL,
    PRIMARY KEY (pokemon_id, mugimendu_izena),
    FOREIGN KEY(pokemon_id) REFERENCES pokemon(id),
    FOREIGN KEY(mugimendu_izena) REFERENCES mugimendua(izena)
);

-- 12. NOTIFIKAZIOA
CREATE TABLE IF NOT EXISTS notifikazioa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    erabiltzaile_id INTEGER NOT NULL,
    mota TEXT NOT NULL,
    izena TEXT NOT NULL,
    deskribapena TEXT,
    eguna_ordua TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(erabiltzaile_id) REFERENCES erabiltzailea(id)
);

INSERT INTO erabiltzailea (izena, abizena, erabilIzena, pasahitza, telegramKontua, rola)
VALUES ('Admin', 'User', 'admin', 'adminpass', NULL, 'admin');

--intsignia guztiak hasieratik gordeta
INSERT INTO intsignia (izena, deskripzioa, helburua) VALUES
('Erabiltzaile bezala erregistratu', 'Plataforman erregistratu zara erabiltzaile bezala, eta hemendik aurrera funtzio guztiak erabiltzeko aukera duzu.', 1),
('Lagun eskaera bidali', 'Beste erabiltzaile bati lagun eskaera bidali diozu, zure sare soziala zabaltzen hasteko.', 1),
('6 lagun lortu', 'Guztira 6 lagun lortu dituzu, 6 erabiltzailek zure eskaerak onartu dituzte.', 6),
('Admin bihurtu', 'Administratzaile rola eskuratu duzu, eta orain kudeaketa eta kontrol funtzio bereziak dituzu eskuragarri.', 1),
('5 talde sortu', '5 talde desberdin sortu dituzu, Pokémonen konbinazio eta estrategiak antolatzeko.', 5),
('Talde bat editatu', 'Sortutako taldeetako bat editatu duzu, bere kideak edo ezarpenak aldatu dituzu.', 1),
('Talde bat ezabatu', 'Lehendik zeneukan talde bat ezabatu duzu.', 1),
('Mota bateko 4 Pokémon lortu', 'Pokémon mota baten 4 pokemon lortu dituzu.', 4),
('Talde bat partekatu', 'Zure taldeetako bat beste erabiltzaileekin partekatu duzu, zure estrategia erakusteko.', 1),
('Espezie informazioa 20 aldiz kontsultatu', 'Pokémon espezieen informazioa 20 aldiz kontsultatu duzu, datuak eta xehetasunak ikertzeko.', 20);
