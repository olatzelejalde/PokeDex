document.addEventListener('DOMContentLoaded', () => {
    const loginButton = document.getElementById('login-button');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const pokeball = document.querySelector('.pokeball');
    
    // Hurrengo orrialdea
    const nextPageUrl = 'home.html'; 
    
    // Animazioaren iraupena
    const animationDuration = 500; 

    loginButton.addEventListener('click', () => {
        // inputak satu diren egiaztatu
        const username = usernameInput.value.trim();
        const password = passwordInput.value.trim();

        // inputak hutsik badaude
        if (username === "" || password === "") {
            alert("⚠️ Please enter both a username and a password.");
            return;
        }
        
        // inputak sartuta badaude
        loginButton.disabled = true;
        
        // open clasea gehitu pokeball elementuari
        pokeball.classList.add('open');
        
        // animazioa amaitzen denean hurrengo orrialdera pasatu
        setTimeout(() => {
            window.location.href = nextPageUrl; // Hurrengo orrialdera bideratu
        }, animationDuration);
    });
});