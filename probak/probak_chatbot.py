from . import BaseTestClass
import json


class TestChatBot(BaseTestClass):

    # =====================================================
    # 🏆 POKETOP TESTAK
    # =====================================================

    def test_poketop_ez_du_talderik(self):
        """
        KASUA: 'PokeTop' botoia sakatuta ez badu talderik sortuta.
        ESPERO: Zerrenda hutsik itzultzea (Frontend-ak 'Oraindik ez duzu talderik' erakutsiko du).
        """
        # 1. Login egin
        self.login('testuser', 'pass123')

        # 2. Eskatu erabiltzailearen taldeak (Botak egiten duen bezala)
        res = self.client.get('/api/taldeak/erabiltzailea/1')
        data = json.loads(res.data)

        # 3. Baieztatu 200 OK dela eta zerrenda hutsa dela
        self.assertEqual(200, res.status_code)
        self.assertEqual([], data)

    def test_poketop_talde_bakarra_mvp(self):
        """
        KASUA: 'PokeTop' sakatu, taldea aukeratu eta Pokemon onena (MVP) itzuli.
        """
        # 1. Sortu espezieak (Mota zehaztuz!)
        # Charmander -> Sua
        self.sortu_espeziea(4, 'Charmander', 'Sua', 39, 52, 43, 60, 50, 65)
        # Mewtwo -> Psikikoa
        self.sortu_espeziea(150, 'Mewtwo', 'Psikikoa', 106, 110, 90, 154, 90, 130)

        # 2. Erabiltzailea sortu (zure SQLak Admin eta beste batzuk sortzen ditu, baina hemen testekoa behar dugu)
        self.db.insert(
            "INSERT INTO erabiltzailea (id, izena, abizena, erabilIzena, pasahitza) VALUES (99, 'Test', 'User', 'testuser', 'pass')",
            [])

        # 3. Taldea eta pokemonak
        self.db.insert("INSERT INTO taldea (id, izena, erabiltzaile_id) VALUES (1, 'TaldeGogorra', 99)", [])

        self.db.insert("INSERT INTO pokemon (id, espezie_izena, izena) VALUES (1, 'Charmander', 'Charmander')", [])
        self.db.insert("INSERT INTO pokemon (id, espezie_izena, izena) VALUES (2, 'Mewtwo', 'Mewtwo')", [])

        self.db.insert("INSERT INTO ditu (taldea_id, pokemon_id) VALUES (1, 1)", [])
        self.db.insert("INSERT INTO ditu (taldea_id, pokemon_id) VALUES (1, 2)", [])

        # 4. Deitu MVP endpoint-a (bot.js: cargarMVP)
        res = self.client.get('/api/taldeak/1/mvp')
        data = json.loads(res.data)

        # 5. Baieztatu Mewtwo dela MVP-a (Media altuagoa duelako)
        self.assertEqual(200, res.status_code)
        self.assertEqual('Mewtwo', data['Izena'])
        self.assertGreater(data['Media'], 100)  # Mewtwo oso indartsua da

    # =====================================================
    # 🍃 POKEMOTA TESTAK
    # =====================================================

    def test_pokemota_espezie_okerra(self):
        """
        KASUA: 'PokeMota' eta espeziearen izena gaizki sartu.
        ESPERO: 404 edo Error mezua.
        """
        res = self.client.get('/api/espezieak/Digimon/info')
        data = json.loads(res.data)

        # APIak error json bat edo 404 itzuli behar du
        status_ok = (res.status_code == 404) or ('error' in data)
        self.assertTrue(status_ok)

    def test_pokemota_espezie_zuzena(self):
        """
        KASUA: 'PokeMota' eta espeziea ondo sartu.
        ESPERO: Indarguneak eta Ahuleziak itzultzea.
        """
        # Gehitu 'Sua' mota parametroa
        self.sortu_espeziea(4, 'Charmander', 'Sua', 39, 52, 43, 60, 50, 65)

        res = self.client.get('/api/espezieak/Charmander/info')
        data = json.loads(res.data)

        self.assertEqual(200, res.status_code)
        self.assertIn('Ahuleziak', data)
        self.assertIn('Indarrak', data)

    # =====================================================
    # ⚡ POKEEBO TESTAK
    # =====================================================

    def test_pokeebo_espezie_okerra(self):
        """
        KASUA: 'PokeEbo' eta espeziea gaizki sartu.
        ESPERO: Zerrenda hutsik.
        """
        res = self.client.get('/api/espezieak/Agumon/ebo')
        data = json.loads(res.data)

        # Normalean zerrenda hutsa itzultzen du ezer aurkitzen ez badu
        self.assertEqual([], data)

    def test_pokeebo_katea_bistaratu(self):
        """
        KASUA: 'PokeEbo' eta espeziea ondo.
        ESPERO: Eboluzio katea itzultzea.
        """
        # Gehitu 'Sua' mota parametroa
        self.sortu_espeziea(4, 'Charmander', 'Sua', 39, 52, 43, 60, 50, 65)

        res = self.client.get('/api/espezieak/Charmander/ebo')
        data = json.loads(res.data)

        self.assertEqual(200, res.status_code)
        self.assertIsInstance(data, list)

        # Katean gutxienez izen bat egon behar da
        names = [p['izena'].lower() for p in data]
        self.assertIn('charmander', names)

    # =====================================================
    # 📡 POKESCAN TESTAK
    # =====================================================

    def test_pokescan_espezie_okerra(self):
        """
        KASUA: 'PokeScan' endpoint-a espezie oker batekin deitzen da.
        ESPERO: 404 errore-mezua eta erantzunean 'error' gakoa egotea.
        """

        # APIari GET eskaera egiten zaio existitzen ez den espezie batekin
        res = self.client.get('/api/espezieak/Ezezaguna/scan')

        # Erantzuna JSON formatura bihurtzen da
        data = json.loads(res.data)

        # HTTP egoera-kodea 404 dela egiaztatzen da
        self.assertEqual(404, res.status_code)

        # Erantzunean 'error' gakoa dagoela egiaztatzen da
        self.assertIn('error', data)

    def test_pokescan_legendarioa(self):
        """
        KASUA: 'PokeScan' eta espezie legendarioa (Mewtwo).
        ESPERO: Estatistika altuak eta datu osoak.
        """
        # Gehitu 'Psikikoa' mota parametroa
        self.sortu_espeziea(150, 'Mewtwo', 'Psikikoa', 106, 110, 90, 154, 90, 130)

        res = self.client.get('/api/espezieak/Mewtwo/scan')
        data = json.loads(res.data)

        self.assertEqual(200, res.status_code)
        self.assertEqual('Mewtwo', data['Izena'])
        self.assertIn('Stats', data)

        # Legendarioa denez, media oso altua izan behar du (> 100 adibidez)
        self.assertGreater(data['Media'], 100)

        # Estatistikak ondo dauden egiaztatu
        stats = data['Stats']
        self.assertEqual(154, stats['AtakeBerezia'])

    def test_pokeebo_azken_eboluzioa(self):
        """
        KASUA: Espezie batek ez du eboluziorik (bakarrik dago).
        ESPERO: APIak gutxienez elementu bat duen zerrenda bueltatzea.
        """

        # Espezie bat sortzen da testean erabiltzeko
        self.sortu_espeziea(999, 'SoloMon', 'Normala', 50, 50, 50, 50, 50, 50)

        # Eboluzioaren endpoint-a deitzen da
        res = self.client.get('/api/espezieak/SoloMon/ebo')

        # Erantzuna JSONera bihurtzen da
        data = json.loads(res.data)

        # Egoera-kodea 200 dela egiaztatzen da (arrakasta)
        self.assertEqual(200, res.status_code)

        # Erantzuna zerrenda bat dela egiaztatzen da
        self.assertIsInstance(data, list)

        # Zerrendak gutxienez elementu bat duela egiaztatzen da
        self.assertGreaterEqual(len(data), 1)


    def test_pokescan_normala(self):
        """
        KASUA: PokeScan endpoint-a espezie zuzen batekin.
        ESPERO: Datu zuzenak bueltatzea eta media 100 baino txikiagoa izatea.
        """

        # Pikachu espeziea sortzen da
        self.sortu_espeziea(25, 'Pikachu', 'Elektrikoa', 35, 55, 40, 50, 50, 90)

        # Scan endpoint-a deitzen da
        res = self.client.get('/api/espezieak/Pikachu/scan')

        # Erantzuna JSONera bihurtzen da
        data = json.loads(res.data)

        # Egoera-kodea 200 dela egiaztatzen da
        self.assertEqual(200, res.status_code)

        # Itzulitako izena "Pikachu" dela egiaztatzen da
        self.assertEqual('Pikachu', data['Izena'])

        # Media 100 baino txikiagoa dela egiaztatzen da
        self.assertLess(data['Media'], 100)
