// Pokémonak kudeatzeko funtzioak
async function kargatuPokemonDatuak() {
    try {
        const response = await fetch(`${API_BASE_URL}/pokemon`);
        pokemonGuztiak = await response.json();
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
    const grid = document.getElementById('pokemon-grid');
    
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
    
    // Ordenatu Pokémon zenbakiaren arabera
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
        <img src="${pokemon.irudia}" alt="${pokemon.izena}" class="pokemon-image"
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
        'normala': 'normal',
        'sua': 'fire',
        'ura': 'water',
        'belarra': 'grass',
        'elektrikoa': 'electric',
        'izotza': 'ice',
        'borroka': 'fighting',
        'pozoia': 'poison',
        'lurra': 'ground',
        'hegaldia': 'flying',
        'psikikoa': 'psychic',
        'intsektua': 'bug',
        'harria': 'rock',
        'mamua': 'ghost',
        'dragoia': 'dragon',
        'iluna': 'dark',
        'altzairua': 'steel',
        'maitagarria': 'fairy'
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
                <img src="${pokemon.irudia}" alt="${pokemon.izena}"
                     onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDIwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHJlY3Qgd2lkdGg9IjIwMCIgaGVpZ2h0PSIyMDAiIGZpbGw9IiNGRjdGN0YiIHN0cm9rZT0iIzIyMjIyNCIgc3Ryb2tlLXdpZHRoPSIzIiByeD0iMTUiLz48dGV4dCB4PSIxMDAiIHk9IjExMCIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjI0IiBmaWxsPSIjMjIyMjI0IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj7lj5bmm7g8L3RleHQ+PC9zdmc+'">
            </div>
            
            <div class="pokemon-detail-types">
                <span class="type ${motaKlasea1}">${pokemon.mota}</span>
                ${pokemon.mota2 ? `<span class="type ${motaKlasea2}">${pokemon.mota2}</span>` : ''}
            </div>
            
            <div class="pokemon-detail-stats">
                <h3 style="text-align: center; color: var(--pokedex-red); margin-bottom: 20px;">ESTATISTIKAK</h3>
                <div class="stat-bar">
                    <label>HP:</label>
                    <div class="stat-bar-outer">
                        <div class="stat-bar-inner" style="width: ${(pokemon.hp / 255) * 100}%"></div>
                    </div>
                    <span style="margin-left: 10px; font-weight: bold;">${pokemon.hp}</span>
                </div>
                <div class="stat-bar">
                    <label>ATAKEA:</label>
                    <div class="stat-bar-outer">
                        <div class="stat-bar-inner" style="width: ${(pokemon.atakea / 255) * 100}%"></div>
                    </div>
                    <span style="margin-left: 10px; font-weight: bold;">${pokemon.atakea}</span>
                </div>
                <div class="stat-bar">
                    <label>DEFENTSA:</label>
                    <div class="stat-bar-outer">
                        <div class="stat-bar-inner" style="width: ${(pokemon.defentsa / 255) * 100}%"></div>
                    </div>
                    <span style="margin-left: 10px; font-weight: bold;">${pokemon.defentsa}</span>
                </div>
                <div class="stat-bar">
                    <label>ABIADURA:</label>
                    <div class="stat-bar-outer">
                        <div class="stat-bar-inner" style="width: ${(pokemon.abiadura / 255) * 100}%"></div>
                    </div>
                    <span style="margin-left: 10px; font-weight: bold;">${pokemon.abiadura}</span>
                </div>
            </div>
            
            <div class="pokemon-detail-actions">
                ${unekoErabiltzailea ? `
                    <button class="pokedex-button" onclick="gehituTaldeari(${pokemon.id})">
                        GEHITU TALDERA
                    </button>
                ` : ''}
                <button class="pokedex-button secondary" onclick="itxiModalak()">
                    ITXI
                </button>
            </div>
        </div>
    `;

    modal.style.display = 'block';
}

async function gehituTaldeari(pokemonId) {
    if (!unekoErabiltzailea) {
        alert('Saioa hasi behar duzu Pokémon bat taldera gehitzeko');
        return;
    }

    const taldeaId = sessionStorage.getItem('hautatutakoTaldeaId');
    
    if (taldeaId) {
        // Badago talde hautatua, gehitu Pokémon-a
        await gehituPokemonHautatuaTaldeari(pokemonId);
        return;
    }

    // Bestela, kargatu taldeak eta erakutsi hautaketa
    try {
        const response = await fetch(`${API_BASE_URL}/taldeak/erabiltzailea/${unekoErabiltzailea.id}`);
        const taldeak = await response.json();
        
        if (taldeak.length === 0) {
            if (confirm('Ez duzu talderik. Talde berri bat sortu nahi duzu?')) {
                erakutsiTaldeaModala();
                // Gorde Pokémon ID-a sessionStorage-n
                sessionStorage.setItem('pendentekoPokemonId', pokemonId);
            }
            return;
        }

        erakutsiTaldeHautaketa(taldeak, pokemonId);
        
    } catch (error) {
        console.error('Errorea taldeak kargatzean:', error);
        alert('Errorea taldeak kargatzean');
    }
}

function erakutsiTaldeHautaketa(taldeak, pokemonId) {
    const modal = document.getElementById('pokemon-modal');
    const xehetasunak = document.getElementById('pokemon-xehetasunak');
    
    let taldeAukerak = '';
    taldeak.forEach(taldea => {
        const libre = taldea.pokemonak.length < 6;
        taldeAukerak += `
            <div class="talde-aukeraketa ${!libre ? 'betea' : ''}" onclick="${libre ? `hautatuTaldea(${taldea.id}, ${pokemonId})` : ''}">
                <strong>${taldea.izena}</strong>
                <span>${taldea.pokemonak.length}/6 Pokémon</span>
                ${!libre ? '<span class="betea-label">BETEA</span>' : ''}
            </div>
        `;
    });

    xehetasunak.innerHTML = `
        <div class="pokemon-detail">
            <div class="pokemon-detail-header">
                <h2>TALDEA HAUTATU</h2>
            </div>
            
            <p style="text-align: center; margin-bottom: 20px;">Aukeratu zein taldetara gehitu nahi duzun Pokémon-a:</p>
            
            <div class="talde-aukeraketa-grid">
                ${taldeAukerak}
            </div>
            
            <div class="pokemon-detail-actions">
                <button class="pokedex-button secondary" onclick="erakutsiTaldeaModala()">
                    TALDE BERRIA
                </button>
                <button class="pokedex-button secondary" onclick="itxiModalak()">
                    UTZI
                </button>
            </div>
        </div>
    `;

    // Añadir estilos para la selección de equipos
    const style = document.createElement('style');
    style.textContent = `
        .talde-aukeraketa-grid {
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin: 20px 0;
        }
        .talde-aukeraketa {
            background-color: var(--pokedex-white);
            border: 3px solid var(--pokedex-black);
            border-radius: 10px;
            padding: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .talde-aukeraketa:hover {
            background-color: var(--pokedex-yellow);
            transform: translateY(-2px);
        }
        .talde-aukeraketa.betea {
            background-color: #f0f0f0;
            cursor: not-allowed;
            opacity: 0.6;
        }
        .betea-label {
            background-color: var(--pokedex-red);
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.8em;
        }
    `;
    document.head.appendChild(style);
}

async function hautatuTaldea(taldeaId, pokemonId) {
    try {
        const response = await fetch(`${API_BASE_URL}/taldeak/${taldeaId}/pokemon`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                pokemon_id: pokemonId
            })
        });

        if (response.ok) {
            const taldeEguneratua = await response.json();
            itxiModalak();
            alert(`✅ ${taldeEguneratua.pokemonak[taldeEguneratua.pokemonak.length - 1].izena} taldera gehitu da!`);
            
            // Insignak egiaztatu
            if (taldeEguneratua.intsigna) {
                alert(`🎉 Zorionak! "${taldeEguneratua.intsigna}" intsigna irabazi duzu!`);
            }
        } else {
            const error = await response.json();
            alert(error.error || 'Errorea Pokémona taldera gehitzean');
        }
    } catch (error) {
        console.error('Errorea Pokémona taldera gehitzean:', error);
        alert('Errorea Pokémona taldera gehitzean');
    }
}

function erakutsiErrorea(mezua) {
    // Erakutsi errore mezu bat estilo Pokédex-ekin
    const grid = document.getElementById('pokemon-grid');
    grid.innerHTML = `
        <div class="error-message" style="grid-column: 1 / -1; text-align: center; padding: 40px;">
            <div style="background-color: var(--pokedex-red); color: white; padding: 20px; border-radius: 15px; border: 3px solid var(--pokedex-black);">
                <h3 style="margin: 0; font-family: 'Press Start 2P', cursive;">ERROREA</h3>
                <p style="margin: 10px 0 0 0;">${mezua}</p>
            </div>
            <button class="pokedex-button" onclick="kargatuPokemonDatuak()" style="margin-top: 20px;">
                SAIATU BERRIZ
            </button>
        </div>
    `;
}

// Funtzio laguntzaileak
function itxiModalak() {
    document.querySelectorAll('.modal').forEach(modal => {
        modal.style.display = 'none';
    });
}

function erakutsiTaldeaModala() {
    itxiModalak();
    document.getElementById('taldea-modal').style.display = 'block';
}

// Bilaketa automatikoa bilaketa barrari
document.getElementById('pokemon-search').addEventListener('input', function(e) {
    // Bilaketa automatikoa 500ms-ko atzerapenarekin
    clearTimeout(this.searchTimeout);
    this.searchTimeout = setTimeout(() => {
        bilatuPokemon();
    }, 500);
});

// Motaren filtroa aldatzeko
document.getElementById('type-filter').addEventListener('change', bilatuPokemon);