const searchInput = document.getElementById('search-input');
const moviesList = document.getElementById('movies-list');
const actorsList = document.getElementById('actors-list');

let debounceTimer;

searchInput.addEventListener('input', (e) => {
    const query = e.target.value.trim();

    clearTimeout(debounceTimer);

    if (query.length < 2) {
        setStaticMessage(moviesList, 'Zadejte alespoň 2 znaky pro vyhledávání...');
        setStaticMessage(actorsList, 'Zadejte alespoň 2 znaky pro vyhledávání...');
        return;
    }

    debounceTimer = setTimeout(() => {
        executeSearch(query);
    }, 300);
});

function setStaticMessage(targetList, text, isError = false) {
    targetList.innerHTML = '';
    const li = document.createElement('li');
    li.className = 'status-msg';
    li.textContent = text;
    if (isError) {
        li.style.color = 'red';
    }
    targetList.appendChild(li);
}

function executeSearch(query) {
    setStaticMessage(moviesList, 'Vyhledávání...');
    setStaticMessage(actorsList, 'Vyhledávání...');

    fetch(`/api/search/?q=${encodeURIComponent(query)}`, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(response => response.json())
    .then(data => {
        const results = data.results;
        
        moviesList.innerHTML = ''; 
        if (results.movies.length === 0) {
            const noMoviesLi = document.createElement('li');
            noMoviesLi.textContent = 'Nenalezeny žádné filmy.';
            moviesList.appendChild(noMoviesLi);
        } else {
            results.movies.forEach(movie => {
                const li = document.createElement('li');
                const link = document.createElement('a');
                
                link.href = `/movie/${movie.id}/`;
                link.textContent = movie.cz_title;
                li.appendChild(link);

                if (movie.en_title) {
                    const small = document.createElement('small');
                    small.style.color = '#777';
                    small.textContent = ` (${movie.en_title})`;
                    li.appendChild(small);
                }

                moviesList.appendChild(li);
            });
        }

        actorsList.innerHTML = '';
        if (results.actors.length === 0) {
            const noActorsLi = document.createElement('li');
            noActorsLi.textContent = 'Nenalezeny žádní herci.';
            actorsList.appendChild(noActorsLi);
        } else {
            results.actors.forEach(actor => {
                const li = document.createElement('li');
                const link = document.createElement('a');

                link.href = `/actor/${actor.id}/`;
                link.textContent = actor.name;
                li.appendChild(link);

                actorsList.appendChild(li);
            });
        }
    })
    .catch(error => {
        console.error('Chyba:', error);
        setStaticMessage(moviesList, 'Chyba načítání dat.', true);
        setStaticMessage(actorsList, 'Chyba načítání dat.', true);
    });
}