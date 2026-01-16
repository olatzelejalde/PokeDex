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
    # Taula sortuak erabiltzailea, intsignia eta erabiltzaileak_intsigniak
    conn.execute("CREATE TABLE IF NOT EXISTS erabiltzailea (id INTEGER PRIMARY KEY AUTOINCREMENT, izena TEXT, abizena TEXT, erabilIzena TEXT UNIQUE, pasahitza TEXT, telegramKontua TEXT, chat_id INTEGER, rola TEXT DEFAULT 'erabiltzailea')")
    conn.execute("CREATE TABLE IF NOT EXISTS intsignia (izena TEXT PRIMARY KEY, deskripzioa TEXT, helburua INTEGER)")
    conn.execute("CREATE TABLE IF NOT EXISTS erabiltzaileak_intsigniak (erabiltzaile_id INTEGER, intsignia_izena TEXT, jarraipena INTEGER DEFAULT 0, eguna_ordua TEXT DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (erabiltzaile_id, intsignia_izena))")
    conn.commit()
    yield db_conn
    conn.close()

def setup_user_and_badges(db_conn):
    conn = db_conn.connection
    # Taulak garbitu test bakoitzerako
    conn.execute("PRAGMA foreign_keys = OFF")
    conn.execute("DELETE FROM erabiltzaileak_intsigniak")
    conn.execute("DELETE FROM intsignia")
    conn.execute("DELETE FROM erabiltzailea")
    conn.execute("PRAGMA foreign_keys = ON")
    
    # Erabiltzaile bat txertatu
    conn.execute("INSERT INTO erabiltzailea (id, izena, abizena, erabilIzena, pasahitza) VALUES (1, 'Jon', 'Doe', 'jon', 'pass')")
    
    # Intsigniak txertatu
    conn.execute("INSERT INTO intsignia VALUES ('Talde bat editatu', 'Sortutako taldeetako bat editatu duzu, bere kideak edo ezarpenak aldatu dituzu.', 1)")
    conn.execute("INSERT INTO intsignia VALUES ('Talde bat ezabatu', 'Lehendik zeneukan talde bat ezabatu duzu.', 1)")
    
    conn.commit()
    return 1

# -------------------------------
# TESTAK
# -------------------------------

def test_erabiltzaileak_intsigniak_lortuta_ez_daudela(client, db):
    uid = setup_user_and_badges(db)
    # Erabiltzailearen intsigniak lortu
    data = client.get(f"/api/erabiltzaileak/{uid}/intsigniak").get_json()
    # Kontrolatu ez dagoela lortutako intsigniarik
    assert len(data) == 2
    assert all(b["lortua"] == 0 for b in data)

def test_lehenengo_intsignia_lortu_da(client, db):
    uid = setup_user_and_badges(db)
    badge = "Talde bat editatu" # Helburua = 1
    
    # POST bat egin, helburua 1 denez, lortua=1 izango da
    client.post(f"/api/erabiltzaileak/{uid}/intsigniak/{badge}")
    
    data = client.get(f"/api/erabiltzaileak/{uid}/intsigniak").get_json()
    # Lortutako intsigniak filtratu
    completed = [b for b in data if b["lortua"] == 1]
    assert len(completed) == 1

def test_bi_intsignia_lortu_dira(client, db):
    uid = setup_user_and_badges(db)
    # Bi intsignia txertatu
    client.post(f"/api/erabiltzaileak/{uid}/intsigniak/Talde bat editatu")
    client.post(f"/api/erabiltzaileak/{uid}/intsigniak/Talde bat ezabatu")

    data = client.get(f"/api/erabiltzaileak/{uid}/intsigniak").get_json()
    completed = [b for b in data if b["lortua"] == 1]
    
    # Biak lortutakoak direla konprobatu
    assert len(completed) == 2

def test_intsignia_aldaketarik_gabe(client, db):
    uid = setup_user_and_badges(db)
    badge = "Talde bat editatu"
    client.post(f"/api/erabiltzaileak/{uid}/intsigniak/{badge}")
    
    # Bi dei jarraian egin eta konparatu
    first = client.get(f"/api/erabiltzaileak/{uid}/intsigniak").get_json()
    second = client.get(f"/api/erabiltzaileak/{uid}/intsigniak").get_json()
    assert first == second

def test_helburua_berriro_lortu_denean_jarraipena_aldatu_gabe(client, db):
    uid = setup_user_and_badges(db)
    badge = "Talde bat editatu"

    # Bi POST jarraian, jarraipena ez da gehitu bigarren aldian
    client.post(f"/api/erabiltzaileak/{uid}/intsigniak/{badge}") # jarr
