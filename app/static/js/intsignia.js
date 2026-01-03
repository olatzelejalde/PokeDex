class IntsigniaManager {
    constructor(userId, gridId) {
        this.userId = userId;
        this.grid = document.getElementById(gridId);

        // Definición de todas las insignias y sus metas
        this.intsigniak = [
            { izena: 'Erabiltzaile gisa erregistratu', iconDefault: '/static/sprites/grisa.png', iconObtained: '/static/sprites/berdea.png', meta: 'erregistratu', desc: 'Erabiltzaile gisa erregistratu zara' },
            { izena: 'Lagun eskaera bidali', iconDefault: '/static/sprites/grisa.png', iconObtained: '/static/sprites/berdea.png', meta: 'lagunEskaeraBidali', desc: 'Lagun eskaera bat bidali duzu' },
            { izena: '6 lagun lortu', iconDefault: '/static/sprites/grisa.png', iconObtained: '/static/sprites/berdea.png', meta: '6Lagun', desc: '6 lagun izan dituzu' },
            { izena: 'Administratzailea izan', iconDefault: '/static/sprites/grisa.png', iconObtained: '/static/sprites/berdea.png', meta: 'admin', desc: 'Administratzaile bihurtu zara' },
            { izena: '5 talde sortu', iconDefault: '/static/sprites/grisa.png', iconObtained: '/static/sprites/berdea.png', meta: '5TaldeSortu', desc: '5 talde sortu dituzu' },
            { izena: 'Talde bat editatu', iconDefault: '/static/sprites/grisa.png', iconObtained: '/static/sprites/berdea.png', meta: 'taldeEditatu', desc: 'Talde bat editatu duzu' },
            { izena: 'Talde bat ezabatu', iconDefault: '/static/sprites/grisa.png', iconObtained: '/static/sprites/berdea.png', meta: 'taldeEzabatu', desc: 'Talde bat ezabatu duzu' },
            { izena: 'Mota bakoitzeko 4 Pokemon lortu', iconDefault: '/static/sprites/grisa.png', iconObtained: '/static/sprites/berdea.png', meta: '4PokemonMota', desc: 'Talde batean mota bakoitzeko 4 Pokémon dituzu' },
            { izena: 'Talde bat partekatu', iconDefault: '/static/sprites/grisa.png', iconObtained: '/static/sprites/berdea.png', meta: 'taldePartekatu', desc: 'Talde bat partekatu duzu' },
            { izena: 'Espezie informazioa 20 aldiz kontsultatu', iconDefault: '/static/sprites/grisa.png', iconObtained: '/static/sprites/berdea.png', meta: 'espezie20', desc: 'Espezieen informazioa 20 aldiz kontsultatu duzu' },
        ];
    }

    async load() {
        this.grid.innerHTML = '';
        this.grid.style.display = 'grid';
        this.grid.style.gridTemplateColumns = 'repeat(auto-fill, minmax(150px, 1fr))';
        this.grid.style.gap = '20px';
        try {
            const res = await fetch(`${API_BASE_URL}/erabiltzaileak/${this.userId}/intsigniak`);
            const obtained = await res.json(); 

            this.intsigniak.forEach(ins => {
                const lortua = obtained.includes(ins.meta);

                const card = document.createElement('div');
                card.className = 'insignia-card' + (lortua ? ' obtained' : '');

                card.innerHTML = `
                    <div class="icon-wrapper">
                        <img src="${lortua ? ins.iconObtained : ins.iconDefault}" alt="${ins.izena}">
                    </div>
                    <div class="insignia-name">${ins.izena}</div>
                    <div class="tooltip">${ins.desc}</div>
                `;

                this.grid.appendChild(card);
            });
        } catch (err) {
            console.error(err);
            this.grid.innerHTML = '<p>Errorea insigniak kargatzean.</p>';
        }
    }
}

// Crear instancia y enlazar con menú
const insigniaManager = new IntsigniaManager(user.id, 'insignak-zerrenda');
document.querySelector('a[data-section="insignak"]').addEventListener('click', () => {
    insigniaManager.load();
});
