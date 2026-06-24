const searchInput = document.getElementById('search-input');
const moviesList = document.getElementById('movies-list');
const actorsList = document.getElementById('actors-list');

let debounceTimer;

searchInput.addEventListener('input', (e) => {
    const query = e.target.value.trim();

    clearTimeout(debounceTimer);

    if (query.length < 2) {
        moviesList.innerHTML = '<li class="status-msg">Zadejte alespoň 2 znaky pro vyhledávání...</li>';
        actorsList.innerHTML = '<li class="status-msg">Zadejte alespoň 2 znaky pro vyhledávání...</li>';
        return;
    }

    debounceTimer = setTimeout(() => {
        executeSearch(query);
    }, 300);
});

function executeSearch(query) {
    moviesList.innerHTML = '<li class="status-msg">Vyhledávání...</li>';
    actorsList.innerHTML = '<li class="status-msg">Vyhledávání...</li>';

    fetch(`/api/search/?q=${encodeURIComponent(query)}`, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(response => response.json())
    .then(data => {
        const results = data.results;
        
        if (results.movies.length === 0) {
            moviesList.innerHTML = '<li>Nenalezeny žádné filmy.</li>';
        } else {
            moviesList.innerHTML = results.movies.map(movie => `
                <li>
                    <a href="/movie/${movie.id}/">${movie.cz_title}</a> 
                    ${movie.en_title ? `<small style="color:#777;">(${movie.en_title})</small>` : ''}
                </li>
            `).join('');
        }

        if (results.actors.length === 0) {
            actorsList.innerHTML = '<li>Nenalezeny žádní herci.</li>';
        } else {
            actorsList.innerHTML = results.actors.map(actor => `
                <li>
                    <a href="/actor/${actor.id}/">${actor.name}</a>
                </li>
            `).join('');
        }
    })
    .catch(error => {
        console.error('Chyba:', error);
        moviesList.innerHTML = '<li class="status-msg" style="color:red;">Chyba načítání dat.</li>';
        actorsList.innerHTML = '<li class="status-msg" style="color:red;">Chyba načítání dat.</li>';
    });
}