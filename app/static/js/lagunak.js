// Lagunak (amigos) kudeatzeko funtzioak

let miLagunak = [];

async function kargatuErabiltzaileLagunak() {
    if (!user) return;
    
    try {
        // Limpiar búsqueda
        const searchInput = document.getElementById('user-search');
        if (searchInput) searchInput.value = '';
        
        // Kargartu nire lagunak
        const resLagunak = await fetch(`${API_BASE_URL}/erabiltzaileak/${user.id}/lagunak`);
        miLagunak = await resLagunak.json();
        
        // Solo mostrar lagunak actuales
        erakutsiLagunak();
    } catch (error) {
        console.error('Errorea lagunak kargatzean:', error);
    }
}

function erakutsiLagunak() {
    const zona = document.getElementById('lagunak-zerrenda');
    
    if (miLagunak.length === 0) {
        zona.innerHTML = `
            <div class="no-lagunak" style="grid-column: 1 / -1; text-align: center; padding: 40px;">
                <h3>Ez duzu lagunrik oraindik</h3>
                <p>Bilatu erabiltzaileak eta gehitu lagunak!</p>
            </div>
        `;
        return;
    }
    
    zona.innerHTML = '<h3 style="grid-column: 1 / -1;">Nire Lagunak</h3>';
    miLagunak.forEach(laguna => {
        const txartela = sortuLagunaTxartela(laguna);
        zona.appendChild(txartela);
    });
}

function sortuLagunaTxartela(erabiltzailea) {
    const txartela = document.createElement('div');
    txartela.className = 'user-card';
    txartela.innerHTML = `
        <div class="user-header">
            <h3>${erabiltzailea.izena} ${erabiltzailea.abizena}</h3>
            <span class="user-username">@${erabiltzailea.erabiltzaileIzena}</span>
        </div>
        <div class="user-info">
            <p><strong>ID:</strong> ${erabiltzailea.id}</p>
            ${erabiltzailea.telegramKontua ? `<p><strong>Telegram:</strong> ${erabiltzailea.telegramKontua}</p>` : ''}
        </div>
        <div class="user-actions">
            <button class="pokedex-button" style="background-color: var(--pokedex-red); color: white;" onclick="kenduLaguna(${erabiltzailea.id})">Ezabatu laguna</button>
        </div>
    `;
    return txartela;
}



function sortuErabiltzaileTxartela(erabiltzailea) {
    const txartela = document.createElement('div');
    txartela.className = 'user-card';
    txartela.innerHTML = `
        <div class="user-header">
            <h3>${erabiltzailea.izena} ${erabiltzailea.abizena}</h3>
            <span class="user-username">@${erabiltzailea.erabiltzaileIzena}</span>
        </div>
        <div class="user-info">
            <p><strong>ID:</strong> ${erabiltzailea.id}</p>
            ${erabiltzailea.telegramKontua ? `<p><strong>Telegram:</strong> ${erabiltzailea.telegramKontua}</p>` : ''}
        </div>
        <div class="user-actions">
            <button class="pokedex-button" onclick="gehituLaguna(${erabiltzailea.id})">Gehitu laguna</button>
        </div>
    `;
    return txartela;
}

async function gehituLaguna(uid2) {
    try {
        const res = await fetch(`${API_BASE_URL}/erabiltzaileak/${user.id}/gehitu-laguna/${uid2}`, {
            method: 'POST'
        });
        if (res.ok) {
            alert('✅ Laguna gehitu da!');
            kargatuErabiltzaileLagunak();
        } else {
            const error = await res.json();
            alert(error.error || 'Errorea laguna gehitzean');
        }
    } catch (error) {
        console.error(error);
    }
}

async function kenduLaguna(uid2) {
    if (!confirm('¿Laguna kendu?')) return;
    try {
        const res = await fetch(`${API_BASE_URL}/erabiltzaileak/${user.id}/kendu-laguna/${uid2}`, {
            method: 'DELETE'
        });
        if (res.ok) {
            alert('✅ Laguna kendua');
            kargatuErabiltzaileLagunak();
        } else {
            alert('Errorea laguna kenduan');
        }
    } catch (error) {
        console.error(error);
    }
}

async function bilatuErabiltzaileak() {
    const searchTerm = document.getElementById('user-search').value.trim().toLowerCase();
    
    if (!searchTerm) {
        // Si vacía la búsqueda, volver a mostrar solo lagunak
        kargatuErabiltzaileLagunak();
        return;
    }
    
    try {
        const res = await fetch(`${API_BASE_URL}/erabiltzaileak`);
        const todos = await res.json();
        
        // Filtrar: no mostrar al usuario actual ni a los lagunak
        const lagunIds = miLagunak.map(l => l.id);
        const resultados = todos.filter(u => 
            u.id !== user.id && 
            !lagunIds.includes(u.id) &&
            (u.erabiltzaileIzena.toLowerCase().includes(searchTerm) ||
             u.izena.toLowerCase().includes(searchTerm) ||
             u.abizena.toLowerCase().includes(searchTerm))
        );
        
        erakutsiResultadosBusqueda(resultados);
    } catch (error) {
        console.error('Errorea bilaketareakoan:', error);
    }
}

function erakutsiResultadosBusqueda(erabiltzaileak) {
    const zona = document.getElementById('lagunak-zerrenda');
    
    if (erabiltzaileak.length === 0) {
        zona.innerHTML = `
            <div class="no-results" style="grid-column: 1 / -1; text-align: center; padding: 40px;">
                <h3>Ez da erabiltzailerik aurkitu</h3>
            </div>
        `;
        return;
    }
    
    zona.innerHTML = '<h3 style="grid-column: 1 / -1;">Bilaketa Emaitzak</h3>';
    erabiltzaileak.forEach(erabiltzailea => {
        const txartela = sortuErabiltzaileTxartela(erabiltzailea);
        zona.appendChild(txartela);
    });
}