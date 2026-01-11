from dataclasses import dataclass
from datetime import datetime

@dataclass
class Notifikazio:
    deskribapena: str
    dataOrdua: datetime
    mota: str

    def __init__(self, deskribapena: str,
                 dataOrdua: datetime, mota: str):
        self.deskribapena = deskribapena
        self.dataOrdua = dataOrdua
        self.mota = mota