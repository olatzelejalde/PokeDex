// Erabiltzailea kudeatzeko funtzioak
function kargatuErabiltzaileProfila() {
    if (!unekoErabiltzailea) {
        document.getElementById('erabiltzailea-info').innerHTML = '<p>Saioa hasi behar duzu zure profila ikusteko</p>';
        return;
    }

    const erabiltzaileaInfo = document.getElementById('erabiltzailea-info');
    const insignakContainer = document.getElementById('insignak-container');

    erabiltzaileaInfo.innerHTML = `
        <div class="profil-informazioa">
            <p><strong>Erabiltzaile Izena:</strong> ${unekoErabiltzailea.izena}</p>
            <p><strong>Telegram Kontua:</strong> ${unekoErabiltzailea.telegramKontua || 'Ez dago konfiguratuta'}</p>
            <p><strong>Talde Kopurua:</strong> ${unekoErabiltzailea.taldeKopurua || 0}</p>
        </div>
        <div class="profil-ekintzak">
            <button class="btn-primary" onclick="aldatuTelegramKontua()">Aldatu Telegram Kontua</button>
        </div>
    `;

    insignakContainer.innerHTML = `
        <h3>Nire Intsignak</h3>
        <div class="insignak-zerrenda">
            ${unekoErabiltzailea.insignak && unekoErabiltzailea.insignak.length > 0 ? 
                unekoErabiltzailea.insignak.map(insigna => `
                    <span class="intsigna">${insigna}</span>
                `).join('') : 
                '<p>Oraindik ez duzu intsignarik irabazi. Sortu taldeak eta partekatu itzazu lortzeko!</p>'
            }
        </div>
    `;
}

function aldatuTelegramKontua() {
    const telegramKontua = prompt('Sartu zure Telegram kontua:');
    if (telegramKontua !== null) {
        // Hemen inplementatuko genuke Telegram kontua eguneratzeko API deia
        alert('Telegram kontua eguneratzeko funtzionalitatea garatzen ari da');
    }
}