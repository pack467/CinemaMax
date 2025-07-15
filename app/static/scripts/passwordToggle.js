function setupPasswordToggle(inputId, toggleId) {
    const passwordInput = document.getElementById(inputId);
    const toggleButton = document.getElementById(toggleId);
    if (passwordInput && toggleButton) {
        toggleButton.addEventListener('click', () => {
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                toggleButton.innerHTML = '<i class="fas fa-eye-slash"></i>';
            } else {
                passwordInput.type = 'password';
                toggleButton.innerHTML = '<i class="fas fa-eye"></i>';
            }
        });
    }
}
document.addEventListener('DOMContentLoaded', function() {
    setupPasswordToggle('current-password', 'toggleCurrentPassword');
    setupPasswordToggle('new-password', 'toggleNewPassword');
    setupPasswordToggle('confirm-password', 'toggleConfirmPassword');
});
