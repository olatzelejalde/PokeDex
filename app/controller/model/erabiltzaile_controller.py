class ErabiltzaileController:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        return [dict(row) for row in self.db.select("SELECT * FROM erabiltzailea")]

    def get_by_id(self, uid):
        rows = self.db.select("SELECT * FROM erabiltzailea WHERE id = ?", [uid])
        return dict(rows[0]) if rows else None
    
    def get_by_erabilIzena(self, erabilIzena):
        rows = self.db.select("SELECT * FROM erabiltzailea WHERE erabilIzena = ?", [erabilIzena])
        return dict(rows[0]) if rows else None

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
        return dict(rows[0]) if rows else None
        