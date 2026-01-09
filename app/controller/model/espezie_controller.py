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
        print(f"DEBUG: {pokemon_name}-(r)en motak kalkulatzen")

        # 1. Pokémon-aren motak lortu
        row = self.db.select("SELECT * FROM espeziea WHERE izena = ?", [pokemon_name])
        if not row:
            return None

        poke = dict(row[0])
        mis_tipos = []
        if poke.get('mota1'): mis_tipos.append(poke['mota1'])
        if poke.get('mota2'): mis_tipos.append(poke['mota2'])

        # 2. Datu-baseko mota posible guztien zerrenda lortu
        rows_motak = self.db.select("SELECT izena FROM mota")
        todos_los_tipos = [r['izena'] for r in rows_motak]

        ahuleziak = []
        indarrak = []

        # Mapaketa bisualak (Euskarazko izenak)
        DISPLAY_NAMES = {
            'normala': 'Normala', 'sua': 'Sua', 'ura': 'Ura', 'belarra': 'Belarra',
            'elektrikoa': 'Elektrikoa', 'izotza': 'Izotza', 'borroka': 'Borroka', 'pozoia': 'Pozoia',
            'lurra': 'Lurra', 'hegaldia': 'Hegaldia', 'psikikoa': 'Psikikoa', 'intsektua': 'Intsektua',
            'harria': 'Harria', 'mamua': 'Mamua', 'dragoia': 'Dragoia', 'iluna': 'Iluna',
            'altzairua': 'Altzairua', 'maitagarria': 'Maitagarria'
        }

        # Moten gakoak (CSS edo irudietarako erabili ohi direnak)
        TYPE_KEY_MAP = {
            'normala': 'normal', 'sua': 'fire', 'ura': 'water', 'belarra': 'grass',
            'elektrikoa': 'electric', 'izotza': 'ice', 'borroka': 'fighting', 'pozoia': 'poison',
            'lurra': 'ground', 'hegaldia': 'flying', 'psikikoa': 'psychic', 'intsektua': 'bug',
            'harria': 'rock', 'mamua': 'ghost', 'dragoia': 'dragon', 'iluna': 'dark',
            'altzairua': 'steel', 'maitagarria': 'fairy'
        }

        # 3. KALKULUA (Mota bakoitzaren eragina defentsan)
        for atacante in todos_los_tipos:
            mult = 1.0
            for defensor in mis_tipos:
                res = self.db.select("""
                    SELECT biderkatzailea FROM eragina 
                    WHERE mota_eraso = ? AND mota_defentsa = ?
                """, [atacante, defensor])

                if res:
                    mult *= res[0]['biderkatzailea']

            # Emaitza 1.0 ez bada, zerrendara gehitu
            if mult != 1.0:
                type_key = TYPE_KEY_MAP.get(atacante, 'normal')
                info = {
                    "Mota": DISPLAY_NAMES.get(atacante, atacante.title()),
                    "Biderkatzailea": mult,
                    "TypeKey": type_key
                }
                if mult > 1: ahuleziak.append(info)   # Kalte gehiago jaso (Ahulezia)
                elif mult < 1: indarrak.append(info)  # Kalte gutxiago jaso (Indarra)

        # 4. Ordenatu eta itzuli
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
        # SQL Errekurtsiboa familia osoa (aurrekoak eta ondorengoak) lortzeko
        sql = """
        WITH RECURSIVE familia AS (
            -- Kateko lehenengo pokémon-a aurkitzen dugu (arbasoa)
            SELECT id, izena, irudia, aurreeboluzioa, 0 AS nivel
            FROM espeziea 
            WHERE id = (
                WITH RECURSIVE ancestros AS (
                    SELECT id, aurreeboluzioa FROM espeziea WHERE LOWER(izena) = LOWER(?)
                    UNION ALL
                    SELECT e.id, e.aurreeboluzioa FROM espeziea e 
                    JOIN ancestros a ON e.id = a.aurreeboluzioa
                )
                SELECT id FROM ancestros WHERE aurreeboluzioa IS NULL
            )
            UNION ALL
            -- Eboluzioetan behera joaten gara
            SELECT e.id, e.izena, e.irudia, e.aurreeboluzioa, f.nivel + 1
            FROM espeziea e
            JOIN familia f ON e.aurreeboluzioa = f.id
        )
        SELECT izena, irudia FROM familia ORDER BY nivel ASC;
        """
        rows = self.db.select(sql, [izena])
        return [dict(row) for row in rows]

    # ---------------------------------------------------------
    # SCAN (Pokémon baten azterketa osoa)
    # ---------------------------------------------------------
    def get_scan_info(self, izena):
        # 1. Espeziearen oinarrizko datuak lortu
        rows = self.db.select("SELECT * FROM espeziea WHERE izena = ?", [izena])
        if not rows:
            return None

        data = dict(rows[0])

        # 2. Estatistiken batez bestekoa kalkulatu (PokeTop logika)
        stats_list = [
            data.get('osasuna', 0),
            data.get('atakea', 0),
            data.get('defentsa', 0),
            data.get('atake_berezia', 0),
            data.get('defentsa_berezia', 0),
            data.get('abiadura', 0)
        ]
        media = sum(stats_list) / 6.0

        # 3. Moten eraginkortasuna kalkulatu (PokeMota logika)
        mis_tipos = []
        if data.get('mota1'): mis_tipos.append(data['mota1'])
        if data.get('mota2'): mis_tipos.append(data['mota2'])

        rows_motak = self.db.select("SELECT izena FROM mota")
        todos_los_tipos = [r['izena'] for r in rows_motak]

        ahuleziak = []
        indarrak = []

        # Izenen mapaketa koherentzia mantentzeko
        DISPLAY_NAMES = {
            'normala': 'Normala', 'sua': 'Sua', 'ura': 'Ura', 'belarra': 'Belarra',
            'elektrikoa': 'Elektrikoa', 'izotza': 'Izotza', 'borroka': 'Borroka', 'pozoia': 'Pozoia',
            'lurra': 'Lurra', 'hegaldia': 'Hegaldia', 'psikikoa': 'Psikikoa', 'intsektua': 'Intsektua',
            'harria': 'Harria', 'mamua': 'Mamua', 'dragoia': 'Dragoia', 'iluna': 'Iluna',
            'altzairua': 'Altzairua', 'maitagarria': 'Maitagarria'
        }

        for atacante in todos_los_tipos:
            mult = 1.0
            for defensor in mis_tipos:
                res = self.db.select("""
                    SELECT biderkatzailea FROM eragina 
                    WHERE mota_eraso = ? AND mota_defentsa = ?
                """, [atacante, defensor])
                if res:
                    mult *= res[0]['biderkatzailea']

            if mult != 1.0:
                info = {
                    "Mota": DISPLAY_NAMES.get(atacante, atacante.title()),
                    "Biderkatzailea": mult
                }
                if mult > 1: ahuleziak.append(info)
                elif mult < 1: indarrak.append(info)

        # Emaitzak ordenatu
        ahuleziak.sort(key=lambda x: x['Biderkatzailea'], reverse=True)
        indarrak.sort(key=lambda x: x['Biderkatzailea'])

        # 4. Objektu konbinatua itzuli
        return {
            "Izena": data['izena'],
            "Irudia": data['irudia'],
            "Media": round(media, 2),
            "Stats": {
                "Osasuna": data.get('osasuna', 0),
                "Atakea": data.get('atakea', 0),
                "Defentsa": data.get('defentsa', 0),
                "AtakeBerezia": data.get('atake_berezia', 0),
                "DefentsaBerezia": data.get('defentsa_berezia', 0),
                "Abiadura": data.get('abiadura', 0)
            },
            "Tipos": mis_tipos,
            "Efectividad": {
                "Ahuleziak": ahuleziak, # Ahuleziak (x2, x4)
                "Indarrak": indarrak     # Erresistentziak (x0.5, x0.25, x0)
            }
        }