const API_BASE_URL = 'http://localhost:5000/api';

console.log('🚀 Register.js kargatuta - API:', API_BASE_URL);

document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ DOM kargatuta');
    
    const registerForm = document.getElementById('register-form');
    const registerButton = document.getElementById('register-button');
    
    if (!registerForm) {
        console.error('❌ register-form ez da aurkitu');
        return;
    }
    if (!registerButton) {
        console.error('❌ register-button ez da aurkitu');
        return;
    }
    
    console.log('✅ Formulario y botón encontrados');

    registerForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        console.log('🎯 Formulario enviado');
        
        await handleRegistration();
    });

    // También por si el clic directo funciona mejor
    registerButton.addEventListener('click', async function(e) {
        e.preventDefault();
        console.log('🖱️ Botón pulsado directamente');
        
        await handleRegistration();
    });
});

async function handleRegistration() {
    console.log('🔍 HandleRegistration ejecutándose');
    
    const name = document.getElementById('name').value.trim();
    const surname = document.getElementById('surname').value.trim();
    const telegram = document.getElementById('telegram').value.trim() || null;
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    
    console.log('📝 Datos del formulario:', { username, password, confirmPassword });

    // Validaciones
    if (!name || !surname || !username || !password || !confirmPassword) {
        showError('Mesedez, bete eremu guztiak');
        return;
    }

    if (password !== confirmPassword) {
        showError('Pasahitzak ez datoz bat');
        return;
    }

    // Comprobar tmb que el nombre de usuario no este en uso
    //if (await isUsernameTaken(username)) {
    //    showError('Erabiltzaile izena dagoeneko erregistratuta dago');
    //    return;
    //}

    // Cambiar estado del botón
    const registerButton = document.getElementById('register-button');
    registerButton.disabled = true;
    registerButton.textContent = 'ERREGISTRATZEN...';

    try {
        console.log('🔗 Intentando conectar al backend...');
        
        const userData = {
            izena: name,
            abizena: surname,
            erabilIzena: username,
            pasahitza: password,
            telegramKontua: telegram || null
        };

        console.log('📤 Enviando datos:', userData);

        const response = await fetch(`${API_BASE_URL}/erabiltzaileak`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        });

        console.log('📨 Respuesta recibida - Status:', response.status);
        console.log('📨 Respuesta recibida - OK:', response.ok);

        if (!response.ok) {
            let errorMessage = 'Errorea erregistratzean';
            
            try {
                const errorData = await response.json();
                console.log('❌ Error data:', errorData);
                errorMessage = errorData.error || errorMessage;
            } catch (parseError) {
                console.error('❌ Error parseando respuesta:', parseError);
                errorMessage = `HTTP Error: ${response.status}`;
            }
            
            throw new Error(errorMessage);
        }

        const user = await response.json();
        console.log('✅ Éxito - Usuario creado:', user);
        
        showSuccess('Erregistroa arrakastatsua! Orain saioa hasi dezakezu.');
        
        // Limpiar formulario
        document.getElementById('register-form').reset();
        
        // Redirigir después de 2 segundos
        setTimeout(() => {
            window.location.href = 'login.html';
        }, 2000);

    } catch (error) {
        console.error('💥 Error completo:', error);
        console.error('💥 Error message:', error.message);
        console.error('💥 Error name:', error.name);
        
        showError(error.message || 'Errorea erregistratzean. Saiatu berriro.');
    } finally {
        // Restaurar botón
        registerButton.disabled = false;
        registerButton.textContent = 'ERREGISTRATU';
    }
}

function showError(message) {
    console.error('🛑 Mostrando error:', message);
    const errorElement = document.getElementById('error-message');
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    }
}

function showSuccess(message) {
    console.log('🎉 Mostrando éxito:', message);
    const successElement = document.getElementById('success-message');
    if (successElement) {
        successElement.textContent = message;
        successElement.style.display = 'block';
    }
}

//async function isUsernameTaken(username) {
//    try {
//        console.log('🔍 Comprobando si el nombre de usuario está en uso:', username);
//        const response = await fetch(`${API_BASE_URL}/erabiltzaileak/check-username?izena=${encodeURIComponent(username)}`);
//        const data = await response.json();
//
//        console.log('✅ Respuesta de verificación:', data);
//        return data.taken;
//    } catch (error) {
//        console.error('❌ Error comprobando nombre de usuario:', error);
//        return false; // Asumir que no está tomado en caso de error
//    }
//}