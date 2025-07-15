document.addEventListener('DOMContentLoaded', function() {
    const heroSlides = document.getElementById('heroSlides');
    const heroDots = document.querySelectorAll('.hero-dot');
    const prevSlideBtn = document.getElementById('prevSlide');
    const nextSlideBtn = document.getElementById('nextSlide');
    const heroSlider = document.querySelector('.hero-slider');
    let currentSlide = 0;
    const slideCount = document.querySelectorAll('.hero-slide').length;
    let slideInterval;

    function goToSlide(index) {
        if (index < 0) currentSlide = slideCount - 1;
        else if (index >= slideCount) currentSlide = 0;
        else currentSlide = index;

        if(heroSlides)
            heroSlides.style.transform = `translateX(-${currentSlide * 100}%)`;

        heroDots.forEach((dot, i) => {
            dot.classList.toggle('active', i === currentSlide);
        });
    }
    function nextSlide() { goToSlide(currentSlide + 1); }
    function prevSlide() { goToSlide(currentSlide - 1); }
    function initSlider() {
        if(heroSlides)
            heroSlides.style.transform = `translateX(0)`;
        slideInterval = setInterval(nextSlide, 5000);
    }

    if(prevSlideBtn) prevSlideBtn.addEventListener('click', prevSlide);
    if(nextSlideBtn) nextSlideBtn.addEventListener('click', nextSlide);
    heroDots.forEach(dot => {
        dot.addEventListener('click', () => {
            const index = parseInt(dot.getAttribute('data-index'));
            goToSlide(index);
        });
    });
    if(heroSlider) {
        heroSlider.addEventListener('mouseenter', () => clearInterval(slideInterval));
        heroSlider.addEventListener('mouseleave', () => slideInterval = setInterval(nextSlide, 5000));
    }
    initSlider();
});
