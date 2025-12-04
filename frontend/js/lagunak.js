function kargatuLagunak() {

    document.getElementById('lagunak-list').innerHTML = `
        <div class="friends-container">
            <div class="friends-card">
                <h2>Laguna ${unekoErabiltzailea.izena}</h2>
                <p><strong>Erabiltzailea:</strong> ${unekoErabiltzailea.izena}</p>
                <p><strong>ID:</strong> ${unekoErabiltzailea.id}</p>
                <p><strong>Telegram:</strong> ${unekoErabiltzailea.telegramKontua || 'Ez dago'}</p>
                <button class="pokedex-button" onclick="mezuaBidali()">Mezua Bidali</button>
            </div>
        </div>
    `;

}

function mezuaBidali() {
    const mezua = prompt('Sartu zure mezua:');
    if (mezua !== null) {
        // Hemen inplementatuko genuke mezua bidaltzeko API deia
        alert('Mezua bidaltzeko funtzionalitatea garatzen ari da');
    }
}