from dataclasses import dataclass
from typing import Optional, List

from app.controller.model.taldea import Taldea

@dataclass
class Erabiltzailea:
    # Erabiltzailearen oinarrizko atributuak
    id: int
    izena: str
    abizena: str
    erabiltzaileIzena: str
    telegramKontua: str
    chat_id: Optional[int]
    pasahitza: str
    rola: str
    # Erlazioak
    lagunZer: List["Erabiltzailea"]
    taldeZer: List["Taldea"]

    def __init__(self, id: int, izena: str, abizena: str, erabiltzaileIzena: str,
                 pasahitza: str, rola: str, telegramKontua: str = "", chat_id: Optional[int] = None):
        # Erabiltzailearen propietateak hasieratu
        
        # Oinarrizko datuak esleitzen ditu
        self.id = id
        self.izena = izena
        self.abizena = abizena
        self.erabiltzaileIzena = erabiltzaileIzena
        self.telegramKontua = telegramKontua
        self.chat_id = chat_id
        self.pasahitza = pasahitza
        self.rola = rola
        # Erlazio-zerrendak hasieratzen ditu
        self.intsigniaZer = []
        self.lagunZer = []
        self.taldeZer = []

    @staticmethod
    def sortu( izena: str, abizena: str, erabilIzena: str, 
                          pasahitza: str, pasahitza2: str, telegramKontua: str = None,
                          db=None) -> "Erabiltzailea":
        # Erabiltzaile berria DBan sortu balidazioekin
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
        # Huts eginez gero
        raise ValueError("Errorea erabiltzailea sortzean")
    
    def gehitu_laguna(self, laguna: "Erabiltzailea") -> None:
        # Laguna memorian gehitu
        if laguna not in self.lagunZer:
            self.lagunZer.append(laguna)

    def kendu_laguna(self, laguna: "Erabiltzailea") -> None:
        # Laguna memorian ezabatu
        if laguna in self.lagunZer:
            self.lagunZer.remove(laguna)

    def erabiltzaileaDa(self, uid: int) -> bool:
        # Erabiltzailea ID hori duen egiaztatu
        return self.id == uid
    
    def getLagunZerrenda(self, telegram: bool) -> List["Erabiltzailea"]:
        # Lagunen zerrenda lortu (Telegram iragazkiarekin aukeran)
        lagunak = []
        for lagun in self.lagunZer:
            if telegram and (lagun.telegramKontua and lagun.chat_id):
                lagunak.append(lagun)
            if not telegram:
                lagunak.append(lagun)
        return lagunak
