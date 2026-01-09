class TaldeaController:
    def __init__(self, db):
        self.db = db

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
        tid= self.db.connection.cursor().lastrowid

        #NOTIFIKAZIOA: Taldea sortu dela erregistratu
        data_gaur= datetime.now().strftime("%Y-%m-%d %H:%M")
        deskribapena= f"Talde berria sortu du: {izena}."
        self.db.insert(
            "INSERT INTO changelog (bertsioa, data, deskribapena, egilea) VALUES (?, ?, ?, ?)",
            ["TALDEA", data_gaur, deskribapena, uid]
        )
        return tid

    def add_pokemon(self, tid, pid):
        self.db.insert("INSERT OR IGNORE INTO ditu (taldea_id, pokemon_id) VALUES (?, ?)", [tid, pid])
        # NOTIFIKAZIOA: Pokemona taldera gehitu dela erregistratu
        data_gaur= datetime.now().strftime("%Y-%m-%d %H:%M")
        deskribapena= f"Pokemona gehitu da taldera: {pid}."
        self.db.insert(
            "INSERT INTO changelog (bertsioa, data, deskribapena, egilea) VALUES (?, ?, ?, ?)",
            ["OKEMON", data_gaur, deskribapena, uid]
        )
    def delete(self, tid):
        self.db.delete("DELETE FROM taldea WHERE id = ?", [tid])

    def remove_pokemon(self, tid, pid):
        self.db.delete("DELETE FROM ditu WHERE taldea_id = ? AND pokemon_id = ?", [tid, pid])