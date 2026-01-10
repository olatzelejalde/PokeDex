class IntsigniaController:
    def __init__(self, db):
        self.db = db

    def get_all_badges_for_user(self, uid):
        """
        Itzultzen ditu erabiltzaileak dituen insignia guztiak,
        eta 'lortua' eremua du bakoitzarentzat.
        """
        query = """
            SELECT 
                i.izena, 
                i.deskripzioa, 
                i.helburua,
                CASE WHEN ei.intsignia_izena IS NOT NULL THEN 1 ELSE 0 END as lortua
            FROM intsignia i
            LEFT JOIN erabiltzaileak_intsigniak ei 
                ON i.izena = ei.intsignia_izena AND ei.erabiltzaile_id = ?
        """
        rows = self.db.select(query, [uid])
        return [dict(row) for row in rows]

    def award_badge(self, uid, badge_name):
        """
        Insignia ematen dio erabiltzaileari, baina bakarrik jada lortuta ez badauka.
        """
        return self.db.insert(
            """
            INSERT OR IGNORE INTO erabiltzaileak_intsigniak (erabiltzaile_id, intsignia_izena, lortua)
            VALUES (?, ?, 1)
            """,
            [uid, badge_name]
        )
