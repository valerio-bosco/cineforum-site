<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { api } from '$lib/api';
  import type { Group } from '$lib/types';
  
  let groups: Group[] = [];
  let allGroups: Group[] = [];
  let loading = true;
  let showCreateModal = false;
  let newGroupName = '';
  let newGroupDescription = '';
  let creating = false;
  let error = '';

  onMount(async () => {
    await loadGroups();
  });

  async function loadGroups() {
    try {
      const response = await api.getGroups();
      groups = response.data.results || response.data;
    } catch (err) {
      console.error('Failed to load groups:', err);
    } finally {
      loading = false;
    }
  }

  async function createGroup() {
    if (!newGroupName.trim()) {
      error = 'Group name is required';
      return;
    }

    creating = true;
    error = '';

    try {
      await api.createGroup(newGroupName, newGroupDescription);
      showCreateModal = false;
      newGroupName = '';
      newGroupDescription = '';
      await loadGroups();
    } catch (err: any) {
      error = err.response?.data?.error || 'Failed to create group';
    } finally {
      creating = false;
    }
  }

  async function joinGroup(groupId: number) {
    try {
      await api.joinGroup(groupId);
      await loadGroups();
    } catch (err: any) {
      alert(err.response?.data?.error || 'Failed to join group');
    }
  }
</script>

<style>
  .container {
    max-width: 1200px;
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

  .create-btn {
    padding: 0.75rem 2rem;
    background: #e50914;
    color: #fff;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
  }

  .create-btn:hover {
    background: #f40612;
  }

  .groups-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 2rem;
  }

  .group-card {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    padding: 2rem;
    transition: all 0.3s ease;
    border: 1px solid transparent;
    cursor: pointer;
  }

  .group-card:hover {
    background: rgba(255, 255, 255, 0.1);
    border-color: #e50914;
    transform: translateY(-4px);
  }

  .group-header {
    display: flex;
    justify-content: space-between;
    align-items: start;
    margin-bottom: 1rem;
  }

  .group-name {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
  }

  .group-description {
    color: #b3b3b3;
    margin-bottom: 1rem;
    line-height: 1.6;
  }

  .group-info {
    display: flex;
    gap: 1.5rem;
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }

  .info-item {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .info-label {
    font-size: 0.8rem;
    color: #808080;
    text-transform: uppercase;
  }

  .info-value {
    font-size: 1rem;
    font-weight: 600;
  }

  .status-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
  }

  .status-active {
    background: #46d369;
    color: #000;
  }

  .status-inactive {
    background: rgba(255, 255, 255, 0.1);
    color: #b3b3b3;
  }

  .status-pending {
    background: #e87c03;
    color: #fff;
  }

  .modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .modal-content {
    background: #181818;
    padding: 2rem;
    border-radius: 8px;
    max-width: 500px;
    width: 90%;
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
  }

  .modal-title {
    font-size: 1.5rem;
    font-weight: 600;
  }

  .close-btn {
    background: none;
    border: none;
    color: #fff;
    font-size: 1.5rem;
    cursor: pointer;
    padding: 0;
    width: 32px;
    height: 32px;
  }

  .form-group {
    margin-bottom: 1.5rem;
  }

  label {
    display: block;
    margin-bottom: 0.5rem;
    color: #b3b3b3;
    font-size: 0.9rem;
  }

  input,
  textarea {
    width: 100%;
    padding: 0.75rem;
    background: #333;
    border: none;
    border-radius: 4px;
    color: #fff;
    font-size: 1rem;
    font-family: inherit;
  }

  textarea {
    min-height: 100px;
    resize: vertical;
  }

  input:focus,
  textarea:focus {
    outline: 2px solid #e50914;
  }

  .error {
    background: #e87c03;
    color: #fff;
    padding: 0.75rem;
    border-radius: 4px;
    margin-bottom: 1rem;
    font-size: 0.9rem;
  }

  .modal-actions {
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
  }

  .btn {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-secondary {
    background: rgba(255, 255, 255, 0.1);
    color: #fff;
  }

  .btn-secondary:hover {
    background: rgba(255, 255, 255, 0.2);
  }

  .btn-primary {
    background: #e50914;
    color: #fff;
  }

  .btn-primary:hover:not(:disabled) {
    background: #f40612;
  }

  .btn-primary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
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
    <h1>Groups</h1>
    <button class="create-btn" on:click={() => showCreateModal = true}>
      Create Group
    </button>
  </div>

  {#if loading}
    <div class="loading">Loading groups...</div>
  {:else if groups.length === 0}
    <div class="empty-state">
      <h2>No Groups Yet</h2>
      <p>Create your first group to start your cineforum journey!</p>
    </div>
  {:else}
    <div class="groups-grid">
      {#each groups as group}
        <div class="group-card" on:click={() => goto(`/groups/${group.id}`)}>
          <div class="group-header">
            <div>
              <div class="group-name">{group.name}</div>
              <span 
                class="status-badge" 
                class:status-active={group.is_proposal_period_active}
                class:status-inactive={!group.is_proposal_period_active}
                class:status-pending={group.membership_status === 'pending'}
              >
                {#if group.membership_status === 'pending'}
                  Pending Approval
                {:else if group.is_proposal_period_active}
                  Proposals Open
                {:else}
                  Inactive
                {/if}
              </span>
            </div>
          </div>

          {#if group.description}
            <p class="group-description">{group.description}</p>
          {/if}

          <div class="group-info">
            <div class="info-item">
              <span class="info-label">Members</span>
              <span class="info-value">{group.members_count}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Admin</span>
              <span class="info-value">{group.administrator.username}</span>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

{#if showCreateModal}
  <div class="modal" on:click={() => showCreateModal = false}>
    <div class="modal-content" on:click|stopPropagation>
      <div class="modal-header">
        <h2 class="modal-title">Create New Group</h2>
        <button class="close-btn" on:click={() => showCreateModal = false}>×</button>
      </div>

      {#if error}
        <div class="error">{error}</div>
      {/if}

      <form on:submit|preventDefault={createGroup}>
        <div class="form-group">
          <label for="name">Group Name *</label>
          <input
            id="name"
            type="text"
            bind:value={newGroupName}
            placeholder="My Cineforum Group"
            required
          />
        </div>

        <div class="form-group">
          <label for="description">Description</label>
          <textarea
            id="description"
            bind:value={newGroupDescription}
            placeholder="Tell us about your group..."
          ></textarea>
        </div>

        <div class="modal-actions">
          <button 
            type="button" 
            class="btn btn-secondary" 
            on:click={() => showCreateModal = false}
          >
            Cancel
          </button>
          <button type="submit" class="btn btn-primary" disabled={creating}>
            {creating ? 'Creating...' : 'Create Group'}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}