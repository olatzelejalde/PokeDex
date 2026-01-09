// Erabiltzailea kudeatzeko funtzioak
function kargatuErabiltzaileProfila() {
    // user viene desde Flask → variable global user
    if (user.rola === 'admin') {
        document.getElementById('erabiltzailea-list').innerHTML = `
        <div class="profile-container">
            <div class="profile-card">
                <h2><img id="profile-pokeball" src="/static/pokeball.webp">ADMINISTRATZAILE FITXA <p class="profile-id">ID: ${user.id}</p></h2>
                <p>Erabiltzaile Izena: ${user.erabiltzaileIzena}</p>
                <p>Izena: ${user.izena}</p>
                <p>Abizena: ${user.abizena}</p>
                <p>Telegram: ${user.telegramKontua || 'Ez dago'}</p>
                <button class="pokedex-button" onclick="aldatuDatuak()">Aldatu nire datuak</button>
            </div>
        </div>
        `;
    } else {
        document.getElementById('erabiltzailea-list').innerHTML = `
            <div class="profile-container">
                <div class="profile-card">
                    <h2><img id="profile-pokeball" src="/static/pokeball.webp">ENTRENATZAILE FITXA <p class="profile-id">ID: ${user.id}</p></h2>
                    <p>Erabiltzaile Izena: ${user.erabiltzaileIzena}</p>
                    <p>Izena: ${user.izena}</p>
                    <p>Abizena: ${user.abizena}</p>
                    <p>Telegram: ${user.telegramKontua || 'Ez dago'}</p>
                    <button class="pokedex-button" onclick="aldatuDatuak()">Aldatu nire datuak</button>
                </div>
            </div>
        `;
    }
}

async function aldatuDatuak() {
    document.getElementById('erabiltzailea-list').classList.remove('active');
    document.getElementById('erabiltzailea-edit').classList.add('active');
    document.getElementById('erabiltzailea-edit').innerHTML = `
        <div class="profile-container">
            <div class="profile-card">
                <h2><img id="profile-pokeball" src="/static/pokeball.webp">ENTRENATZAILE FITXA <p class="profile-id">ID: ${user.id}</p></h2>
                <p>Erabiltzaile Izena: ${user.erabiltzaileIzena}</p>
                <label>Izena: <input id="izena-editatu" type="text" value="${user.izena}"></label>
                <label>Abizena: <input id="abizena-editatu" type="text" value="${user.abizena}"></label>
                <label>Telegram: <input id="telegram-editatu" type="text" value="${user.telegramKontua || ''}"></label>
                <label>Pasahitza: <input id="pasahitza-editatu" type="password" placeholder="Sartu pasahitz berria"></label>
                <label>Konfirmatu Pasahitza: <input id="konfirmatu-pasahitza-editatu" type="password" placeholder="Konfirmatu pasahitza"></label>
                <button class="pokedex-button" onclick="irtenEdiziotik()">Utzi aldaketak</button>
                <button class="pokedex-button" onclick="aldaketakGorde()">Gorde aldaketak</button>
            </div>
        </div>
    `;
}

function irtenEdiziotik() {
    document.getElementById('erabiltzailea-edit').classList.remove('active');
    document.getElementById('erabiltzailea-list').classList.add('active');
}

async function aldaketakGorde() {
    const payload = {};
    const izena = document.getElementById('izena-editatu').value.trim();
    const abizena = document.getElementById('abizena-editatu').value.trim();
    const telegram = document.getElementById('telegram-editatu').value.trim();
    const pasahitza = document.getElementById('pasahitza-editatu').value;
    const konfirmatuPasahitza = document.getElementById('konfirmatu-pasahitza-editatu').value;

    if (izena !== user.izena) payload.izena = izena;
    if (abizena !== user.abizena) payload.abizena = abizena;
    if (telegram !== (user.telegramKontua || '')) payload.telegramKontua = telegram || null;

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
        const res = await fetch(`${API_BASE_URL}/erabiltzaileak/${user.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error('Errorea eguneratzerakoan');
        Object.assign(user, payload);
        alert('Zure datuak ondo eguneratu dira');
        irtenEdiziotik();
        kargatuErabiltzaileProfila();
    } catch (error) {
        console.error(error);
        alert('Errorea eguneratzerakoan. Saiatu berriro.');
    }
}