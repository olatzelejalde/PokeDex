from dataclasses import dataclass
from typing import List, Optional

from app.domain.erabiltzailea import Erabiltzailea

@dataclass
class ErabiltzaileKatalogoa:
    erabiltzaileak: List[Erabiltzailea]
    nireErabiltzaileak: "ErabiltzaileKatalogoa"
    db: object  # Conexión a BD

    def __init__(self, db=None):
        self.erabiltzaileak = []
        self.nireErabiltzaileak = self
        self.db = db

    def bilatu_by_id(self, uid: int) -> Optional[Erabiltzailea]:
        """Bilatu erabiltzailea IDren arabera"""
        for erabiltzailea in self.erabiltzaileak:
            if erabiltzailea.id == uid:
                return erabiltzailea
        return None

    def bilatu_by_erabilIzena(self, erabilIzena: str) -> Optional[Erabiltzailea]:
        """Bilatu erabiltzailea erabiltzaile izenaren arabera"""
        for erabiltzailea in self.erabiltzaileak:
            if erabiltzailea.erabiltzaileIzena == erabilIzena:
                return erabiltzailea
        return None

    def gehitu(self, erabiltzailea: Erabiltzailea) -> None:
        """Gehitu erabiltzailea katalogoan"""
        self.erabiltzaileak.append(erabiltzailea)

    def guztiak(self) -> List[Erabiltzailea]:
        """Itzuli guztiak erabiltzaileak"""
        return self.erabiltzaileak
    
    # ---- Métodos de negocio ----
    
    def erabiltzaileak_kargatu(self) -> None:
        """Erabiltzaile guztiak kargatu BDtik"""
        if not self.db:
            return
        rows = self.db.select("SELECT * FROM erabiltzailea")
        for row in rows:
            user = self._row_to_user(row)
            self.gehitu(user)

        lagunak_rows = self.db.select("SELECT * FROM lagunak")
        for row in lagunak_rows:
            user1 = self.bilatu_by_id(row['erabiltzaile1_id'])
            user2 = self.bilatu_by_id(row['erabiltzaile2_id'])
            if user1 and user2:
                user1.gehitu_laguna(user2)
                user2.gehitu_laguna(user1)
    
    def sortu(self, izena: str, abizena: str, erabilIzena: str, 
              pasahitza: str, pasahitza2: str, telegramKontua: str = None) -> Erabiltzailea:
        """Crea un nuevo usuario usando el método del dominio"""
        user = Erabiltzailea.sortu(
            izena, abizena, erabilIzena, pasahitza, pasahitza2, 
            telegramKontua, self.db
        )
        self.gehitu(user)
        return user
    
    def actualizar(self, uid: int, data: dict) -> Erabiltzailea:
        """Actualiza un usuario"""
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
    
    def login(self, erabilIzena: str, pasahitza: str) -> Optional[Erabiltzailea]:
        """Autentica un usuario"""
        user = self.bilatu_by_erabilIzena(erabilIzena)
        if user and user.pasahitza == pasahitza:
            return user
        return None
    
    # ---- Métodos de amigos ----
    def lortu_lagunak(self, uid: int, telegram_du: bool) -> List[Erabiltzailea]:
        user = self.bilatu_by_id(uid)
        if not user:
            return []
        
        lagunak = user.lagunZer.copy()
        if telegram_du:
            lagunak = [u for u in lagunak if u.telegramKontua and u.chat_id]
        return lagunak
    
    def gehitu_laguna(self, uid1: int, uid2: int) -> None:
        """Añade una amistad entre dos usuarios"""
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
    
    def kendu_laguna(self, uid1: int, uid2: int) -> None:
        """Elimina una amistad entre dos usuarios"""
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
    
    def bilatu_erabiltzaileak_by_nombre(self, izena: str) -> List[Erabiltzailea]:
        """Busca usuarios por nombre de usuario o nombre"""
        return [
            u for u in self.erabiltzaileak
            if izena.lower() in u.erabiltzaileIzena.lower() or
               izena.lower() in u.izena.lower()
        ]
    
    def lotu_telegram_chat_id(self, chat_id: int, telegram_username: Optional[str] = None, erabilIzena: Optional[str] = None) -> Optional[Erabiltzailea]:
        """
        Vincula chat_id cuando el usuario hace /start en el bot.
        - Si viene /start <erabilIzena>, vincula por erabilIzena (recomendado).
        - Si no, intenta vincular por telegram_username contra telegramKontua.
        """
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
            rows = self.db.select("SELECT * FROM erabiltzailea WHERE erabilIzena = ?", [erabilIzena])
            row = rows[0] if rows else None

        elif telegram_username:
            self.db.update(
                "UPDATE erabiltzailea SET chat_id = ? WHERE telegramKontua = ?",
                [chat_id, telegram_username],
            )
            rows = self.db.select("SELECT * FROM erabiltzailea WHERE telegramKontua = ?", [telegram_username])
            row = rows[0] if rows else None

        if not row:
            return None

        updated = self._row_to_user(row)

        # sincroniza memoria (si ya estaba cargado)
        existing = self.bilatu_by_id(updated.id)
        if existing:
            existing.telegramKontua = updated.telegramKontua
            existing.chat_id = updated.chat_id
            return existing

        self.gehitu(updated)
        return updated

    @staticmethod
    def _row_to_user(row) -> Erabiltzailea:
        """Convierte una fila de BD a objeto Erabiltzailea"""
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

