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