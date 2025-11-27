const API_BASE_URL = 'http://localhost:5000/api';

// Aplikazioaren egoera
let unekoErabiltzailea = null;
let pokemonGuztiak = [];
let motaGuztiak = [];

// DOM elementuak
document.addEventListener('DOMContentLoaded', function() {
    hasieratuAplikazioa();
    konfiguratuGertaeraEntzuleak();
});

async function hasieratuAplikazioa() {
    await kargatuPokemonDatuak();
    await kargatuMotak();
    egiaztatuSaioa();
}

function konfiguratuGertaeraEntzuleak() {
    // Nabigazioa
    document.querySelectorAll('.menua a').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const section = e.target.getAttribute('data-section');
            aldatuAtala(section);
            
            // Actualizar clase active
            document.querySelectorAll('.menua a').forEach(a => a.classList.remove('active'));
            e.target.classList.add('active');
        });
    });

    // Bilaketa
    document.getElementById('search-button').addEventListener('click', bilatuPokemon);
    document.getElementById('pokemon-search').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') bilatuPokemon();
    });

    // Saioa botoia
    document.getElementById('btn-saioa').addEventListener('click', erakutsiSaioaModala);

    // Modalak
    document.querySelectorAll('.close').forEach(closeBtn => {
        closeBtn.addEventListener('click', itxiModalak);
    });

    // Saioa
    document.getElementById('btn-saioa-hasi').addEventListener('click', saioaHasi);
    document.getElementById('btn-erregistratu').addEventListener('click', erregistratu);
}

function aldatuAtala(atalIzena) {
    // Ezkutatu atal guztiak
    document.querySelectorAll('.pokedex-main article').forEach(atala => {
        atala.classList.remove('active');
    });

    // Erakutsi hautatutako atala
    document.getElementById(`${atalIzena}-list`).classList.add('active');

    // Kargatu atalaren datu espezifikoak
    if (atalIzena === 'taldeak') {
        kargatuErabiltzaileTaldeak();
    } else if (atalIzena === 'erabiltzailea') {
        kargatuErabiltzaileProfila();
    }
}

function erakutsiAtala(atalIzena) {
    // Ezkutatu atal guztiak
    Object.values(atalak).forEach(atala => {
        atala.classList.remove('section-active');
        atala.classList.add('section-hidden');
    });

    // Erakutsi hautatutako atala
    atalak[atalIzena].classList.remove('section-hidden');
    atalak[atalIzena].classList.add('section-active');

    // Kargatu atalaren datu espezifikoak
    if (atalIzena === 'taldeak') {
        kargatuErabiltzaileTaldeak();
    } else if (atalIzena === 'erabiltzailea') {
        kargatuErabiltzaileProfila();
    }
}

function itxiModalak() {
    document.querySelectorAll('.modal').forEach(modal => {
        modal.style.display = 'none';
    });
}

function erakutsiSaioaModala() {
    document.getElementById('saioa-modal').style.display = 'block';
}

function egiaztatuSaioa() {
    const gordetakoErabiltzailea = localStorage.getItem('unekoErabiltzailea');
    if (gordetakoErabiltzailea) {
        unekoErabiltzailea = JSON.parse(gordetakoErabiltzailea);
        eguneratuNabigazioa();
    } else {
        erakutsiSaioaModala();
    }
}

function eguneratuNabigazioa() {
    const saioaBotoia = document.getElementById('btn-saioa');
    if (unekoErabiltzailea) {
        saioaBotoia.textContent = 'Saioa Itxi';
        saioaBotoia.onclick = saioaItxi;
    } else {
        saioaBotoia.textContent = 'Saioa Hasi';
        saioaBotoia.onclick = erakutsiSaioaModala;
    }
}

async function erregistratu() {
    const izena = document.getElementById('saio-izena').value.trim();
    const pasahitza = document.getElementById('saio-pasahitza').value;

    if (!izena || !pasahitza) {
        alert('Mesedez, bete eremu guztiak');
        return;
    }

    if (izena.length < 3) {
        alert('Erabiltzaile izenak gutxienez 3 karaktere izan behar ditu');
        return;
    }

    if (pasahitza.length < 4) {
        alert('Pasahitzak gutxienez 4 karaktere izan behar ditu');
        return;
    }

    try {
        console.log('📝 Erabiltzailea erregistratzen:', izena);
        
        const response = await fetch(`${API_BASE_URL}/erabiltzaileak`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                izena: izena,
                pasahitza: pasahitza,
                telegramKontua: null 
            })
        });

        const datuak = await response.json();
        
        if (response.ok) {
            console.log('✅ Erabiltzailea erregistratu da:', datuak);
            alert('Erregistroa arrakastatsua! Orain saioa hasi dezakezu.');
            
            // Garbitu formularioa
            document.getElementById('saio-izena').value = '';
            document.getElementById('saio-pasahitza').value = '';
            
            // Erakutsi saioa hasteko mezua
            document.getElementById('saio-izena').placeholder = 'Sartu zure erabiltzaile izena';
            document.getElementById('saio-pasahitza').placeholder = 'Sartu zure pasahitza';
            
        } else {
            console.error('❌ Errorea erregistratzean:', datuak);
            alert(datuak.error || 'Errorea erregistratzean. Saiatu berriro.');
        }
    } catch (error) {
        console.error('❌ Errorea erregistratzean:', error);
        alert('Errorea erregistratzean. Ziurtatu backend-a martxan dagoela.');
    }
}

async function saioaHasi() {
    const izena = document.getElementById('saio-izena').value.trim();
    const pasahitza = document.getElementById('saio-pasahitza').value;

    if (!izena || !pasahitza) {
        alert('Mesedez, bete eremu guztiak');
        return;
    }

    try {
        console.log('🔐 Saioa hasten:', izena);
        
        const response = await fetch(`${API_BASE_URL}/erabiltzaileak/saioa`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ izena, pasahitza })
        });

        const datuak = await response.json();
        
        if (response.ok) {
            unekoErabiltzailea = datuak;
            localStorage.setItem('unekoErabiltzailea', JSON.stringify(unekoErabiltzailea));
            itxiModalak();
            eguneratuNabigazioa();
            alert('Ongi etorri ' + unekoErabiltzailea.izena + '!');
            
            // Eguneratu interfazea
            if (document.getElementById('taldeak-list').classList.contains('active')) {
                kargatuErabiltzaileTaldeak();
            }
            if (document.getElementById('erabiltzailea-info').classList.contains('active')) {
                kargatuErabiltzaileProfila();
            }
            
        } else {
            console.error('❌ Errorea saioa hasten:', datuak);
            alert(datuak.error || 'Errorea saioa hasten. Saiatu berriro.');
        }
    } catch (error) {
        console.error('❌ Errorea saioa hasten:', error);
        alert('Errorea saioa hasten. Ziurtatu backend-a martxan dagoela.');
    }
}

function saioaItxi() {
    unekoErabiltzailea = null;
    localStorage.removeItem('unekoErabiltzailea');
    eguneratuNabigazioa();
    erakutsiSaioaModala();
}

// Kargatzen/Kentzen funtzioak
function erakutsiKargatzen() {
    // Inplementatu kargatzen spinner
}

function ezkutatuKargatzen() {
    // Kendu kargatzen spinner
}

function erakutsiErrorea(mezua) {
    alert(mezua);
}