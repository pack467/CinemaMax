document.addEventListener('DOMContentLoaded', function() {
    // Filter options (checkbox/radio)
    const filterOptions = document.querySelectorAll('.filter-option');
    filterOptions.forEach(option => {
        option.addEventListener('click', (e) => {
            if (e.target.tagName === 'INPUT') return;
            const input = option.querySelector('input');
            if (input) {
                if (input.type === 'checkbox') input.checked = !input.checked;
                else input.checked = true;
                input.dispatchEvent(new Event('change'));
            }
        });
    });
});
