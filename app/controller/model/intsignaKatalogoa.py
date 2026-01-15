class IntsignaKatalogoa:
    def __init__(self, db):
        # Datu-basearen konexioa gordetzen du
        self.db = db

    # ========================
    # Intsignia bilaketa
    # ========================

    # Erabiltzaile baten intsigniak lortzen ditu,
    # eta intsigna lortuta dagoen ala ez adierazten du
    def get_by_user(self, uid):
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
        # Erabiltzaileari intsignia memoriaz esleitzen dio (DBan sortu).
        return self.db.insert(
            """
            INSERT OR IGNORE INTO erabiltzaileak_intsigniak (erabiltzaile_id, intsignia_izena, jarraipena)
            VALUES (?, ?, ?)
            """,
            [uid, badge_name, 0]  
        )
    
    # ========================
    # Intsignia kudeaketa
    # ========================

    def intsigniaDu(self, uid, badge_name) -> bool:
        # Erabiltzaileak intsignia lortuta duen egiaztatzen du.
        badges = self.get_by_user(uid)
        for b in badges:
            if b.get("izena") == badge_name:
                return bool(b.get("lortua", 0))
        return False
    
    #intsigna ez badu
    def intsigniaGehitu(self, uid, badge_name) -> None:
        # Intsigniaren jarraipena handitu eta behar izanez gero sortu.
        if not self.intsigniaDu(uid, badge_name) and not self.existitzenDa(uid, badge_name):    
            self.award(uid, badge_name)
        self.jarraipenaEguneratu(uid, badge_name)

    def jarraipenaEguneratu(self, uid, badge_name) -> None:
        # Jarraipena +1 handitu DBan.
        self.db.update(
            """
            UPDATE erabiltzaileak_intsigniak
            SET jarraipena = jarraipena + 1
            WHERE erabiltzaile_id = ? AND intsignia_izena = ?
            """,
            [uid, badge_name]
        )
    
    def existitzenDa(self, uid, badge_name) -> bool:
        # Erabiltzaileak intsignia erregistroa duen egiaztatu.
        row = self.db.select(
            """
            SELECT 1 FROM erabiltzaileak_intsigniak
            WHERE erabiltzaile_id = ? AND intsignia_izena = ?
            """,
            [uid, badge_name]
        )
        return bool(row)