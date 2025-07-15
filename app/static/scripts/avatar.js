document.addEventListener('DOMContentLoaded', function() {
    const avatarOverlay = document.querySelector('.avatar-overlay');
    const changeAvatar = document.querySelector('.change-avatar');
    if (avatarOverlay) avatarOverlay.addEventListener('click', () => {
        alert('Pilih foto baru untuk profil Anda');
    });
    if (changeAvatar) changeAvatar.addEventListener('click', () => {
        alert('Pilih foto baru untuk profil Anda');
    });
});
