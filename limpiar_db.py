import sqlite3
import os
from config import Config

def init_db():
    db_path = Config.DB_PATH # C:\...\library.sqlite

    # 1. BORRADO FÍSICO DEL ARCHIVO (Para evitar errores de UNIQUE o columnas viejas)
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"🗑️ Fitxategia ezabatu da: {db_path}")
        except PermissionError:
            print(f"❌ ERROREA: Itxi Flask edo DB Browser fitxategia ezabatu ahal izateko.")
            return

    print(f"🔄 Datu-base berria sortzen: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 2. ESKEMA BERRIRO IRAKURRI (Ziurtatu schema.sql-en koma jarri duzula!)
    try:
        with open('app/database/schema.sql', 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        cursor.executescript(schema_sql)
        print("✅ Taulak zuzen sortu dira eskema berriarekin.")
    except Exception as e:
        print(f"❌ Errorea eskeman: {e}")

    conn.commit()
    conn.close()
    print("✨ Hasieratze prozesua amaitu da.")

if __name__ == "__main__":
    init_db()