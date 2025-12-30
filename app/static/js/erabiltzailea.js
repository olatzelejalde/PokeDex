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
    document.getElementById(`erabiltzailea-list`).classList.remove('active');
    document.getElementById(`erabiltzailea-edit`).classList.add('active');
    document.getElementById('erabiltzailea-edit').innerHTML = `
        <div class="profile-container">
            <div class="profile-card">
            <h2><img id="profile-pokeball" src="../static/pokeball.webp">ENTRENATZAILE FITXA <p class="profile-id">ID: ${unekoErabiltzailea.id}</p></h2>
                <p>Erabiltzaile Izena: ${unekoErabiltzailea.erabilIzena}</p>
                <label>Izena: <input id="izena-editatu" type="text" value="${unekoErabiltzailea.izena}"></label>
                <label>Abizena: <input id="abizena-editatu" type="text" value="${unekoErabiltzailea.abizena}"></label>
                <label>Telegram: <input id="telegram-editatu" type="text" value="${unekoErabiltzailea.telegramKontua || ''}"></label>
                <label>Pasahitza: <input id="pasahitza-editatu" type="password" placeholder="Sartu pasahitz berria"></label>
                <label>Konfirmatu Pasahitza: <input id="konfirmatu-pasahitza-editatu" type="password" placeholder="Konfirmatu pasahitza"></label>
                <button class="pokedex-button" onclick="irtenEdiziotik()">Utzi aldaketak</button>
                <button class="pokedex-button" onclick="aldaketakGorde()">Gorde aldaketak</button>
            </div>
        </div>
    `;
}

function irtenEdiziotik() {
    document.getElementById(`erabiltzailea-edit`).classList.remove('active');
    document.getElementById(`erabiltzailea-list`).classList.add('active');
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
    } catch (error) {
        console.error('Errorea erabiltzailea eguneratzerakoan:', error);
        alert('Errorea erabiltzailea eguneratzerakoan. Mesedez, saiatu berriro.');
    }
}