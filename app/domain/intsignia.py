from dataclasses import dataclass

@dataclass
class Intsignia:
    izena: str
    deskipzioa: str
    helburua: str
    kopurua: int

    def __init__(self, izena: str, deskipzioa: str,
                 helburua: str, kopurua: int):
        self.izena = izena
        self.deskipzioa = deskipzioa
        self.helburua = helburua
        self.kopurua = kopurua