class PokemonController:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        rows = self.db.select("""
            SELECT p.*, e.mota1, e.mota2, e.irudia
            FROM pokemon p
            JOIN espeziea e ON p.espezie_izena = e.izena
        """)
        return [dict(row) for row in rows]

    def get_by_id(self, pid):
        rows = self.db.select("""
            SELECT p.*, e.mota1, e.mota2, e.irudia
            FROM pokemon p
            JOIN espeziea e ON p.espezie_izena = e.izena
            WHERE p.id = ?
        """, [pid])
        return dict(rows[0]) if rows else None

    def create(self, espezie_izena, izena=None):
        e = self.db.select("SELECT * FROM espeziea WHERE izena = ?", [espezie_izena])
        if not e:
            raise ValueError("Espeziea ez da existitzen")
        e = dict(e[0])
        self.db.insert("""
            INSERT INTO pokemon (espezie_izena, izena)
            VALUES (?, ?)
        """, [espezie_izena, izena or espezie_izena])
        return self.get_by_id(self.db.connection.cursor().lastrowid)