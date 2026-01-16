import unittest
import sys
import os

# --- KONFIGURAZIOA ---
ruta_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ruta_raiz)

# --- FLASK APLIKAZIOA INPORTATU ---
try:
    from app import create_app
    app = create_app()
except ImportError:
    try:
        from app.app import app
    except ImportError:
        print("Errorea: Ezin izan da Flask aplikazioa aurkitu.")

class FlaskTaldeakTest(unittest.TestCase):

    def setUp(self):
        """Proba bakoitzaren aurretik exekutatzen da"""
        app.config['TESTING'] = True
        self.client = app.test_client()

        # ID adibideak
        self.user_id = 1
        self.talde_id = 1
        self.pokemon_id = 1

    # ---------------------------
    # 1️⃣ TALDE BAT SORTU
    # ---------------------------
    def test_talde_bat_sortu(self):
        """
        ERABILPEN-KASUA: Erabiltzaileak 'Berria sortu' klikatzen du.
        ESPEROTAKO EMAITZA: Talde berria sortzen da.
        """
        data = {
            "izena": "Nire Talde Proba",
            "erabiltzaile_id": self.user_id
        }
        response = self.client.post(f"/api/taldeak/{self.user_id}", json=data)
        self.assertEqual(response.status_code, 201)
        self.assertIn("izena", response.json)
        self.assertEqual(response.json["izena"], "Nire Talde Proba")

    # ---------------------------
    # 2️⃣ TALDE BAT EZABATU
    # ---------------------------
    def test_talde_bat_ezabatu(self):
        """
        ERABILPEN-KASUA: Erabiltzaileak 'Ezabatu' klikatzen du.
        ESPEROTAKO EMAITZA: Taldea ezabatzen da.
        """
        response = self.client.delete(f"/api/taldeak/{self.talde_id}/{self.user_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json)

    # ---------------------------
    # 3️⃣ TALDEAN POKEMON BAT GEHITU
    # ---------------------------
    def test_taldean_pokemon_bat_gehitu(self):
        """
        ERABILPEN-KASUA: Erabiltzaileak 'Gehitu' klikatzen du.
        ESPEROTAKO EMAITZA: Pokemon bat taldera gehitzen da.
        """
        data = {
            "pokemon_id": self.pokemon_id
        }
        response = self.client.post(f"/api/taldeak/{self.talde_id}/pokemon", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("pokemonak", response.json)

    # ---------------------------
    # 4️⃣ TALDETIK POKEMON BAT EZABATU
    # ---------------------------
    def test_taldetik_pokemon_bat_kendu(self):
        """
        ERABILPEN-KASUA: Erabiltzaileak 'Editatu' → Pokemon bat aukeratu → Ezabatu.
        ESPEROTAKO EMAITZA: Pokemon taldetik kentzen da.
        """
        response = self.client.delete(f"/api/taldeak/{self.talde_id}/pokemon/{self.pokemon_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json)


if __name__ == '__main__':
    unittest.main()
