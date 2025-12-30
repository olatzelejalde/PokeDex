class IntsigniaController:
    def __init__(self, db):
        self.db = db

    def get_by_user(self, uid):
        rows = self.db.select("""
            SELECT i.* FROM intsignia i
            JOIN erabiltzaileak_intsigniak ei ON i.izena = ei.intsignia_izena
            WHERE ei.erabiltzaile_id = ?
        """, [uid])
        return [dict(row) for row in rows]

    def award(self, uid, izena):
        self.db.insert("INSERT OR IGNORE INTO erabiltzaileak_intsigniak (erabiltzaile_id, intsignia_izena) VALUES (?, ?)", [uid, izena])