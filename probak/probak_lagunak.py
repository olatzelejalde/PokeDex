import json
from . import BaseTestClass


class TestLagunakKudeaketa(BaseTestClass):


    # =====================================================
    # LAGUN ZERRENDA
    # =====================================================


    def test_kargatu_lagun_zerrenda_hutsik(self):
        """
        KASUA: Erabiltzaileak ez du lagunik.
        ESPERO: APIak zerrenda hutsik ([]) itzultzea 200 OK-rekin.
        """
        self.login('asier_user', 'pass123')
        # Erregistratutako route-a: /api/erabiltzaileak/<int:uid>/lagunak
        res = self.client.get('/api/erabiltzaileak/1/lagunak')
        data = json.loads(res.data)


        self.assertEqual(200, res.status_code)
        self.assertEqual([], data)


    # =====================================================
    # LAGUNAK GEHITU
    # =====================================================


    def test_gehitu_laguna_zuzena(self):
        """
        KASUA: Erabiltzaile batek beste bat gehitzen du laguna gisa.
        ESPERO: 200 OK eta zerrendan laguna agertzea.
        """
        self.login('asier_user', 'pass123')
       
        # 1. Gehitu laguna (ID:1-ek ID:2 gehitu)
        # Route: /api/erabiltzaileak/<int:uid1>/gehitu-laguna/<int:uid2>
        res = self.client.post('/api/erabiltzaileak/1/gehitu-laguna/2')
        self.assertEqual(200, res.status_code)


        # 2. Egiaztatu zerrendan dagoela (JS-ko kargatuErabiltzaileLagunak funtzioa simulatu)
        res_list = self.client.get('/api/erabiltzaileak/1/lagunak')
        data_list = json.loads(res_list.data)
       
        # Ziurtatu ID: 2 duen laguna zerrendan dagoela
        self.assertTrue(any(laguna['id'] == 2 for laguna in data_list))


    def test_gehitu_laguna_bere_burua_ezin(self):
        """
        KASUA: Erabiltzaileak bere burua gehitu nahi du.
        ESPERO: Errore mezu bat (JS-ko alert-ean agertuko litzatekeena).
        """
        self.login('asier_user', 'pass123')
        res = self.client.post('/api/erabiltzaileak/1/gehitu-laguna/1')
       
        # APIak 400 Bad Request edo errorea bueltatu behar du
        self.assertNotEqual(200, res.status_code)


    # =====================================================
    # LAGUNAK EZABATU
    # =====================================================


    def test_kendu_laguna_zuzena(self):
        """
        KASUA: Laguna zerrendatik kentzea.
        ESPERO: 200 OK eta zerrenda berriz hutsik egotea.
        """
        self.login('asier_user', 'pass123')
       
        # Lehenik gehitu (ziurtatzeko badagoela)
        self.client.post('/api/erabiltzaileak/1/gehitu-laguna/2')
       
        # Orain ezabatu (JS-ko kenduLaguna funtzioa)
        res = self.client.delete('/api/erabiltzaileak/1/kendu-laguna/2')
        self.assertEqual(200, res.status_code)


        # Egiaztatu zerrenda hutsik dagoela
        res_check = self.client.get('/api/erabiltzaileak/1/lagunak')
        self.assertEqual(json.loads(res_check.data), [])


    # =====================================================
    # BILAKETA LOGIKA
    # =====================================================


    def test_bilaketa_erabiltzaile_guztiak(self):
        """
        KASUA: Bilatzaileak erabiltzaile guztien zerrenda behar du (frontend iragazkirako).
        ESPERO: Zerrenda osoa itzultzea.
        """
        self.login('asier_user', 'pass123')
        # JS-ko fetch(`${API_BASE_URL}/erabiltzaileak`)
        res = self.client.get('/api/erabiltzaileak')
        data = json.loads(res.data)


        self.assertEqual(200, res.status_code)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

