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

TYPE_KEY_MAP = {k: k for k in DISPLAY_NAMES.keys()}
class EspezieController:
    def __init__(self, db):
        self.db = db

    # Espezie guztiak lortu izenaren arabera ordenatuta
    def get_all(self):
        return [dict(row) for row in self.db.select("SELECT * FROM espeziea ORDER BY izena")]

    # Espezie bat bilatu bere izenaren arabera
    def get_by_name(self, izena):
        rows = self.db.select("SELECT * FROM espeziea WHERE izena = ?", [izena])
        return dict(rows[0]) if rows else None

    # Espezie berri bat sortu datu-basean
    def create(self, izena, mota1, mota2, osasuna, atakea, defentsa,
               atake_berezia, defentsa_berezia, abiadura, irudia, deskribapena=None):
        if not izena or not mota1:
            raise ValueError("Izena eta mota1 beharrezkoak dira")
        self.db.insert(
            """INSERT INTO espeziea (izena, mota1, mota2, osasuna, atakea, defentsa,
               atake_berezia, defentsa_berezia, abiadura, irudia, deskribapena)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [izena, mota1, mota2, osasuna, atakea, defentsa,
             atake_berezia, defentsa_berezia, abiadura, irudia, deskribapena]
        )

    # Moten arteko eraginkortasuna kalkulatu (ahuleziak eta indarrak)
    def get_type_effectiveness(self, pokemon_name):
        row = self.db.select("SELECT * FROM espeziea WHERE izena = ?", [pokemon_name])
        if not row:
            return None
        poke = dict(row[0])

        mis_tipos_eus = []
        if poke.get('mota1'): mis_tipos_eus.append(poke['mota1'].lower())
        if poke.get('mota2'): mis_tipos_eus.append(poke['mota2'].lower())

        multiplicadores = {}

        for t_eus in mis_tipos_eus:
            t_eng = EUS_TO_ENG.get(t_eus, t_eus)

            url = f"https://pokeapi.co/api/v2/type/{t_eng}"
            response = requests.get(url)

            if response.status_code != 200:
                print(f"Error API: No se encontró el tipo {t_eng}")
                continue
            relaciones = response.json()['damage_relations']
            for t in relaciones['double_damage_from']:
                name = t['name']
                multiplicadores[name] = multiplicadores.get(name, 1.0) * 2.0
            for t in relaciones['half_damage_from']:
                name = t['name']
                multiplicadores[name] = multiplicadores.get(name, 1.0) * 0.5
            for t in relaciones['no_damage_from']:
                name = t['name']
                multiplicadores[name] = multiplicadores.get(name, 1.0) * 0.0

        ahuleziak = []
        indarrak = []
        for tipo_ataque, mult in multiplicadores.items():
            if mult == 1.0: continue
            info = {
                "Mota": DISPLAY_NAMES.get(tipo_ataque, tipo_ataque.title()),
                "Biderkatzailea": mult,
                "TypeKey": tipo_ataque
            }
            if mult > 1: ahuleziak.append(info)
            else: indarrak.append(info)

        ahuleziak.sort(key=lambda x: x['Biderkatzailea'], reverse=True)
        indarrak.sort(key=lambda x: x['Biderkatzailea'])

        return {
            "Izena": pokemon_name,
            "Espezie": poke['irudia'],
            "Ahuleziak": ahuleziak,
            "Indarrak": indarrak
        }
    # ---------------------------------------------------------
    # EBOLUZIOA
    # ---------------------------------------------------------
    def get_ebo_info(self, izena):
        sql = """
        SELECT izena, irudia 
        FROM espeziea 
        WHERE eboluzio_chain_id = (
            SELECT eboluzio_chain_id FROM espeziea WHERE LOWER(izena) = LOWER(?)
        )
        ORDER BY id ASC;
        """
        rows = self.db.select(sql, [izena])
        return [dict(row) for row in rows]
    # ---------------------------------------------------------
    # SCAN (Pokémon baten azterketa osoa)
    # ---------------------------------------------------------
    def get_scan_info(self, izena):
        row = self.db.select("SELECT * FROM espeziea WHERE LOWER(izena) = LOWER(?)", [izena])
        if not row: return None
        poke = dict(row[0])

        stats = {
            "Osasuna": poke['osasuna'], "Atakea": poke['atakea'], "Defentsa": poke['defentsa'],
            "AtakeBerezia": poke['atake_berezia'], "DefentsaBerezia": poke['defentsa_berezia'], "Abiadura": poke['abiadura']
        }
        media = round(sum(stats.values()) / 6, 1)

        return {
            "Izena": poke['izena'],
            "Irudia": poke['irudia'],
            "Media": media,
            "Stats": stats,
            "Efectividad": self.get_type_effectiveness(izena) # REUTILIZA LA API
        }