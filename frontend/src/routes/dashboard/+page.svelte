<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { api } from '$lib/api';
  import type { Group, CineforumSession } from '$lib/types';
  
  let groups: Group[] = [];
  let recentSessions: CineforumSession[] = [];
  let loading = true;

  onMount(async () => {
    try {
      const [groupsRes, sessionsRes] = await Promise.all([
        api.getGroups(),
        api.getSessions()
      ]);
      
      groups = groupsRes.data.results || groupsRes.data;
      recentSessions = sessionsRes.data.results || sessionsRes.data;
      recentSessions = recentSessions.slice(0, 6);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      loading = false;
    }
  });

  function getImageUrl(path: string) {
    return path ? `https://image.tmdb.org/t/p/w500${path}` : '/placeholder.jpg';
  }
</script>

<style>
  .dashboard {
    padding: 2rem 0;
  }

  h1 {
    font-size: 2.5rem;
    margin-bottom: 2rem;
    font-weight: 600;
  }

  h2 {
    font-size: 1.5rem;
    margin: 3rem 0 1.5rem;
    font-weight: 600;
  }

  .section {
    margin-bottom: 3rem;
  }

  .groups-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
  }

  .group-card {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    padding: 1.5rem;
    cursor: pointer;
    transition: all 0.3s ease;
    border: 1px solid transparent;
  }

  .group-card:hover {
    background: rgba(255, 255, 255, 0.1);
    border-color: #e50914;
    transform: translateY(-4px);
  }

  .group-name {
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
  }

  .group-info {
    color: #b3b3b3;
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
  }

  .group-status {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.8rem;
    margin-top: 0.5rem;
  }

  .status-active {
    background: #46d369;
    color: #000;
  }

  .status-inactive {
    background: rgba(255, 255, 255, 0.1);
    color: #b3b3b3;
  }

  .sessions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
  }

  .session-card {
    position: relative;
    border-radius: 8px;
    overflow: hidden;
    cursor: pointer;
    transition: transform 0.3s ease;
  }

  .session-card:hover {
    transform: scale(1.05);
  }

  .session-poster {
    width: 100%;
    aspect-ratio: 2/3;
    object-fit: cover;
  }

  .session-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(180deg, transparent 0%, #000 100%);
    padding: 1rem;
  }

  .session-title {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 0.25rem;
  }

  .session-date {
    font-size: 0.8rem;
    color: #b3b3b3;
  }

  .empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: #b3b3b3;
  }

  .empty-state h3 {
    font-size: 1.5rem;
    margin-bottom: 1rem;
    color: #fff;
  }

  .cta-button {
    display: inline-block;
    padding: 0.75rem 2rem;
    background: #e50914;
    color: #fff;
    text-decoration: none;
    border-radius: 4px;
    margin-top: 1rem;
    font-weight: 600;
    transition: background 0.2s;
  }

  .cta-button:hover {
    background: #f40612;
  }

  .loading {
    text-align: center;
    padding: 4rem;
    color: #b3b3b3;
  }
</style>

{#if loading}
  <div class="loading">Loading...</div>
{:else}
  <div class="dashboard">
    <h1>Welcome to Cineforum</h1>

    <div class="section">
      <h2>Your Groups</h2>
      
      {#if groups.length > 0}
        <div class="groups-grid">
          {#each groups as group}
            <div class="group-card" on:click={() => goto(`/groups/${group.id}`)}>
              <div class="group-name">{group.name}</div>
              <div class="group-info">{group.members_count} members</div>
              <div class="group-info">Admin: {group.administrator.username}</div>
              <span class="group-status" class:status-active={group.is_proposal_period_active} class:status-inactive={!group.is_proposal_period_active}>
                {group.is_proposal_period_active ? 'Proposals Open' : 'Inactive'}
              </span>
            </div>
          {/each}
        </div>
      {:else}
        <div class="empty-state">
          <h3>You're not in any groups yet</h3>
          <p>Create or join a group to start your cineforum journey!</p>
          <a href="/groups" class="cta-button">Explore Groups</a>
        </div>
      {/if}
    </div>

    <div class="section">
      <h2>Recent Sessions</h2>
      
      {#if recentSessions.length > 0}
        <div class="sessions-grid">
          {#each recentSessions as session}
            <div class="session-card" on:click={() => goto(`/sessions/${session.id}`)}>
              <img 
                src={getImageUrl(session.film.poster_path)} 
                alt={session.film.title}
                class="session-poster"
              />
              <div class="session-overlay">
                <div class="session-title">{session.film.title}</div>
                <div class="session-date">
                  {new Date(session.selected_at).toLocaleDateString()}
                </div>
              </div>
            </div>
          {/each}
        </div>
      {:else}
        <div class="empty-state">
          <p>No sessions yet. Start proposing films in your groups!</p>
        </div>
      {/if}
    </div>
  </div>
{/if}