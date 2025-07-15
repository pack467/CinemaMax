document.addEventListener('DOMContentLoaded', function() {
    function updateEmptyFavorites() {
        const movieGrid = document.querySelector('.movie-grid');
        const emptyFavorites = document.querySelector('.empty-favorites');
        const hasCards = movieGrid.querySelectorAll('.movie-card').length > 0;
        if (!hasCards) {
            movieGrid.style.display = "none";
            emptyFavorites.style.display = "block";
        } else {
            movieGrid.style.display = "grid";
            emptyFavorites.style.display = "none";
        }
    }

    // Jalankan saat load
    updateEmptyFavorites();

    // Event hapus favorite
    document.querySelectorAll('.remove-favorite').forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            const card = this.closest('.movie-card');
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            setTimeout(() => {
                card.remove();
                updateEmptyFavorites();
            }, 300);
        });
    });
});
