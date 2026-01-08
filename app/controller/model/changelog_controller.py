class ChangelogController:
    def __init__(self,db):
        self.db = db

    def lortu_aldaketa_guztiak(self):
        # Datu basetik aldaketak hartu (id-aren arabera ordenatuta, berrienak lehenengo)
        query = "SELECT * FROM changelog ORDER BY id DESC"
        rows = self.db.execute(query)
        return [dict(row) for row in rows]
    
    def gehitu_aldaketa(self,bertsioa, data, deskribapena, egilea):
        # Aldaketa berri bat gordetzeko
        query = "INSERT INTO changelog (bertsioa, data, deskribapena, egilea) VALUES (?, ?, ?, ?)"
        self.db.insert(query, [bertsioa, data, deskribapena, egilea])