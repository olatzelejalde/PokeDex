// Erabiltzailea kudeatzeko funtzioak
function kargatuErabiltzaileProfila() {

    document.getElementById('erabiltzailea-list').innerHTML = `
        <div class="profile-container">
            <div class="profile-card">
            <h2><img id="profile-pokeball" src="../static/pokeball.webp">ENTRENATZAILE FITXA <p class="profile-id">ID: ${unekoErabiltzailea.id}</p></h2>
                <p>Erabiltzaile Izena: ${unekoErabiltzailea.erabilIzena}</p>
                <p>Izena: ${unekoErabiltzailea.izena}</p>
                <p>Abizena: ${unekoErabiltzailea.abizena}</p>
                <p>Telegram: ${unekoErabiltzailea.telegramKontua || 'Ez dago'}</p>
                <button class="pokedex-button" onclick="aldatuDatuak()">Aldatu nire datuak</button>
            </div>
        </div>
    `;
}

async function aldatuDatuak() {
    document.getElementById('erabiltzailea-list').style.display = 'none';
    document.getElementById('erabiltzailea-edit').style.display = 'block';
    document.getElementById('erabiltzailea-edit').innerHTML = `
        <div class="profile-container">
            <div class="profile-card">
            <h2><img id="profile-pokeball" src="../static/pokeball.webp">ENTRENATZAILE FITXA <p class="profile-id">ID: ${unekoErabiltzailea.id}</p></h2>
                <p>Erabiltzaile Izena: ${unekoErabiltzailea.erabilIzena}</p>
                <label>Izena: </label>
                <input id="izena-editatu" type="text" value="${unekoErabiltzailea.izena}">
                <label>Abizena: </label>
                <input id="abizena-editatu" type="text" value="${unekoErabiltzailea.abizena}">
                <label>Telegram: </label>
                <input id="telegram-editatu" type="text" value="${unekoErabiltzailea.telegramKontua || ''}">
                <label>Pasahitza: </label>
                <input id="pasahitza-editatu" type="password" placeholder="Sartu pasahitz berria">
                <label>Konfirmatu Pasahitza: </label>
                <input id="konfirmatu-pasahitza-editatu" type="password" placeholder="Konfirmatu pasahitza">
                <button class="pokedex-button" onclick="irtenEdiziotik()">Utzi aldaketak</button>
                <button class="pokedex-button" onclick="aldaketakGorde()">Gorde aldaketak</button>
            </div>
        </div>
    `;
}

function irtenEdiziotik() {
    document.getElementById('erabiltzailea-edit').style.display = 'none';
    document.getElementById('erabiltzailea-list').style.display = 'block';
}

async function aldaketakGorde() {
    const payload = {};
    const izena = document.getElementById('izena-editatu').value.trim();
    const abizena = document.getElementById('abizena-editatu').value.trim();
    const telegram = document.getElementById('telegram-editatu').value.trim();
    const pasahitza = document.getElementById('pasahitza-editatu').value;
    const konfirmatuPasahitza = document.getElementById('konfirmatu-pasahitza-editatu').value;

    if (izena !== unekoErabiltzailea.izena) {
        payload.izena = izena;
    }
    if (abizena !== unekoErabiltzailea.abizena) {
        payload.abizena = abizena;
    }
    if (telegram !== (unekoErabiltzailea.telegramKontua || '')) {
        payload.telegramKontua = telegram || null;
    }

    if (pasahitza || konfirmatuPasahitza) {
        if (pasahitza !== konfirmatuPasahitza) {
            alert('Pasahitzak ez datoz bat');
            return;
        }
        payload.pasahitza = pasahitza;
    }

    if (Object.keys(payload).length === 0) {
        alert('Ez dago aldaketarik gordetzeko');
        irtenEdiziotik();
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/erabiltzaileak/${unekoErabiltzailea.id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });
        if (!response.ok) {
            throw new Error('Errorea erabiltzailea eguneratzerakoan');
        }

        Object.assign(unekoErabiltzailea, payload);
        localStorage.setItem('unekoErabiltzailea', JSON.stringify(unekoErabiltzailea));
        alert('Zure datuak ondo eguneratu dira');
        irtenEdiziotik();
        kargatuErabiltzaileProfila();
        alert('Zure datuak ondo eguneratu dira');
    } catch (error) {
        console.error('Errorea erabiltzailea eguneratzerakoan:', error);
        alert('Errorea erabiltzailea eguneratzerakoan. Mesedez, saiatu berriro.');
    }
}