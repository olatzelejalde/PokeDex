from dataclasses import dataclass
from typing import Optional, List

from app.domain.intsignia import Intsignia
from app.domain.taldea import Taldea
from app.domain.notifikazio import Notifikazio

@dataclass
class Erabiltzailea:
    id: int
    izena: str
    abizena: str
    erabiltzaileIzena: str
    telegramKontua: str
    chat_id: Optional[int]
    pasahitza: str
    rola: str
    intsigniaZer: List["Intsignia"]
    lagunZer: List["Erabiltzailea"]
    taldeZer: List["Taldea"]
    notifZer: List["Notifikazio"]

    def __init__(self, id: int, izena: str, abizena: str, erabiltzaileIzena: str,
                 pasahitza: str, rola: str, telegramKontua: str = "", chat_id: Optional[int] = None):
        self.id = id
        self.izena = izena
        self.abizena = abizena
        self.erabiltzaileIzena = erabiltzaileIzena
        self.telegramKontua = telegramKontua
        self.chat_id = chat_id
        self.pasahitza = pasahitza
        self.rola = rola
        self.intsigniaZer = []
        self.lagunZer = []
        self.taldeZer = []
        self.notifZer = []

    @staticmethod
    def sortu( izena: str, abizena: str, erabilIzena: str, 
                          pasahitza: str, pasahitza2: str, telegramKontua: str = None,
                          db=None) -> "Erabiltzailea":
        """Datuak balidatu eta erabiltzailea sortu"""
        if not erabilIzena or len(pasahitza) < 4 or pasahitza != pasahitza2:
            raise ValueError("Datuak ez dira baliozkoak")
        
        # erabiltzaile izena jada existitzen den egiaztatu
        if db:
            badago = db.select("SELECT 1 FROM erabiltzailea WHERE erabilIzena = ?", [erabilIzena])
            if badago:
                raise ValueError("Erabiltzaile izena jada erregistratuta dago")
            
            # DBan erabiltzailea sortu
            db.insert(
                """INSERT INTO erabiltzailea (izena, abizena, erabilIzena, pasahitza, telegramKontua)
                   VALUES (?, ?, ?, ?, ?)""",
                [izena, abizena, erabilIzena, pasahitza, telegramKontua]
            )
            
            # DBtik sortutako erabiltzailea lortu
            rows = db.select("SELECT * FROM erabiltzailea WHERE erabilIzena = ?", [erabilIzena])
            if rows:
                row = rows[0]
                return Erabiltzailea(
                    id=row['id'],
                    izena=row['izena'],
                    abizena=row['abizena'],
                    erabiltzaileIzena=row['erabilIzena'],
                    pasahitza=row['pasahitza'],
                    rola=row['rola'],
                    telegramKontua=row['telegramKontua'],
                    chat_id=row['chat_id']
                )  
        raise ValueError("Errorea erabiltzailea sortzean")
    
    def gehitu_laguna(self, laguna: "Erabiltzailea") -> None:
        if laguna not in self.lagunZer:
            self.lagunZer.append(laguna)

    def kendu_laguna(self, laguna: "Erabiltzailea") -> None:
        if laguna in self.lagunZer:
            self.lagunZer.remove(laguna)
