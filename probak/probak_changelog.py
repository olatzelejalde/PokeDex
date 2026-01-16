import unittest
import sys
import os
# Proiektuaren erroko karpeta (PokeDex) Python-en bilaketa-bidera gehitzen dugu
ruta_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ruta_raiz)
# -------------------------------

try:
    from app import create_app
    app = create_app() 
except ImportError:
    try:
        from app.app import app 
    except ImportError:
        print("Errorea: Ezin izan da Flask aplikazioaren fitxategia aurkitu.")

class FlaskChangelogTest(unittest.TestCase):

    def setUp(self):
        """Proba bakoitzaren aurretik exekutatzen da: bezeroa konfiguratzen dugu"""
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_ikusi_notifikazioak_zerrenda(self):
        """
        ERABILPEN-KASUA: Erabiltzaileak Changelog-an klikatzen du eta notifikazio berriak ditu.
        ESPEROTAKO EMAITZA: Sistemak notifikazio berrien zerrenda erakutsiko du.
        """
        response = self.client.get('/api/changelog')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_notifikazioak_erabiltzailearen_arabera_filtratu(self):
        """
        ERABILPEN-KASUA: Erabiltzaileak notifikazioak erabiltzailearen arabera filtratzea erabakitzen du.
        ESPEROTAKO EMAITZA: Sistemak notifikazioak erabiltzailearen arabera filtratuta erakusten ditu.
        """
        # Adibidea: '1' ID-a duen erabiltzailearen notifikazioak eskatu
        response = self.client.get('/api/changelog?egilea=1')
        self.assertEqual(response.status_code, 200)
        # Egiaztatu emaitza guztiek egile bera dutela (APIaren diseinuaren arabera)
        for notif in response.json:
            self.assertEqual(str(notif['egilea']), '1')

    def test_notifikazioak_ekintzaren_arabera_filtratu(self):
        """
        ERABILPEN-KASUA: Erabiltzaileak ekintza baten arabera filtratzea erabakitzen du.
        ESPEROTAKO EMAITZA: Sistemak notifikazio horren zerrenda filtratua erakutsiko du.
        """
        # Adibidea: 'TALDEA' motako ekintzak filtratu
        response = self.client.get('/api/changelog?bertsioa=TALDEA')
        self.assertEqual(response.status_code, 200)
        for notif in response.json:
            self.assertEqual(notif['bertsioa'], 'TALDEA')

    def test_sarrera_ontzi_hutsa(self):
        """
        ERABILPEN-KASUA: Erabiltzaileak Changelog-an klikatzen du eta ez daude notifikazio berririk.
        ESPEROTAKO EMAITZA: Sistemak sarrera-ontzi hutsa erakutsiko du.
        """
        # Proba honetarako, APIak zerrenda huts bat itzultzen duela simulatzen dugu
        # (Datu-basea hutsik badago edo parametro ez-existenteekin filtratzean)
        response = self.client.get('/api/changelog?egilea=999999') 
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])

    def test_errorea_notifikatu(self):
        """
        ERABILPEN-KASUA: Erabiltzaileak Changelog-an klikatzen du eta ez da sarrera-ontzia agertzen.
        ESPEROTAKO EMAITZA: Sistemak errore bat gertatu dela notifikatuko du.
        """
        # Bide oker baten bidez errorea probatu
        response = self.client.get('/api/notifikazioak-okerrak')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()