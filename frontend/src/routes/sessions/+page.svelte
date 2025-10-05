<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { api } from '$lib/api';
  import type { CineforumSession } from '$lib/types';
  
  let sessions: CineforumSession[] = [];
  let loading = true;

  onMount(async () => {
    await loadSessions();
  });

  async function loadSessions() {
    try {
      const response = await api.getSessions();
      sessions = response.data.results || response.data;
    } catch (error) {
      console.error('Failed to load sessions:', error);
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

  h1 {
    font-size: 2.5rem;
    font-weight: 600;
    margin-bottom: 2rem;
  }

  .sessions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 2rem;
  }

  .session-card {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    overflow: hidden;
    transition: all 0.3s ease;
    cursor: pointer;
    border: 1px solid transparent;
  }

  .session-card:hover {
    background: rgba(255, 255, 255, 0.1);
    border-color: #e50914;
    transform: translateY(-4px);
  }

  .session-poster {
    width: 100%;
    aspect-ratio: 2/3;
    object-fit: cover;
  }

  .session-info {
    padding: 1.5rem;
  }

  .session-title {
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    line-height: 1.4;
  }

  .session-meta {
    color: #b3b3b3;
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
  }

  .session-group {
    display: inline-block;
    background: rgba(229, 9, 20, 0.2);
    color: #e50914;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-top: 0.5rem;
  }

  .participants-count {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: 0.75rem;
    color: #b3b3b3;
    font-size: 0.9rem;
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

  .empty-state a {
    color: #e50914;
    text-decoration: none;
  }

  .empty-state a:hover {
    text-decoration: underline;
  }
</style>

<div class="container">
  <h1>Cineforum Sessions</h1>

  {#if loading}
    <div class="loading">Loading sessions...</div>
  {:else if sessions.length === 0}
    <div class="empty-state">
      <h2>No Sessions Yet</h2>
      <p>Join a group and start proposing films to create your first session!</p>
      <p><a href="/groups">Browse Groups →</a></p>
    </div>
  {:else}
    <div class="sessions-grid">
      {#each sessions as session}
        <div class="session-card" on:click={() => goto(`/sessions/${session.id}`)}>
          <img 
            src={getImageUrl(session.film.poster_path)} 
            alt={session.film.title}
            class="session-poster"
          />
          <div class="session-info">
            <div class="session-title">{session.film.title}</div>
            <div class="session-meta">
              {new Date(session.selected_at).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              })}
            </div>
            <div class="session-group">{session.group.name}</div>
            <div class="participants-count">
              👥 {session.participants_count} participants
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>