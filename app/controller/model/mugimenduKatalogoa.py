from dataclasses import dataclass

@dataclass
class MugimenduKatalogoa:
    def __init__(self, db):
        self.db = db

    # ========================
    # Mugimendu bilaketa
    # ========================

    # espezie izena bidez mugimenduak lortzen ditu
    def get_by_espezie(self, espezie_izena):
        rows = self.db.select("""
            SELECT m.* FROM mugimendua m
            JOIN jakin_dezake em ON m.izena = em.mugimendu_izena
            WHERE em.espezie_izena = ?
        """, [espezie_izena])
        return [dict(row) for row in rows]
