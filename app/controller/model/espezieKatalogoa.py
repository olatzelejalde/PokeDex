from dataclasses import dataclass
import requests

DISPLAY_NAMES = {
    'normal': 'Normala', 'fire': 'Sua', 'water': 'Ura', 'grass': 'Belarra',
    'electric': 'Elektrikoa', 'ice': 'Izotza', 'fighting': 'Borroka', 'poison': 'Pozoia',
    'ground': 'Lurra', 'flying': 'Hegaldia', 'psychic': 'Psikikoa', 'bug': 'Intsektua',
    'rock': 'Harria', 'ghost': 'Mamua', 'dragon': 'Dragoia', 'dark': 'Iluna',
    'steel': 'Altzairua', 'fairy': 'Maitagarria'
}

EUS_TO_ENG = {
    'normala': 'normal', 'sua': 'fire', 'ura': 'water', 'belarra': 'grass',
    'elektrikoa': 'electric', 'izotza': 'ice', 'borroka': 'fighting', 'pozoia': 'poison',
    'lurra': 'ground', 'hegaldia': 'flying', 'psikikoa': 'psychic', 'intsektua': 'bug',
    'harria': 'rock', 'mamua': 'ghost', 'dragoia': 'dragon', 'iluna': 'dark',
    'altzairua': 'steel', 'maitagarria': 'fairy'
}

@dataclass
class EspezieKatalogoa:
    def __init__(self, db):
        self.db = db

    # ========================
    # Espezie bilaketa
    # ========================

    # Espezie guztiak lortzen ditu
    def get_all(self):
        return [dict(row) for row in self.db.select("SELECT * FROM espeziea ORDER BY izena")]

    # Izena bidez espezie bat lortzen du
    def get_by_name(self, izena):
        rows = self.db.select("SELECT * FROM espeziea WHERE LOWER(izena) = LOWER(?)", [izena])
        return dict(rows[0]) if rows else None

    # ========================
    # SORTU
    # ========================
    def create(self, izena, mota1, mota2, osasuna, atakea, defentsa,
               atake_berezia, defentsa_berezia, abiadura, irudia, deskribapena=None):
        # Espezie berria sortu DBan
        if not izena or not mota1:
            raise ValueError("Izena eta mota1 beharrezkoak dira")
        self.db.insert(
            """INSERT INTO espeziea (izena, mota1, mota2, osasuna, atakea, defentsa,
               atake_berezia, defentsa_berezia, abiadura, irudia, deskribapena)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [izena, mota1, mota2, osasuna, atakea, defentsa,
             atake_berezia, defentsa_berezia, abiadura, irudia, deskribapena]
        )
    
    # ========================
    # Kontzultak
    # ========================

    # Moten arteko eraginkortasuna kalkulatu (ahuleziak eta indarrak)
    def get_type_effectiveness(self, espezie_name):
        row = self.db.select("SELECT * FROM espeziea WHERE LOWER(izena) = LOWER(?)", [espezie_name])
        if not row:
            return None

        poke = dict(row[0])

        mis_tipos_eus = []
        if poke.get('mota1'):
            mis_tipos_eus.append(str(poke['mota1']).lower())
        if poke.get('mota2'):
            mis_tipos_eus.append(str(poke['mota2']).lower())

        multiplicadores = {}

        for t_eus in mis_tipos_eus:
            t_eng = EUS_TO_ENG.get(t_eus, t_eus)
            url = f"https://pokeapi.co/api/v2/type/{t_eng}"
            try:
                response = requests.get(url, timeout=10)
            except Exception:
                continue

            if response.status_code != 200:
                continue

            relaciones = response.json().get('damage_relations', {})

            for t in relaciones.get('double_damage_from', []):
                name = t['name']
                multiplicadores[name] = multiplicadores.get(name, 1.0) * 2.0
            for t in relaciones.get('half_damage_from', []):
                name = t['name']
                multiplicadores[name] = multiplicadores.get(name, 1.0) * 0.5
            for t in relaciones.get('no_damage_from', []):
                name = t['name']
                multiplicadores[name] = multiplicadores.get(name, 1.0) * 0.0

        ahuleziak = []
        indarrak = []
        for tipo_ataque, mult in multiplicadores.items():
            if mult == 1.0:
                continue
            info = {
                "Mota": DISPLAY_NAMES.get(tipo_ataque, tipo_ataque.title()),
                "Biderkatzailea": mult,
                "TypeKey": tipo_ataque,
            }
            if mult > 1:
                ahuleziak.append(info)
            else:
                indarrak.append(info)

        ahuleziak.sort(key=lambda x: x['Biderkatzailea'], reverse=True)
        indarrak.sort(key=lambda x: x['Biderkatzailea'])

        return {
            "Izena": poke.get('izena', espezie_name),
            "Espezie": poke.get('irudia'),
            "Ahuleziak": ahuleziak,
            "Indarrak": indarrak,
        }

    # ---------------------------------------------------------
    # EBOLUZIOA (PokéAPI bidez, irudiak DB-tik)
    # ---------------------------------------------------------
    def get_ebo_info(self, izena):
        db_row = self.db.select(
            "SELECT id FROM espeziea WHERE LOWER(izena) = LOWER(?)",
            [izena],
        )

        species_ref = str(db_row[0]['id']) if db_row else str(izena).lower()
        try:
            species = requests.get(
                f"https://pokeapi.co/api/v2/pokemon-species/{species_ref}",
                timeout=10,
            )
        except Exception:
            return []

        if species.status_code != 200:
            return []

        chain_url = (species.json().get('evolution_chain') or {}).get('url')
        if not chain_url:
            return []

        try:
            chain_res = requests.get(chain_url, timeout=10)
        except Exception:
            return []
        if chain_res.status_code != 200:
            return []

        chain = chain_res.json().get('chain')
        if not chain:
            return []

        names = []

        def _walk(node):
            if not node:
                return
            sp = (node.get('species') or {}).get('name')
            if sp:
                names.append(sp)
            for nxt in node.get('evolves_to', []) or []:
                _walk(nxt)

        _walk(chain)

        result = []
        for n in names:
            r = self.db.select(
                "SELECT izena, irudia FROM espeziea WHERE LOWER(izena) = LOWER(?)",
                [n],
            )
            if r:
                result.append({"izena": r[0]['izena'], "irudia": r[0]['irudia']})
            else:
                result.append({"izena": n.title(), "irudia": ""})

        return result

    # ---------------------------------------------------------
    # SCAN (Pokémon baten azterketa osoa)
    # ---------------------------------------------------------
    def get_scan_info(self, izena):
        rows = self.db.select("SELECT * FROM espeziea WHERE LOWER(izena) = LOWER(?)", [izena])
        if not rows:
            return None

        poke = dict(rows[0])
        stats = {
            "Osasuna": poke.get('osasuna', 0),
            "Atakea": poke.get('atakea', 0),
            "Defentsa": poke.get('defentsa', 0),
            "AtakeBerezia": poke.get('atake_berezia', 0),
            "DefentsaBerezia": poke.get('defentsa_berezia', 0),
            "Abiadura": poke.get('abiadura', 0),
        }
        media = round(sum(stats.values()) / 6.0, 2)

        eff = self.get_type_effectiveness(poke.get('izena', izena)) or {"Ahuleziak": [], "Indarrak": []}

        return {
            "Izena": poke.get('izena', izena),
            "Irudia": poke.get('irudia', ''),
            "Media": media,
            "Stats": stats,
            "Efectividad": {
                "Ahuleziak": eff.get('Ahuleziak', []),
                "Indarrak": eff.get('Indarrak', []),
            },
        }
