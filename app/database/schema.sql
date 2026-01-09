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
    eboluzio_chain_id INTEGER,
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
-- 13. ERAGINA
CREATE TABLE IF NOT EXISTS eragina (
    mota_eraso TEXT NOT NULL,
    mota_defentsa TEXT NOT NULL,
    biderkatzailea REAL NOT NULL, -- Ej: 2.0, 0.5, 0.0
    PRIMARY KEY (mota_eraso, mota_defentsa),
    FOREIGN KEY(mota_eraso) REFERENCES mota(izena),
    FOREIGN KEY(mota_defentsa) REFERENCES mota(izena)
);

-- 14. JARRAITU
CREATE TABLE IF NOT EXISTS jarraitu (
    erabiltzaile_id_1 INTEGER NOT NULL, -- El que sigue
    erabiltzaile_id_2 INTEGER NOT NULL, -- El seguido
    eguna_ordua TEXT DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (erabiltzaile_id_1, erabiltzaile_id_2),
    FOREIGN KEY(erabiltzaile_id_1) REFERENCES erabiltzailea(id),
    FOREIGN KEY(erabiltzaile_id_2) REFERENCES erabiltzailea(id)
);

INSERT INTO erabiltzailea (izena, abizena, erabilIzena, pasahitza, telegramKontua, rola)
VALUES ('Admin', 'User', 'admin', 'adminpass', NULL, 'admin');

-- A. MOTAK GEHITU
INSERT OR IGNORE INTO mota (izena, indarra) VALUES
('normala', 'fisikoa'), ('sua', 'berezia'), ('ura', 'berezia'),
('belarra', 'berezia'), ('elektrikoa', 'berezia'), ('izotza', 'berezia'),
('borroka', 'fisikoa'), ('pozoia', 'fisikoa'), ('lurra', 'fisikoa'),
('hegaldia', 'fisikoa'), ('psikikoa', 'berezia'), ('intsektua', 'fisikoa'),
('harria', 'fisikoa'), ('mamua', 'fisikoa'), ('dragoia', 'berezia'),
('iluna', 'berezia'), ('altzairua', 'fisikoa'), ('maitagarria', 'berezia');

-- B. ERAGINA ERLAZIOAK
-- ---------------------------------------------------------
-- ERAGINA TAULAREN DATU GUZTIAK (MOTEN TAULA)
-- ---------------------------------------------------------

-- 1. NORMALA (Normal)
-- Ez die mamuei eragiten, ahula harria eta altzairuaren aurka
INSERT OR IGNORE INTO eragina (mota_eraso, mota_defentsa, biderkatzailea) VALUES
('normala', 'mamua', 0.0),
('normala', 'harria', 0.5),
('normala', 'altzairua', 0.5);

-- 2. SUA (Fuego)
INSERT OR IGNORE INTO eragina (mota_eraso, mota_defentsa, biderkatzailea) VALUES
('sua', 'belarra', 2.0), ('sua', 'izotza', 2.0), ('sua', 'intsektua', 2.0), ('sua', 'altzairua', 2.0),
('sua', 'sua', 0.5), ('sua', 'ura', 0.5), ('sua', 'harria', 0.5), ('sua', 'dragoia', 0.5);

-- 3. URA (Agua)
INSERT OR IGNORE INTO eragina (mota_eraso, mota_defentsa, biderkatzailea) VALUES
('ura', 'sua', 2.0), ('ura', 'lurra', 2.0), ('ura', 'harria', 2.0),
('ura', 'ura', 0.5), ('ura', 'belarra', 0.5), ('ura', 'dragoia', 0.5);

-- 4. BELARRA (Planta)
INSERT OR IGNORE INTO eragina (mota_eraso, mota_defentsa, biderkatzailea) VALUES
('belarra', 'ura', 2.0), ('belarra', 'lurra', 2.0), ('belarra', 'harria', 2.0),
('belarra', 'sua', 0.5), ('belarra', 'belarra', 0.5), ('belarra', 'pozoia', 0.5),
('belarra', 'hegaldia', 0.5), ('belarra', 'intsektua', 0.5), ('belarra', 'dragoia', 0.5), ('belarra', 'altzairua', 0.5);

-- 5. ELEKTRIKOA (Eléctrico)
INSERT OR IGNORE INTO eragina (mota_eraso, mota_defentsa, biderkatzailea) VALUES
('elektrikoa', 'ura', 2.0), ('elektrikoa', 'hegaldia', 2.0),
('elektrikoa', 'elektrikoa', 0.5), ('elektrikoa', 'belarra', 0.5), ('elektrikoa', 'dragoia', 0.5),
('elektrikoa', 'lurra', 0.0);

-- 6. IZOTZA (Hielo)
INSERT OR IGNORE INTO eragina (mota_eraso, mota_defentsa, biderkatzailea) VALUES
('izotza', 'belarra', 2.0), ('izotza', 'lurra', 2.0), ('izotza', 'hegaldia', 2.0), ('izotza', 'dragoia', 2.0),
('izotza', 'sua', 0.5), ('izotza', 'ura', 0.5), ('izotza', 'izotza', 0.5), ('izotza', 'altzairua', 0.5);

-- 7. BORROKA (Lucha)
INSERT OR IGNORE INTO eragina (mota_eraso, mota_defentsa, biderkatzailea) VALUES
('borroka', 'normala', 2.0), ('borroka', 'izotza', 2.0), ('borroka', 'harria', 2.0), ('borroka', 'iluna', 2.0), ('borroka', 'altzairua', 2.0),
('borroka', 'pozoia', 0.5), ('borroka', 'hegaldia', 0.5), ('borroka', 'psikikoa', 0.5), ('borroka', 'intsektua', 0.5), ('borroka', 'maitagarria', 0.5),
('borroka', 'mamua', 0.0);

-- 8. POZOIA (Veneno)
INSERT OR IGNORE INTO eragina (mota_eraso, mota_defentsa, biderkatzailea) VALUES
('pozoia', 'belarra', 2.0), ('pozoia', 'maitagarria', 2.0),
('pozoia', 'pozoia', 0.5), ('pozoia', 'lurra', 0.5), ('pozoia', 'harria', 0.5), ('pozoia', 'mamua', 0.5),
('pozoia', 'altzairua', 0.0);

-- 9. LURRA (Tierra)
INSERT OR IGNORE INTO eragina (mota_eraso, mota_defentsa, biderkatzailea) VALUES
('lurra', 'sua', 2.0), ('lurra', 'elektrikoa', 2.0), ('lurra', 'pozoia', 2.0), ('lurra', 'harria', 2.0), ('lurra', 'altzairua', 2.0),
('lurra', 'belarra', 0.5), ('lurra', 'intsektua', 0.5),
('lurra', 'hegaldia', 0.0);

-- 10. HEGALDIA (Volador)
INSERT OR IGNORE INTO eragina (mota_eraso, mota_defentsa, biderkatzailea) VALUES
('hegaldia', 'belarra', 2.0), ('hegaldia', 'borroka', 2.0), ('hegaldia', 'intsektua', 2.0),
('hegaldia', 'elektrikoa', 0.5), ('hegaldia', 'harria', 0.5), ('hegaldia', 'altzairua', 0.5);

-- 11. PSIKIKOA (Psíquico)
INSERT OR IGNORE INTO eragina (mota_eraso, mota_defentsa, biderkatzailea) VALUES
('psikikoa', 'borroka', 2.0), ('psikikoa', 'pozoia', 2.0),
('psikikoa', 'psikikoa', 0.5), ('psikikoa', 'altzairua', 0.5),
('psikikoa', 'iluna', 0.0);

-- 12. INTSEKTUA (Bicho)
INSERT OR IGNORE INTO eragina (mota_eraso, mota_defentsa, biderkatzailea) VALUES
('intsektua', 'belarra', 2.0), ('intsektua', 'psikikoa', 2.0), ('intsektua', 'iluna', 2.0),
('intsektua', 'sua', 0.5), ('intsektua', 'borroka', 0.5), ('intsektua', 'pozoia', 0.5),
('intsektua', 'hegaldia', 0.5), ('intsektua', 'mamua', 0.5), ('intsektua', 'altzairua', 0.5), ('intsektua', 'maitagarria', 0.5);

-- 13. HARRIA (Roca)
INSERT OR IGNORE INTO eragina (mota_eraso, mota_defentsa, biderkatzailea) VALUES
('harria', 'sua', 2.0), ('harria', 'izotza', 2.0), ('harria', 'hegaldia', 2.0), ('harria', 'intsektua', 2.0),
('harria', 'borroka', 0.5), ('harria', 'lurra', 0.5), ('harria', 'altzairua', 0.5);

-- 14. MAMUA (Fantasma)
INSERT OR IGNORE INTO eragina (mota_eraso, mota_defentsa, biderkatzailea) VALUES
('mamua', 'psikikoa', 2.0), ('mamua', 'mamua', 2.0),
('mamua', 'iluna', 0.5),
('mamua', 'normala', 0.0);

-- 15. DRAGOIA (Dragón)
INSERT OR IGNORE INTO eragina (mota_eraso, mota_defentsa, biderkatzailea) VALUES
('dragoia', 'dragoia', 2.0),
('dragoia', 'altzairua', 0.5),
('dragoia', 'maitagarria', 0.0);

-- 16. ILUNA (Siniestro)
INSERT OR IGNORE INTO eragina (mota_eraso, mota_defentsa, biderkatzailea) VALUES
('iluna', 'psikikoa', 2.0), ('iluna', 'mamua', 2.0),
('iluna', 'borroka', 0.5), ('iluna', 'iluna', 0.5), ('iluna', 'maitagarria', 0.5);

-- 17. ALTZAIRUA (Acero)
INSERT OR IGNORE INTO eragina (mota_eraso, mota_defentsa, biderkatzailea) VALUES
('altzairua', 'izotza', 2.0), ('altzairua', 'harria', 2.0), ('altzairua', 'maitagarria', 2.0),
('altzairua', 'sua', 0.5), ('altzairua', 'ura', 0.5), ('altzairua', 'elektrikoa', 0.5), ('altzairua', 'altzairua', 0.5);

-- 18. MAITAGARRIA (Hada)
INSERT OR IGNORE INTO eragina (mota_eraso, mota_defentsa, biderkatzailea) VALUES
('maitagarria', 'borroka', 2.0), ('maitagarria', 'dragoia', 2.0), ('maitagarria', 'iluna', 2.0),
('maitagarria', 'sua', 0.5), ('maitagarria', 'pozoia', 0.5), ('maitagarria', 'altzairua', 0.5);

-- Espeziea taulari 'aurreeboluzioa' zutabea gehitu
ALTER TABLE espeziea
ADD COLUMN aurreeboluzioa INTEGER;

-- Formatua: (id, izena, mota1, mota2, osasuna, atakea, defentsa, atake_berezia, defentsa_berezia, abiadura, irudia, deskribapena, aurreeboluzioa)

-- Bulbasaur familia
INSERT INTO espeziea VALUES (1, 'Bulbasaur', 'belarra', 'pozoia', 45, 49, 49, 65, 65, 45, '1.png', 'Deskribapena...', NULL);
INSERT INTO espeziea VALUES (2, 'Ivysaur', 'belarra', 'pozoia', 60, 62, 63, 80, 80, 60, '2.png', 'Deskribapena...', 1);
INSERT INTO espeziea VALUES (3, 'Venusaur', 'belarra', 'pozoia', 80, 82, 83, 100, 100, 80, '3.png', 'Deskribapena...', 2);

-- Charmander familia
INSERT INTO espeziea VALUES (4, 'Charmander', 'sua', NULL, 39, 52, 43, 60, 50, 65, '4.png', 'Deskribapena...', NULL);
INSERT INTO espeziea VALUES (5, 'Charmeleon', 'sua', NULL, 58, 64, 58, 80, 65, 80, '5.png', 'Deskribapena...', 4);
INSERT INTO espeziea VALUES (6, 'Charizard', 'sua', 'hegaldia', 78, 84, 78, 109, 85, 100, '6.png', 'Deskribapena...', 5);

-- Squirtle familia
INSERT INTO espeziea VALUES (7, 'Squirtle', 'ura', NULL, 44, 48, 65, 50, 64, 43, '7.png', 'Deskribapena...', NULL);
INSERT INTO espeziea VALUES (8, 'Wartortle', 'ura', NULL, 59, 63, 80, 65, 80, 58, '8.png', 'Deskribapena...', 7);
INSERT INTO espeziea VALUES (9, 'Blastoise', 'ura', NULL, 79, 83, 100, 85, 105, 78, '9.png', 'Deskribapena...', 8);

-- Caterpie familia
INSERT INTO espeziea VALUES (10, 'Caterpie', 'intsektua', NULL, 45, 30, 35, 20, 20, 45, '10.png', '...', NULL);
INSERT INTO espeziea VALUES (11, 'Metapod', 'intsektua', NULL, 50, 20, 55, 25, 25, 30, '11.png', '...', 10);
INSERT INTO espeziea VALUES (12, 'Butterfree', 'intsektua', 'hegaldia', 60, 45, 50, 90, 80, 70, '12.png', '...', 11);

-- Gastly familia
INSERT INTO espeziea VALUES (92, 'Gastly', 'mamua', 'pozoia', 30, 35, 30, 100, 35, 80, '92.png', '...', NULL);
INSERT INTO espeziea VALUES (93, 'Haunter', 'mamua', 'pozoia', 45, 50, 45, 115, 55, 95, '93.png', '...', 92);
INSERT INTO espeziea VALUES (94, 'Gengar', 'mamua', 'pozoia', 60, 65, 60, 130, 75, 110, '94.png', '...', 93);

-- Rattata familia (#019 - #020)
INSERT INTO espeziea VALUES (19, 'Rattata', 'normala', NULL, 30, 56, 35, 25, 35, 72, '19.png', 'Hortz oso gogorrak ditu.', NULL);
INSERT INTO espeziea VALUES (20, 'Raticate', 'normala', NULL, 55, 81, 60, 50, 70, 97, '20.png', 'Edozer karraskatzen du.', 19);

-- Pikachu familia (#025 - #026)
INSERT INTO espeziea VALUES (25, 'Pikachu', 'elektrikoa', NULL, 35, 55, 40, 50, 50, 90, '25.png', 'Masailan argindarra gordetzen du.', NULL);
INSERT INTO espeziea VALUES (26, 'Raichu', 'elektrikoa', NULL, 60, 90, 55, 90, 80, 110, '26.png', 'Isatsarekin lurrera deskargatzen du.', 25);

-- Spearow familia (#021 - #022)
INSERT INTO espeziea VALUES (21, 'Spearow', 'normala', 'hegaldia', 40, 60, 30, 31, 31, 70, '21.png', 'Oso kaskagorra da.', NULL);
INSERT INTO espeziea VALUES (22, 'Fearow', 'normala', 'hegaldia', 65, 90, 65, 61, 61, 100, '22.png', 'Moko luze eta indartsua du.', 21);

-- Sandshrew familia (#027 - #028)
INSERT INTO espeziea VALUES (27, 'Sandshrew', 'lurra', NULL, 50, 75, 85, 20, 30, 40, '27.png', 'Lur azpian bizi da.', NULL);
INSERT INTO espeziea VALUES (28, 'Sandslash', 'lurra', NULL, 75, 100, 110, 45, 55, 65, '28.png', 'Arantzaz beteta dauka bizkarra.', 27);

-- Zubat familia (#041 - #042)
INSERT INTO espeziea VALUES (41, 'Zubat', 'pozoia', 'hegaldia', 40, 45, 35, 30, 40, 55, '41.png', 'Leize ilunetan bizi da.', NULL);
INSERT INTO espeziea VALUES (42, 'Golbat', 'pozoia', 'hegaldia', 75, 80, 70, 65, 75, 90, '42.png', 'Odola xurgatzea maite du.', 41);

-- Abra familia (#063 - #065)
INSERT INTO espeziea VALUES (63, 'Abra', 'psikikoa', NULL, 25, 20, 15, 105, 55, 90, '63.png', 'Egunean 18 ordu egiten du lo.', NULL);
INSERT INTO espeziea VALUES (64, 'Kadabra', 'psikikoa', NULL, 40, 35, 30, 120, 70, 105, '64.png', 'Koilara batekin boterea kontzentratzen du.', 63);
INSERT INTO espeziea VALUES (65, 'Alakazam', 'psikikoa', NULL, 55, 50, 45, 135, 95, 120, '65.png', 'Burmuina etengabe hazten zaio.', 64);

-- Dratini familia (#147 - #149)
INSERT INTO espeziea VALUES (147, 'Dratini', 'dragoia', NULL, 41, 64, 45, 50, 50, 50, '147.png', '...', NULL);
INSERT INTO espeziea VALUES (148, 'Dragonair', 'dragoia', NULL, 61, 84, 65, 70, 70, 70, '148.png', '...', 147);
INSERT INTO espeziea VALUES (149, 'Dragonite', 'dragoia', 'hegaldia', 91, 134, 95, 100, 100, 80, '149.png', '...', 148);

-- Eboluziorik gabeko espezieak
INSERT INTO espeziea VALUES (142, 'Aerodactyl', 'harria', 'hegaldia', 80, 105, 65, 60, 75, 130, '142.png', '...', NULL);
INSERT INTO espeziea VALUES (143, 'Snorlax', 'normala', NULL, 160, 110, 65, 65, 110, 30, '143.png', '...', NULL);
INSERT INTO espeziea VALUES (150, 'Mewtwo', 'psikikoa', NULL, 106, 110, 90, 154, 90, 130, '150.png', '...', NULL);