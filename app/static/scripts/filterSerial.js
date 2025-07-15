document.addEventListener('DOMContentLoaded', function () {
    const filterBtns = document.querySelectorAll('.filter-btn');
    const movieGrid = document.getElementById('movieGrid');
    const paginationContainer = document.getElementById('paginationContainer');
    let currentFilter = 'trending';
    let currentPage = 1;

    function fetchFilms(filter, page) {
        fetch(`/serial_data?filter=${filter}&page=${page}`)
            .then(response => response.json())
            .then(data => {
                renderMovieGrid(data.films);
                renderPagination(data.total, page);
            });
    }

    function renderMovieGrid(films) {
        movieGrid.innerHTML = '';
        if (!films.length) {
            movieGrid.innerHTML = '<p style="text-align:center;">Tidak ada film.</p>';
            return;
        }
        films.forEach(film => {
            let genresHtml = (film.genres_list || []).map(g => `<span class="genre">${g}</span>`).join('');
            movieGrid.innerHTML += `
                <a href="/watch?id=${film.id}" class="movie-card">
                    <img src="/static/covers/${film.gambar_portrait || 'No-Image_Availbale-Potrait.png'}" alt="${film.judul}" class="movie-poster">
                    <div class="movie-info">
                        <h3 class="movie-title">${film.judul}</h3>
                        <div class="movie-meta">
                            <span>${film.tahun_rilis}</span>
                            <span class="movie-rating"><i class="fas fa-star"></i> ${Number(film.rating).toFixed(1)}</span>
                        </div>
                        <div class="genres">
                            ${genresHtml}
                        </div>
                    </div>
                </a>`;
        });
    }

    function renderPagination(total, page) {
        const totalPages = Math.ceil(total / 18);
        let html = '';
        if (totalPages <= 1) { paginationContainer.innerHTML = ''; return; }
        if (page > 1) {
            html += `<button class="page-btn" data-page="${page - 1}"><i class="fas fa-chevron-left"></i></button>`;
        }
        for (let p = 1; p <= totalPages; p++) {
            html += `<button class="page-btn${p === page ? ' active' : ''}" data-page="${p}">${p}</button>`;
        }
        if (page < totalPages) {
            html += `<button class="page-btn" data-page="${page + 1}"><i class="fas fa-chevron-right"></i></button>`;
        }
        paginationContainer.innerHTML = html;

        // Add event listeners for pagination
        document.querySelectorAll('.page-btn').forEach(btn => {
            btn.onclick = function () {
                let goPage = Number(btn.getAttribute('data-page'));
                if (goPage !== page) {
                    currentPage = goPage;
                    fetchFilms(currentFilter, currentPage);
                    window.scrollTo(0, 0);
                }
            }
        });
    }

    // Filter button events
    filterBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentFilter = btn.id === 'trendingBtn' ? 'trending' : btn.id === 'newBtn' ? 'new' : 'recommended';
            currentPage = 1;
            fetchFilms(currentFilter, currentPage);
        });
    });

    // Initial fetch
    fetchFilms(currentFilter, currentPage);
});
