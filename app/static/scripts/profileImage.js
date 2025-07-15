document.addEventListener('DOMContentLoaded', function() {
    // Klik tombol "Ganti Foto Profil" langsung buka file dialog
    const gantiAvatarBtn = document.querySelector('.change-avatar');
    const fileInput = document.getElementById('fotoProfil');
    const avatarPreview = document.getElementById('avatarPreview');
    if (gantiAvatarBtn && fileInput) {
        gantiAvatarBtn.addEventListener('click', function(e) {
            fileInput.click();
        });
    }
    // Preview gambar sebelum upload
    if (fileInput && avatarPreview) {
        fileInput.addEventListener('change', function() {
            const file = fileInput.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    avatarPreview.src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    }
});
