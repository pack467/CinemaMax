document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.movie-rating').forEach(function(el) {
        // Cari angka setelah icon (misal "7.879" atau "10.0")
        let html = el.innerHTML;
        let match = html.match(/<i[^>]*><\/i>\s*([0-9.,]+)/);
        if (match) {
            let rating = parseFloat(match[1].replace(',', '.'));
            if (!isNaN(rating)) {
                let ratingStr = rating.toFixed(1);
                el.innerHTML = html.replace(match[1], ratingStr);
            }
        }
    });
    // Hero section (class hero-rating)
    document.querySelectorAll('.hero-rating').forEach(function(el) {
        let html = el.innerHTML;
        let match = html.match(/<i[^>]*><\/i>\s*([0-9.,]+)/);
        if (match) {
            let rating = parseFloat(match[1].replace(',', '.'));
            if (!isNaN(rating)) {
                let ratingStr = rating.toFixed(1);
                el.innerHTML = html.replace(match[1], ratingStr);
            }
        }
    });
});
