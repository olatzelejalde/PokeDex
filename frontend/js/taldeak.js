// Taldeak kudeatzeko funtzioak
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
        const taldeTxartela = sortuTaldeTxartela(taldea);
        taldeakZerrenda.appendChild(taldeTxartela);
    });
}

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
            <button class="pokedex-button" onclick="gehituPokemonTaldeari(${taldea.id})">
                GEHITU POKÉMON
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
    
    // Gorde talde ID-a sessionStorage-n
    sessionStorage.setItem('hautatutakoTaldeaId', taldeaId);
    
    alert('Hautatu Pokémon bat zure taldera gehitzeko');
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
                if (document.getElementById('erabiltzailea-info').classList.contains('active')) {
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