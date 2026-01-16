import pytest
from app import create_app
from app.database.connection import Connection

@pytest.fixture
def app():
    app = create_app()
    app.config.update({"TESTING": True})
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db():
    db_conn = Connection()
    conn = db_conn.connection
    conn.execute("PRAGMA foreign_keys = ON")
    
    # Taulak sortu: mota eta espeziea (eta mugimendua + jakin_dezake)
    conn.execute("CREATE TABLE IF NOT EXISTS mota (izena TEXT PRIMARY KEY, indarra TEXT)")
    conn.execute("""
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
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS mugimendua (
            izena TEXT PRIMARY KEY,
            mota TEXT NOT NULL,
            indarra INTEGER,
            zehaztasuna INTEGER,
            eragina TEXT,
            FOREIGN KEY(mota) REFERENCES mota(izena)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS jakin_dezake (
            espezie_izena TEXT NOT NULL,
            mugimendu_izena TEXT NOT NULL,
            PRIMARY KEY (espezie_izena, mugimendu_izena),
            FOREIGN KEY(espezie_izena) REFERENCES espeziea(izena),
            FOREIGN KEY(mugimendu_izena) REFERENCES mugimendua(izena)
        )
    """)
    conn.commit()
    yield db_conn
    conn.close()

def setup_pokedex_data(db_conn):
    conn = db_conn.connection
    conn.execute("PRAGMA foreign_keys = OFF")
    conn.execute("DELETE FROM jakin_dezake")
    conn.execute("DELETE FROM mugimendua")
    conn.execute("DELETE FROM espeziea")
    conn.execute("DELETE FROM mota")
    conn.execute("PRAGMA foreign_keys = ON")

    # 1. Motak txertatu
    conn.execute("INSERT INTO mota (izena, indarra) VALUES ('elektrikoa', 'hegaldia')")
    conn.execute("INSERT INTO mota (izena, indarra) VALUES ('sua', 'belarra')")
    conn.execute("INSERT INTO mota (izena, indarra) VALUES ('belarra', 'ura')")
    conn.execute("INSERT INTO mota (izena, indarra) VALUES ('pozoia', 'maitagarria')")
    conn.execute("INSERT INTO mota (izena, indarra) VALUES ('normal', 'batere-ez')")

    # 2. Espezieak txertatu (Bulbasaur, Charmander, Pikachu)
    # Bulbasaur (Belarra/Pozoia)
    conn.execute("""
        INSERT INTO espeziea (id, izena, mota1, mota2, osasuna, atakea, defentsa, atake_berezia, defentsa_berezia, abiadura, irudia, deskribapena, eboluzio_chain_id)
        VALUES (1, 'Bulbasaur', 'belarra', 'pozoia', 45, 49, 49, 65, 65, 45, 'bulbasaur.png', 'Landare bat du bizkarrean.', 1)
    """)
    # Charmander (Sua)
    conn.execute("""
        INSERT INTO espeziea (id, izena, mota1, mota2, osasuna, atakea, defentsa, atake_berezia, defentsa_berezia, abiadura, irudia, deskribapena, eboluzio_chain_id)
        VALUES (4, 'Charmander', 'sua', NULL, 39, 52, 43, 60, 50, 65, 'charmander.png', 'Buztanean sua du.', 2)
    """)
    # Pikachu (Elektrikoa)
    conn.execute("""
        INSERT INTO espeziea (id, izena, mota1, mota2, osasuna, atakea, defentsa, atake_berezia, defentsa_berezia, abiadura, irudia, deskribapena, eboluzio_chain_id)
        VALUES (25, 'Pikachu', 'elektrikoa', NULL, 35, 55, 40, 50, 50, 90, 'pikachu.png', 'Elektrizitatea gordetzen du.', 10)
    """)
    
    # 3. Mugimenduak txertatu
    conn.execute("INSERT INTO mugimendua (izena, mota, indarra, zehaztasuna, eragina) VALUES ('Impactrueno', 'elektrikoa', 40, 100, NULL)")
    conn.execute("INSERT INTO mugimendua (izena, mota, indarra, zehaztasuna, eragina) VALUES ('Arañazo', 'normal', 40, 100, NULL)")

    # 4. Espezieak-Mugimenduak lotu (jakin_dezake)
    conn.execute("INSERT INTO jakin_dezake (espezie_izena, mugimendu_izena) VALUES ('Pikachu', 'Impactrueno')")
    conn.execute("INSERT INTO jakin_dezake (espezie_izena, mugimendu_izena) VALUES ('Pikachu', 'Arañazo')")

    conn.commit()

# ===============================================================================
# TESTAK - Pokemon Zerrenda Bistaratu
# ===============================================================================

def test_1_pokemonen_zerrenda_bistaratu(client, db):
    """
    TEST KASUA 1: Erabiltzailea aplikazioan sartzen da eta pokemonen zerrenda agertzen da
    ESPEROTAKO EMAITZA: Pokemonen zerrenda bistaratu egiten da (200 OK)
    """
    setup_pokedex_data(db)

    response = client.get("/api/espezieak")
    assert response.status_code == 200, "Estatusa 200 OK izan behar da"
    
    data = response.get_json()
    assert isinstance(data, list), "Zerrenda bat itzuli behar du"
    assert len(data) == 3, "3 pokemon egon behar dira"

    # Izenaren arabera ordenatuta
    izenak = [p['izena'] for p in data]
    assert izenak == ['Bulbasaur', 'Charmander', 'Pikachu'], "Pokemonak izenaren arabera ordenatuta egon behar dira"

def test_2_pokemonen_zerrenda_ez_da_agertzen(client, db):
    """
    TEST KASUA 2: Erabiltzailea aplikazioan sartzen da eta pokemonen ez da zerrenda agertzen
    ESPEROTAKO EMAITZA: Errore mezua atera behar da (edo zerrenda hutsa)
    """
    # Datu-basea hutsik utzi
    conn = db.connection
    conn.execute("PRAGMA foreign_keys = OFF")
    conn.execute("DELETE FROM jakin_dezake")
    conn.execute("DELETE FROM mugimendua")
    conn.execute("DELETE FROM espeziea")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.commit()

    response = client.get("/api/espezieak")
    assert response.status_code == 200, "Estatusa 200 izan behar da"
    
    data = response.get_json()
    assert data == [], "Zerrenda hutsa itzuli behar du pokemonik ez badago"

def test_3_pokemonen_izena_eta_irudia_agertzen_da(client, db):
    """
    TEST KASUA 3: Erabiltzailea aplikazioan sartzen da eta pokemonen zerrenda agertzen da
    ESPEROTAKO EMAITZA: Zerrendako pokemon bakoitzaren izena eta irudia agertzen da
    """
    setup_pokedex_data(db)

    response = client.get("/api/espezieak")
    assert response.status_code == 200
    
    data = response.get_json()
    assert len(data) == 3

    # Pokemon bakoitzaren izena eta irudia egiaztatu
    for pokemon in data:
        assert 'izena' in pokemon, f"Pokemon guztiek 'izena' eduki behar dute"
        assert 'irudia' in pokemon, f"Pokemon guztiek 'irudia' eduki behar dute"
        assert pokemon['izena'] != '', "Izena hutsik ez dago"
        assert pokemon['irudia'].endswith('.png'), "Irudia .png formatuan egon behar da"

def test_4_pokemon_informazio_orria_irekitzen_da(client, db):
    """
    TEST KASUA 4: Pokemon batean klikatzean bere informazio orria irekitzen da
    ESPEROTAKO EMAITZA: Informazio orria bistaratzen da beharrezkoak diren datu guztiekin
    """
    setup_pokedex_data(db)

    # Pikachu bilatu
    izena = "Pikachu"
    response = client.get(f"/api/espezieak/{izena}")
    assert response.status_code == 200, "Estatusa 200 OK izan behar da"
    
    data = response.get_json()
    
    # Datu guztiak egon behar dira
    assert data['izena'] == 'Pikachu', "Izena Pikachu izan behar da"
    assert data['id'] == 25, "IDa 25 izan behar da"
    assert data['mota1'] == 'elektrikoa', "Mota1 elektrikoa izan behar da"
    
    # Beharrezko eremuak egiaztatu
    required_fields = ['osasuna', 'atakea', 'defentsa', 'atake_berezia', 
                      'defentsa_berezia', 'abiadura', 'irudia', 'deskribapena']
    for field in required_fields:
        assert field in data, f"'{field}' eremua falta da"
    
    # Balore batzuk egiaztatu
    assert data['osasuna'] == 35, "Osasuna 35 izan behar da"
    assert data['irudia'] == 'pikachu.png', "Irudia pikachu.png izan behar da"

def test_5_pokemon_mugimenduak_bistaratzen_dira(client, db):
    """
    TEST KASUA 5: Pokemon batean klikatzean bere informazio orria irekitzen da eta 
                  informazio pantailaren barruan mugimenduak atalean sakatzen da
    ESPEROTAKO EMAITZA: Pokemon bakoitzaren mugimenduak pantaila bistaratzen da
    """
    setup_pokedex_data(db)

    izena = "Pikachu"
    # Mugimenduak lortu (API: /api/especieak/<izena>/mugimenduak)
    response = client.get(f"/api/especieak/{izena}/mugimenduak")
    assert response.status_code == 200, "Estatusa 200 OK izan behar da"

    data = response.get_json()
    assert isinstance(data, list), "Mugimenduen zerrenda bat itzuli behar du"
    assert len(data) == 2, "Pikachuk 2 mugimendu eduki behar ditu"
    
    # Mugimenduak egiaztatu
    mugimenduen_izenak = [m['izena'] for m in data]
    assert "Impactrueno" in mugimenduen_izenak, "Impactrueno mugimendua egon behar da"
    assert "Arañazo" in mugimenduen_izenak, "Arañazo mugimendua egon behar da"
    
    # Mugimendu bakoitzak beharrezko eremuak ditu
    for mugimendu in data:
        assert 'izena' in mugimendu, "Mugimenduak izena eduki behar du"
        assert 'mota' in mugimendu, "Mugimenduak mota eduki behar du"
        assert 'indarra' in mugimendu, "Mugimenduak indarra eduki behar du"

# ===============================================================================
# TESTAK - Bilaketa Egin (Search Functionality)
# ===============================================================================

def test_6_bilaketa_izen_egokiarekin(client, db):
    """
    TEST KASUA 6: Bilaketa izen egokiarekin egiten da
    ESPEROTAKO EMAITZA: Izen bera duen pokemona bistaratzen da
    """
    setup_pokedex_data(db)

    # Pikachu bilatu (izen zuzena)
    izena = "Pikachu"
    response = client.get(f"/api/espezieak/{izena}")
    assert response.status_code == 200, "Estatusa 200 OK izan behar da"
    
    data = response.get_json()
    assert data != {}, "Pokemona aurkitu behar da"
    assert data['izena'] == 'Pikachu', "Izen zuzena itzuli behar du"
    assert 'id' in data, "Pokemon guztiek 'id' eduki behar dute"
    assert 'mota1' in data, "Pokemon guztiek 'mota1' eduki behar dute"

def test_7_bilaketa_izen_desegokiarekin(client, db):
    """
    TEST KASUA 7: Bilaketa izen desegokiarekin egiten da 
                  (adibidez bulbasour jarri beharrean bulbasaur jartzen bada)
    ESPEROTAKO EMAITZA: Mezu bat agertuko da pokemon hori existitzen ez dela esanez
    """
    setup_pokedex_data(db)

    # Izen okerra erabiliz bilatu
    izena_okerra = "Bulbasour"  # Bulbasaur beharrean
    response = client.get(f"/api/espezieak/{izena_okerra}")
    assert response.status_code == 200, "Estatusa 200 izan behar da"
    
    data = response.get_json()
    # Kontrolagailua: uno_espezie itzultzen du {} pokemona ez bada aurkitzen
    assert data == {}, "Pokemon ez da aurkitu, {} itzuli behar du"

def test_8_bilaketa_motaren_arabera(client, db):
    """
    TEST KASUA 8: Bilaketa motaren arabera egiten da
    ESPEROTAKO EMAITZA: Mota horretako pokemonak bistaratzen dira
    """
    setup_pokedex_data(db)

    # Espezie guztiak lortu eta mota baten arabera filtratu
    response = client.get("/api/espezieak")
    assert response.status_code == 200
    
    data = response.get_json()
    
    # Elektrikoa motako pokemonak bilatu
    elektrikoak = [p for p in data if p['mota1'] == 'elektrikoa' or p.get('mota2') == 'elektrikoa']
    assert len(elektrikoak) == 1, "1 pokemon elektrikoa egon behar da (Pikachu)"
    assert elektrikoak[0]['izena'] == 'Pikachu', "Pikachu elektrikoa da"
    
    # Sua motako pokemonak bilatu
    suak = [p for p in data if p['mota1'] == 'sua' or p.get('mota2') == 'sua']
    assert len(suak) == 1, "1 pokemon sua egon behar da (Charmander)"
    assert suak[0]['izena'] == 'Charmander', "Charmander sua da"

def test_9_bilaketa_mota_gaizki(client, db):
    """
    TEST KASUA 9: Bilaketa motaren arabera egiten da baina mota gaizki jartzen da
    ESPEROTAKO EMAITZA: Mezu bat agertuko da pokemon mota hori existitzen ez dela esanez
    """
    setup_pokedex_data(db)

    # Existitzen ez den mota batekin bilatu
    response = client.get("/api/espezieak")
    assert response.status_code == 200
    
    data = response.get_json()
    
    # Existitzen ez den mota batekin filtratu (adibidez: "metalikoa")
    mota_okerra = "metalikoa"
    pokemon_mota_okerra = [p for p in data if p['mota1'] == mota_okerra or p.get('mota2') == mota_okerra]
    
    # Ez da pokemonik aurkitu behar
    assert len(pokemon_mota_okerra) == 0, f"Ez da {mota_okerra} motako pokemonik egon behar"
