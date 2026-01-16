import unittest
import os
from run import app
from app.database.connection import Connection

class BaseTestClass(unittest.TestCase):
    def setUp(self):
        # 1. Test ingurunea konfiguratu
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.db = Connection()

        # 2. GARBIKETA OSOA: Taula guztiak ezabatu kargatu aurretik
        tables_to_drop = [
            'notifikazioa', 'daki', 'ditu', 'taldea', 'erabiltzaileak_intsigniak',
            'jakin_dezake', 'mugimendua', 'pokemon', 'espeziea', 'mota',
            'lagunak', 'changelog', 'intsignia', 'erabiltzailea'
        ]

        for table in tables_to_drop:
            self.db.connection.execute(f"DROP TABLE IF EXISTS {table}")

        # 3. Eskema kargatu (Taulak sortu + Hasierako datuak txertatu)
        # Ziurtatu bidea zuzena dela zure proiektuaren egituraren arabera
        schema_path = os.path.join(os.path.dirname(__file__), '../app/database/schema.sql')

        with open(schema_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
            self.db.connection.executescript(sql_script)

        # 4. Testetarako datu espezifikoak (Mota batzuk ziurtatu)
        motak = ['Sua', 'Ura', 'Belarra', 'Psikikoa', 'Normala', 'Elektrikoa']
        for m in motak:
            self.db.insert("INSERT OR IGNORE INTO mota (izena, indarra) VALUES (?, '')", [m])

    def tearDown(self):
        pass

    # ========================
    # FUNTZIO LAGUNTZAILEAK
    # ========================

    def login(self, username, password):
        """Login egiteko laguntzailea"""
        return self.client.post('/api/erabiltzaileak/saioa', json={
            'erabiltzaileIzena': username,
            'pasahitza': password
        })

    def sortu_espeziea(self, id, izena, mota1, hp, atk, defense, sp_atk, sp_def, speed):
        """Espezieak sortzeko laguntzailea"""
        # Ziurtatu mota existitzen dela
        self.db.insert("INSERT OR IGNORE INTO mota (izena, indarra) VALUES (?, '')", [mota1])

        self.db.insert("""
            INSERT OR IGNORE INTO espeziea 
            (id, izena, mota1, osasuna, atakea, defentsa, atake_berezia, defentsa_berezia, abiadura, irudia)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'url_test')
        """, [id, izena, mota1, hp, atk, defense, sp_atk, sp_def, speed])