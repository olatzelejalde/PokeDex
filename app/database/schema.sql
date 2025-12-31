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

-- 7. INTSIGNIA
CREATE TABLE IF NOT EXISTS intsignia (
    izena TEXT PRIMARY KEY,
    deskribapena TEXT NOT NULL,
    helburua TEXT NOT NULL
);

-- 8. ERABILTZAILEAK INTSIGNIAK
CREATE TABLE IF NOT EXISTS erabiltzaileak_intsigniak (
    erabiltzaile_id INTEGER NOT NULL,
    intsignia_izena TEXT NOT NULL,
    jarraipena INTEGER DEFAULT 0,
    eguna_ordua TEXT DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (erabiltzaile_id, intsignia_izena),
    FOREIGN KEY(erabiltzaile_id) REFERENCES erabiltzailea(id),
    FOREIGN KEY(intsignia_izena) REFERENCES intsignia(izena)
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