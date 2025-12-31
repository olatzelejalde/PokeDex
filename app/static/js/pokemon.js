// Pokémonak kudeatzeko funtzioak
async function kargatuPokemonDatuak() {
    try {
        const response = await fetch(`${API_BASE_URL}/pokemon`);
        pokemonGuztiak = await response.json();
        console.log("✅ Pokémon recibidos:", pokemonGuztiak.length, pokemonGuztiak[0]);
        erakutsiPokemon(pokemonGuztiak);
    } catch (error) {
        console.error('Errorea Pokémonak kargatzean:', error);
        erakutsiErrorea('Ezin izan dira Pokémon datuak kargatu');
    }
}

async function kargatuMotak() {
    try {
        const response = await fetch(`${API_BASE_URL}/pokemon/motak`);
        motaGuztiak = await response.json();
        const motaFiltroa = document.getElementById('type-filter');
        motaFiltroa.innerHTML = '<option value="">Mota guztiak</option>';
        motaGuztiak.forEach(mota => {
            const aukera = document.createElement('option');
            aukera.value = mota;
            aukera.textContent = mota;
            motaFiltroa.appendChild(aukera);
        });
    } catch (error) {
        console.error('Errorea motak kargatzean:', error);
    }
}

function erakutsiPokemon(pokemonZerrenda) {
    console.log("🎯 erakutsiPokemon llamado con", pokemonZerrenda.length, "pokemons");
    const grid = document.getElementById('pokemon-grid');
    console.log("📦 Grid encontrado:", grid);
    if (pokemonZerrenda.length === 0) {
        grid.innerHTML = `
            <div class="no-results" style="grid-column: 1 / -1; text-align: center; padding: 40px;">
                <h3>Ez da Pokémonik aurkitu</h3>
                <p>Saiatu beste bilaketa termino bat erabiltzen</p>
            </div>
        `;
        return;
    }
    grid.innerHTML = '';
    const ordenatutakoPokemon = pokemonZerrenda.sort((a, b) => a.id - b.id);
    ordenatutakoPokemon.forEach(pokemon => {
        const txartela = sortuPokemonTxartela(pokemon);
        grid.appendChild(txartela);
    });
}

function sortuPokemonTxartela(pokemon) {
    const txartela = document.createElement('div');
    txartela.className = `pokemon-card ${lortuMotaKlasea(pokemon.mota)}`;
    txartela.addEventListener('click', () => erakutsiPokemonXehetasunak(pokemon));
    txartela.innerHTML = `
        <div class="pokemon-id">#${String(pokemon.id).padStart(3, '0')}</div>
        <img src="/static/sprites/pokemon/${pokemon.id}.png" alt="${pokemon.izena}" class="pokemon-image"
             onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIwIiBoZWlnaHQ9IjEyMCIgdmlld0JveD0iMCAwIDEyMCAxMjAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHJlY3Qgd2lkdGg9IjEyMCIgaGVpZ2h0PSIxMjAiIGZpbGw9IiNGRjdGN0YiIHN0cm9rZT0iIzIyMjIyNCIgc3Ryb2tlLXdpZHRoPSIyIiByeD0iMTAiLz48dGV4dCB4PSI2MCIgeT0iNjUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzIyMjIyNCIgdGV4dC1hbmNob3I9Im1pZGRsZSI+5Y+W5pu4PC90ZXh0Pjwvc3ZnPg=='">
        <div class="pokemon-name">${pokemon.izena}</div>
        <div class="pokemon-types">
            <span class="type ${lortuMotaKlasea(pokemon.mota)}">${pokemon.mota}</span>
            ${pokemon.mota2 ? `<span class="type ${lortuMotaKlasea(pokemon.mota2)}">${pokemon.mota2}</span>` : ''}
        </div>
    `;
    return txartela;
}

function lortuMotaKlasea(mota) {
    const motaMapa = {
        'normala': 'normal', 'sua': 'fire', 'ura': 'water', 'belarra': 'grass',
        'elektrikoa': 'electric', 'izotza': 'ice', 'borroka': 'fighting', 'pozoia': 'poison',
        'lurra': 'ground', 'hegaldia': 'flying', 'psikikoa': 'psychic', 'intsektua': 'bug',
        'harria': 'rock', 'mamua': 'ghost', 'dragoia': 'dragon', 'iluna': 'dark',
        'altzairua': 'steel', 'maitagarria': 'fairy'
    };
    return motaMapa[mota.toLowerCase()] || 'normal';
}

function bilatuPokemon() {
    const bilaketaTerminoa = document.getElementById('pokemon-search').value.toLowerCase().trim();
    const hautatutakoMota = document.getElementById('type-filter').value;
    let iragazitakoPokemon = pokemonGuztiak;
    if (bilaketaTerminoa) {
        iragazitakoPokemon = iragazitakoPokemon.filter(pokemon =>
            pokemon.izena.toLowerCase().includes(bilaketaTerminoa) ||
            String(pokemon.id).includes(bilaketaTerminoa)
        );
    }
    if (hautatutakoMota) {
        iragazitakoPokemon = iragazitakoPokemon.filter(pokemon =>
            pokemon.mota === hautatutakoMota || pokemon.mota2 === hautatutakoMota
        );
    }
    erakutsiPokemon(iragazitakoPokemon);
}

function erakutsiPokemonXehetasunak(pokemon) {
    const modal = document.getElementById('pokemon-modal');
    const xehetasunak = document.getElementById('pokemon-xehetasunak');
    const motaKlasea1 = lortuMotaKlasea(pokemon.mota);
    const motaKlasea2 = pokemon.mota2 ? lortuMotaKlasea(pokemon.mota2) : null;
    xehetasunak.innerHTML = `
        <div class="pokemon-detail">
            <div class="pokemon-detail-header">
                <h2>${pokemon.izena}</h2>
                <span class="pokemon-detail-number">#${String(pokemon.id).padStart(3, '0')}</span>
            </div>
            <div class="pokemon-detail-image">
                <img src="/static/sprites/pokemon/${pokemon.id}.png" alt="${pokemon.izena}" onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDIwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHJlY3Qgd2lkdGg9IjIwMCIgaGVpZ2h0PSIyMDAiIGZpbGw9IiNGRjdGN0YiIHN0cm9rZT0iIzIyMjIyNCIgc3Ryb2tlLXdpZHRoPSIzIiByeD0iMTUiLz48dGV4dCB4PSIxMDAiIHk9IjExMCIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjI0IiBmaWxsPSIjMjIyMjI0IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj7lj5bmm7g8L3RleHQ+PC9zdmc+'">
            </div>
            <div class="pokemon-detail-types">
                <span class="type ${motaKlasea1}">${pokemon.mota}</span>
                ${pokemon.mota2 ? `<span class="type ${motaKlasea2}">${pokemon.mota2}</span>` : ''}
            </div>
            <div class="pokemon-detail-stats">
                <h3 style="text-align: center; color: var(--pokedex-red); margin-bottom: 20px;">ESTATISTIKAK</h3>
                <div class="stat-bar">
                    <label>HP:</label>
                    <div class="stat-bar-outer"><div class="stat-bar-inner" style="width: ${(pokemon.hp/200)*100}%"></div></div>
                    <span>${pokemon.hp}</span>
                </div>
                <div class="stat-bar">
                    <label>ATAKEA:</label>
                    <div class="stat-bar-outer"><div class="stat-bar-inner" style="width: ${(pokemon.atakea/200)*100}%"></div></div>
                    <span>${pokemon.atakea}</span>
                </div>
                <div class="stat-bar">
                    <label>DEFENTSA:</label>
                    <div class="stat-bar-outer"><div class="stat-bar-inner" style="width: ${(pokemon.defentsa/200)*100}%"></div></div>
                    <span>${pokemon.defentsa}</span>
                </div>
                <div class="stat-bar">
                    <label>ABIADURA:</label>
                    <div class="stat-bar-outer"><div class="stat-bar-inner" style="width: ${(pokemon.abiadura/200)*100}%"></div></div>
                    <span>${pokemon.abiadura}</span>
                </div>
            </div>
            <div class="pokemon-detail-actions">
                <button class="pokedex-button secondary" onclick="itxiModalak()">ITXI</button>
            </div>
        </div>
    `;
    modal.style.display = 'block';
}

function itxiModalak() {
    document.querySelectorAll('.modal').forEach(modal => modal.style.display = 'none');
}

// Bilaketa automatikoa
document.getElementById('pokemon-search').addEventListener('input', function (e) {
    clearTimeout(this.searchTimeout);
    this.searchTimeout = setTimeout(() => bilatuPokemon(), 500);
});
document.getElementById('type-filter').addEventListener('change', bilatuPokemon);