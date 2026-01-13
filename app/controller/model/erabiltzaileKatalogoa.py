from typing import List, Optional
from dataclasses import dataclass

from app.controller.model.erabiltzailea import Erabiltzailea


class ErabiltzaileKatalogoa:

    def __init__(self, db):
        self.db = db
        self.erabiltzaileak: List[Erabiltzailea] = []
        self.nireErabiltzaileak = self

    # ========================
    # MAPPERS
    # ========================

    def _row_to_user(self, row) -> Erabiltzailea:
        return Erabiltzailea(
            id=row['id'],
            izena=row['izena'],
            abizena=row['abizena'],
            erabiltzaileIzena=row['erabilIzena'],
            pasahitza=row['pasahitza'],
            rola=row['rola'],
            telegramKontua=row['telegramKontua'],
            chat_id=row['chat_id']
        )

    def _user_to_dict(self, u: Erabiltzailea) -> dict:
        return {
            'id': u.id,
            'izena': u.izena,
            'abizena': u.abizena,
            'erabiltzaileIzena': u.erabiltzaileIzena,
            'telegramKontua': u.telegramKontua or '',
            'rola': u.rola,
        }

    # ========================
    # kargatu from BD
    # ========================

    # erabiltzaileak kargatzen ditu DB-tik
    def erabiltzaileak_kargatu(self) -> None:
        if not self.db:
            return

        rows = self.db.select("SELECT * FROM erabiltzailea")
        for row in rows:
            self.gehitu(self._row_to_user(row))

        lagunak_rows = self.db.select("SELECT * FROM lagunak")
        for row in lagunak_rows:
            user1 = self.bilatu_by_id(row['erabiltzaile1_id'])
            user2 = self.bilatu_by_id(row['erabiltzaile2_id'])
            if user1 and user2:
                user1.gehitu_laguna(user2)
                user2.gehitu_laguna(user1)

    # ========================
    # Listak / Bilaketak
    # ========================

    # erabiltzaile guztiak itzultzen ditu
    def guztiak(self) -> List[Erabiltzailea]:
        return self.erabiltzaileak

    # id bidez erabiltzailea bilatzen du
    def bilatu_by_id(self, uid: int) -> Optional[Erabiltzailea]:
        for erabiltzailea in self.erabiltzaileak:
            if erabiltzailea.erabiltzaileaDa(uid):
                return erabiltzailea
        return None

    # datuak mapeatzen ditu dict formatura
    def to_dict(self, user: Erabiltzailea) -> dict:
        return self._user_to_dict(user)

    # ========================
    # Sortu / eguneratu
    # ========================

    # sortu erabiltzailea db-tik eta gehitu katalogoara
    def sortu(self, izena: str, abizena: str, erabilIzena: str,
              pasahitza: str, pasahitza2: str,
              telegramKontua: str = None) -> Erabiltzailea:
        user = Erabiltzailea.sortu(
            izena, abizena, erabilIzena,
            pasahitza, pasahitza2,
            telegramKontua, self.db
        )
        self.gehitu(user)
        return user

    # erabiltzailea eguneratu
    def eguneratu(self, uid: int, data: dict) -> Erabiltzailea:
        user = self.bilatu_by_id(uid)
        if not user:
            raise ValueError("Erabiltzailea ez da existitzen")

        updates = []
        params = []

        if 'izena' in data:
            updates.append('izena = ?')
            params.append(data['izena'])
            user.izena = data['izena']
        if 'abizena' in data:
            updates.append('abizena = ?')
            params.append(data['abizena'])
            user.abizena = data['abizena']
        if 'telegramKontua' in data:
            updates.append('telegramKontua = ?')
            params.append(data['telegramKontua'])
            user.telegramKontua = data['telegramKontua']
        if 'pasahitza' in data and data['pasahitza']:
            updates.append('pasahitza = ?')
            params.append(data['pasahitza'])
            user.pasahitza = data['pasahitza']
        if 'chat_id' in data:
            updates.append('chat_id = ?')
            params.append(data['chat_id'])
            user.chat_id = data['chat_id']

        if not updates:
            raise ValueError("Ez dago aldaketarik gordetzeko")

        if self.db:
            params.append(uid)
            query = f"UPDATE erabiltzailea SET {', '.join(updates)} WHERE id = ?"
            self.db.update(query, params)

        return user

    # ========================
    # Autentikazioa
    # ========================

    # saioa hasteko metodoa
    def login(self, erabilIzena, pasahitza):
        rows = self.db.select(
            "SELECT * FROM erabiltzailea WHERE erabilIzena = ? AND pasahitza = ?",
            [erabilIzena, pasahitza]
        )
        return self._row_to_user(rows[0]) if rows else None

    # ========================
    # Lagunak
    # ========================

    # erabiltzailearen lagunak lortzen ditu
    def lortu_lagunak(self, uid: int, telegram_du: bool) -> List[Erabiltzailea]:
        user = self.bilatu_by_id(uid)
        if not user:
            return []
        return user.getLagunZerrenda(telegram_du)

    # bi erabiltzaileei lagunak gehitzen dizkie
    def gehitu_laguna(self, uid1: int, uid2: int) -> None:
        if uid1 == uid2:
            raise ValueError("Ezin duzu zeure buruari laguna egin")

        if uid1 > uid2:
            uid1, uid2 = uid2, uid1

        user = self.bilatu_by_id(uid1)
        lagun = self.bilatu_by_id(uid2)
        if not user or not lagun:
            raise ValueError("Erabiltzailea ez da existitzen")

        user.gehitu_laguna(lagun)
        lagun.gehitu_laguna(user)

        if self.db:
            rows = self.db.select(
                "SELECT 1 FROM lagunak WHERE erabiltzaile1_id = ? AND erabiltzaile2_id = ?",
                [uid1, uid2]
            )
            if rows:
                raise ValueError("Jadanik lagunak zarete")

            self.db.insert(
                "INSERT INTO lagunak (erabiltzaile1_id, erabiltzaile2_id) VALUES (?, ?)",
                [uid1, uid2]
            )

    # bi erabiltzaileetatik laguna kentzen die
    def kendu_laguna(self, uid1: int, uid2: int) -> None:
        if uid1 > uid2:
            uid1, uid2 = uid2, uid1

        user = self.bilatu_by_id(uid1)
        lagun = self.bilatu_by_id(uid2)
        if not user or not lagun:
            raise ValueError("Erabiltzailea ez da existitzen")

        user.kendu_laguna(lagun)
        lagun.kendu_laguna(user)

        if self.db:
            self.db.delete(
                "DELETE FROM lagunak WHERE erabiltzaile1_id = ? AND erabiltzaile2_id = ?",
                [uid1, uid2]
            )

    # ========================
    # Bilaketak Telegram
    # ========================

    # izena bidez erabiltzaileak bilatzen ditu
    def bilatu_erabiltzaileak_by_nombre(self, izena: str) -> List[Erabiltzailea]:
        return [
            u for u in self.erabiltzaileak
            if izena.lower() in u.erabiltzaileIzena.lower()
            or izena.lower() in u.izena.lower()
        ]

    # telegram kontua edo erabilIzena bidez chat_id lotzen du
    def lotu_telegram_chat_id(
        self,
        chat_id: int,
        telegram_username: Optional[str] = None,
        erabilIzena: Optional[str] = None
    ) -> Optional[Erabiltzailea]:

        if not self.db:
            return None

        row = None

        if erabilIzena:
            if telegram_username:
                self.db.update(
                    "UPDATE erabiltzailea SET telegramKontua = ?, chat_id = ? WHERE erabilIzena = ?",
                    [telegram_username, chat_id, erabilIzena],
                )
            else:
                self.db.update(
                    "UPDATE erabiltzailea SET chat_id = ? WHERE erabilIzena = ?",
                    [chat_id, erabilIzena],
                )
            rows = self.db.select(
                "SELECT * FROM erabiltzailea WHERE erabilIzena = ?", [erabilIzena]
            )
            row = rows[0] if rows else None

        elif telegram_username:
            self.db.update(
                "UPDATE erabiltzailea SET chat_id = ? WHERE telegramKontua = ?",
                [chat_id, telegram_username],
            )
            rows = self.db.select(
                "SELECT * FROM erabiltzailea WHERE telegramKontua = ?", [telegram_username]
            )
            row = rows[0] if rows else None

        if not row:
            return None

        updated = self._row_to_user(row)

        existing = self.bilatu_by_id(updated.id)
        if existing:
            existing.telegramKontua = updated.telegramKontua
            existing.chat_id = updated.chat_id
            return existing

        self.gehitu(updated)
        return updated

    # ========================
    # Memoria
    # ========================

    # erabiltzailea gehitzen du katalogoara
    def gehitu(self, erabiltzailea: Erabiltzailea) -> None:
        self.erabiltzaileak.append(erabiltzailea)