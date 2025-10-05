<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { api } from '$lib/api';
  import type { Film } from '$lib/types';
  
  let films: Film[] = [];
  let loading = true;

  onMount(async () => {
    await loadFilms();
  });

  async function loadFilms() {
    try {
      const response = await api.getFilms();
      films = response.data.results || response.data;
    } catch (error) {
      console.error('Failed to load films:', error);
    } finally {
      loading = false;
    }
  }

  function getImageUrl(path: string) {
    return path ? `https://image.tmdb.org/t/p/w500${path}` : '/placeholder.jpg';
  }
</script>

<style>
  .container {
    max-width: 1400px;
    margin: 0 auto;
  }

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
  }

  h1 {
    font-size: 2.5rem;
    font-weight: 600;
  }

  .search-btn {
    padding: 0.75rem 2rem;
    background: #e50914;
    color: #fff;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
    transition: background 0.2s;
  }

  .search-btn:hover {
    background: #f40612;
  }

  .films-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 2rem;
  }

  .film-card {
    transition: transform 0.3s ease;
    cursor: pointer;
  }

  .film-card:hover {
    transform: scale(1.05);
  }

  .film-poster {
    width: 100%;
    aspect-ratio: 2/3;
    object-fit: cover;
    border-radius: 8px;
    margin-bottom: 1rem;
  }

  .film-title {
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    line-height: 1.4;
  }

  .film-meta {
    color: #b3b3b3;
    font-size: 0.9rem;
  }

  .film-rating {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    background: rgba(229, 9, 20, 0.2);
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.85rem;
    font-weight: 600;
    margin-top: 0.5rem;
  }

  .loading {
    text-align: center;
    padding: 4rem;
    color: #b3b3b3;
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
</style>

<div class="container">
  <div class="header">
    <h1>Films</h1>
    <a href="/films/search" class="search-btn">Search Films</a>
  </div>

  {#if loading}
    <div class="loading">Loading films...</div>
  {:else if films.length === 0}
    <div class="empty-state">
      <h2>No Films Yet</h2>
      <p>Films will appear here once they are proposed in your groups.</p>
      <p><a href="/films/search" style="color: #e50914;">Search and propose films →</a></p>
    </div>
  {:else}
    <div class="films-grid">
      {#each films as film}
        <div class="film-card">
          <img 
            src={getImageUrl(film.poster_path)} 
            alt={film.title}
            class="film-poster"
          />
          <div class="film-title">{film.title}</div>
          <div class="film-meta">
            {film.release_date ? new Date(film.release_date).getFullYear() : 'N/A'}
          </div>
          {#if film.vote_average > 0}
            <div class="film-rating">
              ⭐ {film.vote_average.toFixed(1)}
            </div>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</div>