class TaldeaController:
    def __init__(self, db,pokemon_ctrl):
        self.db = db
        self.pokemon_ctrl = pokemon_ctrl

    def get_by_user(self, uid):
        rows = self.db.select("""
            SELECT t.*, COUNT(tp.pokemon_id) as pokemon_kop
            FROM taldea t
            LEFT JOIN ditu tp ON t.id = tp.taldea_id
            WHERE t.erabiltzaile_id = ?
            GROUP BY t.id
        """, [uid])
        return [dict(row) for row in rows]

    def get_pokemonak(self, tid):
        rows = self.db.select("""
            SELECT p.*, e.mota1, e.mota2, e.irudia
            FROM ditu tp
            JOIN pokemon p ON tp.pokemon_id = p.id
            JOIN espeziea e ON p.espezie_izena = e.izena
            WHERE tp.taldea_id = ?
        """, [tid])
        return [dict(row) for row in rows]

    def create(self, izena, uid):
        self.db.insert("INSERT INTO taldea (izena, erabiltzaile_id) VALUES (?, ?)", [izena, uid])
        return self.db.connection.cursor().lastrowid

    def add_pokemon(self, tid, pid):
        self.db.insert("INSERT OR IGNORE INTO ditu (taldea_id, pokemon_id) VALUES (?, ?)", [tid, pid])
    def delete(self, tid):
        self.db.delete("DELETE FROM taldea WHERE id = ?", [tid])

    def remove_pokemon(self, tid, pid):
        self.db.delete("DELETE FROM ditu WHERE taldea_id = ? AND pokemon_id = ?", [tid, pid])

    def get_mvp(self, tid):
        return self.pokemon_ctrl.get_best_pokemon_by_group(tid)