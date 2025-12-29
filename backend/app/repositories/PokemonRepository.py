from app.database.connection import db
from app.models.Pokemon import Pokemon, Espeziea, Mota

class PokemonRepository:

    @staticmethod
    def get_by_id(pokemon_id: int) -> Optional[Pokemon]:
        query = """
        SELECT p.id, p.izena, p.irudia, p.espezieIzena,
        FROM pokemon p
        WHERE p.id = ?
        """
        result = db.execute(query, (pokemon_id,), fetch_one=True)
        if not result:
            return None
        return Pokemon(
            id=result['id'],
            izena=result['izena'],
            irudia=result['irudia'],
            espezieIzena=result['espezieIzena']
        )
    
    @staticmethod
    def get_all(limit: int = 50, offset: int = 0) -> List[Pokemon]:
        query = """
        SELECT p.id, p.izena, p.irudia, p.espezieIzena
        FROM pokemon p
        LIMIT ? OFFSET ?
        """
        results = db.execute_query(query, (limit, offset))

        return [Pokemon(
            id=row['id'],
            izena=row['izena'],
            irudia=row['irudia'],
            espezieIzena=row['espezieIzena']
        ) for row in results]
    
@staticmethod
def search_by_name(name: str) -> List[Pokemon]:
    query = """
    SELECT p.id, p.izena, p.irudia, p.espezieIzena
    FROM pokemon p
    WHERE p.izena LIKE ?
    """
    results = db.execute_query(query, (f"%{name}%",))

    return [Pokemon(
        id=row['id'],
        izena=row['izena'],
        irudia=row['irudia'],
        espezieIzena=row['espezieIzena']
    ) for row in results]

@staticmethod
def get_types() -> List[Mota]:
    query = """
    SELECT izena, efektibitatea
    FROM mota
    ORDER BY izena ASC
    """
    results = db.execute_query(query)

    return [Mota(
        izena=row['izena'],
        efektibitatea=row['efektibitatea']
    ) for row in results]