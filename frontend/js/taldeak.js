//--------------------------------------------------
// 1. Erabiltzailearen taldeak kargatzeko funtzioa
//--------------------------------------------------
async function kargatuErabiltzaileTaldeak() {
    if (!unekoErabiltzailea) {
        document.getElementById('taldeak-zerrenda').innerHTML = `
            <div class="error-message" style="text-align: center; padding: 40px;">
                <p>Saioa hasi behar duzu zure taldeak ikusteko</p>
                <button class="pokedex-button" onclick="erakutsiSaioaModala()">SAIOA HASI</button>
            </div>
        `;
        return;
    }

    try {
        console.log('Taldeak kargatzen erabiltzailea:', unekoErabiltzailea.id);
        const response = await fetch(`${API_BASE_URL}/taldeak/erabiltzailea/${unekoErabiltzailea.id}`);
        
        if (!response.ok) {
            throw new Error(`HTTP errorea: ${response.status}`);
        }
        
        const taldeak = await response.json();
        console.log('Taldeak jaso dira:', taldeak);
        erakutsiTaldeak(taldeak);
    } catch (error) {
        console.error('Errorea taldeak kargatzean:', error);
        erakutsiTaldeakErrorea('Errorea taldeak kargatzean: ' + error.message);
    }
}

// 1.1. Taldeak erakusteko funtzioa
function erakutsiTaldeak(taldeak) {
    const taldeakZerrenda = document.getElementById('taldeak-zerrenda');
    
    if (!taldeakZerrenda) {
        console.error('Ez da aurkitu taldeak-zerrenda elementua');
        return;
    }
    
    if (taldeak.length === 0) {
        taldeakZerrenda.innerHTML = `
            <div class="no-taldeak" style="text-align: center; padding: 40px;">
                <h3>Ez duzu talderik</h3>
                <p>Sortu lehen talde bat hasi ahal izateko!</p>
                <button class="pokedex-button" onclick="erakutsiTaldeaModala()">TALDE BERRIA SORTU</button>
            </div>
        `;
        return;
    }
    
    taldeakZerrenda.innerHTML = '';

    taldeak.forEach(taldea => {
        document.getElementById('taldeak-zerrenda').appendChild((
            sortuTxartelaHutsuneekin(taldea)
        ));
    });
}

// 1.2. Txartelen informazioa erakusteko funtzioa
function sortuTaldeTxartela(taldea) {
    const txartela = document.createElement('div');
    txartela.className = 'taldea-card';
    txartela.innerHTML = `
        <div class="taldea-header">
            <h3>${taldea.izena}</h3>
            <span>${taldea.pokemonKopurua || taldea.pokemonak.length}/6 Pokémon</span>
        </div>
        
        <div class="taldea-pokemonak">
            ${(taldea.pokemonak || []).map(pokemon => `
                <div class="pokemon-mini">
                    <img src="${pokemon.irudia}" alt="${pokemon.izena}" >
                    <div style="font-size: 0.8em; margin-top: 5px;">${pokemon.izena}</div>
                </div>
            `).join('')}
            
        </div>
        
        <div class="taldea-actions">
            <button data-team-id="${taldea.id}" class="pokedex-button" onclick="taldeaEditatu(${taldea.id})">
                TALDEA EDITATU
            </button>
            <button class="pokedex-button secondary" onclick="partekatuTaldea(${taldea.id})">
                PARTEKATU
            </button>
            <button class="pokedex-button" style="background-color: var(--pokedex-red); color: white;" 
                    onclick="ezabatuTaldea(${taldea.id})">
                EZABATU
            </button>
        </div>
    `;

    return txartela;
}

// 1.3. Taldea 6 pokemon baino gutxiago baditu, hutsuneak jarri
function hutsuneakBete(taldeaCard, taldea) {
    const actuales = (taldea.pokemonak || []).length;
    const faltan   = 6 - actuales;
    if (faltan <= 0) return;                       // equipo lleno
    const contenedor = taldeaCard.querySelector('.taldea-pokemonak');

    for (let i = 0; i < faltan; i++) {
        const slot = document.createElement('div');
        slot.className = 'pokemon-mini add-slot';
        slot.onclick   = () => gehituPokemonTaldeari(taldea.id);
        slot.innerHTML = `
            <img src="../static/pokeball.webp" alt="Gehitu" style="opacity:.45">
            <div style="font-size:0.7em;margin-top:5px">+ Gehitu</div>`;
        contenedor.appendChild(slot);
    }
}

// 1.4. Talde txartel osoa sortzeko funtzioa
function sortuTxartelaHutsuneekin(taldea) {
    const txartela = sortuTaldeTxartela(taldea);
    hutsuneakBete(txartela, taldea);
    return txartela;
}

//--------------------------------------------------
// 2. Taldea editatzeko funtzioak
//--------------------------------------------------
let editingTaldeaId = null;
function taldeaEditatu(taldeaId) {
    editingTaldeaId = taldeaId;

    // Botón DENTRO de la tarjeta que se está editando
    const botoia = document.querySelector(`.btn-editatu[data-team-id="${taldeaId}"]`);
    if (!botoia) return;

    botoia.textContent = 'Gorde aldaketak';
    botoia.onclick = () => gordeTaldeAldaketak(taldeaId);

    // Resto de tu lógica (iconos de borrar, etc.)
    document.querySelectorAll('.delete-icon').forEach(icon => icon.remove());

    const container = document.querySelector(`.taldea-pokemonak[data-team-id="${taldeaId}"]`);
    container.querySelectorAll('.pokemon-mini').forEach(card => {
        const icon = document.createElement('span');
        icon.className = 'delete-icon';
        icon.innerHTML = '🗑️';
        icon.style.cssText = `
            position:absolute;top:2px;right:2px;cursor:pointer;
            font-size:16px;background:rgba(255,255,255,.85);border-radius:50%;
            width:22px;height:22px;display:flex;align-items:center;justify-content:center;`;
        icon.onclick = () => borrarPokemonDeTaldea(taldeaId, card.dataset.pokemonId);
        card.style.position = 'relative';
        card.appendChild(icon);
    });
}

// 2.1. Talde aldaketak gordetzeko funtzioa
async function borrarPokemonDeTaldea(teamId, pokemonId) {
    if (!confirm('Seguru zaude Pokémon hau ezabatu nahi duzula?')) return;

    const res = await fetch(`${API_BASE_URL}/taldeak/${teamId}/pokemon/${pokemonId}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' }
    });

    if (!res.ok) return alert('Errorea ezabatzerakoan');

    /* Actualizar vista: quitar nodo del DOM */
    const card = document.querySelector(
        `.taldea-pokemonak[data-team-id="${teamId}"] .pokemon-mini[data-pokemon-id="${pokemonId}"]`
    );
    if (card) card.remove();

    /* Actualizar contador */
    const contador = document.querySelector(
        `.taldea-card:has(.taldea-pokemonak[data-team-id="${teamId}"]) .taldea-header span`
    );
    const nuevo = parseInt(contador.textContent) - 1;
    contador.textContent = `${nuevo}/6 Pokémon`;
}

function erakutsiTaldeaModala() {
    if (!unekoErabiltzailea) {
        alert('Saioa hasi behar duzu talde bat sortzeko');
        erakutsiSaioaModala();
        return;
    }
    
    document.getElementById('taldea-izena').value = '';
    document.getElementById('taldea-modal').style.display = 'block';
}

// Konfiguratu botoia HTML kargatzean
document.addEventListener('DOMContentLoaded', function() {
    const taldeaGordeBtn = document.getElementById('btn-taldea-gorde');
    if (taldeaGordeBtn) {
        taldeaGordeBtn.addEventListener('click', sortuTaldea);
    }
    
    const taldeBerriaBtn = document.getElementById('btn-talde-berria');
    if (taldeBerriaBtn) {
        taldeBerriaBtn.addEventListener('click', erakutsiTaldeaModala);
    }
});

async function sortuTaldea() {
    const izena = document.getElementById('taldea-izena').value.trim();

    if (!izena) {
        alert('Mesedez, idatzi taldearen izena');
        return;
    }

    if (!unekoErabiltzailea) {
        alert('Saioa hasi behar duzu talde bat sortzeko');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/taldeak`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                izena: izena,
                erabiltzailea_id: unekoErabiltzailea.id
            })
        });

        if (response.ok) {
            const taldeBerria = await response.json();
            itxiModalak();
            kargatuErabiltzaileTaldeak();
            alert(`✅ "${taldeBerria.izena}" taldea sortu da!`);
        } else {
            const error = await response.json();
            alert(error.error || 'Errorea taldea sortzean');
        }
    } catch (error) {
        console.error('Errorea taldea sortzean:', error);
        alert('Errorea taldea sortzean. Ziurtatu backend-a martxan dagoela.');
    }
}

async function gehituPokemonTaldeari(taldeaId) {
    if (!unekoErabiltzailea) {
        alert('Saioa hasi behar duzu');
        return;
    }

    // Aldatu Pokémon atalera eta erakutsi taldearen informazioa
    aldatuAtala('pokemon');
}

async function partekatuTaldea(taldeaId) {
    if (!unekoErabiltzailea) {
        alert('Saioa hasi behar duzu taldeak partekatzeko');
        return;
    }

    if (!unekoErabiltzailea.telegramKontua) {
        const telegramKontua = prompt('Ez duzu Telegram konturik. Sartu zure Telegram kontua:');
        if (telegramKontua) {
            // Hemen eguneratu erabiltzailearen Telegram kontua
            alert('Telegram kontua eguneratzeko funtzionalitatea garatzen ari da');
        }
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/taldeak/${taldeaId}/partekatu`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({})
        });

        if (response.ok) {
            const emaitza = await response.json();
            alert('✅ ' + emaitza.message);
            
            if (emaitza.intsigna) {
                alert(`🎉 Zorionak! "${emaitza.intsigna}" intsigna irabazi duzu!`);
                // Eguneratu erabiltzailearen datuak
                const userResponse = await fetch(`${API_BASE_URL}/erabiltzaileak/${unekoErabiltzailea.id}`);
                unekoErabiltzailea = await userResponse.json();
                localStorage.setItem('unekoErabiltzailea', JSON.stringify(unekoErabiltzailea));
                
                // Eguneratu profila bistan badago
                if (document.getElementById('erabiltzailea-list').classList.contains('active')) {
                    kargatuErabiltzaileProfila();
                }
            }
        } else {
            const error = await response.json();
            alert('❌ ' + error.error);
        }
    } catch (error) {
        console.error('Errorea taldea partekatzean:', error);
        alert('❌ Errorea taldea partekatzean. Ziurtatu backend-a martxan dagoela.');
    }
}

async function ezabatuTaldea(taldeaId) {
    if (!confirm('Ziur zaude talde hau ezabatu nahi duzula? Ekintza hau ezin da desegin.')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/taldeak/${taldeaId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            kargatuErabiltzaileTaldeak();
            alert('✅ Taldea ezabatu da');
        } else {
            const error = await response.json();
            alert('❌ ' + (error.error || 'Errorea taldea ezabatzean'));
        }
    } catch (error) {
        console.error('Errorea taldea ezabatzean:', error);
        alert('❌ Errorea taldea ezabatzean');
    }
}

function erakutsiTaldeakErrorea(mezua) {
    const taldeakZerrenda = document.getElementById('taldeak-zerrenda');
    if (taldeakZerrenda) {
        taldeakZerrenda.innerHTML = `
            <div class="error-message" style="text-align: center; padding: 40px;">
                <div style="background-color: var(--pokedex-red); color: white; padding: 20px; border-radius: 15px; border: 3px solid var(--pokedex-black);">
                    <h3 style="margin: 0; font-family: 'Press Start 2P', cursive;">ERROREA</h3>
                    <p style="margin: 10px 0 0 0;">${mezua}</p>
                </div>
                <button class="pokedex-button" onclick="kargatuErabiltzaileTaldeak()" style="margin-top: 20px;">
                SAIATU BERRIZ
                </button>
            </div>
        `;
    }
}

// Pokémon bat taldera gehitzean
async function gehituPokemonHautatuaTaldeari(pokemonId) {
    const taldeaId = sessionStorage.getItem('hautatutakoTaldeaId');
    
    if (!taldeaId) {
        alert('Ez da talderik hautatu. Mesedez, hautatu talde bat lehenik.');
        return;
    }

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
            sessionStorage.removeItem('hautatutakoTaldeaId');
            alert(`✅ Pokémon-a taldera gehitu da!`);
            
            // Eguneratu taldeen zerrenda
            kargatuErabiltzaileTaldeak();
        } else {
            const error = await response.json();
            alert('❌ ' + error.error);
        }
    } catch (error) {
        console.error('Errorea Pokémona taldera gehitzean:', error);
        alert('❌ Errorea Pokémona taldera gehitzean');
    }
}