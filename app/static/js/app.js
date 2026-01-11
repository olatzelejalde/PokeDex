const API_BASE_URL = 'http://localhost:5000/api';

let pokemonGuztiak = [];
let motaGuztiak = [];

document.addEventListener('DOMContentLoaded', function () {
    kargatuPokemonDatuak();
    kargatuMotak();
    konfiguratuGertaeraEntzuleak();
    konfiguratuBotLogika(); //ANE
});

function konfiguratuGertaeraEntzuleak() {
    document.querySelectorAll('.menua a').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const section = e.target.getAttribute('data-section');
            aldatuAtala(section);
            document.querySelectorAll('.menua a').forEach(a => a.classList.remove('active'));
            e.target.classList.add('active');
        });
    });

    document.getElementById('search-button').addEventListener('click', bilatuPokemon);
    document.getElementById('pokemon-search').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') bilatuPokemon();
    });

    document.getElementById('search-button').addEventListener('click', bilatuPokemon);
    document.getElementById('pokemon-search').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') bilatuPokemon();
    });

    document.getElementById('type-filter').addEventListener('change', bilatuPokemon);
    document.getElementById('pokemon-search').addEventListener('input', function (e) {
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => bilatuPokemon(), 500);
    });

    document.getElementById('type-filter').addEventListener('change', bilatuPokemon);

    // Búsqueda de usuarios
    document.getElementById('search-users-button').addEventListener('click', bilatuErabiltzaileak);
    document.getElementById('user-search').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') bilatuErabiltzaileak();
    });

    // Botón cerrar sesión
    document.getElementById('btn-saioa').addEventListener('click', () => {
        window.location.href = '/auth/logout';
    });

    // Bot
    document.getElementById('bot').addEventListener('click', () =>
        document.getElementById('bot-panel').classList.toggle('hidden')
    );
}

function aldatuAtala(atalIzena) {
    document.querySelectorAll('.pokedex-main article').forEach(atala => {
        atala.classList.remove('active');
    });
    document.getElementById(`${atalIzena}-list`).classList.add('active');

    // Mostrar/esconder barras de búsqueda
    document.getElementById('search-pokemon').style.display = atalIzena === 'pokemon' ? 'flex' : 'none';
    document.getElementById('search-lagunak').style.display = atalIzena === 'lagunak' ? 'flex' : 'none';

    if (atalIzena === 'taldeak') {
        kargatuErabiltzaileTaldeak();
    } else if (atalIzena === 'erabiltzailea') {
        kargatuErabiltzaileProfila();
    } else if (atalIzena === 'lagunak') {
        kargatuErabiltzaileLagunak();

    } else if(atalIzena === 'intsigniak'){ //OLATZ
        intsigniakKargatu(erabiltzaileId);
    }
}

/* ===========================================================
   BOT-AREN BOTOIAK ETA PANTAILA GEHIGARRIA
   =========================================================== */
const botData = {
    pokeTop: {
        title: "PokeTop",
        color: "#ffcccc",
        borderColor: "#dc0a2d",
        content: `
            <p>🏆 <strong>TOP POKEMON</strong></p>
            <ul style="list-style:none; padding:0; text-align:left; margin-left: 20px;">
                <li>1. Mewtwo (CP: 4178)</li>
                <li>2. Slaking (CP: 4000)</li>
                <li>3. Machamp (CP: 3500)</li>
            </ul>
        `
    },
    pokeMota: {
        title: "PokeMota",
        color: "#ccffcc",
        borderColor: "#4dad5b",
        content: `
            <p>🍃 <strong>ANALISIS DE TIPOS</strong></p>
            <div style="background:rgba(255,255,255,0.5); padding:10px; border-radius:5px;">
                <p>Sua: 15% | Ura: 45%</p>
                <p>Belarra: 40%</p>
            </div>
            <p style="margin-top:10px; font-size:9px;">Gomendioa: Erabili elektrikoak.</p>
        `
    },
    pokeEbo: {
        title: "PokeEbo",
        color: "#ffffcc",
        borderColor: "#eed535",
        content: `
            <p>⚡ <strong>EBOLUZIOAK</strong></p>
            <p>Prest daudenak:</p>
            <p> ➤ Pikachu ➔ Raichu</p>
            <p> ➤ Eevee ➔ Jolteon</p>
        `
    },
    pokeScan: {
        title: "PokeScan",
        color: "#cce5ff",
        borderColor: "#2663ac",
        content: `
            <p>📡 <strong>ESKANEATZEN...</strong></p>
            <p>Bip... Bip... Bip...</p>
            <p style="color:red; font-weight:bold; margin-top:10px;">⚠️ ERROREA</p>
            <p>Ez da seinalerik aurkitu.</p>
        `
    }
};

function konfiguratuBotLogika() {
    const modal = document.getElementById('retro-modal');
    const botPanel = document.getElementById('bot-panel');
    const modalTitle = document.getElementById('modal-title');
    const modalBody = document.getElementById('modal-body');
    const modalBox = document.getElementById('modal-box-color');
    const modalHeader = document.querySelector('.modal-header');
    const closeX = document.querySelector('.close-retro');
    const closeOk = document.querySelector('.retro-ok-btn');
    const options = document.querySelectorAll('.bot-option');

    if (!modal) return;

    const openModal = (action) => {
        const data = botData[action];
        if (!data) return;

        modalTitle.innerHTML = data.title;
        modalBody.innerHTML = data.content;

        if(modalBox) {
            modalBox.style.backgroundColor = data.color;
            modalBox.style.borderColor = data.borderColor;
        }
        if(closeOk) {
            closeOk.classList.remove('pokeTop', 'pokeMota', 'pokeEbo', 'pokeScan');
            closeOk.classList.add(action);
        }
        if(modalHeader) {
            modalHeader.classList.remove('pokeTop', 'pokeMota', 'pokeEbo', 'pokeScan');
            modalHeader.classList.add(action);
        }

        modal.classList.remove('hidden');
        if(botPanel) botPanel.classList.add('hidden');
    };

    const closeModal = () => {
        modal.classList.add('hidden');
    };

    options.forEach(option => {
        option.addEventListener('click', (e) => {
            e.stopPropagation();
            const action = option.getAttribute('data-action');
            openModal(action);
        });
    });

    if (closeX) closeX.addEventListener('click', closeModal);
    if (closeOk) closeOk.addEventListener('click', closeModal);

    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });
}