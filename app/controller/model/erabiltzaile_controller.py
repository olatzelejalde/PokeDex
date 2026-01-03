from app.domain.erabiltzailea import Erabiltzailea
from app.domain.erabiltzaileKatalogoa import ErabiltzaileKatalogoa


def _row_to_user(row) -> Erabiltzailea:
    return Erabiltzailea(
        id=row['id'],
        izena=row['izena'],
        abizena=row['abizena'],
        erabiltzaileIzena=row['erabilIzena'],
        pasahitza=row['pasahitza'],
        rola=row['rola'],
        telegramKontua=row['telegramKontua'],
    )


def _user_to_dict(u: Erabiltzailea) -> dict:
    return {
        'id': u.id,
        'izena': u.izena,
        'abizena': u.abizena,
        'erabiltzaileIzena': u.erabiltzaileIzena,
        'telegramKontua': u.telegramKontua or '',
        'rola': u.rola,
    }


class ErabiltzaileController:
    def __init__(self, db):
        self.db = db
        self.katalogoa = ErabiltzaileKatalogoa()
        self._load_katalogoa()

    def _load_katalogoa(self):
        """Kargatu guztiak erabiltzaileak katalogoan"""
        rows = self.db.select("SELECT * FROM erabiltzailea")
        for row in rows:
            user = _row_to_user(row)
            self.katalogoa.gehitu(user)

    # ---- Public helpers to expose dicts to the API layer ----
    def to_dict(self, user: Erabiltzailea) -> dict:
        return _user_to_dict(user)

    # ---- Queries ----
    def get_all(self):
        return self.katalogoa.guztiak()

    def get_by_id(self, uid):
        user = self.katalogoa.bilatu_by_id(uid)
        if user is None:
            # Saiatu datu-basean
            rows = self.db.select("SELECT * FROM erabiltzailea WHERE id = ?", [uid])
            if rows:
                user = _row_to_user(rows[0])
                self.katalogoa.gehitu(user)
        return user
    
    def get_by_erabilIzena(self, erabilIzena):
        user = self.katalogoa.bilatu_by_erabilIzena(erabilIzena)
        if user is None:
            # Saiatu datu-basean
            rows = self.db.select("SELECT * FROM erabiltzailea WHERE erabilIzena = ?", [erabilIzena])
            if rows:
                user = _row_to_user(rows[0])
                self.katalogoa.gehitu(user)
        return user

    # ---- Mutations ----
    def create(self, izena, abizena, erabilIzena, pasahitza, pasahitza2, telegramKontua=None):
        if not erabilIzena or len(pasahitza) < 4 or pasahitza != pasahitza2:
            raise ValueError("Datuak ez dira baliozkoak")
        badago = self.db.select("SELECT 1 FROM erabiltzailea WHERE erabilIzena = ?", [erabilIzena])
        if badago:
            raise ValueError("Erabiltzaile izena jada erregistratuta dago")
        self.db.insert(
            """INSERT INTO erabiltzailea (izena, abizena, erabilIzena, pasahitza, telegramKontua)
               VALUES (?, ?, ?, ?, ?)""",
            [izena, abizena, erabilIzena, pasahitza, telegramKontua]
        )
        # Gehitu katalogoari
        user = self.get_by_erabilIzena(erabilIzena)
        if user and not self.katalogoa.bilatu_by_id(user.id):
            self.katalogoa.gehitu(user)

    def update(self, uid, data):
        updates = []
        params = []
        if 'izena' in data:
            updates.append('izena = ?')
            params.append(data['izena'])
        if 'abizena' in data:
            updates.append('abizena = ?')
            params.append(data['abizena'])
        if 'telegramKontua' in data:
            updates.append('telegramKontua = ?')
            params.append(data['telegramKontua'])
        if 'pasahitza' in data and data['pasahitza']:
            updates.append('pasahitza = ?')
            params.append(data['pasahitza'])
        
        if not updates:
            raise ValueError("Ez dago aldaketarik gordetzeko")
        
        params.append(uid)
        query = f"UPDATE erabiltzailea SET {', '.join(updates)} WHERE id = ?"
        self.db.update(query, params)
        
        # Eguneratu katalogoan
        user = self.katalogoa.bilatu_by_id(uid)
        if user:
            if 'izena' in data:
                user.izena = data['izena']
            if 'abizena' in data:
                user.abizena = data['abizena']
            if 'telegramKontua' in data:
                user.telegramKontua = data['telegramKontua']
            if 'pasahitza' in data and data['pasahitza']:
                user.pasahitza = data['pasahitza']

    def login(self, erabilIzena, pasahitza):
        rows = self.db.select(
            "SELECT * FROM erabiltzailea WHERE erabilIzena = ? AND pasahitza = ?",
            [erabilIzena, pasahitza]
        )
        return _row_to_user(rows[0]) if rows else None
    