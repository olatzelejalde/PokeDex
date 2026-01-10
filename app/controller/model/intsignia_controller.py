class IntsigniaController:
    def __init__(self, db):
        self.db = db

    def get_all_badges_for_user(self, uid):
        """
        Devuelve todas las insignias y, para cada una, su progreso y si ya fue obtenida.
        """
        query = """
            SELECT 
                i.izena, 
                i.deskripzioa, 
                i.helburua,
                COALESCE(ei.jarraipena, 0) as jarraipena,
                CASE WHEN ei.intsignia_izena IS NOT NULL THEN 1 ELSE 0 END as lortua
            FROM intsignia i
            LEFT JOIN erabiltzaileak_intsigniak ei 
                ON i.izena = ei.intsignia_izena AND ei.erabiltzaile_id = ?
        """
        rows = self.db.select(query, [uid])
        return [dict(row) for row in rows]

    def award_badge(self, uid, badge_name):
        """
        Otorga una insignia al usuario solo si no la tiene ya.
        """
        return self.db.insert(
            """
            INSERT OR IGNORE INTO erabiltzaileak_intsigniak (erabiltzaile_id, intsignia_izena, jarraipena)
            VALUES (?, ?, ?)
            """,
            [uid, badge_name, 0]  
        )
