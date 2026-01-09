// Taldeak kudeatzeko funtzioak
async function kargatuErabiltzaileTaldeak() {
    if (!user) {
        document.getElementById('taldeak-zerrenda').innerHTML = `
            <div class="error-message" style="text-align: center; padding: 40px;">
                <p>Saioa hasi behar duzu zure taldeak ikusteko</p>
                <button class="pokedex-button" onclick="window.location.href='/login'">SAIOA HASI</button>
            </div>
        `;
        return;
    }
    try {
        const res = await fetch(`${API_BASE_URL}/taldeak/erabiltzailea/${user.id}`);
        const taldeak = await res.json();
        erakutsiTaldeak(taldeak);
    } catch (err) {
        console.error(err);
    }
}

function erakutsiTaldeak(taldeak) {
    const zona = document.getElementById('taldeak-zerrenda');
    if (taldeak.length === 0) {
        zona.innerHTML = `
            <div class="no-taldeak" style="text-align: center; padding: 40px;">
                <h3>Ez duzu talderik</h3>
                <button class="pokedex-button" onclick="erakutsiTaldeaModala()">TALDE BERRIA SORTU</button>
            </div>
        `;
        return;
    }
    zona.innerHTML = '';
    taldeak.forEach(t => zona.appendChild(sortuTaldeTxartela(t)));
}

function erakutsiTaldeaModala() {
    document.getElementById('taldea-izena').value = '';
    document.getElementById('taldea-modal').style.display = 'block';
}

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

function sortuTaldeTxartela(taldea) {
    const card = document.createElement('div');
    card.className = 'taldea-card';
    const slotak = Array.from({ length: 6 }, (_, i) => taldea.pokemonak[i] || null);
    card.innerHTML = `
        <div class="taldea-header">
            <h3>${taldea.izena}</h3>
            <span>${taldea.pokemonak.length}/6 Pokémon</span>
        </div>
        <div class="taldea-pokemonak">
            ${slotak.map((p, idx) => p ? `
                <div class="pokemon-mini" data-slot="${idx}">
                    <img src="/static/sprites/pokemon/${p.id}.png" alt="${p.izena}" >
                    <div>${p.izena}</div>
                </div>
            ` : `
                <div class="pokemon-mini" data-slot="${idx}" onclick="eskatuPokemonTaldearentzat(${taldea.id})" style="cursor: pointer;">
                    <div class="hutsunea">+</div>
                    <div style="margin-top: 6px; font-size: 0.8em;">Gehitu</div>
                </div>
            `).join('')}
        </div>
        <div class="taldea-actions">
            <button class="pokedex-button secondary" onclick="lortuLagunak(${taldea.id})">PARTEKATU</button>
            <button class="pokedex-button" style="background-color: var(--pokedex-yellow); color: black;" onclick="editatuTaldea(${taldea.id})">EDITATU</button>
            <button class="pokedex-button" style="background-color: var(--pokedex-red); color: white;" onclick="ezabatuTaldea(${taldea.id})">EZABATU</button>
        </div>
    `;
    return card;
}

function bilatuPokemonSarrera(sarrera) {
    const clean = sarrera.trim().toLowerCase();
    return pokemonGuztiak.find(p => String(p.id) === clean || p.izena.toLowerCase() === clean);
}

async function eskatuPokemonTaldearentzat(taldeId) {
    if (!user) {
        alert('Saioa hasi behar duzu Pokémonak gehitzeko');
        return;
    }

    if (!pokemonGuztiak || pokemonGuztiak.length === 0) {
        try {
            await kargatuPokemonDatuak();
        } catch (error) {
            console.error(error);
            alert('Ezin izan da Pokémon zerrenda kargatu');
            return;
        }
    }

    erakutsiPokemonAukeraketa(taldeId);
}

function erakutsiPokemonAukeraketa(taldeId) {
    let modal = document.getElementById('pokemon-aukeraketa');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'pokemon-aukeraketa';
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content pokedex-modal large">
                <span class="close" onclick="itxiPokemonAukeraketa()">&times;</span>
                <h3>Hautatu Pok&eacute;mon bat</h3>
                <div class="pokemon-aukeraketa-grid"></div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    const grid = modal.querySelector('.pokemon-aukeraketa-grid');
    grid.innerHTML = pokemonGuztiak.map(p => `
        <div class="pokemon-choice-card" data-id="${p.id}">
            <div class="pokemon-choice-id">#${String(p.id).padStart(3, '0')}</div>
            <img src="/static/sprites/pokemon/${p.id}.png" alt="${p.izena}">
            <div class="pokemon-choice-name">${p.izena}</div>
            <div class="pokemon-choice-types">
                <span class="type ${lortuMotaKlasea(p.mota)}">${p.mota}</span>
                ${p.mota2 ? `<span class="type ${lortuMotaKlasea(p.mota2)}">${p.mota2}</span>` : ''}
            </div>
        </div>
    `).join('');

    grid.querySelectorAll('.pokemon-choice-card').forEach(el => {
        el.onclick = () => {
            const pid = Number(el.getAttribute('data-id'));
            const hautatua = pokemonGuztiak.find(pk => pk.id === pid);
            if (!hautatua) return;
            window.taldeaGehituContext = taldeId;
            window.taldeaGehituReturnList = true;
            itxiPokemonAukeraketa();
            erakutsiPokemonXehetasunak(hautatua);
        };
    });

    modal.style.display = 'block';
}

function itxiPokemonAukeraketa() {
    const modal = document.getElementById('pokemon-aukeraketa');
    if (modal) modal.style.display = 'none';
}

async function gehituPokemonTaldean(taldeId, pokemonId) {
    try {
        const res = await fetch(`${API_BASE_URL}/taldeak/${taldeId}/pokemon`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pokemon_id: pokemonId })
        });

        if (res.ok) {
            kargatuErabiltzaileTaldeak();
        } else {
            const error = await res.json();
            alert(error.error || 'Errorea Pokémona gehitzerakoan');
        }
    } catch (error) {
        console.error(error);
        alert('Ezin izan da Pokémona gehitu');
    }
}

async function gehituPokemonXehetasunetatik(pokemonId) {
    const taldeId = window.taldeaGehituContext;
    if (!taldeId) {
        alert('Ez da aukeratutako talderik');
        return;
    }
    await gehituPokemonTaldean(taldeId, pokemonId);
    window.taldeaGehituContext = null;
    itxiModalak();
}

async function lortuLagunak(taldeId) {
    try {
        const res = await fetch(`${API_BASE_URL}/erabiltzaileak/${user.id}/lagunak/telegram`);
        if (res.ok) {
            const data = await res.json();
            await navigator.clipboard.writeText(data.partekatzekoURL);
            alert('Taldearen esteka kopiatu da zure arbelean!');
        } else {
            const error = await res.json();
            alert(error.error || 'Errorea taldearen esteka partekatzean');
        }
    } catch (error) {
        console.error(error);
    }
}

async function ezabatuTaldea(taldeId) {
    if (!confirm('Ziur zaude talde hau ezabatu nahi duzula? Ekintza hau ezin da atzera bota.')) {
        return;
    }
    try {
        const res = await fetch(`${API_BASE_URL}/taldeak/${taldeId}`, {
            method: 'DELETE'
        });
        if (res.ok) {
            kargatuErabiltzaileTaldeak();
        } else {
            const error = await res.json();
            alert(error.error || 'Errorea taldearen ezabaketan');
        }
    } catch (error) {
        console.error(error);
    }
}

async function editatuTaldea(taldeId) {
    alert('Taldearen editatzea oraindik ez dago martxan.');
}

async function sortuTaldea() {
    const izena = document.getElementById('taldea-izena').value.trim();
    if (!izena) {
        alert('Mesedez, idatzi taldearen izena');
        return;
    }
    if (!user) {
        alert('Saioa hasi behar duzu talde bat sortzeko');
        return;
    }
    try {
        const res = await fetch(`${API_BASE_URL}/taldeak`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ izena: izena, erabiltzaile_id: user.id })
        });
        if (res.ok) {
            const taldeBerria = await res.json();
            itxiModalak();
            kargatuErabiltzaileTaldeak();
        } else {
            const error = await res.json();
            alert(error.error || 'Errorea taldea sortzean');
        }
    } catch (error) {
        console.error(error);
    }
}

// Modala
function erakutsiPartekatuModala(taldeId, lagunak) {
    let modal = document.getElementById('taldea-partekatu-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'taldea-partekatu-modal';
        modal.className = 'retro-modal';
        modal.innerHTML = `
            <div class="modal-box">
                <div class="modal-header">
                    <h3>Aukeratu laguna</h3>
                    <span class="close-retro" id="partekatu-close">&times;</span>
                </div>
                <div class="modal-body">
                    <div id="partekatu-lagunak-lista" class="lagunak-lista"></div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        modal.querySelector('#partekatu-close').onclick = itxiPartekatuModala;
        modal.addEventListener('click', (e) => {
            if (e.target === modal) itxiPartekatuModala();
        });
    }

    const lista = modal.querySelector('#partekatu-lagunak-lista');
    if (!lagunak || lagunak.length === 0) {
        lista.innerHTML = `<p style="text-align:center;">Ez duzu Telegram kontua duten lagunik</p>`;
    } else {
        lista.innerHTML = lagunak.map(l => `
            <div class="retro-lagun-card" data-lagun="${l.id}">
                <div class="retro-lagun-header">
                    <div class="retro-lagun-info">
                        <div class="retro-lagun-name">${l.erabiltzaileIzena}</div>
                        <div class="retro-lagun-handle">@${l.telegramKontua}</div>
                    </div>
                </div>
                <div class="retro-lagun-arrow">►</div>
            </div>
        `).join('');
        lista.querySelectorAll('.retro-lagun-card').forEach(card => {
            card.onclick = () => taldeaPartekatu(taldeId, Number(card.dataset.lagun));
        });
    }
    modal.classList.remove('hidden');
    modal.style.display = 'flex';
}

function itxiPartekatuModala() {
    const modal = document.getElementById('taldea-partekatu-modal');
    if (modal) {
        modal.classList.add('hidden');
        modal.style.display = 'none';
    }
}

// Telegram bidez taldea bidali
async function taldeaPartekatu(taldeId, lagunId) {
    try {
        const res = await fetch(`${API_BASE_URL}/taldeak/${taldeId}/partekatu/${user.id}/${lagunId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: user.id, lagun_id: lagunId })
        });
        const data = await res.json();
        if (res.ok) {
            alert('Taldea Telegram bidez bidali da');
            itxiPartekatuModala();
        } else {
            alert(data.error || 'Errorea taldea partekatzean');
        }
    } catch (error) {
        console.error(error);
        alert('Ezin izan da taldea partekatu');
    }
}

async function partekatuTaldea(taldeId) {
    try {
        const res = await fetch(`${API_BASE_URL}/erabiltzaileak/${user.id}/lagunak/telegram`);
        const lagunak = await res.json();
        erakutsiPartekatuModala(taldeId, lagunak);
    } catch (error) {
        console.error(error);
        alert('Ezin izan dira lagunak kargatu');
    }
}