from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

from app.domain.taldea import Taldea

@dataclass
class TaldeKatalogoa:
    taldeak: List[Taldea]
    nireTalde: "TaldeKatalogoa"
    db: object  # Conexión a BD

    def __init__(self, db=None):
        self.taldeak = []
        self.nireTalde = self
        self.db = db

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

    # ---- Métodos de negocio ----

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

    def sortu(self, izena: str, erabiltzaile_id: int) -> Taldea:
        """Sortu talde berria"""
        taldea = Taldea.sortu(izena, erabiltzaile_id, self.db)
        self.gehitu(taldea)

        #NOTIFIKAZIOA: Taldea sortu dela erregistratu
        data_gaur= datetime.now().strftime("%Y-%m-%d %H:%M")
        deskribapena= f"Talde berria sortu du: {izena}."
        self.db.insert(
            "INSERT INTO changelog (bertsioa, data, deskribapena, egilea) VALUES (?, ?, ?, ?)",
            ["TALDEA", data_gaur, deskribapena, str(erabiltzaile_id)]
        )
        return taldea

    def ezabatu(self, tid: int) -> None:
        """Ezabatu taldea"""
        if self.db:
            self.db.delete("DELETE FROM taldea WHERE id = ?", [tid])
        self.taldeak = [t for t in self.taldeak if t.id != tid]

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
            result = [self._row_to_pokemon_dict(row) for row in rows]
            return result
        return []

    def gehitu_pokemon(self, tid: int, pid: int) -> None:
        """Gehitu pokemona taldera"""
        if not self.db:
            return

        # Asegurar que el pokemon existe; si no, crearlo a partir de espeziea
        exists = self.db.select("SELECT id FROM pokemon WHERE id = ?", [pid])
        if not exists:
            espezie = self.db.select("SELECT id, izena FROM espeziea WHERE id = ?", [pid])
            if not espezie:
                raise ValueError("Espeziea ez da existitzen")
            esp = espezie[0]
            # Crear entrada mínima en pokemon con mismo id
            self.db.insert(
                "INSERT INTO pokemon (id, espezie_izena, izena) VALUES (?, ?, ?)",
                [esp['id'], esp['izena'], esp['izena']]
            )

        self.db.insert(
            "INSERT INTO ditu (taldea_id, pokemon_id) VALUES (?, ?)",
            [tid, pid]
        )
        # NOTIFIKAZIOA: Pokemona taldera gehitu dela erregistratu
        data_gaur= datetime.now().strftime("%Y-%m-%d %H:%M")
        deskribapena= f"Pokemona gehitu da taldera: {pid}."

        egilea = "unknown"
        try:
            owner_rows = self.db.select("SELECT erabiltzaile_id FROM taldea WHERE id = ?", [tid])
            if owner_rows:
                egilea = str(owner_rows[0]["erabiltzaile_id"])
        except Exception:
            pass

        self.db.insert(
            "INSERT INTO changelog (bertsioa, data, deskribapena, egilea) VALUES (?, ?, ?, ?)",
            ["POKEMON", data_gaur, deskribapena, egilea]
        )

    def kendu_pokemon(self, tid: int, pid: int) -> None:
        """Kendu pokemona taldetik"""
        if self.db:
            self.db.delete(
                "DELETE FROM ditu WHERE taldea_id = ? AND pokemon_id = ?",
                [tid, pid]
            )

    #def get_pokemonak(self, tid: int):
    #    return self.db.select(
    #        "SELECT p.id, p.izena FROM pokemon p JOIN ditu d ON d.pokemon_id = p.id WHERE d.taldea_id = ?",
    #        [tid]
    #    )


    @staticmethod
    def _row_to_pokemon_dict(row) -> dict:
        """Convierte una fila de pokemon a diccionario"""
        # sqlite3.Row es dict-like, acceso directo con []
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
        except (KeyError, TypeError) as e:
            # Si falla, retornar dict vacío o con valores por defecto
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
