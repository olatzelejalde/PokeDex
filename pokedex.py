import pokebase as pb
from flask import Flask, jsonify, render_template, send_from_directory

app = Flask(__name__)

def pokemonDataKargatu(limitea=20):
   pokemonZerrenda = []

   pokemonRangoa = pb.APIResourceList('pokemon')

   for i, entry in enumerate(pokemonRangoa):
      if i >= limitea:
         break
      info = pb.pokemon(entry['name'])
      irudia = pb.SpriteResource('pokemon', info.id, other=True, official_artwork=True)
      listaMota = [t.type.name for t in info.types]
      pokemonZerrenda.append({
            'id': info.id,
            'name': info.name,
            'sprite_url': irudia.url,
            'types': listaMota
      })
   return pokemonZerrenda

@app.route('/')
def index():
   return render_template('home.html')


@app.route('/api/pokemon')
def pokemonApi():
   return jsonify(pokemonDataKargatu())
if __name__ == '__main__':
   app.run(debug=True)
