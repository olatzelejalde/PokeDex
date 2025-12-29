/*SOZIALA*/
CREATE TABLE IF NOT EXISTS erabiltzailea (
    erabiltzaileIzena VARCHAR(50) PRIMARY KEY,
    izena VARCHAR(100) NOT NULL,
    abizena VARCHAR(100) NOT NULL,
    pasahitza VARCHAR(100) NOT NULL,
    rola VARCHAR(50) NOT NULL DEFAULT 'erabiltzailea'
);

CREATE TABLE IF NOT EXISTS jarraitu (
    erabiltzaileIzena1 VARCHAR(50),
    erabiltzaileIzena2 VARCHAR(50),
    PRIMARY KEY (erabiltzaileIzena1, erabiltzaileIzena2),
    FOREIGN KEY (erabiltzaileIzena1) REFERENCES erabiltzailea(erabiltzaileIzena) ON DELETE CASCADE,
    FOREIGN KEY (erabiltzaileIzena2) REFERENCES erabiltzailea(erabiltzaileIzena) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS notifikazioMota (
    mota VARCHAR(50) PRIMARY KEY,
);

CREATE TABLE IF NOT EXISTS bidali (
    erabiltzaileIzena VARCHAR(50) PRIMARY KEY,
    notifikazioMota VARCHAR(50) PRIMARY KEY,
    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP PRIMARY KEY,
    deskribapena VARCHAR(255) NOT NULL,
    FOREIGN KEY (erabiltzaileIzena) REFERENCES erabiltzailea(erabiltzaileIzena) ON DELETE CASCADE,
    FOREIGN KEY (notifikazioMota) REFERENCES notifikazioMota(mota) ON DELETE CASCADE
);

/*POKEMON*/
CREATE TABLE IF NOT EXISTS pokemon (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    izena VARCHAR(100) NOT NULL,
    irudia VARCHAR(255) NOT NULL,
    espezieIzena VARCHAR(100),
    FOREIGN KEY (espeziea) REFERENCES espeziea(izena) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS espeziea (
    id INTEGER PRIMARY KEY,
    izena VARCHAR(100) PRIMARY KEY,
    irudia VARCHAR(255) NOT NULL,
    deskripzioa VARCHAR(500) NOT NULL,ç
    osasuna INTEGER NOT NULL,
    atakea INTEGER NOT NULL,
    defentsa INTEGER NOT NULL,
    abiadura INTEGER NOT NULL,
    defentsaBerezia INTEGER NOT NULL,
    atakeBerezia INTEGER NOT NULL,
);

CREATE TABLE IF NOT EXISTS mota (
    izena VARCHAR(50) PRIMARY KEY,
    indarra INT NOT NULL,
);

CREATE TABLE IF NOT EXISTS eragina (
    motaEraso VARCHAR(50),
    motaDefentsa VARCHAR(50),
    biderkatzailea FLOAT NOT NULL,
    PRIMARY KEY (motaEraso, motaDefentsa),
    FOREIGN KEY (motaEraso) REFERENCES mota(izena) ON DELETE CASCADE,
    FOREIGN KEY (motaDefentsa) REFERENCES mota(izena) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS dauka (
    espezieIzena VARCHAR(100),
    motaIzena VARCHAR(50),
    PRIMARY KEY (espezieIzena, motaIzena),
    FOREIGN KEY (espezieIzena) REFERENCES espeziea(izena) ON DELETE CASCADE,
    FOREIGN KEY (motaIzena) REFERENCES mota(izena) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS eboluzionatu (
    aurrekoEspeziea VARCHAR(100),
    hurrengoEspeziea VARCHAR(100),
    PRIMARY KEY (aurrekoEspeziea, hurrengoEspeziea)
    FOREIGN KEY (aurrekoEspeziea) REFERENCES espeziea(izena) ON DELETE CASCADE,
    FOREIGN KEY (hurrengoEspeziea) REFERENCES espeziea(izena) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS mugimendua (
    izena VARCHAR(100) PRIMARY KEY,
    mota VARCHAR(50) NOT NULL,
    indarra INTEGER NOT NULL,
    zehaztasuna INTEGER NOT NULL,
    FOREIGN KEY (mota) REFERENCES mota(izena) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS daki (
    pokemonId INTEGER,
    mugimenduIzena VARCHAR(100),
    PRIMARY KEY (pokemonId, mugimenduIzena),
    FOREIGN KEY (pokemonId) REFERENCES pokemon(id) ON DELETE CASCADE,
    FOREIGN KEY (mugimenduIzena) REFERENCES mugimendua(izena) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS jakinDezake (
    espezieIzena VARCHAR(100),
    mugimenduIzena VARCHAR(100),
    PRIMARY KEY (espezieIzena, mugimenduIzena),
    FOREIGN KEY (espezieIzena) REFERENCES espeziea(izena) ON DELETE CASCADE,
    FOREIGN KEY (mugimenduIzena) REFERENCES mugimendua(izena) ON DELETE CASCADE
);

/*POKEMON ERABILTZAILEA*/
CREATE TABLE IF NOT EXISTS intsignia (
    izena VARCHAR(100) PRIMARY KEY,
    deskribapena VARCHAR(255) NOT NULL,
    helburua VARCHAR(255) NOT NULL,
);

CREATE TABLE IF NOT EXISTS jarraipena (
    intsigniaIzena VARCHAR(100) PRIMARY KEY,
    erabiltzaileIzena VARCHAR(50) NOT NULL,
    kopurua INTEGER NOT NULL,
    FOREIGN KEY (erabiltzaileIzena) REFERENCES erabiltzailea(erabiltzaileIzena) ON DELETE CASCADE,
    FOREIGN KEY (intsigniaIzena) REFERENCES intsignia(izena) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS taldea (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    izena VARCHAR(100) NOT NULL,
    erabiltzaileIzena VARCHAR(50) NOT NULL,
    FOREIGN KEY (erabiltzaileIzena) REFERENCES erabiltzailea(erabiltzaileIzena) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ditu (
    taldeaId INTEGER,
    pokemonId INTEGER,
    PRIMARY KEY (taldeaId, pokemonId),
    FOREIGN KEY (taldeaId) REFERENCES taldea(id) ON DELETE CASCADE,
    FOREIGN KEY (pokemonId) REFERENCES pokemon(id) ON DELETE CASCADE
);


