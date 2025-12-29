class PokemonController:
    def __init__(self, db):
        self.db = db

    def create_pokemon(self, pokemon_data):
        if not pokemon_data.get('izena') or not pokemon_data.get('id'):
            raise ValueError("Datuak falta dira: 'izena' eta 'id' beharrezkoak dira.")
        
        self.db.insert (
            sentence="INSERT INTO pokemon (id, izena, irudia, espezieIzena) VALUES (?, ?, ?, ?)",
            params=(pokemon_data['id'], pokemon_data['izena'], pokemon_data.get('irudia'), pokemon_data.get('espezieIzena'))
        )
    
    def get_all(self):
        rows = self.db.select(
            sentence="SELECT * FROM pokemon ORDER BY id ASC"
        )
        return [dict(row) for row in rows]
    
    def get_by_id(self, pokemon_id):
        rows = self.db.select(
            sentence="SELECT * FROM pokemon WHERE id = ?",
            params=[pokemon_id]
        )
        return dict(rows[0]) if rows else None
    
    