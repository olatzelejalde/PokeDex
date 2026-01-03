// Lagunak (amigos) kudeatzeko funtzioak

async function kargatuErabiltzaileLagunak() {
    try {
        const response = await fetch(`${API_BASE_URL}/erabiltzaileak`);
        const todos = await response.json();
        // Filtrar para no mostrar al usuario actual
        const lagunak = todos.filter(u => u.id !== user.id);
        erakutsiErabiltzaileak(lagunak);
    } catch (error) {
        console.error('Errorea lagunak kargatzean:', error);
    }
}

function erakutsiErabiltzaileak(erabiltzaileak) {
    const grid = document.getElementById('lagunak-zerrenda');
    if (erabiltzaileak.length === 0) {
        grid.innerHTML = `
            <div class="no-results" style="grid-column: 1 / -1; text-align: center; padding: 40px;">
                <h3>Ez da erabiltzailerik aurkitu</h3>
            </div>
        `;
        return;
    }
    grid.innerHTML = '';
    erabiltzaileak.forEach(erabiltzailea => {
        const txartela = sortuErabiltzaileTxartela(erabiltzailea);
        grid.appendChild(txartela);
    });
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
            <button class="pokedex-button secondary" onclick="gehituLaguna(${erabiltzailea.id})">Gehitu laguna</button>
        </div>
    `;
    return txartela;
}

async function bilatuErabiltzaileak() {
    const bilaketaTerminoa = document.getElementById('user-search').value.toLowerCase().trim();
    
    try {
        const response = await fetch(`${API_BASE_URL}/erabiltzaileak`);
        const todos = await response.json();
        let iragazitakoak = todos.filter(u => u.id !== user.id);
        
        if (bilaketaTerminoa) {
            iragazitakoak = iragazitakoak.filter(u =>
                u.erabiltzaileIzena.toLowerCase().includes(bilaketaTerminoa) ||
                u.izena.toLowerCase().includes(bilaketaTerminoa) ||
                u.abizena.toLowerCase().includes(bilaketaTerminoa)
            );
        }
        
        erakutsiErabiltzaileak(iragazitakoak);
    } catch (error) {
        console.error('Errorea bilaketareakoan:', error);
    }
}

async function gehituLaguna(erabiltzaileId) {
    alert(`Laguna gehitu funtzionalitatea bukatu gabe (user ${erabiltzaileId})`);
    // TODO: Implementar endpoint para agregar amigos
}