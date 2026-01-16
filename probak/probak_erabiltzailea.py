#python -m unittest discover -p "probak_*.py"
import json
from . import BaseTestClass


class TestErabiltzaileKudeaketa(BaseTestClass):


    # =====================================================
    # PROFILA IKUSI
    # =====================================================


    def test_profila_kargatu_zuzena(self):
        """
        KASUA: Erabiltzaileak bere profila kargatzen du (kargatuErabiltzaileProfila).
        ESPERO: APIak datu guztiak itzultzea (izena, rola, telegram...).
        """
        # 1. Login egin
        self.login('testuser', 'pass123')


        # 2. Eskatu erabiltzailearen datuak
        res = self.client.get('/api/erabiltzaileak/1')
        data = json.loads(res.data)


        # 3. Baieztatu 200 OK dela eta datuak zuzenak direla
        self.assertEqual(200, res.status_code)
        self.assertEqual('testuser', data['erabiltzaileIzena'])
        self.assertIn('rola', data)
        self.assertIn('izena', data)


    # =====================================================
    # DATUAK EGUNERATU
    # =====================================================


    def test_aldaketak_gorde_zuzena(self):
        """
        KASUA: Izena eta Telegram kontua aldatu eta gorde (aldaketakGorde).
        ESPERO: Datu-basean aldaketak ondo islatzea eta 200 OK itzultzea.
        """
        self.login('testuser', 'pass123')


        payload = {
            "izena": "IzenBerria",
            "abizena": "AbizenBerria",
            "telegramKontua": "@pokenews_bot"
        }


        # PUT eskaera egin datu berriekin
        res = self.client.put('/api/erabiltzaileak/1',
                             data=json.dumps(payload),
                             content_type='application/json')


        self.assertEqual(200, res.status_code)
       
        # Baieztatu DBan aldatu dela datuak berriz eskatuz
        res_info = self.client.get('/api/erabiltzaileak/1')
        data_info = json.loads(res_info.data)
        self.assertEqual('IzenBerria', data_info['izena'])
        self.assertEqual('@pokenews_bot', data_info['telegramKontua'])


    def test_pasahitza_aldatu_zuzena(self):
        """
        KASUA: Pasahitza aldatzen da.
        ESPERO: APIak aldaketa onartzea.
        """
        self.login('testuser', 'pass123')
       
        payload = {
            "pasahitza": "PasahitzBerria123"
        }


        res = self.client.put('/api/erabiltzaileak/1',
                             data=json.dumps(payload),
                             content_type='application/json')
       
        self.assertEqual(200, res.status_code)
