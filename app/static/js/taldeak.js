document.addEventListener('DOMContentLoaded', () => {
    // 1. Elementos
    const btnBerria = document.getElementById('btn-talde-berria');
    const modal = document.getElementById('taldea-modal');
    const btnGorde = document.getElementById('btn-taldea-gorde');
    const inputIzena = document.getElementById('taldea-izena');
    const closeBtn = modal ? modal.querySelector('.close') : null;

    // 2. Abrir Modal
    if (btnBerria && modal) {
        btnBerria.addEventListener('click', () => {
            modal.style.display = 'block';
            inputIzena.value = ''; // Limpiar input al abrir
            inputIzena.focus();
        });
    }

    // 3. Cerrar Modal
    if (closeBtn) closeBtn.addEventListener('click', () => modal.style.display = 'none');
    window.addEventListener('click', (e) => {
        if (e.target == modal) modal.style.display = 'none';
    });

    // 4. GUARDAR (LA PARTE IMPORTANTE JSON)
    if (btnGorde) {
        btnGorde.addEventListener('click', async () => {
            const izena = inputIzena.value.trim();
            if (!izena) {
                alert("Mesedez, idatzi izen bat.");
                return;
            }

            try {
                // --- CAMBIO CLAVE: ENVIAR COMO JSON ---
                const response = await fetch('/taldea/create', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'  // <--- ESTO ES LO IMPORTANTE
                    },
                    body: JSON.stringify({ izena: izena })  // <--- EMPAQUETAMOS COMO JSON
                });

                const data = await response.json();

                if (response.ok) {
                    modal.style.display = 'none';
                    kargatuErabiltzaileTaldeak(); // Recargar la lista
                    alert("Taldea sortu da!");
                } else {
                    alert("Errorea: " + (data.error || "Ezin izan da sortu"));
                }
            } catch (error) {
                console.error("Errorea:", error);
            }
        });
    }

    // Cargar la lista al entrar
    kargatuErabiltzaileTaldeak();
});

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
    zona.innerHTML = '';
    if (taldeak.length === 0) {
        zona.style.display = 'flex';
        zona.style.justifyContent = 'center';
        zona.style.alignItems = 'center';
        zona.style.width = '100%';

        zona.innerHTML = `
            <div class="no-taldeak" style="text-align: center; color: #333;">
                <h3 style="font-size: 24px; margin-bottom: 20px;">Ez duzu talderik</h3>
                <p>Erabili goiko botoia bat sortzeko</p> 
            </div>
        `;
        return;
    }
    zona.style.display = '';
    zona.style.justifyContent = '';
    zona.style.alignItems = '';
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