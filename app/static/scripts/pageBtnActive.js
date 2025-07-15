document.addEventListener('DOMContentLoaded', function() {
    const pageBtns = document.querySelectorAll('.page-btn');
    pageBtns.forEach(btn => {
        if (!btn.querySelector('i')) { // Skip arrow buttons
            btn.addEventListener('click', () => {
                pageBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
        }
    });
});
