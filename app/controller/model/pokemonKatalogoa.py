from dataclasses import dataclass
from typing import List

@dataclass
class PokemonKatalogoa:
    def __init__(self, db):
        self.db = db
        self.cached_groups = None  # Taldeen datuak memorian gordetzeko (cache)

    # ========================
    # Pokemon bilaketa
    # ========================

    #Pokemon guztiak lortzen ditu
    def get_all(self):
        rows = self.db.select("""
            SELECT p.*, e.mota1, e.mota2, e.irudia
            FROM pokemon p
            JOIN espeziea e ON p.espezie_izena = e.izena
        """)
        return [dict(row) for row in rows]

    #Id bidez pokemon bat lortzen du
    def get_by_id(self, pid):
        rows = self.db.select("""
            SELECT p.*, e.mota1, e.mota2, e.irudia
            FROM pokemon p
            JOIN espeziea e ON p.espezie_izena = e.izena
            WHERE p.id = ?
        """, [pid])
        return dict(rows[0]) if rows else None
    
    # Talde bateko pokemonak lortzen ditu
    def get_users_with_pokemon(self, talde_id=None):
        data = self.cached_groups or []
        if talde_id is not None:
            for g in data:
                if g["TaldeId"] == talde_id:
                    return g
            return None
        return data

    # ========================
    # SORTU
    # ========================

    # Pokemon berria sortzen du
    def create(self, espezie_izena, izena=None):
        e = self.db.select("SELECT * FROM espeziea WHERE izena = ?", [espezie_izena])
        if not e:
            raise ValueError("Espeziea ez da existitzen")
        e = dict(e[0])
        self.db.insert("""
            INSERT INTO pokemon (espezie_izena, izena)
            VALUES (?, ?)
        """, [espezie_izena, izena or espezie_izena])
        return self.get_by_id(self.db.connection.cursor().lastrowid)
    
    # ========================
    # TOP POKEMONA
    # ========================

    #pokemon zerrendatik onena duen pokemona lortzen du
    def get_best_pokemon_from_list(self, pokemonak):
        if not pokemonak:
            return None

        pokemon_onena = None
        media_onena = -1

        for p in pokemonak:
            nombre = p.get("Pokemon_Izena") or p.get("izena")
            if not nombre:
                continue

            rows = self.db.select(
                "SELECT * FROM espeziea WHERE LOWER(izena) = LOWER(?)",
                [nombre]
            )

            if not rows:
                continue

            stats = dict(rows[0])

            suma = (
                stats.get('osasuna', 0) +
                stats.get('atakea', 0) +
                stats.get('defentsa', 0) +
                stats.get('atake_berezia', 0) +
                stats.get('defentsa_berezia', 0) +
                stats.get('abiadura', 0)
            )

            media = suma / 6.0

            if media > media_onena:
                media_onena = media
                pokemon_onena = {
                    "Izena": stats.get('izena'),
                    "Media": round(media, 2),
                    "PokeImage": stats.get('irudia'),
                    "Estatistikak": {
                        "Osasuna": stats.get('osasuna', 0),
                        "Atakea": stats.get('atakea', 0),
                        "Defentsa": stats.get('defentsa', 0),
                        "AtakeBerezia": stats.get('atake_berezia', 0),
                        "DefentsaBerezia": stats.get('defentsa_berezia', 0),
                        "Atake berezia": stats.get('atake_berezia', 0),
                        "Defentsa berezia": stats.get('defentsa_berezia', 0),
                        "Abiadura": stats.get('abiadura', 0),
                    },
                }

        return pokemon_onena