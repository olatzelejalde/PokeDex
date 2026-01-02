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

    if (atalIzena === 'taldeak') {
        kargatuErabiltzaileTaldeak();
    } else if (atalIzena === 'erabiltzailea') {
        kargatuErabiltzaileProfila();
    }
}

/* ===========================================================
   NUEVA LÓGICA: BOTONES DEL BOT Y VENTANA MODAL
   =========================================================== */

// 1. Datos para rellenar la ventana según el botón
const botData = {
    pokeTop: {
        title: "POKE TOP",
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
        title: "POKE MOTA",
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
        title: "POKE EBO",
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
        title: "POKE SCAN",
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

// 2. Función que activa los clicks en los botones de colores y la ventana
function konfiguratuBotLogika() {
    const modal = document.getElementById('retro-modal');
    const botPanel = document.getElementById('bot-panel');
    const modalTitle = document.getElementById('modal-title');
    const modalBody = document.getElementById('modal-body');
    const modalBox = document.getElementById('modal-box-color');
    const closeX = document.querySelector('.close-retro');
    const closeOk = document.querySelector('.retro-ok-btn');
    const options = document.querySelectorAll('.bot-option');

    // Si falta algo en el HTML, paramos para no dar errores
    if (!modal) return;

    // Función para abrir la ventana con datos
    const openModal = (action) => {
        const data = botData[action];
        if (!data) return;

        // Rellenar info
        modalTitle.innerHTML = data.title;
        modalBody.innerHTML = data.content;

        // Cambiar colores
        if(modalBox) {
            modalBox.style.backgroundColor = data.color;
            modalBox.style.borderColor = data.borderColor;
        }

        // Mostrar ventana y ocultar panel de botones
        modal.classList.remove('hidden');
        if(botPanel) botPanel.classList.add('hidden');
    };

    // Función para cerrar la ventana
    const closeModal = () => {
        modal.classList.add('hidden');
    };

    // Asignar click a cada botón de color (Rojo, Verde, Amarillo, Azul)
    options.forEach(option => {
        option.addEventListener('click', (e) => {
            e.stopPropagation(); // Evitar conflictos
            const action = option.getAttribute('data-action');
            openModal(action);
        });
    });

    // Cerrar con la X
    if (closeX) closeX.addEventListener('click', closeModal);

    // Cerrar con el botón OK
    if (closeOk) closeOk.addEventListener('click', closeModal);

    // Cerrar si clicamos fuera (en el fondo oscuro)
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });
}