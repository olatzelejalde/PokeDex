class EspezieController:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        return [dict(row) for row in self.db.select("SELECT * FROM espeziea ORDER BY izena")]

    def get_by_name(self, izena):
        rows = self.db.select("SELECT * FROM espeziea WHERE izena = ?", [izena])
        return dict(rows[0]) if rows else None

    def create(self, izena, mota1, mota2, osasuna, atakea, defentsa,
               atake_berezia, defentsa_berezia, abiadura, irudia, deskribapena=None):
        if not izena or not mota1:
            raise ValueError("Izena eta mota1 beharrezkoak dira")
        self.db.insert(
            """INSERT INTO espeziea (izena, mota1, mota2, osasuna, atakea, defentsa,
               atake_berezia, defentsa_berezia, abiadura, irudia, deskribapena)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [izena, mota1, mota2, osasuna, atakea, defentsa,
             atake_berezia, defentsa_berezia, abiadura, irudia, deskribapena]
        )