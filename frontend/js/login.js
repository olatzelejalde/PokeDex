const API_BASE_URL = 'http://localhost:5000/api';

document.addEventListener('DOMContentLoaded', function()  {
    const loginForm = document.getElementById('login-form');
    const errorMessage = document.getElementById('error-message');

    const unekoErabiltzailea = localStorage.getItem('unekoErabiltzailea');
    if (unekoErabiltzailea) {
        window.location.href = 'index.html';
        return;
    }
    loginForm.addEventListener('submit', async function(event) {
        event.preventDefault();

        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;
        errorMessage.style.display = 'none';

        if (!username || !password) {
            errorMessage.textContent = 'Mesedez, bete eremu guztiak.';
            return;
        }

        const loginBtn = document.getElementById('login-button');
        loginBtn.disabled = true;
        loginBtn.textContent = 'Sartzen...';

        try {
            console.log('Saioa hasten: ', username);

            const response = await fetch(`${API_BASE_URL}/erabiltzaileak/saioa`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({izena: username, pasahitza: password }),
            });
            const datuak = await response.json();

            if (response.ok) {
                console.log('Saioa hasi da: ', datuak.izena);
                localStorage.setItem('unekoErabiltzailea', JSON.stringify(datuak));

                const pokeball = document.querySelector('.pokeball');
                pokeball.classList.add('open');

                setTimeout(() => {
                    window.location.href = 'index.html';
                }, 1500);
            } else {
                console.error('Saioa hasteko errorea: ', datuak);
                erakutsiErrorea(datuak.error || 'Errorea saioa hastean.');
            }
        } catch (error) {
            console.error('Sareko errorea: ', error);
            erakutsiErrorea('Sareko errorea gertatu da. Mesedez, saiatu berriro.');
        } finally {
            loginBtn.disabled = false;
            loginBtn.textContent = 'Sartu';
        }
    });

    function erakutsiErrorea(mezua) {
        errorMessage.textContent = mezua;
        errorMessage.style.display = 'block';
    }
});