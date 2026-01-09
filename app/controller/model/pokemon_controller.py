import random

class PokemonController:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        rows = self.db.select("""
            SELECT p.*, e.mota1, e.mota2, e.irudia
            FROM pokemon p
            JOIN espeziea e ON p.espezie_izena = e.izena
        """)
        return [dict(row) for row in rows]

    def get_by_id(self, pid):
        rows = self.db.select("""
            SELECT p.*, e.mota1, e.mota2, e.irudia
            FROM pokemon p
            JOIN espeziea e ON p.espezie_izena = e.izena
            WHERE p.id = ?
        """, [pid])
        return dict(rows[0]) if rows else None

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

    def _generate_new_groups(self):
        try:
            rows = self.db.select("SELECT izena, irudia FROM espeziea")
            all_pokemons = [dict(row) for row in rows] if rows else []
            if not all_pokemons: raise Exception("Datu-basea hutsik dago")
        except:
            # DB-ak huts egiten badu, Pikachu lehenetsi moduan erabili
            all_pokemons = [{"izena": "Pikachu", "irudia": ""}]

        fake_data = []
        entrenadoreZerrenda = ["Ash", "Misty", "Brock", "Gary"]

        for i, nombre in enumerate(entrenadoreZerrenda):
            team_size = random.randint(3, 6)  # 3 eta 6 Pokémon arteko taldea
            real_size = min(len(all_pokemons), team_size)
            selected_pokemons = random.sample(all_pokemons, real_size)  # Ausaz aukeratu

            pokemons_talde = []
            for p in selected_pokemons:
                pokemons_talde.append({
                    "Pokemon_Izena": p['izena'],
                    "Irudia": p['irudia']
                })

            talde = {
                "ErabiltzaileIzena": nombre,
                "TaldeId": i + 1,
                "Izena": f"{nombre}-(r)en taldea",
                "Pokemon": pokemons_talde
            }
            fake_data.append(talde)
        return fake_data

    # Erabiltzaileak eta beren Pokémon-ak lortu (edo talde espezifiko bat)
    def get_users_with_pokemon(self, talde_id=None):
        if self.cached_groups is None:
            self.cached_groups = self._generate_new_groups()

        data = self.cached_groups
        if talde_id is not None:
            for g in data:
                if g["TaldeId"] == talde_id: return g
            return None
        return data

    # Talde bateko Pokémon onena (MVP) lortu estatistiken batez bestekoa erabiliz
    def get_best_pokemon_by_group(self, talde_id):
        talde = self.get_users_with_pokemon(talde_id)
        if not talde: return None

        pokemon_onena = None
        mediaonena = -1

        for p in talde["Pokemon"]:
            nombre = p["Pokemon_Izena"]
            rows = self.db.select("SELECT * FROM espeziea WHERE izena = ?", [nombre])
            if rows:
                stats = dict(rows[0])
                # Estatistika guztien batura
                suma_stats = (
                        stats.get('osasuna', 0) +
                        stats.get('atakea', 0) +
                        stats.get('defentsa', 0) +
                        stats.get('atake_berezia', 0) +
                        stats.get('defentsa_berezia', 0) +
                        stats.get('abiadura', 0)
                )
                media = suma_stats / 6.0

                # Batez besteko altuena duena gorde
                if media > mediaonena:
                    mediaonena = media
                    pokemon_onena = {
                        "Izena": stats['izena'],
                        "Media": round(media, 2),
                        "Id": stats['id'],
                        "PokeImage": stats['irudia'],
                        "Estatistikak": {
                            "Osasuna": stats['osasuna'],
                            "Atakea": stats['atakea'],
                            "Defentsa": stats['defentsa'],
                            "AtakeBerezia": stats.get('atake_berezia', 0),
                            "DefentsaBerezia": stats.get('defentsa_berezia', 0),
                            "Abiadura": stats['abiadura']
                        }
                    }
        return pokemon_onena