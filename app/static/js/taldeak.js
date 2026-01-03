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

function sortuTaldeTxartela(taldea) {
    const card = document.createElement('div');
    card.className = 'taldea-card';
    card.innerHTML = `
        <div class="taldea-header">
            <h3>${taldea.izena}</h3>
            <span>${taldea.pokemonak.length}/6 Pokémon</span>
        </div>
        <div class="taldea-pokemonak">
            ${taldea.pokemonak.map(p => `
                <div class="pokemon-mini">
                    <img src="${p.irudia}" alt="${p.izena}">
                    <div>${p.izena}</div>
                </div>
            `).join('')}
        </div>
        <div class="taldea-actions">
            <button class="pokedex-button secondary" onclick="partekatuTaldea(${taldea.id})">PARTEKATU</button>
            <button class="pokedex-button" style="background-color: var(--pokedex-red); color: white;" onclick="ezabatuTaldea(${taldea.id})">EZABATU</button>
        </div>
    `;
    return card;
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
            alert(`✅ "${taldeBerria.izena}" taldea sortu da!`);
        } else {
            const error = await res.json();
            alert(error.error || 'Errorea taldea sortzean');
        }
    } catch (error) {
        console.error(error);
    }
}