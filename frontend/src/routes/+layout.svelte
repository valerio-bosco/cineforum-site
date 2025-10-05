<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { api } from '$lib/api';
  import { browser } from '$app/environment';
  
  let user: any = null;
  let isMenuOpen = false;

  onMount(() => {
    if (browser) {
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        user = JSON.parse(storedUser);
      }
    }
  });

  function handleLogout() {
    api.logout();
    user = null;
  }

  function toggleMenu() {
    isMenuOpen = !isMenuOpen;
  }
</script>

<style>
  :global(body) {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    background: #141414;
    color: #fff;
  }

  :global(*) {
    box-sizing: border-box;
  }

  .layout {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  header {
    background: linear-gradient(180deg, #000 0%, transparent 100%);
    padding: 1rem 4%;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 1000;
    transition: background 0.3s ease;
  }

  header.scrolled {
    background: #141414;
  }

  nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    max-width: 1400px;
    margin: 0 auto;
  }

  .logo {
    font-size: 2rem;
    font-weight: 700;
    color: #e50914;
    text-decoration: none;
    letter-spacing: -1px;
  }

  .nav-links {
    display: flex;
    gap: 2rem;
    align-items: center;
  }

  .nav-links a {
    color: #e5e5e5;
    text-decoration: none;
    font-size: 0.95rem;
    transition: color 0.2s;
  }

  .nav-links a:hover {
    color: #fff;
  }

  .user-menu {
    position: relative;
  }

  .user-button {
    background: transparent;
    border: none;
    color: #fff;
    cursor: pointer;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    font-size: 0.95rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .user-button:hover {
    background: rgba(255, 255, 255, 0.1);
  }

  .dropdown {
    position: absolute;
    top: 100%;
    right: 0;
    background: #000;
    border: 1px solid #333;
    border-radius: 4px;
    padding: 0.5rem 0;
    min-width: 180px;
    margin-top: 0.5rem;
  }

  .dropdown button {
    width: 100%;
    background: transparent;
    border: none;
    color: #fff;
    padding: 0.75rem 1rem;
    text-align: left;
    cursor: pointer;
    font-size: 0.9rem;
  }

  .dropdown button:hover {
    background: rgba(255, 255, 255, 0.1);
  }

  main {
    flex: 1;
    margin-top: 70px;
    padding: 2rem 4%;
    max-width: 1400px;
    width: 100%;
    margin-left: auto;
    margin-right: auto;
  }

  @media (max-width: 768px) {
    .nav-links {
      display: none;
    }
  }
</style>

<div class="layout">
  <header>
    <nav>
      <a href="/" class="logo">CINEFORUM</a>
      
      {#if user}
        <div class="nav-links">
          <a href="/dashboard">Dashboard</a>
          <a href="/groups">Groups</a>
          <a href="/films">Films</a>
          
          <div class="user-menu">
            <button class="user-button" on:click={toggleMenu}>
              {user.username}
              <span>▼</span>
            </button>
            
            {#if isMenuOpen}
              <div class="dropdown">
                <button on:click={handleLogout}>Logout</button>
              </div>
            {/if}
          </div>
        </div>
      {:else}
        <div class="nav-links">
          <a href="/login">Login</a>
          <a href="/register">Register</a>
        </div>
      {/if}
    </nav>
  </header>

  <main>
    <slot />
  </main>
</div>