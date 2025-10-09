document.addEventListener('DOMContentLoaded', () => {
    const menuLinks = document.querySelectorAll('.menua a');
    const sections = document.querySelectorAll('.pokedex-main [id]');
    const redDot = document.getElementById('red-dot');

    const nextPageUrl = 'login.html';

    let POKEDEX_API_URL = '/api/pokemon';
    let POKEMON_LIST_CONTAINER = document.getElementById('pokemon-list');

    if (sections.length > 0) {
        sections[0].classList.add('active'); // Mostrar la primera sección por defecto
    }

    if (menuLinks.length > 0) {
        menuLinks[0].classList.add('active');
        pokedexaKargatu();
    }

    menuLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href').substring(1);
            const targetSection = document.getElementById(targetId);

            menuLinks.forEach(l => l.classList.remove('active'));

            sections.forEach(section => {
                section.classList.remove('active');
            });
            if (targetSection){
                targetSection.classList.add('active');
                link.classList.add('active');
            }
        });
    });

    if (redDot){
        redDot.addEventListener('click', () => {
            window.location.href = nextPageUrl;
        });
    }

});


//Pokemon kartak sortzeko funtzioa

function pokemonKartakSortu(pokemon) {
    // 🌟 Uso de 'types' y 'sprite_url' para coincidir con la respuesta de Flask
    const klaseMota = pokemon.types[0].toLowerCase();
    
    // Genera los spans para cada tipo
    const spanMota = pokemon.types.map(t => 
        `<span class="type ${t.toLowerCase()}">${t}</span>`
    ).join(' ');

    return `
    <div class="pokemon-card ${klaseMota}">
        <div class="pokemon-id">#${pokemon.id.toString().padStart(3, '0')}</div>
        <img src="${pokemon.sprite_url}" alt="${pokemon.name}">
        <h2 class="pokemon-name">${pokemon.name}</h2>
        <div class="pokemon-types">
            ${spanMota}
        </div>
    </div>
    `;
}

async function pokedexaKargatu() {
    // Evita recargar si ya hay contenido (opcional, para mejorar rendimiento)
    if (POKEMON_LIST_CONTAINER.children.length > 1 && !document.getElementById('loading-message')) {
        return; 
    }

    try {
        POKEMON_LIST_CONTAINER.innerHTML = 
            '<p id="loading-message" style="grid-column: 1 / -1; text-align: center; color: #333;">Kargatzen...</p>';
            
        // 🌟 Llama a la API de tu servidor Flask
        const response = await fetch(POKEDEX_API_URL);
        const data = await response.json();

        console.log('Pokédex data fetched:', data);

        let HTMLKartak = '';
        data.forEach(pokemon => {
            HTMLKartak += pokemonKartakSortu(pokemon);
        });
        
        // Reemplaza el mensaje de carga con las cartas
        POKEMON_LIST_CONTAINER.innerHTML = HTMLKartak;

    } catch (error) {
        console.error('Error fetching Pokédex data:', error);
        POKEMON_LIST_CONTAINER.innerHTML = 
            '<p style="grid-column: 1 / -1; text-align: center; color: red;">Ezin izan dira Pokémonak kargatu. Mesedez, egiaztatu Flask zerbitzaria martxan dagoen.</p>';
    }
}
