<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { api } from '$lib/api';
  import type { Group, GroupFilm } from '$lib/types';
  
  let group: Group | null = null;
  let proposedFilms: GroupFilm[] = [];
  let loading = true;
  let isAdmin = false;
  let selectedFilm: GroupFilm | null = null;

  $: groupId = parseInt($page.params.id);

  onMount(async () => {
    await loadGroupData();
  });

  async function loadGroupData() {
    try {
      const [groupRes, filmsRes] = await Promise.all([
        api.getGroup(groupId),
        api.getGroup(groupId).then(res => 
          fetch(`${import.meta.env.VITE_API_URL}/groups/${groupId}/proposed_films/`, {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
          }).then(r => r.json())
        )
      ]);
      
      group = groupRes.data;
      proposedFilms = filmsRes;
      
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      isAdmin = group.administrator.id === user.id;
    } catch (error) {
      console.error('Failed to load group:', error);
    } finally {
      loading = false;
    }
  }

  async function startProposalPeriod() {
    try {
      await api.startProposalPeriod(groupId);
      await loadGroupData();
    } catch (err: any) {
      alert(err.response?.data?.error || 'Failed to start proposal period');
    }
  }

  async function endProposalPeriod() {
    try {
      await api.endProposalPeriod(groupId);
      await loadGroupData();
    } catch (err: any) {
      alert(err.response?.data?.error || 'Failed to end proposal period');
    }
  }

  async function randomizeFilm() {
    try {
      const response = await api.randomizeFilm(groupId);
      selectedFilm = response.data.selected_film;
    } catch (err: any) {
      alert(err.response?.data?.error || 'Failed to randomize film');
    }
  }

  async function confirmSelection() {
    if (!selectedFilm) return;
    
    try {
      await api.confirmFilmSelection(groupId, selectedFilm.film.id);
      selectedFilm = null;
      await loadGroupData();
      alert('Session created successfully!');
    } catch (err: any) {
      alert(err.response?.data?.error || 'Failed to confirm selection');
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

  .group-header {
    margin-bottom: 3rem;
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
    margin-bottom: 0.5rem;
  }

  .group-meta {
    color: #b3b3b3;
    margin-bottom: 1rem;
  }

  .status-badge {
    display: inline-block;
    padding: 0.35rem 0.85rem;
    border-radius: 12px;
    font-size: 0.85rem;
    font-weight: 600;
    margin-left: 1rem;
  }

  .status-active {
    background: #46d369;
    color: #000;
  }

  .status-inactive {
    background: rgba(255, 255, 255, 0.1);
    color: #b3b3b3;
  }

  .admin-controls {
    display: flex;
    gap: 1rem;
    margin-top: 1.5rem;
  }

  .btn {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 4px;
    font-size: 0.95rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-primary {
    background: #e50914;
    color: #fff;
  }

  .btn-primary:hover {
    background: #f40612;
  }

  .btn-secondary {
    background: rgba(255, 255, 255, 0.1);
    color: #fff;
  }

  .btn-secondary:hover {
    background: rgba(255, 255, 255, 0.2);
  }

  .section {
    margin-bottom: 3rem;
  }

  h2 {
    font-size: 1.75rem;
    margin-bottom: 1.5rem;
    font-weight: 600;
  }

  .films-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 1.5rem;
  }

  .film-card {
    position: relative;
    border-radius: 8px;
    overflow: hidden;
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
  }

  .film-info {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(180deg, transparent 0%, #000 100%);
    padding: 1.5rem 1rem 1rem;
  }

  .film-title {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 0.25rem;
  }

  .film-meta {
    font-size: 0.8rem;
    color: #b3b3b3;
  }

  .priority-badge {
    position: absolute;
    top: 0.5rem;
    right: 0.5rem;
    background: rgba(0, 0, 0, 0.8);
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
  }

  .empty-state {
    text-align: center;
    padding: 4rem 2rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    color: #b3b3b3;
  }

  .empty-state h3 {
    font-size: 1.25rem;
    margin-bottom: 0.5rem;
    color: #fff;
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
  }

  .modal-content {
    background: #181818;
    padding: 2rem;
    border-radius: 8px;
    max-width: 600px;
    width: 90%;
    text-align: center;
  }

  .selected-film {
    margin: 2rem 0;
  }

  .selected-poster {
    width: 300px;
    max-width: 100%;
    border-radius: 8px;
    margin-bottom: 1rem;
  }

  .modal-actions {
    display: flex;
    gap: 1rem;
    justify-content: center;
  }

  .loading {
    text-align: center;
    padding: 4rem;
    color: #b3b3b3;
  }
</style>

{#if loading}
  <div class="loading">Loading...</div>
{:else if group}
  <div class="container">
    <div class="group-header">
      <a href="/groups" class="back-link">← Back to Groups</a>
      
      <h1>{group.name}</h1>
      
      <div class="group-meta">
        <span>Admin: {group.administrator.username}</span>
        <span> • </span>
        <span>{group.members_count} members</span>
        <span 
          class="status-badge"
          class:status-active={group.is_proposal_period_active}
          class:status-inactive={!group.is_proposal_period_active}
        >
          {group.is_proposal_period_active ? 'Proposals Open' : 'Inactive'}
        </span>
      </div>

      {#if group.description}
        <p style="color: #b3b3b3; margin-top: 1rem;">{group.description}</p>
      {/if}

      {#if isAdmin}
        <div class="admin-controls">
          {#if group.is_proposal_period_active}
            <button class="btn btn-secondary" on:click={endProposalPeriod}>
              End Proposal Period
            </button>
          {:else}
            <button class="btn btn-primary" on:click={startProposalPeriod}>
              Start Proposal Period
            </button>
            {#if proposedFilms.length > 0}
              <button class="btn btn-primary" on:click={randomizeFilm}>
                Randomize Film
              </button>
            {/if}
          {/if}
          <button class="btn btn-secondary" on:click={() => goto(`/films/search?group=${groupId}`)}>
            Propose Film
          </button>
        </div>
      {:else if group.is_proposal_period_active}
        <div class="admin-controls">
          <button class="btn btn-primary" on:click={() => goto(`/films/search?group=${groupId}`)}>
            Propose Film
          </button>
        </div>
      {/if}
    </div>

    <div class="section">
      <h2>Proposed Films ({proposedFilms.length})</h2>
      
      {#if proposedFilms.length === 0}
        <div class="empty-state">
          <h3>No films proposed yet</h3>
          <p>Start proposing films for the next cineforum session!</p>
        </div>
      {:else}
        <div class="films-grid">
          {#each proposedFilms as groupFilm}
            <div class="film-card">
              <img 
                src={getImageUrl(groupFilm.film.poster_path)} 
                alt={groupFilm.film.title}
                class="film-poster"
              />
              {#if groupFilm.priority_weight !== 1.0}
                <div class="priority-badge">
                  Priority: {groupFilm.priority_weight.toFixed(1)}x
                </div>
              {/if}
              <div class="film-info">
                <div class="film-title">{groupFilm.film.title}</div>
                <div class="film-meta">
                  Proposed by {groupFilm.proposed_by.username}
                </div>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  </div>
{/if}

{#if selectedFilm}
  <div class="modal" on:click={() => selectedFilm = null}>
    <div class="modal-content" on:click|stopPropagation>
      <h2>Film Selected!</h2>
      
      <div class="selected-film">
        <img 
          src={getImageUrl(selectedFilm.film.poster_path)} 
          alt={selectedFilm.film.title}
          class="selected-poster"
        />
        <h3>{selectedFilm.film.title}</h3>
        <p style="color: #b3b3b3;">
          Proposed by {selectedFilm.proposed_by.username}
        </p>
      </div>

      <p style="margin-bottom: 2rem;">
        Confirm this selection to create a cineforum session?
      </p>

      <div class="modal-actions">
        <button class="btn btn-secondary" on:click={() => selectedFilm = null}>
          Cancel
        </button>
        <button class="btn btn-primary" on:click={confirmSelection}>
          Confirm Selection
        </button>
      </div>
    </div>
  </div>
{/if}