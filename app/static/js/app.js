const API_BASE_URL = 'http://localhost:5000/api';

let pokemonGuztiak = [];
let motaGuztiak = [];

document.addEventListener('DOMContentLoaded', function () {
    kargatuPokemonDatuak();
    kargatuMotak();
    konfiguratuGertaeraEntzuleak();
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
    } else if (atalIzena === 'intsigniak'){ //OLATZ
        intsigniakKargatu(erabiltzaileId);
    }
}

// Backend-etik intsignien karga OLATZ
async function intsigniakKargatu(erabiltzaileId) {
    try {
        // Erabiltzailearen intsigniak lortzen ditugu API-tik
        const res = await fetch(`${API_BASE_URL}/erabiltzaileak/${erabiltzaileId}/intsigniak`);
        const intsigniak = await res.json();

        // Hemen erabakiko da intsignia lortu den edo ez. jarraipena >= helburua bada, lortua izango da
        intsigniak.forEach(ins => {
            ins.lortua = ins.jarraipena >= ins.helburua;
        });

        // Grid-ean intsigniak renderizatzen ditugu
        renderIntsigniak(intsigniak);
    } catch (err) {
        // Erroreak kontrolatzen ditugu eta kontsolan erakusten dira
        console.error("Errorea egon da intsigniak kargatzerakoan:", err);
    }
}
