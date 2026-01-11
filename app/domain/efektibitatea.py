from dataclasses import dataclass

@dataclass
class Efektibitatea:
    biderkatzailea: float

    def __init__(self, biderkatzailea: float):
        self.biderkatzailea = biderkatzailea