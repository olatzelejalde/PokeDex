from dataclasses import dataclass

@dataclass
class MotaKatalogoa:
    def __init__(self, db):
        self.db = db

    # ========================
    # Mota bilaketa
    # ========================
    
    # mota guztiak lortzen ditu
    def get_all(self):
        return [dict(row) for row in self.db.select("SELECT * FROM mota")]
