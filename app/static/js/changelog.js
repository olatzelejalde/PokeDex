window.addEventListener('load', function() {
        const kanpaia = document.getElementById('changelog-trigger');
        
        if (kanpaia) {
            kanpaia.onclick = function(e) {
                e.preventDefault(); 
                console.log("KLIK EGIN DA!"); // Honek esango digu botoiak funtzionatzen duen

                // 1) Ezkutatu artikulu guztiak (active klasea kendu)
                document.querySelectorAll('main article').forEach(art => {
                    art.classList.remove('active');
                });

                // 2) Bilatzaileak ezkutatu
                const bilatzaileaPokemon = document.getElementById('search-pokemon');
                const bilatzaileaLagunak = document.getElementById('search-lagunak');
                if (bilatzaileaPokemon) bilatzaileaPokemon.style.display = 'none';
                if (bilatzaileaLagunak) bilatzaileaLagunak.style.display = 'none';

                // 3) Erakutsi changelog atala
                const atala = document.getElementById('changelog-list');
                if (atala) atala.classList.add('active');

                // 4) Kendu menuko active klasea
                document.querySelectorAll('.menua a').forEach(a => a.classList.remove('active'));

                // 4. Eskatu datuak APIari
                fetch('/api/changelog')
                    .then(res => res.json())
                    .then(data => {
                        console.log("Datuak jaso dira:", data);
                        const container = document.getElementById("changelog-append-here");

    
                        if (container) {
                        // Datuak badaude, txartel zurietan erakutsi
                            container.innerHTML = data.map(d => `
                            <div class="notif-txartela">
                                <div class="notif-ikonoa">
                                    <svg viewBox="0 0 24 24" width="24" height="24">
                                        <path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.89 2 2 2zm6-6v-5c0-3.07-1.64-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.63 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z"></path>
                                    </svg>
                                </div>
                                <div class="notif-testua">
                                    <span class="notif-data"><strong>${d.data}</strong></span>
                                    <span class="notif-desk"><strong>${d.bertsioa}:</strong> ${d.deskribapena}</span>
                                </div>
                            </div>
        `).join('');
    }
})
        .catch(err => {
    console.error('Errorea:', err);
    const container = document.getElementById("changelog-append-here");
    if (container) {
        container.innerHTML = `<p style="color: red; font-family: 'Press Start 2P'; font-size: 10px;">
            ERROREA: Ezin izan dira notifikazioak kargatu.</p>`;
    }
});
            };
        }
    });
    function filtratuNotifikazioak() {
    const testua = document.getElementById('filter-text').value.toLowerCase();
    const mota = document.getElementById('filter-type').value;
    const data = document.getElementById('filter-date').value;

    const notifikazioak = document.querySelectorAll('.notif-txartela');

    notifikazioak.forEach(notifikazio => {
        const desk = notifikazio.querySelector('.notif-desk')?.innerText.toLowerCase() || '';
        const dataText = notifikazio.querySelector('.notif-data')?.innerText || '';

        const motaText = desk.toUpperCase(); // POKEMON / TALDEA barruan doa

        const testuaLortua = desk.includes(testua);
        const motaLortua = mota === "" || motaText.includes(mota);
        const dataLortua = data === "" || dataText.includes(data);

        notifikazio.style.display =
            testuaLortua && motaLortua && dataLortua ? 'flex' : 'none';
    });
}
// Este código "vigila" los clics en el menú para cerrar el changelog
document.addEventListener('click', function(e) {
    if (e.target.closest('.menua a')) {
        const changelog = document.getElementById('changelog-list');
        const searchBar = document.getElementById('search-pokemon');
        
        if (changelog) {
            changelog.classList.remove('active');
        }
        
        // Si vuelves a Pokémon, asegúrate de que el buscador aparezca
        if (e.target.getAttribute('data-section') === 'pokemon') {
            if (searchBar) searchBar.style.display = 'flex';
        }
    }
});
const btnTaldeaGorde = document.getElementById('btn-taldea-gorde');
if (btnTaldeaGorde) {
    btnTaldeaGorde.addEventListener('click', function() {
        const izenaEl = document.getElementById('taldea-izena');
        const izena = izenaEl ? izenaEl.value : '';
        if (izena) {
            // Enviamos la notificación a TU sistema de changelog
            const egilea = (typeof user !== 'undefined' && user && user.id) ? String(user.id) : 'system';
            fetch('/api/changelog', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    bertsioa: 'TALDEA',
                    deskribapena: `Talde berria sortu da: ${izena}`,
                    data: new Date().toISOString().split('T')[0],
                    egilea: egilea,
                })
            });
        }
    });
}