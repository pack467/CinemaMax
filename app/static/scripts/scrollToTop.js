document.addEventListener('DOMContentLoaded', function() {
    const scrollTop = document.getElementById('scrollTop');
    if (!scrollTop) return;
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300 || window.pageYOffset > 500) {
            scrollTop.classList.add('active');
        } else {
            scrollTop.classList.remove('active');
        }
    });
    scrollTop.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
});
