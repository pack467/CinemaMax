document.addEventListener('DOMContentLoaded', function() {
    // TEST: Pastikan script aktif!
    console.log('login.js aktif!');

    // Form login/register DOM
    const forms = document.querySelectorAll('.auth-form');
    const loginTab = document.getElementById('login-tab');
    const registerTab = document.getElementById('register-tab');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');

    // Pindah form lewat link bawah
    document.querySelectorAll('.auth-switch a').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const tabId = link.getAttribute('data-tab');
            // Show/hide form
            forms.forEach(form => form.classList.remove('active'));
            document.getElementById(`${tabId}-form`).classList.add('active');
            // Highlight tab label di atas
            loginTab.classList.toggle('active', tabId === "login");
            registerTab.classList.toggle('active', tabId === "register");
        });
    });

    // Password show/hide toggle
    document.querySelectorAll('.password-toggle').forEach(toggle => {
        toggle.addEventListener('click', function() {
            const input = toggle.previousElementSibling;
            const icon = toggle.querySelector('i');
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    });

    // JANGAN ADA preventDefault pada submit! Biar submit ke backend Flask!
    // (Kecuali kamu mau AJAX/validasi front-end)

    // Contoh jika ingin validasi front-end password sama (tidak wajib)
    // document.getElementById('registerForm').addEventListener('submit', function(e) {
    //     const pw = registerForm.querySelector('input[name="password"]').value;
    //     const pw2 = registerForm.querySelector('input[name="password_confirm"]').value;
    //     if (pw !== pw2) {
    //         e.preventDefault();
    //         alert("Password tidak sama!");
    //     }
    // });

});
