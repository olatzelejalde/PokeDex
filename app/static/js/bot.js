// 1. DATU FINKOAK (KONFIGURAZIOA)
const botConfigs = {
    pokeMota: {
        title: "🍃 POKEMOTA",
        color: "#ccffcc",
        borderColor: "#4dad5b",
        clickFunc: "cargarPokeMotaInfo"
    },
    pokeEbo: {
        title: "⚡ POKEEBO",
        color: "#ffffcc",
        borderColor: "#eed535",
        clickFunc: "cargarPokeMotaInfo"
    },
    pokeScan: {
        title: "📡 POKESCAN",
        color: "#cce5ff",
        borderColor: "#2663ac",
        clickFunc: "cargarPokeMotaInfo"
    }
};

/* ===========================================================
   LAGUNTZAILEA: ZERRENDA ERRENDERIZATU (BERSIO HANDIA / KLASIKOA)
   =========================================================== */
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

    // Modala irekitzeko funtzioa
    const openModal = async (action) => {
        // Modala erakutsi eta bot panela ezkutatu
        modal.classList.remove('hidden');
        if (botPanel) botPanel.classList.add('hidden');

        if (modalBox) {
            modalBox.style.backgroundColor = ''; // Aurreko kolorea garbitu
            modalBox.style.borderColor = '';
        }

        // Aurreko kolore-klaseak garbitu eta berria gehitu
        if (modalHeader) {
            modalHeader.classList.remove('pokeTop', 'pokeMota', 'pokeEbo', 'pokeScan');
            modalHeader.classList.add(action);
        }
        if (closeOk) {
            closeOk.classList.remove('pokeTop', 'pokeMota', 'pokeEbo', 'pokeScan');
            closeOk.classList.add(action);
        }

        // -----------------------------------------------------
        // A KASUA: POKETOP (Sailkapena)
        // -----------------------------------------------------
        if (action === 'pokeTop') {
            modalTitle.innerHTML = "🏆 POKETOP";
            if (modalBox) {
                modalBox.style.backgroundColor = "#ffcccc";
                modalBox.style.borderColor = "#dc0a2d";
            }
            modalBody.innerHTML = "<p>Kargatzen...</p>";

            try {
                // APIari taldeen zerrenda eskatu
                const response = await fetch('/api/taldeak/list');
                const usuarios = await response.json();

                // Irudien URLak zuzentzeko laguntzailea
                const fixImg = (url) => {
                    if (!url) return '/static/styles/pokeball.webp';
                    return url.startsWith('http') ? url : `/static/sprites/pokemon/${url.split('/').pop()}`;
                };

                let html = `
                <div class="selection-container">
                    <h2 class="title-text">Aukeratu talde bat:</h2>
                    <div class="trainers-grid">
                `;

                usuarios.forEach((user, index) => {
                    // Atzeko planoko gradienteak txartelentzat
                    const backgrounds = [
                        'linear-gradient(135deg, #FF9A9E 0%, #FECFEF 100%)', // Larrosa
                        'linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)', // Morea
                        'linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%)', // Urdina
                        'linear-gradient(135deg, #fccb90 0%, #d57eeb 100%)'  // Laranja
                    ];
                    const bgStyle = backgrounds[index % backgrounds.length];

                    let pokemonsHtml = '<div class="mini-poke-grid">';
                    if(user.Pokemon && user.Pokemon.length > 0){
                        user.Pokemon.forEach(p => {
                            pokemonsHtml += `<img src="${fixImg(p.Irudia)}" class="mini-poke-img" alt="${p.Pokemon_Izena}">`;
                        });
                    }
                    pokemonsHtml += '</div>';

                    html += `
                    <div class="trainer-card" style="background: ${bgStyle};" onclick="cargarMVP(${user.TaldeId})">
                        <div class="team-name">TALDEA ${user.TaldeId}</div>
                        ${pokemonsHtml}
                    </div>`;
                });

                html += `
                    </div>
                    <div id="mvp-result" style="margin-top:30px; width:100%;"></div>
                </div>`;

                modalBody.innerHTML = html;
            } catch (error) {
                modalBody.innerHTML = `<p style="color:red">Errorea: ${error.message}</p>`;
            }
        }
        // -----------------------------------------------------
        // B KASUA: MOTA, EBO eta SCAN (Zerrenda erakutsi)
        // -----------------------------------------------------
        else if (action === 'pokeMota' || action === 'pokeEbo' || action === 'pokeScan') {

            // 1. Titulua eta Koloreak ezarri
            if (action === 'pokeMota') {
                modalTitle.innerHTML = "🍃 POKEMOTA ";
                if(modalBox) { modalBox.style.backgroundColor = "#ccffcc"; modalBox.style.borderColor = "#4dad5b"; }
            }
            else if (action === 'pokeEbo') {
                modalTitle.innerHTML = "⚡ POKEEBO ";
                if(modalBox) { modalBox.style.backgroundColor = "#ffffcc"; modalBox.style.borderColor = "#eed535"; }
            }
            else if (action === 'pokeScan') {
                modalTitle.innerHTML = "📡 POKESCAN ";
                if(modalBox) { modalBox.style.backgroundColor = "#cce5ff"; modalBox.style.borderColor = "#2663ac"; }
            }

            // 2. Emaitzen edukiontzia prestatu
            modalBody.innerHTML = '<div id="tool-result"></div>';

            // 3. Zerrenda errenderizatzeko funtzio nagusiari deitu
            renderPokemonList('tool-result', action);
        }
    };

    // Modala ixteko funtzioa
    const closeModal = () => {
        modal.classList.add('hidden');
    };

    // Aukera bakoitzari klik gertaera gehitu
    options.forEach(option => {
        option.addEventListener('click', (e) => {
            e.stopPropagation();
            const action = option.getAttribute('data-action');
            openModal(action);
        });
    });

    // Ixteko botoien gertaerak
    if (closeX) closeX.addEventListener('click', closeModal);
    if (closeOk) closeOk.addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => { if (e.target === modal) closeModal(); });
}

// ---------------------------------------------------------
// FUNTZIO LAGUNTZAILEAK (konfiguratuBotLogika-tik KANPO)
// ---------------------------------------------------------

// 1. FUNTZIO NAGUSIA: POKEMON ZERRENDA (IKUS-ENTZUNEZKOA)
async function renderPokemonList(containerId, modo) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = '<p style="text-align:center; font-family:\'Press Start 2P\'; font-size:10px;">Kargatzen...</p>';

    try {
        const response = await fetch('/api/espezieak/list');
        let pokemons = await response.json();

        // Ordenatu Pokedex-eko IDaren arabera
        pokemons.sort((a, b) => a.id - b.id);

        container.innerHTML = `
            <p style="text-align:center; font-family:'Press Start 2P', cursive; font-size:12px; font-weight:bold; margin-bottom:15px; color:#333;">
                AUKERATU BAT:
            </p>
        `;

        const grid = document.createElement('div');
        // Grid estiloak sareta moduan erakusteko
        grid.style.display = 'grid';
        grid.style.gridTemplateColumns = 'repeat(4, 1fr)';
        grid.style.gap = '15px';
        grid.style.maxHeight = '400px';
        grid.style.overflowY = 'auto';
        grid.style.padding = '5px';

        pokemons.forEach(p => {
            const card = document.createElement('div');
            card.style.cursor = 'pointer';
            card.style.textAlign = 'center';
            card.style.padding = '18px';
            card.style.border = '3px solid #000000';
            card.style.background = 'white';
            card.style.borderRadius = '12px';
            card.style.fontFamily = "'Press Start 2P', cursive";
            card.style.minWidth = '110px';
            card.style.transition = 'transform 0.1s';
            card.onmouseover = () => card.style.transform = 'scale(1.03)';
            card.onmouseout = () => card.style.transform = 'scale(1)';

            const imgUrl = p.irudia.startsWith('http') ? p.irudia : `/static/sprites/pokemon/${p.irudia.split('/').pop()}`;

            // Txartel bakoitzaren barruko irudiaren tamaina doitu
            card.innerHTML = `
                <img src="${imgUrl}" 
                    style="width:90px; height:90px; object-fit:contain; image-rendering:pixelated;" 
                    onerror="this.src='/static/styles/pokeball.webp'">
                <div style="font-size:10px; font-weight:bold; margin-top:12px; text-transform:uppercase;">
                    ${p.izena}
                </div>
            `;

            // Klik egitean, dagokion informazioa kargatu
            card.onclick = () => {
                container.innerHTML = '';
                if (modo === 'pokeMota') cargarPokeMotaInfo(p.izena);
                else if (modo === 'pokeEbo') cargarPokeEboInfo(p.izena);
                else if (modo === 'pokeScan') cargarPokeScanInfo(p.izena);
            };

            grid.appendChild(card);
        });

        container.appendChild(grid);
    } catch (error) {
        console.error(error);
        container.innerHTML = '<p style="color:red; text-align:center; font-family:\'Press Start 2P\'; font-size:10px;">Errorea...</p>';
    }
}

// 2. MVP KARGATU (POKETOP SAILA)
async function cargarMVP(taldeId) {
    const divResultado = document.getElementById('mvp-result');
    divResultado.innerHTML = '<p style="text-align:center;">Kalkulatzen...</p>';

    try {
        const response = await fetch(`/api/taldeak/${taldeId}/mvp`);
        if (!response.ok) throw new Error("Ez da pokemonik aurkitu");

        const pokemon = await response.json();

        // Irudiaren logika
        const irudiaUrl = pokemon.PokeImage.startsWith('http')
            ? pokemon.PokeImage
            : `/static/sprites/pokemon/${pokemon.PokeImage.split('/').pop()}`;

        // Estatistiken datuak
        const stats = pokemon.Estatistikak;
        const hp = stats.Osasuna;
        const atk = stats.Atakea;
        const def = stats.Defentsa;
        const spa = stats['Atake berezia'] || stats.AtakeBerezia;
        const spd = stats['Defentsa berezia'] || stats.DefentsaBerezia;
        const spe = stats.Abiadura;

        // Diseinu HTML hobetua errenderizatu
        divResultado.innerHTML = `
            <div style="
                border: 4px solid #FFD700; 
                background: #FFFBEA; 
                padding: 15px; 
                border-radius: 20px; 
                max-width: 550px; 
                margin: 0 auto; 
                font-family: 'Verdana', sans-serif;
                box-shadow: 0 4px 10px rgba(0,0,0,0.15);
            ">
                <div style="text-align: center; margin-bottom: 15px; border-bottom: 2px solid #eee; padding-bottom: 10px;">
                    <h2 style="margin: 0; font-size: 18px; color: #444; text-transform: uppercase;">
                        TALDEA ${taldeId} </h2>
                    <h1 style="margin: 0; font-size: 22px; color: #D32F2F; font-weight: 800; letter-spacing: 1px;">
                        POKETOP
                    </h1>
                </div>

                <div style="display: flex; align-items: center; justify-content: center; gap: 20px;">
                    <div style="flex: 1; text-align: center; display: flex; flex-direction: column; align-items: center;">
                        <img src="${irudiaUrl}" alt="${pokemon.Izena}" style="
                            width: 120px; 
                            height: 120px; 
                            object-fit: contain; 
                            filter: drop-shadow(4px 4px 5px rgba(0,0,0,0.3));
                        ">
                        <div style="margin-top: 10px; font-size: 22px; font-weight: 900; color: #D32F2F; text-transform: uppercase;">
                            ${pokemon.Izena}
                        </div>
                    </div>

                    <div style="flex: 0 0 160px; display: flex; flex-direction: column; gap: 6px; font-size: 15px;">
                        <div style="display: flex; align-items: center; justify-content: space-between;">
                            <div><span>❤️</span> <b>HP</b></div> <b style="font-size:16px;">${hp}</b>
                        </div>
                        <div style="display: flex; align-items: center; justify-content: space-between;">
                            <div><span>⚔️</span> <b>Atk</b></div> <b style="font-size:16px;">${atk}</b>
                        </div>
                        <div style="display: flex; align-items: center; justify-content: space-between;">
                            <div><span>🛡️</span> <b>Def</b></div> <b style="font-size:16px;">${def}</b>
                        </div>
                        <div style="display: flex; align-items: center; justify-content: space-between;">
                            <div><span>🔮</span> <b>Atk.Ber</b></div> <b style="font-size:16px;">${spa}</b>
                        </div>
                        <div style="display: flex; align-items: center; justify-content: space-between;">
                            <div><span>🔰</span> <b>Def.Ber</b></div> <b style="font-size:16px;">${spd}</b>
                        </div>
                        <div style="display: flex; align-items: center; justify-content: space-between;">
                            <div><span>💨</span> <b>Abd</b></div> <b style="font-size:16px;">${spe}</b>
                        </div>
                    </div>
                </div>
            </div>
        `;
    } catch (error) {
        console.error(error);
        divResultado.innerHTML = "<p style='text-align:center; color:red;'>Errorea datuak lortzean.</p>";
    }
}

// 3. MOTA INFORMAZIOA KARGATU (POKEMOTA)
async function cargarPokeMotaInfo(izena) {
    const divRes = document.getElementById('tool-result') || document.getElementById('mota-result');

    if (!divRes) {
        console.error("Ez da aurkitu emaitzak erakusteko edukiontzia");
        return;
    }
    divRes.innerHTML = "Kalkulatzen...";

    try {
        const res = await fetch(`/api/espezieak/${izena}/info`);
        if (!res.ok) throw new Error("Errorea");
        const data = await res.json();

        const getPillColor = (mult) => {
            if (mult === 4) return '#ff4444';
            if (mult === 2) return '#ffaa00';
            if (mult === 1) return '#ffee00';
            if (mult === 0.5) return '#3399ff';
            if (mult === 0.25) return '#44cc44';
            if (mult === 0) return '#333333';
            return '#ccc';
        };

        const getPillText = (mult) => {
            if (mult === 0.5) return '1/2';
            if (mult === 0.25) return '1/4';
            return 'x' + mult;
        };

        const TYPE_ICONS = {
            'normal': '⚪', 'fire': '🔥', 'water': '💧', 'grass': '🍃',
            'electric': '⚡', 'ice': '❄️', 'fighting': '👊', 'poison': '☠️',
            'ground': '🏜️', 'flying': '🕊️', 'psychic': '🔮', 'bug': '🐞',
            'rock': '🪨', 'ghost': '👻', 'dragon': '🐉', 'dark': '🌑',
            'steel': '🔩', 'fairy': '✨'
        };

        const renderRow = (list) => {
            if (!list || list.length === 0) return '<div style="opacity:0.6; font-size:12px;">Ez dauka</div>';
            const grouped = {};
            list.forEach(item => {
                if (!grouped[item.Biderkatzailea]) grouped[item.Biderkatzailea] = [];
                grouped[item.Biderkatzailea].push(item);
            });

            let html = '<div style="display:flex; flex-direction:column; gap:8px;">';
            for (const mult in grouped) {
                const items = grouped[mult];
                const color = getPillColor(parseFloat(mult));
                const text = getPillText(parseFloat(mult));
                let rowHtml = `
                    <div style="display:flex; align-items:center; background:rgba(255,255,255,0.5); border-radius:15px; padding:4px 12px;">
                        <span style="background:${color}; color:white; padding:3px 8px; border-radius:10px; font-weight:bold; font-size:12px; margin-right:12px; min-width:35px; text-align:center; border: 1px solid rgba(0,0,0,0.2);">
                            ${text}
                        </span>
                        <div style="display:flex; gap:8px;">`;
                items.forEach(typeObj => {
                    const icon = TYPE_ICONS[typeObj.TypeKey] || '❓';
                    rowHtml += `<span title="${typeObj.Mota}" style="font-size:18px; cursor:help;">${icon}</span>`;
                });
                rowHtml += `</div></div>`;
                html += rowHtml;
            }
            html += '</div>';
            return html;
        };

        const irudiaUrl = data.Espezie.startsWith('http') ? data.Espezie : `/static/sprites/pokemon/${data.Espezie.split('/').pop()}`;

        divRes.innerHTML = `
            <div style="
                margin: 20px auto; 
                background: #ccffcc; 
                border: 6px solid #4dad5b; 
                border-radius: 20px; 
                padding: 30px; 
                display:flex; 
                gap: 40px; 
                align-items: center; 
                max-width: 800px;
                box-shadow: 8px 8px 0 rgba(0,0,0,0.2); 
                font-family: 'Press Start 2P', cursive;
            ">
                <div style="text-align:center; min-width: 200px;"> 
                    <img src="${irudiaUrl}" style="width:180px; height:180px; object-fit:contain; filter: drop-shadow(5px 5px 0px rgba(0,0,0,0.2)); image-rendering: pixelated;">
                    <h3 style="margin: 20px 0 0 0; color: #1a4422; font-size: 18px; text-transform: uppercase; letter-spacing: 2px;">
                        ${data.Izena}
                    </h3>
                </div>
                <div style="flex-grow:1; display:flex; flex-direction:column; gap:25px;">
                    <div><h4 style="margin:0 0 15px 0; color: #1a4422; font-size: 14px; text-transform: uppercase; border-bottom: 2px solid #4dad5b; padding-bottom: 5px;">AHULEZIAK:</h4>${renderRow(data.Ahuleziak)}</div>
                    <div><h4 style="margin:0 0 15px 0; color: #1a4422; font-size: 14px; text-transform: uppercase; border-bottom: 2px solid #4dad5b; padding-bottom: 5px;">INDARRAK:</h4>${renderRow(data.Indarrak)}</div>
                </div>
            </div>
        `;
    } catch (e) {
        console.error(e);
        divRes.innerHTML = `<p style="color:red; font-size:10px;">Errorea datuak lortzean.</p>`;
    }
}

// 4. POKEEBO (Eboluzioa) - PIXEL ART ESTILOA
async function cargarPokeEboInfo(izena) {
    const divRes = document.getElementById('tool-result');
    divRes.innerHTML = "<p style='text-align:center; font-family:\"Press Start 2P\"; font-size:10px;'>Kargatzen...</p>";

    try {
        const res = await fetch(`/api/espezieak/${izena}/ebo`);
        const familia = await res.json();

        divRes.innerHTML = "";
        const contenedor = document.createElement('div');
        // Estilo retroa GBA motakoa
        Object.assign(contenedor.style, {
            display: "flex", alignItems: "center", justifyContent: "center", gap: "25px", padding: "30px",
            background: "#fef9c3", border: "4px solid #facc15", borderRadius: "15px"
        });

        familia.forEach((p, index) => {
            const esSeleccionado = p.izena.toLowerCase() === izena.toLowerCase();
            contenedor.innerHTML += `
                <div style="text-align:center;">
                    <img src="${lortuIrudiaUrl(p.irudia)}" style="width:110px; height:110px; image-rendering:pixelated;">
                    <div style="font-family:'Press Start 2P'; font-size:11px; margin-top:10px; color:${esSeleccionado ? '#dc2626' : '#713f12'}; text-transform:uppercase;">
                        ${p.izena}
                    </div>
                </div>
            `;
            if (index < familia.length - 1) {
                contenedor.innerHTML += `<div style="font-size:30px; color:#facc15;">➔</div>`;
            }
        });
        divRes.appendChild(contenedor);
    } catch (e) {
        divRes.innerHTML = "<p>Errorea.</p>";
    }
}

// 5. POKESCAN (Estatistkak) - PIXEL ART ESTILOA
async function cargarPokeScanInfo(izena) {
    const divRes = document.getElementById('tool-result');
    divRes.innerHTML = '<p style="text-align:center; font-family:\'Press Start 2P\'; margin-top:50px;">Eskaneatzen...</p>';

    try {
        const res = await fetch(`/api/espezieak/${izena}/scan`);
        const data = await res.json();
        const stats = data.Stats;
        const maxStat = 255; // Valor máximo para calcular el porcentaje de las barras

        // Función para dibujar las barras con más espacio y visibilidad
        const drawBar = (val, color) => {
            const pct = (val / maxStat) * 100;
            return `
                <div style="width: 120px; background: #eee; height: 16px; border: 2px solid #333; margin-left: 15px; position: relative; box-shadow: inset 2px 2px 0 rgba(0,0,0,0.1);">
                    <div style="width: ${pct}%; background: ${color}; height: 100%; border-right: 2px solid rgba(0,0,0,0.2);"></div>
                </div>`;
        };

        const TYPE_ICONS = {
            'Altzairua': '⚙️', 'Belarra': '🌿', 'Intsektua': '🐞', 'Izotza': '❄️',
            'Maitagarria': '✨', 'Sua': '🔥', 'Ura': '💧', 'Normala': '🔘',
            'Elektrikoa': '⚡', 'Borroka': '🥊', 'Pozoia': '🧪', 'Lurra': '⛰️',
            'Hegaldia': '🕊️', 'Psikikoa': '🔮', 'Harria': '💎', 'Mamua': '👻',
            'Dragoia': '🐲', 'Iluna': '🌑'
        };

        let iconosFortalezas = data.Efectividad.Indarrak.map(f =>
            `<span title="${f.Mota}" style="font-size: 24px; margin: 0 6px;">${TYPE_ICONS[f.Mota] || '❓'}</span>`
        ).join('');

        const imgUrl = data.Irudia.startsWith('http') ? data.Irudia : `/static/sprites/pokemon/${data.Irudia.split('/').pop()}`;

        divRes.innerHTML = `
            <div style="
                margin: 20px auto; 
                background: #cce5ff; 
                border: 6px solid #2663ac; 
                border-radius: 20px; 
                padding: 35px; 
                max-width: 900px;
                box-shadow: 10px 10px 0 rgba(0,0,0,0.2);
                font-family: 'Press Start 2P', cursive; 
                color: #333;
            ">
                <div style="display: flex; gap: 40px; align-items: center; justify-content: space-evenly; margin-bottom: 35px; flex-wrap: wrap;">
                    
                    <div style="text-align: center; flex: 1; min-width: 250px;">
                        <img src="${imgUrl}" style="width: 220px; height: 220px; image-rendering: pixelated; filter: drop-shadow(6px 6px 0px rgba(0,0,0,0.1));">
                        <div style="font-size: 20px; margin-top: 20px; text-transform: uppercase; color: #1b4a7a; letter-spacing: 2px;">
                            ${data.Izena}
                        </div>
                        <div style="font-size: 10px; color: #1b4a7a; margin-top: 15px; background: rgba(255,255,255,0.6); padding: 8px; border-radius: 8px; border: 2px solid #fff; display: inline-block;">
                            BATEZ BESTEKO: ${data.Media}
                        </div>
                    </div>
                    
                    <div style="
                        background: #fff; 
                        border: 4px solid #1b4a7a; 
                        border-radius: 15px; 
                        padding: 25px; 
                        box-shadow: 6px 6px 0px rgba(0,0,0,0.1);
                        flex: 1;
                        min-width: 320px;
                    ">
                        <div style="text-align: center; font-size: 14px; margin-bottom: 20px; border-bottom: 3px solid #cce5ff; padding-bottom: 10px; color: #1b4a7a; letter-spacing: 1px;">
                            BASE STATS
                        </div>
                        
                        <div style="display: flex; flex-direction: column; gap: 12px;">
                            <div style="display: flex; align-items: center; font-size: 11px;">
                                <span style="width: 60px; font-weight: bold; color: #444;">HP</span> 
                                <span style="width: 45px; text-align: right; color: #d32f2f;">${stats.Osasuna}</span> 
                                ${drawBar(stats.Osasuna, '#ff4444')}
                            </div>
                            <div style="display: flex; align-items: center; font-size: 11px;">
                                <span style="width: 60px; font-weight: bold; color: #444;">ATK</span> 
                                <span style="width: 45px; text-align: right; color: #ef6c00;">${stats.Atakea}</span> 
                                ${drawBar(stats.Atakea, '#ffaa00')}
                            </div>
                            <div style="display: flex; align-items: center; font-size: 11px;">
                                <span style="width: 60px; font-weight: bold; color: #444;">DEF</span> 
                                <span style="width: 45px; text-align: right; color: #f9a825;">${stats.Defentsa}</span> 
                                ${drawBar(stats.Defentsa, '#eed535')}
                            </div>
                            <div style="display: flex; align-items: center; font-size: 11px;">
                                <span style="width: 60px; font-weight: bold; color: #444;">SPA</span> 
                                <span style="width: 45px; text-align: right; color: #1565c0;">${stats.AtakeBerezia}</span> 
                                ${drawBar(stats.AtakeBerezia, '#3399ff')}
                            </div>
                            <div style="display: flex; align-items: center; font-size: 11px;">
                                <span style="width: 60px; font-weight: bold; color: #444;">SPD</span> 
                                <span style="width: 45px; text-align: right; color: #2e7d32;">${stats.DefentsaBerezia}</span> 
                                ${drawBar(stats.DefentsaBerezia, '#44cc44')}
                            </div>
                            <div style="display: flex; align-items: center; font-size: 11px;">
                                <span style="width: 60px; font-weight: bold; color: #444;">SPE</span> 
                                <span style="width: 45px; text-align: right; color: #c2185b;">${stats.Abiadura}</span> 
                                ${drawBar(stats.Abiadura, '#ff66cc')}
                            </div>
                        </div>
                    </div>
                </div>

                <div style="text-align: center; border-top: 3px solid rgba(27, 74, 122, 0.2); padding-top: 25px;">
                    <div style="font-size: 14px; color: #1b4a7a; margin-bottom: 15px; letter-spacing: 2px; text-transform: uppercase;">
                        INDARGUNEAK:
                    </div>
                    <div style="display: inline-flex; align-items: center; background: rgba(255,255,255,0.7); padding: 12px 30px; border-radius: 40px; border: 3px solid #fff; box-shadow: 4px 4px 0px rgba(0,0,0,0.05);">
                        <div style="background: #2663ac; color: white; padding: 6px 14px; border-radius: 12px; font-size: 14px; margin-right: 20px; border: 2px solid rgba(0,0,0,0.1);">
                            1/2
                        </div>
                        <div style="display: flex; align-items: center; gap: 12px;">
                            ${iconosFortalezas || '<span style="font-size:10px; opacity:0.5;">Batere ez</span>'}
                        </div>
                    </div>
                </div>
            </div>`;

    } catch (e) {
        console.error(e);
        divRes.innerHTML = "<p style='text-align:center; color:red; font-family:\"Press Start 2P\"; font-size:10px;'>Errorea.</p>";
    }
}
// Esportazioak (Window objektuan jarri globalki eskuragarri izateko)
window.cargarPokeMotaInfo = cargarPokeMotaInfo;
window.cargarPokeEboInfo = cargarPokeEboInfo;
window.cargarPokeScanInfo = cargarPokeScanInfo;
window.cargarMVP = cargarMVP;