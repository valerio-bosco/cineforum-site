<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { api } from '$lib/api';
  import type { TMDBMovie } from '$lib/types';
  
  let searchQuery = '';
  let searchResults: TMDBMovie[] = [];
  let searching = false;
  let selectedMovie: TMDBMovie | null = null;
  let proposing = false;

  $: groupId = $page.url.searchParams.get('group');

  async function searchFilms() {
    if (!searchQuery.trim()) return;

    searching = true;
    try {
      const response = await api.searchTMDB(searchQuery);
      searchResults = response.data.results || [];
    } catch (error) {
      console.error('Search failed:', error);
      searchResults = [];
    } finally {
      searching = false;
    }
  }

  async function proposeFilm(movie: TMDBMovie) {
    if (!groupId) {
      alert('No group selected');
      return;
    }

    proposing = true;
    try {
      await api.proposeFilm(movie.id, parseInt(groupId));
      alert('Film proposed successfully!');
      goto(`/groups/${groupId}`);
    } catch (err: any) {
      alert(err.response?.data?.error || 'Failed to propose film');
    } finally {
      proposing = false;
    }
  }

  function getImageUrl(path: string | null) {
    return path ? `https://image.tmdb.org/t/p/w500${path}` : '/placeholder.jpg';
  }

  function handleKeyPress(e: KeyboardEvent) {
    if (e.key === 'Enter') {
      searchFilms();
    }
  }
</script>

<style>
  .container {
    max-width: 1400px;
    margin: 0 auto;
  }

  .back-link {
    color: #b3b3b3;
    text-decoration: none;
    margin-bottom: 1rem;
    display: inline-block;
  }

  .back-link:hover {
    color: #fff;
  }

  h1 {
    font-size: 2.5rem;
    font-weight: 600;
    margin-bottom: 2rem;
  }

  .search-section {
    margin-bottom: 3rem;
  }

  .search-bar {
    display: flex;
    gap: 1rem;
    max-width: 600px;
  }

  input {
    flex: 1;
    padding: 1rem;
    background: #333;
    border: none;
    border-radius: 4px;
    color: #fff;
    font-size: 1rem;
  }

  input:focus {
    outline: 2px solid #e50914;
  }

  .search-btn {
    padding: 1rem 2rem;
    background: #e50914;
    border: none;
    border-radius: 4px;
    color: #fff;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
    white-space: nowrap;
  }

  .search-btn:hover:not(:disabled) {
    background: #f40612;
  }

  .search-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .results-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1.5rem;
  }

  .movie-card {
    position: relative;
    border-radius: 8px;
    overflow: hidden;
    transition: transform 0.3s ease;
    cursor: pointer;
    background: rgba(255, 255, 255, 0.05);
  }

  .movie-card:hover {
    transform: scale(1.05);
  }

  .movie-poster {
    width: 100%;
    aspect-ratio: 2/3;
    object-fit: cover;
  }

  .movie-info {
    padding: 1rem;
  }

  .movie-title {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    line-height: 1.4;
  }

  .movie-meta {
    font-size: 0.85rem;
    color: #b3b3b3;
    margin-bottom: 0.25rem;
  }

  .movie-rating {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    background: rgba(229, 9, 20, 0.2);
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.85rem;
    font-weight: 600;
  }

  .modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.9);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 2rem;
    overflow-y: auto;
  }

  .modal-content {
    background: #181818;
    border-radius: 8px;
    max-width: 800px;
    width: 100%;
    position: relative;
  }

  .modal-header {
    position: relative;
    height: 400px;
    overflow: hidden;
  }

  .backdrop {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .backdrop-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(180deg, transparent 0%, #181818 100%);
    padding: 2rem;
  }

  .close-btn {
    position: absolute;
    top: 1rem;
    right: 1rem;
    background: rgba(0, 0, 0, 0.8);
    border: none;
    color: #fff;
    font-size: 1.5rem;
    cursor: pointer;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .modal-body {
    padding: 2rem;
  }

  .modal-title {
    font-size: 2rem;
    font-weight: 600;
    margin-bottom: 1rem;
  }

  .modal-overview {
    color: #b3b3b3;
    line-height: 1.6;
    margin-bottom: 1.5rem;
  }

  .modal-meta {
    display: flex;
    gap: 2rem;
    margin-bottom: 2rem;
  }

  .meta-item {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .meta-label {
    font-size: 0.8rem;
    color: #808080;
    text-transform: uppercase;
  }

  .meta-value {
    font-size: 1rem;
    font-weight: 600;
  }

  .modal-actions {
    display: flex;
    gap: 1rem;
  }

  .btn {
    padding: 0.75rem 2rem;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-primary {
    background: #e50914;
    color: #fff;
    flex: 1;
  }

  .btn-primary:hover:not(:disabled) {
    background: #f40612;
  }

  .btn-primary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .btn-secondary {
    background: rgba(255, 255, 255, 0.1);
    color: #fff;
  }

  .btn-secondary:hover {
    background: rgba(255, 255, 255, 0.2);
  }

  .empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: #b3b3b3;
  }

  .empty-state h2 {
    font-size: 1.5rem;
    margin-bottom: 1rem;
    color: #fff;
  }

  .searching {
    text-align: center;
    padding: 4rem;
    color: #b3b3b3;
  }
</style>

<div class="container">
  {#if groupId}
    <a href="/groups/{groupId}" class="back-link">← Back to Group</a>
  {:else}
    <a href="/films" class="back-link">← Back to Films</a>
  {/if}

  <h1>Search Films</h1>

  <div class="search-section">
    <div class="search-bar">
      <input
        type="text"
        bind:value={searchQuery}
        on:keypress={handleKeyPress}
        placeholder="Search for a film..."
      />
      <button class="search-btn" on:click={searchFilms} disabled={searching}>
        {searching ? 'Searching...' : 'Search'}
      </button>
    </div>
  </div>

  {#if searching}
    <div class="searching">Searching...</div>
  {:else if searchResults.length > 0}
    <div class="results-grid">
      {#each searchResults as movie}
        <div class="movie-card" on:click={() => selectedMovie = movie}>
          <img 
            src={getImageUrl(movie.poster_path)} 
            alt={movie.title}
            class="movie-poster"
          />
          <div class="movie-info">
            <div class="movie-title">{movie.title}</div>
            <div class="movie-meta">
              {movie.release_date ? new Date(movie.release_date).getFullYear() : 'N/A'}
            </div>
            {#if movie.vote_average > 0}
              <div class="movie-rating">
                ⭐ {movie.vote_average.toFixed(1)}
              </div>
            {/if}
          </div>
        </div>
      {/each}
    </div>
  {:else if searchQuery}
    <div class="empty-state">
      <h2>No Results Found</h2>
      <p>Try searching with different keywords</p>
    </div>
  {:else}
    <div class="empty-state">
      <h2>Search for Films</h2>
      <p>Enter a film title to search The Movie Database</p>
    </div>
  {/if}
</div>

{#if selectedMovie}
  <div class="modal" on:click={() => selectedMovie = null}>
    <div class="modal-content" on:click|stopPropagation>
      <div class="modal-header">
        <img 
          src={getImageUrl(selectedMovie.backdrop_path || selectedMovie.poster_path)} 
          alt={selectedMovie.title}
          class="backdrop"
        />
        <div class="backdrop-overlay">
          <h2 class="modal-title">{selectedMovie.title}</h2>
        </div>
        <button class="close-btn" on:click={() => selectedMovie = null}>×</button>
      </div>

      <div class="modal-body">
        {#if selectedMovie.overview}
          <p class="modal-overview">{selectedMovie.overview}</p>
        {/if}

        <div class="modal-meta">
          <div class="meta-item">
            <span class="meta-label">Release Date</span>
            <span class="meta-value">
              {selectedMovie.release_date ? new Date(selectedMovie.release_date).toLocaleDateString() : 'N/A'}
            </span>
          </div>
          {#if selectedMovie.vote_average > 0}
            <div class="meta-item">
              <span class="meta-label">Rating</span>
              <span class="meta-value">⭐ {selectedMovie.vote_average.toFixed(1)}/10</span>
            </div>
          {/if}
          <div class="meta-item">
            <span class="meta-label">Votes</span>
            <span class="meta-value">{selectedMovie.vote_count.toLocaleString()}</span>
          </div>
        </div>

        <div class="modal-actions">
          {#if groupId}
            <button 
              class="btn btn-primary" 
              on:click={() => proposeFilm(selectedMovie)}
              disabled={proposing}
            >
              {proposing ? 'Proposing...' : 'Propose This Film'}
            </button>
          {/if}
          <button class="btn btn-secondary" on:click={() => selectedMovie = null}>
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
{/if}