# Exekutatzeko: python -m unittest probak.probak_taldea_partekatu
import json
import sys
import types
import unittest
from unittest.mock import patch
from flask import Flask

# Stub de flask_cors y requests para evitar dependencias opcionales al importar la app
if 'flask_cors' not in sys.modules:
    m = types.ModuleType('flask_cors')
    def CORS(app, *args, **kwargs): return app
    m.CORS = CORS
    sys.modules['flask_cors'] = m

if 'requests' not in sys.modules:
    r = types.ModuleType('requests')
    def _dummy_get(*args, **kwargs):
        class _Resp:
            status_code = 200
            def json(self): return {}
        return _Resp()
    r.get = _dummy_get
    sys.modules['requests'] = r

from . import BaseTestClass
from app.controller.ui.bistaKontroladorea import register_all_routes
import inspect

class FakeTime:
    def __init__(self, start=0.0):
        self.t = start
    def monotonic(self):
        return self.t
    def advance(self, dt):
        self.t += dt

class FakeTelegramService:
    def __init__(self, should_succeed=True, delay=0.0, time_provider=None):
        self.should_succeed = should_succeed
        self.delay = delay
        self.time = time_provider
    def taldeaPartekatu(self, chat_id, erabiltzaileIzena, taldea_izena, pokemonak):
        if self.time and self.delay:
            self.time.advance(self.delay)
        return self.should_succeed

class FakeLimiter:
    def __init__(self, allow=True):
        self.allow = allow
    def try_acquire(self):
        return self.allow
    def release(self):
        pass

class TestTaldeaPartekatu(BaseTestClass):

    def _build_app(self, telegram_service=None, time_provider=None, limiter=None, limit=50):
        app = Flask(__name__)
        app.secret_key = 'test'
        app.config['TESTING'] = True

        # bista kontroladorearen route guztiak erregistratu
        params = set(inspect.signature(register_all_routes).parameters.keys())
        kwargs = {'db': self.db}

        # Katalogoak: baimenduta badaude, None pasatzen dugu BDtik sortzeko
        if 'users_katalogo' in params:
            kwargs['users_katalogo'] = None
        if 'taldeak_katalogo' in params:
            kwargs['taldeak_katalogo'] = None

        # Telegram service: argk onartzen ez bada, monkeypatch modura erabiliko dugu
        import app.controller.ui.bistaKontroladorea as bk
        if telegram_service is not None:
            if 'telegram_service_override' in params:
                kwargs['telegram_service_override'] = telegram_service
            elif 'telegram_service' in params:
                kwargs['telegram_service'] = telegram_service
            else:
                # Fallback: klasea ordezkatzen dugu fake entornoan
                bk.TelegramService = lambda: telegram_service

        # Time provider
        if time_provider is not None and 'time_provider' in params:
            kwargs['time_provider'] = time_provider

        # Concurrency
        if 'concurrency_limiter' in params:
            kwargs['concurrency_limiter'] = limiter or FakeLimiter(allow=True)
        if 'concurrency_limit' in params:
            kwargs['concurrency_limit'] = limit

        register_all_routes(app, **kwargs)
        return app.test_client()

    # Erabiltzaile bat db fake-ean sartzen du
    def _insert_user(self, uid, izena, abizena, erabilIzena, pasahitza, chat_id=None):
        self.db.insert(
            "INSERT INTO erabiltzailea (id, izena, abizena, erabilIzena, pasahitza) VALUES (?, ?, ?, ?, ?)",
            [uid, izena, abizena, erabilIzena, pasahitza]
        )
        if chat_id is not None:
            try:
                self.db.insert("UPDATE erabiltzailea SET chat_id = ? WHERE id = ?", [chat_id, uid])
            except Exception:
                pass

    # Talde bat db fake-ean sartzen du
    def _insert_team(self, tid, izena, erabiltzaile_id):
        self.db.insert("INSERT INTO taldea (id, izena, erabiltzaile_id) VALUES (?, ?, ?)", [tid, izena, erabiltzaile_id])

    # Erabiltzaile batek beste bat lagun gisa gehitzen du API bidez db fake-ean
    def _add_friend_via_api(self, client, uid1, uid2):
        res = client.post(f'/api/erabiltzaileak/{uid1}/gehitu-laguna/{uid2}')
        # Ignorar insignias; solo confirmar que no falle 4xx
        assert res.status_code in (200, 201), f'gehitu-laguna failed: {res.status_code} {res.data}'

    # =====================================================
    # 🛡️ TALDEA PARTEKATU TESTAK
    # =====================================================

    # 1. Talderik ez daudenean → lista hutsa eta ez du partekatu baimentzen.
    def test_zerrenda_hutsa(self):
        # Usuarios y amistad (para que el precheck de amigos pase)
        self._insert_user(201, 'U1', 'A', 'u1', 'p', chat_id=111)
        self._insert_user(202, 'U2', 'B', 'u2', 'p', chat_id=222)
        client = self._build_app()
        self._add_friend_via_api(client, 201, 202)

        # Talde zerrenda hutsik
        res = client.get('/api/taldeak/erabiltzailea/201')
        data = json.loads(res.data)
        self.assertEqual(200, res.status_code)
        self.assertEqual([], data)

        # Existitzen ez den taldea partekatu → 404
        res = client.post('/api/taldeak/999/partekatu/201/202')
        data = json.loads(res.data)
        self.assertEqual(404, res.status_code)
        self.assertEqual('Erabiltzaile edo taldea ez da existitzen', data['error'])

    # 2. Erabiltzaileak ez du Telegramen lagunik → “Lagunak ez du /start egin Telegram bot-ean (chat_id falta da)”.
    def test_lagunik_ez(self):
        self._insert_user(301, 'U1', 'A', 'u1', 'p', chat_id=311)
        self._insert_user(302, 'U2', 'B', 'u2', 'p', chat_id=None)  # laguna chat_id gabe
        self._insert_team(310, 'TaldeX', 301)
        client = self._build_app()

        res = client.post('/api/taldeak/310/partekatu/301/302')
        data = json.loads(res.data)
        self.assertEqual(400, res.status_code)
        self.assertEqual('Lagunak ez du /start egin Telegram bot-ean (chat_id falta da)', data['error'])

    # 3. Erabiltzaileak lagun bakarra duenean → partekatu eta “Taldea partekatu da” erakusten du.
    def test_lagun_partekatu_ok(self):
        self._insert_user(401, 'U1', 'A', 'u1', 'p', chat_id=411)
        self._insert_user(402, 'U2', 'B', 'u2', 'p', chat_id=422)
        self._insert_team(410, 'TeamA', 401)

        timep = FakeTime()
        telegram = FakeTelegramService(should_succeed=True, delay=0.5, time_provider=timep)
        client = self._build_app(telegram_service=telegram, time_provider=timep, limiter=FakeLimiter(allow=True))
        self._add_friend_via_api(client, 401, 402)

        res = client.post('/api/taldeak/410/partekatu/401/402')
        data = json.loads(res.data)
        self.assertEqual(200, res.status_code)
        self.assertEqual('Taldea partekatu da', data['message'])

    # 4. Telegram ez dago erabilgarri → “Ezin izan da taldea Telegram bidez bidali”.
    def test_telegram_ez_dago_erabilgarri(self):
        self._insert_user(501, 'U1', 'A', 'u1', 'p', chat_id=511)
        self._insert_user(502, 'U2', 'B', 'u2', 'p', chat_id=522)
        self._insert_team(510, 'TeamB', 501)

        timep = FakeTime()
        telegram = FakeTelegramService(should_succeed=False, delay=0.0, time_provider=timep)
        client = self._build_app(telegram_service=telegram, time_provider=timep)
        self._add_friend_via_api(client, 501, 502)

        res = client.post('/api/taldeak/510/partekatu/501/502')
        data = json.loads(res.data)
        self.assertEqual(502, res.status_code)
        self.assertEqual('Ezin izan da taldea Telegram bidez bidali', data['error'])

    # 5. Laguna Telegramen konektatuta ez dagoenean → partekatu aurretik konektatu eskatzea.
    def test_lagun_telegramen_konektatuta_ez(self):
        self._insert_user(601, 'U1', 'A', 'u1', 'p', chat_id=611)
        self._insert_user(602, 'U2', 'B', 'u2', 'p', chat_id=None)  # chat_id falta
        self._insert_team(610, 'TeamC', 601)

        timep = FakeTime()
        telegram = FakeTelegramService(should_succeed=True, delay=0.0, time_provider=timep)
        client = self._build_app(telegram_service=telegram, time_provider=timep)
        self._add_friend_via_api(client, 601, 602)

        res = client.post('/api/taldeak/610/partekatu/601/602')
        data = json.loads(res.data)
        self.assertEqual(400, res.status_code)
        self.assertEqual('Lagunak ez du /start egin Telegram bot-ean (chat_id falta da)', data['error'])

    # 6. Prozesua > 2s → uko egin “2 segundo pasa dira. Saiatu berriro” mezuarekin.
    def test_prozesua_greater_2s(self):
        self._insert_user(701, 'U1', 'A', 'u1', 'p', chat_id=711)
        self._insert_user(702, 'U2', 'B', 'u2', 'p', chat_id=722)
        self._insert_team(710, 'TeamD', 701)

        timep = FakeTime()
        telegram = FakeTelegramService(should_succeed=True, delay=2.1, time_provider=timep)
        client = self._build_app(telegram_service=telegram, time_provider=timep)
        self._add_friend_via_api(client, 701, 702)

        res = client.post('/api/taldeak/710/partekatu/701/702')
        data = json.loads(res.data)
        self.assertEqual(408, res.status_code)
        self.assertEqual('2 segundo pasa dira. Saiatu berriro', data['error'])

    # 7. Prozesua < 2s → ondo partekatu.
    def test_prozesua_less_2s_ok(self):
        self._insert_user(801, 'U1', 'A', 'u1', 'p', chat_id=811)
        self._insert_user(802, 'U2', 'B', 'u2', 'p', chat_id=822)
        self._insert_team(810, 'TeamE', 801)

        timep = FakeTime()
        telegram = FakeTelegramService(should_succeed=True, delay=1.9, time_provider=timep)
        client = self._build_app(telegram_service=telegram, time_provider=timep)
        self._add_friend_via_api(client, 801, 802)

        res = client.post('/api/taldeak/810/partekatu/801/802')
        data = json.loads(res.data)
        self.assertEqual(200, res.status_code)
        self.assertEqual('Taldea partekatu da', data['message'])

    # 8. 50+ erabiltzaile aldi berean partekatzen → blokeatu eta mezua erakutsi.
    def test_blokeoa_50_erabiltzaile(self):
        self._insert_user(901, 'U1', 'A', 'u1', 'p', chat_id=911)
        self._insert_user(902, 'U2', 'B', 'u2', 'p', chat_id=922)
        self._insert_team(910, 'TeamF', 901)

        timep = FakeTime()
        telegram = FakeTelegramService(should_succeed=True, delay=0.0, time_provider=timep)
        limiter = FakeLimiter(allow=False)  # simula 50 en curso
        client = self._build_app(telegram_service=telegram, time_provider=timep, limiter=limiter, limit=50)
        self._add_friend_via_api(client, 901, 902)

        res = client.post('/api/taldeak/910/partekatu/901/902')
        data = json.loads(res.data)
        self.assertEqual(429, res.status_code)
        self.assertEqual('Itxaron mesedez, 50 erabiltzaile baitaude bere taldea partekatzen', data['error'])
