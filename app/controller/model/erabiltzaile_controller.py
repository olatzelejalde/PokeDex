from app.domain.erabiltzailea import Erabiltzaile


def _row_to_user(row) -> Erabiltzaile:
    return Erabiltzaile(
        id=row['id'],
        izena=row['izena'],
        abizena=row['abizena'],
        erabilIzena=row['erabilIzena'],
        telegramKontua=row['telegramKontua'],
        rola=row['rola'],
    )


def _user_to_dict(u: Erabiltzaile) -> dict:
    return {
        'id': u.id,
        'izena': u.izena,
        'abizena': u.abizena,
        'erabilIzena': u.erabilIzena,
        'telegramKontua': u.telegramKontua,
        'rola': u.rola,
    }


class ErabiltzaileController:
    def __init__(self, db):
        self.db = db

    # ---- Public helpers to expose dicts to the API layer ----
    def to_dict(self, user: Erabiltzaile) -> dict:
        return _user_to_dict(user)

    # ---- Queries ----
    def get_all(self):
        rows = self.db.select("SELECT * FROM erabiltzailea")
        return [_row_to_user(row) for row in rows]

    def get_by_id(self, uid):
        rows = self.db.select("SELECT * FROM erabiltzailea WHERE id = ?", [uid])
        return _row_to_user(rows[0]) if rows else None
    
    def get_by_erabilIzena(self, erabilIzena):
        rows = self.db.select("SELECT * FROM erabiltzailea WHERE erabilIzena = ?", [erabilIzena])
        return _row_to_user(rows[0]) if rows else None

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

    def login(self, erabilIzena, pasahitza):
        rows = self.db.select(
            "SELECT * FROM erabiltzailea WHERE erabilIzena = ? AND pasahitza = ?",
            [erabilIzena, pasahitza]
        )
        return _row_to_user(rows[0]) if rows else None
    