import sqlite3
from config import Config

def init_db():
    db_path = Config.DB_PATH
    print(f"🔄 Datu-base berria sortzen helbide honetan: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Jatorrizko eskema irakurri eta exekutatu
    try:
        with open('app/database/schema.sql', 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        cursor.executescript(schema_sql)
        print("✅ Taulak zuzen sortu dira.")
    except Exception as e:
        print(f"❌ Errorea taulak sortzean: {e}")

    # 2. EBOLUZIOEN EGUNERAKETAK EXEKUTATU
    print("🚀 Eboluzio-lerroak lotzen...")
    try:
        # Zutabea existitzen dela ziurtatu (schema.sql-ek ez balu)
        try:
            cursor.execute("ALTER TABLE espeziea ADD COLUMN aurreeboluzioa INTEGER;")
        except sqlite3.OperationalError:
            pass # Existitzen denez, aurrera

        # --- CHARMANDER FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 4 WHERE id = 5") # Charmeleon
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 5 WHERE id = 6") # Charizard

        # --- BULBASAUR FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 1 WHERE id = 2") # Ivysaur
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 2 WHERE id = 3") # Venusaur

        # --- SQUIRTLE FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 7 WHERE id = 8") # Wartortle
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 8 WHERE id = 9") # Blastoise

        # --- CATERPIE FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 10 WHERE id = 11") # Metapod
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 11 WHERE id = 12") # Butterfree

        # --- WEEDLE FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 13 WHERE id = 14") # Kakuna
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 14 WHERE id = 15") # Beedrill

        # --- PIDGEY FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 16 WHERE id = 17") # Pidgeotto
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 17 WHERE id = 18") # Pidgeot

        # --- GASTLY FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 92 WHERE id = 93") # Haunter
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 93 WHERE id = 94") # Gengar

        # --- DRATINI FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 147 WHERE id = 148") # Dragonair
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 148 WHERE id = 149") # Dragonite

        # --- RATTATA FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 19 WHERE id = 20") # Raticate

        # --- SPEAROW FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 21 WHERE id = 22") # Fearow

        # --- EKANS FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 23 WHERE id = 24") # Arbok

        # --- PIKACHU FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 25 WHERE id = 26") # Raichu

        # --- SANDSHREW FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 27 WHERE id = 28") # Sandslash

        # --- NIDORAN ♀ FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 29 WHERE id = 30") # Nidorina
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 30 WHERE id = 31") # Nidoqueen

        # --- NIDORAN ♂ FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 32 WHERE id = 33") # Nidorino
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 33 WHERE id = 34") # Nidoking

        # --- CLEFAIRY FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 35 WHERE id = 36") # Clefable

        # --- VULPIX FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 37 WHERE id = 38") # Ninetales

        # --- JIGGLYPUFF FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 39 WHERE id = 40") # Wigglytuff

        # --- ZUBAT FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 41 WHERE id = 42") # Golbat

        # --- ODDISH FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 43 WHERE id = 44") # Gloom
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 44 WHERE id = 45") # Vileplume

        # --- PARAS FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 46 WHERE id = 47") # Parasect

        # --- VENONAT FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 48 WHERE id = 49") # Venomoth

        # --- DIGLETT FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 50 WHERE id = 51") # Dugtrio

        # --- MEOWTH FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 52 WHERE id = 53") # Persian

        # --- PSYDUCK FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 54 WHERE id = 55") # Golduck

        # --- MANKEY FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 56 WHERE id = 57") # Primeape

        # --- GROWLITHE FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 58 WHERE id = 59") # Arcanine

        # --- POLIWAG FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 60 WHERE id = 61") # Poliwhirl
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 61 WHERE id = 62") # Poliwrath

        # --- ABRA FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 63 WHERE id = 64") # Kadabra
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 64 WHERE id = 65") # Alakazam

        # --- MACHOP FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 66 WHERE id = 67") # Machoke
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 67 WHERE id = 68") # Machamp

        # --- BELLSPROUT FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 69 WHERE id = 70") # Weepinbell
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 70 WHERE id = 71") # Victreebel

        # --- TENTACOOL FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 72 WHERE id = 73") # Tentacruel

        # --- GEODUDE FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 74 WHERE id = 75") # Graveler
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 75 WHERE id = 76") # Golem

        # --- PONYTA FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 77 WHERE id = 78") # Rapidash

        # --- SLOWPOKE FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 79 WHERE id = 80") # Slowbro

        # --- MAGNEMITE FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 81 WHERE id = 82") # Magneton

        # --- DODUO FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 84 WHERE id = 85") # Dodrio

        # --- SEEL FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 86 WHERE id = 87") # Dewgong

        # --- GRIMER FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 88 WHERE id = 89") # Muk

        # --- SHELLDER FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 90 WHERE id = 91") # Cloyster

        # --- DROWZEE FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 96 WHERE id = 97") # Hypno

        # --- KRABBY FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 98 WHERE id = 99") # Kingler

        # --- VOLTORB FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 100 WHERE id = 101") # Electrode

        # --- EXEGGCUTE FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 102 WHERE id = 103") # Exeggutor

        # --- CUBONE FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 104 WHERE id = 105") # Marowak

        # --- KOFFING FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 109 WHERE id = 110") # Weezing

        # --- RHYHORN FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 111 WHERE id = 112") # Rhydon

        # --- HORSEA FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 116 WHERE id = 117") # Seadra

        # --- GOLDEEN FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 118 WHERE id = 119") # Seaking

        # --- STARYU FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 120 WHERE id = 121") # Starmie

        # --- MAGIKARP FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 129 WHERE id = 130") # Gyarados

        # --- OMANYTE FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 138 WHERE id = 139") # Omastar

        # --- KABUTO FAMILIA ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 140 WHERE id = 141") # Kabutops

        # --- EEVEE-REN ADARKATZEA (Kasu berezia) ---
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 133 WHERE id = 134") # Vaporeon
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 133 WHERE id = 135") # Jolteon
        cursor.execute("UPDATE espeziea SET aurreeboluzioa = 133 WHERE id = 136") # Flareon

        print("✅ Eboluzioak zuzen lotu dira.")
    except Exception as e:
        print(f"⚠️ Oharra: Errorea eboluzioak eguneratzean: {e}")

    conn.commit()
    conn.close()
    print("✨ Hasieratze prozesua amaitu da.")

if __name__ == "__main__":
    init_db()