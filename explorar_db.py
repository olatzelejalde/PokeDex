# explorar_db.py
import sqlite3
import sys

def explorar_bd(nombre_db='library.sqlite'):
    try:
        conn = sqlite3.connect(nombre_db)
        cursor = conn.cursor()
        
        print(f"📊 Explorando: {nombre_db}")
        print("=" * 50)
        
        # 1. Ver tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tablas = cursor.fetchall()
        
        if not tablas:
            print("📭 No hay tablas")
            return
        
        print(f"📋 Tablas encontradas ({len(tablas)}):")
        for tabla in tablas:
            print(f"  • {tabla[0]}")
        
        print("\n" + "=" * 50)
        
        # 2. Explorar cada tabla
        for tabla_nombre, in tablas:
            print(f"\n📁 TABLA: {tabla_nombre}")
            print("-" * 30)
            
            # Ver estructura
            cursor.execute(f"PRAGMA table_info({tabla_nombre})")
            columnas = cursor.fetchall()
            print("Columnas:")
            for col in columnas:
                print(f"  {col[0]:2} | {col[1]:15} | {col[2]:10} | {'NOT NULL' if col[3] else 'NULLABLE'}")
            
            # Ver conteo
            cursor.execute(f"SELECT COUNT(*) FROM {tabla_nombre}")
            total = cursor.fetchone()[0]
            print(f"\nTotal registros: {total}")
            
            # Ver primeros 3 registros
            if total > 0:
                cursor.execute(f"SELECT * FROM {tabla_nombre} LIMIT 3")
                registros = cursor.fetchall()
                
                # Nombres de columnas
                nombres_columnas = [desc[0] for desc in cursor.description]
                print("\nPrimeros registros:")
                print(" | ".join(nombres_columnas))
                print("-" * 40)
                
                for registro in registros:
                    print(" | ".join(str(item) if item is not None else "NULL" for item in registro))
                
                if total > 3:
                    print(f"... y {total - 3} registros más")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Error: {e}")
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo: {nombre_db}")

if __name__ == "__main__":
    # Puedes pasar el nombre de la BD como argumento
    db_name = sys.argv[1] if len(sys.argv) > 1 else 'library.sqlite'
    explorar_bd(db_name)