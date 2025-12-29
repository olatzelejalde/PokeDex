from dataclasses import dataclass
from typing import Optional

@dataclass
class Erabiltzailea:
    izena: str
    abizena: str
    erabiltzaileIzena: str
    telegramKontua: Optional[str] = None
    pasahitza: str
    rola: str
    intsignaZerrenda: list = None
    lagunZerrenda: list = None
    taldeZerrenda: list = None
    notifikazioZerrenda: list = None

    def to_dict(self):
        return {
            "izena": self.izena,
            "abizena": self.abizena,
            "erabiltzaileIzena": self.erabiltzaileIzena,
            "telegramKontua": self.telegramKontua,
            "pasahitza": self.pasahitza,
            "rola": self.rola,
            "intsignaZerrenda": self.intsignaZerrenda or [],
            "lagunZerrenda": self.lagunZerrenda or [],
            "taldeZerrenda": self.taldeZerrenda or [],
            "notifikazioZerrenda": self.notifikazioZerrenda or []
        }
    
@dataclass
class Taldea:
    id: int
    izena: str
    erabiltzaileIzena: str
    pokemonak: list = None

    def to_dict(self):
        return {
            "id": self.id,
            "izena": self.izena,
            "erabiltzaileIzena": self.erabiltzaileIzena,
            "pokemonak": self.pokemonak or []
        }