from dataclasses import dataclass
from typing import List


@dataclass
class Taldea:
    izena: str

    def __init__(self, id: int, izena: str, erabiltzaile_id: int):
        self.id = id
        self.izena = izena
        self.erabiltzaile_id = erabiltzaile_id

    @staticmethod
    def sortu(izena: str, erabiltzaile_id: int, db=None) -> "Taldea":
        """Sortu talde berria DBan"""
        if not izena or len(izena.strip()) == 0:
            raise ValueError("Taldearen izena ezin da hutsik egon")
        
        if db:
            db.insert(
                "INSERT INTO taldea (izena, erabiltzaile_id) VALUES (?, ?)",
                [izena, erabiltzaile_id]
            )
            
            rows = db.select("SELECT * FROM taldea WHERE izena = ? AND erabiltzaile_id = ?", 
                           [izena, erabiltzaile_id])
            if rows:
                row = rows[0]
                return Taldea(
                    id=row['id'],
                    izena=row['izena'],
                    erabiltzaile_id=row['erabiltzaile_id']
                )
        
        raise ValueError("Errorea taldea sortzean")
