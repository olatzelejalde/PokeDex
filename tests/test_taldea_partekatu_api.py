import unittest
from dataclasses import dataclass
from typing import Any, List, Optional
from unittest.mock import patch

from flask import Flask


@dataclass
class FakeUser:
    id: int
    erabiltzaileIzena: str
    chat_id: Optional[int] = None


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

    # Prevent polling threads during tests.
    # register_all_routes uses env var checks; we ensure it's off.

    with patch.object(bistaKontroladorea, "TelegramService", new=lambda *a, **k: telegram), \
         patch.object(bistaKontroladorea, "IntsignaKatalogoa", new=lambda db: intsignia):
        bistaKontroladorea.register_all_routes(app, FakeDB(), users_katalogo=users, taldeak_katalogo=taldeak)

    return app


class TaldeaPartekatuApiTests(unittest.TestCase):
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
        friend = FakeUser(id=11, erabiltzaileIzena="bob", chat_id=999)
        team = FakeTeam(id=1, izena="MyTeam", erabiltzaile_id=10)

        users = FakeUsersKatalogoa({10: user, 11: friend})
        taldeak = FakeTaldeKatalogoa({1: team}, pokemon_by_team={1: [{"id": 1, "izena": "Bulbasaur"}]})
        telegram = FakeTelegram(result=False)
        intsignia = FakeIntsignaKatalogoa()

        app = build_app(users=users, taldeak=taldeak, telegram=telegram, intsignia=intsignia)
        client = app.test_client()

        resp = client.post("/api/taldeak/1/partekatu/10/11")
        self.assertEqual(resp.status_code, 502)
        self.assertEqual(resp.get_json(), {"error": "Ezin izan da taldea Telegram bidez bidali"})

        self.assertEqual(len(telegram.calls), 1)
        chat_id, jabea, taldea_izena, pokemonak = telegram.calls[0]
        self.assertEqual(chat_id, 999)
        self.assertEqual(jabea, "alice")
        self.assertEqual(taldea_izena, "MyTeam")
        self.assertEqual(pokemonak, [{"id": 1, "izena": "Bulbasaur"}])

    def test_partekatu_success_awards_badge(self):
        user = FakeUser(id=10, erabiltzaileIzena="alice", chat_id=123)
        friend = FakeUser(id=11, erabiltzaileIzena="bob", chat_id=999)
        team = FakeTeam(id=1, izena="MyTeam", erabiltzaile_id=10)

        users = FakeUsersKatalogoa({10: user, 11: friend})
        taldeak = FakeTaldeKatalogoa({1: team})
        telegram = FakeTelegram(result=True)
        intsignia = FakeIntsignaKatalogoa()

        app = build_app(users=users, taldeak=taldeak, telegram=telegram, intsignia=intsignia)
        client = app.test_client()

        resp = client.post("/api/taldeak/1/partekatu/10/11")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), {"message": "Taldea partekatu da"})

        self.assertEqual(intsignia.gehitu_calls, [(10, "Talde bat partekatu")])

    def test_list_teams_empty(self):
        user = FakeUser(id=10, erabiltzaileIzena="alice")
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
        user = FakeUser(id=10, erabiltzaileIzena="alice")
        users = FakeUsersKatalogoa({10: user}, telegram_friends_by_user={10: []})
        taldeak = FakeTaldeKatalogoa({})
        telegram = FakeTelegram(result=True)
        intsignia = FakeIntsignaKatalogoa()

        app = build_app(users=users, taldeak=taldeak, telegram=telegram, intsignia=intsignia)
        client = app.test_client()

        resp = client.get("/api/erabiltzaileak/10/lagunak/telegram")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), [])

    def test_ui_text_for_no_telegram_friends_matches_requirement(self):
        # This validates the acceptance-criteria wording used in the share modal.
        with open("app/static/js/taldeak.js", "r", encoding="utf-8") as f:
            js = f.read()
        self.assertIn("Ez dituzu lagunik Telegramen", js)


if __name__ == "__main__":
    unittest.main()
