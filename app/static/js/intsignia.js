async function renderIntsigniak(intsigniak) {
    // Intsigniak erakusteko grid-a eta kontadorea lortu
    const grid = document.getElementById('intsigniak-zerrenda');
    const kont = document.getElementById('intsigniak_kont');
    if (!grid || !kont) return; // Grid edo kontadorea ez badago, irten

    // Grid-a garbitu
    grid.innerHTML = '';
    let lortutakoIntsigniak = 0; // Lortutako intsignien kontadorea

    // Intsignia bakoitza iteratu
    intsigniak.forEach(ins => {
        // Intsigniaren txartela sortu
        const card = document.createElement('div');
        card.className = `intsignia-card ${ins.lortua ? 'obtained' : 'locked'}`;
        card.innerHTML = `
            <div class="icon-wrapper">
                <img src="/static/sprites/${ins.lortua ? 'berdea.png' : 'grisa.png'}"
                     alt="${ins.izena}">
            </div>
            <div class="intsignia-name">${ins.izena}</div>
        `;

        // Tooltip flotantea sortu
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = ins.deskripzioa;
        card.appendChild(tooltip);

        // Txartela grid-ean gehitu
        grid.appendChild(card);

        // Lortutako intsignien kopurua eguneratu
        if (ins.lortua) lortutakoIntsigniak++;

        // Lehen aldiz lortutako intsignia notifikatzeko
        if (ins.lortua && !ins.mezua) {
            const mezua = document.createElement('div');
            mezua.className = 'intsignia-mezua';
             mezua.innerHTML = `
            <p>Zorionak! <strong>"${ins.izena}"</strong> intsignia lortu duzu.</p>
            <button>Itxi</button>
        `;
        document.body.appendChild(mezua);

        // Itxi botoia funtzioa
        mezua.querySelector('button').addEventListener('click', () => mezua.remove());

        // Markatu jada notifikatu dela, ez ager dadin berriro
        ins.mezua = true;
    }

        // tooltip-a erakutsi eta ezkutatu
        card.addEventListener('mouseenter', () => {
            tooltip.style.visibility = 'visible';
            tooltip.style.opacity = '1';
        });
        card.addEventListener('mouseleave', () => {
            tooltip.style.visibility = 'hidden';
            tooltip.style.opacity = '0';
        });
    });

    // Kontadorea eguneratu
    kont.textContent =
        `Lortutako intsigniak: ${lortutakoIntsigniak} / ${intsigniak.length}`;
}
