import os
import sys
import unittest
from dataclasses import dataclass
from typing import Optional
from unittest.mock import MagicMock, patch

from flask import Flask


# Allow running this file directly on Windows:
# `python .\tests\test_acceptance_unittest.py`
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)


@dataclass
class FakeUser:
    id: int
    erabiltzaileIzena: str
    izena: str = ""
    abizena: str = ""
    chat_id: Optional[int] = None
    telegramKontua: Optional[str] = None
    rola: str = "user"


@dataclass
class FakeTeam:
    id: int
    izena: str
    erabiltzaile_id: int


class FakeDB:
    def select(self, sentence: str, parameters=None):
        return []

    def insert(self, sentence: str, parameters=None):
        return None

    def update(self, sentence: str, parameters=None):
        return None

    def delete(self, sentence: str, parameters=None):
        return None


class FakeUsersKatalogoa:
    def __init__(
        self,
        users_by_id: dict[int, FakeUser],
        *,
        telegram_friends_by_user: Optional[dict[int, list[FakeUser]]] = None,
    ):
        self._users_by_id = users_by_id
        self._telegram_friends_by_user = telegram_friends_by_user or {}

    def bilatu_by_id(self, uid: int):
        return self._users_by_id.get(uid)

    def lortu_lagunak(self, uid: int, *, telegram_du: bool = False):
        if telegram_du:
            return self._telegram_friends_by_user.get(uid, [])
        return []


class FakeTaldeKatalogoa:
    def __init__(self, team_by_id: dict[int, FakeTeam], pokemon_by_team: Optional[dict[int, list[dict]]] = None):
        self._team_by_id = team_by_id
        self._pokemon_by_team = pokemon_by_team or {}

    def bilatu_by_id(self, tid: int):
        return self._team_by_id.get(tid)

    def get_pokemonak(self, tid: int) -> list[dict]:
        return self._pokemon_by_team.get(tid, [])

    def bilatu_by_erabiltzaile(self, uid: int):
        return [t for t in self._team_by_id.values() if t.erabiltzaile_id == uid]


class FakeIntsignaKatalogoa:
    def __init__(self):
        self._has_badge: set[tuple[int, str]] = set()
        self.gehitu_calls: list[tuple[int, str]] = []

    def intsigniaDu(self, uid: int, badge_name: str) -> bool:
        return (uid, badge_name) in self._has_badge

    def intsigniaGehitu(self, uid: int, badge_name: str) -> None:
        self._has_badge.add((uid, badge_name))
        self.gehitu_calls.append((uid, badge_name))


class FakeTelegram:
    def __init__(self, result: bool):
        self.result = result
        self.calls: list[tuple[int, str, str, list[dict]]] = []

    def taldeaPartekatu(self, chat_id: int, jabea: str, taldea_izena: str, pokemonak: list[dict]) -> bool:
        self.calls.append((chat_id, jabea, taldea_izena, pokemonak))
        return self.result


def build_app(*, users: FakeUsersKatalogoa, taldeak: FakeTaldeKatalogoa, telegram: FakeTelegram, intsignia: FakeIntsignaKatalogoa) -> Flask:
    from app.controller.ui import bistaKontroladorea

    app = Flask(__name__)
    app.config.update(TESTING=True, SECRET_KEY="test")

    with patch.object(bistaKontroladorea, "TelegramService", new=lambda *a, **k: telegram), \
         patch.object(bistaKontroladorea, "IntsignaKatalogoa", new=lambda db: intsignia):
        bistaKontroladorea.register_all_routes(app, FakeDB(), users_katalogo=users, taldeak_katalogo=taldeak)

    return app


class TaldeaPartekatuApiTests(unittest.TestCase):
    def test_list_teams_empty(self):
        user = FakeUser(id=10, erabiltzaileIzena="alice", chat_id=123)
        users = FakeUsersKatalogoa({10: user})
        taldeak = FakeTaldeKatalogoa({})
        telegram = FakeTelegram(result=True)
        intsignia = FakeIntsignaKatalogoa()

        app = build_app(users=users, taldeak=taldeak, telegram=telegram, intsignia=intsignia)
        client = app.test_client()

        resp = client.get("/api/taldeak/erabiltzailea/10")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), [])

    def test_get_telegram_friends_empty_returns_empty_list(self):
        user = FakeUser(id=10, erabiltzaileIzena="alice", chat_id=123)
        users = FakeUsersKatalogoa({10: user}, telegram_friends_by_user={10: []})
        taldeak = FakeTaldeKatalogoa({})
        telegram = FakeTelegram(result=True)
        intsignia = FakeIntsignaKatalogoa()

        app = build_app(users=users, taldeak=taldeak, telegram=telegram, intsignia=intsignia)
        client = app.test_client()

        resp = client.get("/api/erabiltzaileak/10/lagunak/telegram")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), [])

    def test_get_telegram_friends_one_friend_returns_friend(self):
        user = FakeUser(id=10, erabiltzaileIzena="alice", chat_id=123)
        friend = FakeUser(id=11, erabiltzaileIzena="bob", chat_id=999, telegramKontua="bob_telegram")
        users = FakeUsersKatalogoa({10: user, 11: friend}, telegram_friends_by_user={10: [friend]})
        taldeak = FakeTaldeKatalogoa({})
        telegram = FakeTelegram(result=True)
        intsignia = FakeIntsignaKatalogoa()

        app = build_app(users=users, taldeak=taldeak, telegram=telegram, intsignia=intsignia)
        client = app.test_client()

        resp = client.get("/api/erabiltzaileak/10/lagunak/telegram")
        self.assertEqual(resp.status_code, 200)
        payload = resp.get_json()
        self.assertIsInstance(payload, list)
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["id"], 11)
        self.assertEqual(payload[0]["erabiltzaileIzena"], "bob")
        self.assertEqual(payload[0]["telegramKontua"], "bob_telegram")

    def test_partekatu_missing_user_or_friend_or_team_returns_404(self):
        users = FakeUsersKatalogoa({})
        taldeak = FakeTaldeKatalogoa({})
        telegram = FakeTelegram(result=True)
        intsignia = FakeIntsignaKatalogoa()

        app = build_app(users=users, taldeak=taldeak, telegram=telegram, intsignia=intsignia)
        client = app.test_client()

        resp = client.post("/api/taldeak/1/partekatu/10/11")
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.get_json(), {"error": "Erabiltzaile edo taldea ez da existitzen"})

    def test_partekatu_friend_missing_chat_id_returns_400(self):
        user = FakeUser(id=10, erabiltzaileIzena="alice", chat_id=123)
        friend = FakeUser(id=11, erabiltzaileIzena="bob", chat_id=None)
        team = FakeTeam(id=1, izena="MyTeam", erabiltzaile_id=10)

        users = FakeUsersKatalogoa({10: user, 11: friend})
        taldeak = FakeTaldeKatalogoa({1: team})
        telegram = FakeTelegram(result=True)
        intsignia = FakeIntsignaKatalogoa()

        app = build_app(users=users, taldeak=taldeak, telegram=telegram, intsignia=intsignia)
        client = app.test_client()

        resp = client.post("/api/taldeak/1/partekatu/10/11")
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.get_json(), {"error": "Lagunak ez du /start egin Telegram bot-ean (chat_id falta da)"})

    def test_partekatu_telegram_send_fails_returns_502(self):
        user = FakeUser(id=10, erabiltzaileIzena="alice", chat_id=123)
        friend = FakeUser(id=11, erabiltzaileIzena="bob", chat_id=456)
        team = FakeTeam(id=1, izena="MyTeam", erabiltzaile_id=10)

        users = FakeUsersKatalogoa({10: user, 11: friend})
        taldeak = FakeTaldeKatalogoa({1: team})
        telegram = FakeTelegram(result=False)
        intsignia = FakeIntsignaKatalogoa()

        app = build_app(users=users, taldeak=taldeak, telegram=telegram, intsignia=intsignia)
        client = app.test_client()

        resp = client.post("/api/taldeak/1/partekatu/10/11")
        self.assertEqual(resp.status_code, 502)
        self.assertEqual(resp.get_json(), {"error": "Ezin izan da taldea Telegram bidez bidali"})

    def test_partekatu_success_awards_badge_once(self):
        user = FakeUser(id=10, erabiltzaileIzena="alice", chat_id=123)
        friend = FakeUser(id=11, erabiltzaileIzena="bob", chat_id=456)
        team = FakeTeam(id=1, izena="MyTeam", erabiltzaile_id=10)
        pokemon_by_team = {1: [{"id": 1, "izena": "Bulbasaur"}]}

        users = FakeUsersKatalogoa({10: user, 11: friend})
        taldeak = FakeTaldeKatalogoa({1: team}, pokemon_by_team=pokemon_by_team)
        telegram = FakeTelegram(result=True)
        intsignia = FakeIntsignaKatalogoa()

        app = build_app(users=users, taldeak=taldeak, telegram=telegram, intsignia=intsignia)
        client = app.test_client()

        resp1 = client.post("/api/taldeak/1/partekatu/10/11")
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp1.get_json(), {"message": "Taldea partekatu da"})
        self.assertEqual(intsignia.gehitu_calls, [(10, "Talde bat partekatu")])
        self.assertEqual(len(telegram.calls), 1)

        resp2 = client.post("/api/taldeak/1/partekatu/10/11")
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(resp2.get_json(), {"message": "Taldea partekatu da"})
        self.assertEqual(intsignia.gehitu_calls, [(10, "Talde bat partekatu")])
        self.assertEqual(len(telegram.calls), 2)

    def test_ui_text_for_no_telegram_friends_matches_requirement(self):
        js_path = os.path.join(REPO_ROOT, "app", "static", "js", "taldeak.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        self.assertIn("Ez dituzu lagunik Telegramen", js)


class TelegramServiceUnitTests(unittest.TestCase):
    def test_taldea_partekatu_uses_send_photo_when_png_available(self):
        from app.services.telegram_service import TelegramService

        svc = TelegramService(token="TEST")
        svc._try_render_team_png = MagicMock(return_value=b"PNG")
        svc.send_photo = MagicMock(return_value=True)
        svc.send_message = MagicMock(return_value=False)

        ok = svc.taldeaPartekatu(123, "alice", "Team", [{"id": 1, "izena": "Bulbasaur"}])
        self.assertTrue(ok)
        svc.send_photo.assert_called_once()
        svc.send_message.assert_not_called()

    def test_taldea_partekatu_falls_back_to_send_message_when_send_photo_fails(self):
        from app.services.telegram_service import TelegramService

        svc = TelegramService(token="TEST")
        svc._try_render_team_png = MagicMock(return_value=b"PNG")
        svc.send_photo = MagicMock(return_value=False)
        svc.send_message = MagicMock(return_value=True)

        ok = svc.taldeaPartekatu(123, "alice", "Team", [{"id": 1, "izena": "Bulbasaur", "mota": "Grass"}])
        self.assertTrue(ok)
        svc.send_photo.assert_called_once()
        svc.send_message.assert_called_once()

    def test_send_message_returns_false_without_token(self):
        from app.services.telegram_service import TelegramService

        svc = TelegramService(token="")
        ok = svc.send_message(123, "hi")
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
