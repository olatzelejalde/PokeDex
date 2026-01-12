class ChangelogController:
    def __init__(self,db):
        self.db = db
        self.db.insert("""
            CREATE TABLE IF NOT EXISTS changelog (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bertsioa TEXT NOT NULL,
                data TEXT NOT NULL,
                deskribapena TEXT NOT NULL,
                egilea TEXT NOT NULL
            )
        """)

    def lortu_aldaketa_guztiak(self):
        # Datu basetik aldaketak hartu (id-aren arabera ordenatuta, berrienak lehenengo)
        query = "SELECT * FROM changelog ORDER BY id DESC"
        rows = self.db.select(query) 
        return [dict(row) for row in rows]
    
    def gehitu_aldaketa(self,bertsioa, data, deskribapena, egilea):
        # Aldaketa berri bat gordetzeko
        query = "INSERT INTO changelog (bertsioa, data, deskribapena, egilea) VALUES (?, ?, ?, ?)"
        self.db.insert(query, [bertsioa, data, deskribapena, egilea])
    
    def lortu_lagunen_ekintzak(self, nire_id):
    # Query honek nire lagunen (jarraitzen ditudanen) ekintzak bakarrik ekartzen ditu
        query = """
            SELECT c.*, e.izena as egile_izena 
            FROM changelog c
            JOIN lagun_egiten l ON c.egilea = l.lagun_id
            JOIN erabiltzailea e ON c.egilea = e.id
            WHERE l.erabiltzaile_id = ?
            ORDER BY c.id DESC
        """
        rows = self.db.select(query, [nire_id])
        return [dict(row) for row in rows]