document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('login-form');
  const btn = document.getElementById('login-button');
  const pokeball = document.querySelector('.pokeball');

  if (!form || !btn || !pokeball) return;

  const playAndSubmit = (e) => {
    // Avoid double submissions and let the animation play
    e.preventDefault();
    btn.disabled = true;

    // Trigger pokeball opening animation
    pokeball.classList.add('open');

    // Submit after the animation completes
    setTimeout(() => {
      form.submit();
    }, 700); // match CSS transition timing in auth.css
  };

  // Click on SARTU
  btn.addEventListener('click', playAndSubmit);

  // Enter key submits the form as well
  form.addEventListener('submit', playAndSubmit);
});
