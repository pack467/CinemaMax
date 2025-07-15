document.addEventListener('DOMContentLoaded', function() {
    const userProfile = document.getElementById('userProfile');
    const profileDropdown = document.getElementById('profileDropdown');
    if (!userProfile || !profileDropdown) return;
    userProfile.addEventListener('click', function(e) {
        e.stopPropagation();
        profileDropdown.classList.toggle('active');
    });
    document.addEventListener('click', function(e) {
        if (!userProfile.contains(e.target)) {
            profileDropdown.classList.remove('active');
        }
    });
});
