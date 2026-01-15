from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

from app.controller.model.taldea import Taldea

@dataclass
class TaldeKatalogoa:
    def __init__(self, db=None):
        self.db = db
        self.taldeak: List[Taldea] = []
        self.nireTalde = self

    # ========================
    # KATALOGOA METODOAK
    # ========================

    def bilatu_by_id(self, tid: int) -> Optional[Taldea]:
        """Bilatu taldea IDren arabera"""
        for taldea in self.taldeak:
            if taldea.id == tid:
                return taldea
        return None

    def bilatu_by_erabiltzaile(self, uid: int) -> List[Taldea]:
        """Bilatu erabiltzailearen taldeak"""
        return [t for t in self.taldeak if t.erabiltzaile_id == uid]

    def gehitu(self, taldea: Taldea) -> None:
        """Gehitu taldea katalogoan"""
        self.taldeak.append(taldea)

    def guztiak(self) -> List[Taldea]:
        """Itzuli guztiak taldeak"""
        return self.taldeak

    # ========================
    # kargatu from BD
    # ========================

    def kargatu_from_bd(self) -> None:
        """Kargatu guztiak taldeak BDtik"""
        if not self.db:
            return
        rows = self.db.select("SELECT * FROM taldea")
        for row in rows:
            taldea = Taldea(
                id=row['id'],
                izena=row['izena'],
                erabiltzaile_id=row['erabiltzaile_id']
            )
            self.gehitu(taldea)

    # ========================
    # SORTU / EZABATU
    # ========================

    def sortu(self, izena: str, erabiltzaile_id: int) -> Taldea:
        """Sortu talde berria"""
        taldea = Taldea.sortu(izena, erabiltzaile_id, self.db)
        self.gehitu(taldea)

        # 1. Erabiltzailearen izena lortu datu-basetik
        erabiltzailea = self.db.select("SELECT izena FROM erabiltzailea WHERE id = ?", [erabiltzaile_id])
        egile_izena = erabiltzailea[0]['izena'] if erabiltzailea else "Erabiltzaile ezezaguna"

        # 2. Deskribapena prestatu egilearen izenarekin
        data_gaur = datetime.now().strftime("%Y-%m-%d %H:%M")
        deskribapena = f"{egile_izena}-(e)k talde berria sortu du: {izena}."
    
        # 3. Txertatu changelog taulan
        self.db.insert(
            "INSERT INTO changelog (bertsioa, data, deskribapena, egilea) VALUES (?, ?, ?, ?)",
            ["TALDEA", data_gaur, deskribapena, str(erabiltzaile_id)]
        )
    
        return taldea

    def ezabatu(self, tid: int) -> None:
        """Ezabatu taldea eta notifikazioa sortu"""
        if self.db:
            # 1. Taldearen informazioa lortu (ezabatu aurretik!)
            query_info = """
                SELECT t.izena as talde_izena, e.izena as egile_izena, e.id as egile_id
                FROM taldea t
                JOIN erabiltzailea e ON t.erabiltzaile_id = e.id
                WHERE t.id = ?
            """
            datuak = self.db.select(query_info, [tid])

            if datuak:
                info = datuak[0]
                talde_izena = info['talde_izena']
                egile_izena = info['egile_izena']
                egile_id = info['egile_id']

                # 2. Taldea datu-basetik ezabatu
                self.db.delete("DELETE FROM taldea WHERE id = ?", [tid])

                # 3. Notifikazioa changelog taulan txertatu
                data_gaur = datetime.now().strftime("%Y-%m-%d %H:%M")
                deskribapena = f"{egile_izena}-(e)k {talde_izena} taldea ezabatu du."
                
                self.db.insert(
                    "INSERT INTO changelog (bertsioa, data, deskribapena, egilea) VALUES (?, ?, ?, ?)",
                    ["TALDEA", data_gaur, deskribapena, str(egile_id)]
                )

        # 4. Lokaleko zerrendatik ezabatu (lehen zenuen bezala)
        self.taldeak = [t for t in self.taldeak if t.id != tid]

    # ========================
    # POKEMON (TALDEAREN KONTROLA)
    # ========================

    def get_pokemonak(self, tid: int) -> List[dict]:
        """Lortu taldearen pokemonak"""
        if self.db:
            rows = self.db.select(
                """SELECT p.id, p.izena, e.irudia, e.mota1 as mota, e.mota2,
                          e.osasuna as hp, e.atakea, e.defentsa, 
                          e.atake_berezia, e.defentsa_berezia, e.abiadura, e.deskribapena
                   FROM pokemon p
                   JOIN ditu d ON p.id = d.pokemon_id
                   JOIN espeziea e ON p.espezie_izena = e.izena
                   WHERE d.taldea_id = ?""",
                [tid]
            )
            return [self._row_to_pokemon_dict(row) for row in rows]
        return []

    def gehitu_pokemon(self, tid: int, pid: int) -> None:
        """Gehitu pokemona taldera"""
        if not self.db:
            return

        exists = self.db.select("SELECT id FROM pokemon WHERE id = ?", [pid])
        if not exists:
            espezie = self.db.select("SELECT id, izena FROM espeziea WHERE id = ?", [pid])
            if not espezie:
                raise ValueError("Espeziea ez da existitzen")
            esp = espezie[0]
            self.db.insert(
                "INSERT INTO pokemon (id, espezie_izena, izena) VALUES (?, ?, ?)",
                [esp['id'], esp['izena'], esp['izena']]
            )

        self.db.insert(
            "INSERT INTO ditu (taldea_id, pokemon_id) VALUES (?, ?)",
            [tid, pid]
        )
        # 2. Informazioa lortu notifikaziorako: Erabiltzailea, Taldearen izena eta Pokemonaren izena
        query = """
            SELECT e.izena as egile_izena, e.id as egile_id, t.izena as talde_izena, p.izena as poke_izena
            FROM taldea t
            JOIN erabiltzailea e ON t.erabiltzaile_id = e.id
            JOIN pokemon p ON p.id = ?
            WHERE t.id = ?
        """
        datuak = self.db.select(query, [pid, tid])

        if datuak:
            info = datuak[0]
            egile_izena = info['egile_izena']
            egile_id = info['egile_id']
            talde_izena = info['talde_izena']
            poke_izena = info['poke_izena']

            # 3. Deskribapena osatu
            data_gaur = datetime.now().strftime("%Y-%m-%d %H:%M")
            deskribapena = f"{egile_izena}-(e)k {poke_izena} gehitu du {talde_izena} taldera."

            # 4. Changelog-ean txertatu
            self.db.insert(
                "INSERT INTO changelog (bertsioa, data, deskribapena, egilea) VALUES (?, ?, ?, ?)",
                ["POKEMON", data_gaur, deskribapena, str(egile_id)]
            )

    def kendu_pokemon(self, tid: int, pid: int) -> None:
        """Kendu pokemona taldetik"""
        if self.db:
            self.db.delete(
                "DELETE FROM ditu WHERE taldea_id = ? AND pokemon_id = ?",
                [tid, pid]
            )

        data_gaur = datetime.now().strftime("%Y-%m-%d %H:%M")
        deskribapena = f"Pokemona kendu da taldetik: {pid}."

        egilea = "unknown"
        try:
            owner_rows = self.db.select(
                "SELECT erabiltzaile_id FROM taldea WHERE id = ?", [tid]
            )
            if owner_rows:
                egilea = str(owner_rows[0]["erabiltzaile_id"])
        except Exception:
            pass

        self.db.insert(
            "INSERT INTO changelog (bertsioa, data, deskribapena, egilea) VALUES (?, ?, ?, ?)",
            ["POKEMON", data_gaur, deskribapena, egilea]
        )

    # ========================
    # KONTROL METODOAK
    # ========================

    def get_by_user(self, uid):
        rows = self.db.select("""
            SELECT t.*, COUNT(tp.pokemon_id) as pokemon_kop
            FROM taldea t
            LEFT JOIN ditu tp ON t.id = tp.taldea_id
            WHERE t.erabiltzaile_id = ?
            GROUP BY t.id
        """, [uid])
        return [dict(row) for row in rows]

    def get_pokemonak_controller(self, tid):
        rows = self.db.select("""
            SELECT p.*, e.mota1, e.mota2, e.irudia
            FROM ditu tp
            JOIN pokemon p ON tp.pokemon_id = p.id
            JOIN espeziea e ON p.espezie_izena = e.izena
            WHERE tp.taldea_id = ?
        """, [tid])
        return [dict(row) for row in rows]

    def create(self, izena, uid):
        return self.db.insert(
            "INSERT INTO taldea (izena, erabiltzaile_id) VALUES (?, ?)",
            [izena, uid]
        )

    def add_pokemon(self, tid, pid):
        self.db.insert(
            "INSERT OR IGNORE INTO ditu (taldea_id, pokemon_id) VALUES (?, ?)",
            [tid, pid]
        )

    def delete(self, tid):
        self.db.delete("DELETE FROM taldea WHERE id = ?", [tid])

    def remove_pokemon(self, tid, pid):
        self.db.delete(
            "DELETE FROM ditu WHERE taldea_id = ? AND pokemon_id = ?",
            [tid, pid]
        )

    # ========================
    # LAGUNTZAILEAK
    # ========================

    @staticmethod
    def _row_to_pokemon_dict(row) -> dict:
        try:
            return {
                'id': row['id'],
                'izena': row['izena'],
                'irudia': row['irudia'],
                'mota': row['mota'],
                'mota2': row['mota2'] if row['mota2'] else None,
                'hp': row['hp'],
                'atakea': row['atakea'],
                'defentsa': row['defentsa'],
                'atake_berezia': row['atake_berezia'],
                'defentsa_berezia': row['defentsa_berezia'],
                'abiadura': row['abiadura'],
                'deskribapena': row['deskribapena']
            }
        except (KeyError, TypeError):
            return {
                'id': None,
                'izena': 'Unknown',
                'irudia': None,
                'mota': 'Unknown',
                'mota2': None,
                'hp': 0,
                'atakea': 0,
                'defentsa': 0,
                'atake_berezia': 0,
                'defentsa_berezia': 0,
                'abiadura': 0
            }