// Erabiltzailea kudeatzeko funtzioak
function kargatuErabiltzaileProfila() {

    document.getElementById('erabiltzailea-list').innerHTML = `
        <div class="profile-container">
            <div class="profile-card">
                <h2><img id="profile-pokeball" src="../static/pokeball.webp">ENTRENATZAILE FITXA <p class="profile-id">ID: ${unekoErabiltzailea.id}</p></h2>
                <p>Izena: ${unekoErabiltzailea.izena}</p>
                <p>Abizena: ${unekoErabiltzailea.abizena}</p>
                <p>Erabiltzaile Izena: ${unekoErabiltzailea.erabilIzena}</p>
                <p>Telegram: ${unekoErabiltzailea.telegramKontua || 'Ez dago'}</p>
                <button class="pokedex-button" onclick="aldatuDatuak()">Aldatu nire datuak</button>
            </div>
        </div>
    `;
}

async function aldatuDatuak() {
    if (!unekoErabiltzailea) {
        alert('Saioa hasi behar duzu zure datuak aldatzeko');
        return;
    }

    // Crear formulario/modal para editar datos
    const izenaBerria = prompt('Izen berria:', unekoErabiltzailea.izena);
    if (izenaBerria === null) return; // Usuario canceló

    const abizenaBerria = prompt('Abizen berria:', unekoErabiltzailea.abizena);
    if (abizenaBerria === null) return;

    const erabilIzenaBerria = prompt('Erabiltzaile izen berria:', unekoErabiltzailea.erabilIzena);
    if (erabilIzenaBerria === null) return;

    const telegramBerria = prompt('Telegram kontu berria:', unekoErabiltzailea.telegramKontua || '');
    if (telegramBerria === null) return;

    try {
        const response = await fetch(`${API_BASE_URL}/erabiltzaileak/${unekoErabiltzailea.id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                izena: izenaBerria,
                abizena: abizenaBerria,
                erabilIzena: erabilIzenaBerria,
                telegramKontua: telegramBerria
            })
        });

        if (response.ok) {
            const erabiltzaileaEguneratua = await response.json();
            
            // Actualizar usuario en localStorage y variable global
            unekoErabiltzailea = erabiltzaileaEguneratua;
            localStorage.setItem('unekoErabiltzailea', JSON.stringify(unekoErabiltzailea));
            
            // Recargar perfil
            kargatuErabiltzaileProfila();
            alert('Datuak arrakastaz eguneratu dira!');
        } else {
            const errorData = await response.json();
            alert(errorData.error || 'Errorea datuak eguneratzean');
        }
    } catch (error) {
        console.error('Errorea datuak eguneratzean:', error);
        alert('Errorea datuak eguneratzean');
    }
}