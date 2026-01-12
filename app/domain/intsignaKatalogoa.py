class IntsignaKatalogoa:
    def __init__(self, db):
        self.db = db

    def get_by_user(self, uid):
        """
        Devuelve todas las insignias y, para cada una, su progreso y si ya fue obtenida.
        """
        query = """
            SELECT 
                i.izena, 
                i.deskripzioa, 
                i.helburua,
                COALESCE(ei.jarraipena, 0) as jarraipena,
                CASE WHEN COALESCE(ei.jarraipena, 0) >= i.helburua THEN 1 ELSE 0 END as lortua
            FROM intsignia i
            LEFT JOIN erabiltzaileak_intsigniak ei 
                ON i.izena = ei.intsignia_izena AND ei.erabiltzaile_id = ?
        """
        rows = self.db.select(query, [uid])
        return [dict(row) for row in rows]

    def award(self, uid, badge_name):
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
    
    def intsigniaDu(self, uid, badge_name) -> bool:
        helburua = self.db.select(
            """
            SELECT helburua FROM intsignia
            WHERE izena = ?
            """,
            [badge_name]
        )
        jarraipena = self.db.select(
            """
            SELECT jarraipena FROM erabiltzaileak_intsigniak
            WHERE intsignia_izena = ? AND erabiltzaile_id = ?
            """,
            [badge_name, uid]
        )
        if helburua == jarraipena:
            return True
        return False
    
    def jarraipenaEguneratu(self, uid, badge_name) -> None:
        """Erabiltzailearen intsigniaren jarraipena eguneratu"""
        self.db.update(
            """
            UPDATE erabiltzaileak_intsigniak
            SET jarraipena = jarraipena + 1
            WHERE erabiltzaile_id = ? AND intsignia_izena = ?
            """,
            [uid, badge_name]
        )
    
    def existitzenDa(self, uid, badge_name) -> bool:
        """Egiaztatu erabiltzaileak intsignia bat duen"""
        row = self.db.select(
            """
            SELECT 1 FROM erabiltzaileak_intsigniak
            WHERE erabiltzaile_id = ? AND intsignia_izena = ?
            """,
            [uid, badge_name]
        )
        return bool(row)
    
    def intsigniaGehitu(self, uid, badge_name) -> None:
        if not self.intsigniaDu(uid, badge_name) and not self.existitzenDa(uid, badge_name):    
            self.award(uid, badge_name)
        self.jarraipenaEguneratu(uid, badge_name)