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

    conn.commit()
    conn.close()
    print("✨ Hasieratze prozesua amaitu da.")

if __name__ == "__main__":
    init_db()