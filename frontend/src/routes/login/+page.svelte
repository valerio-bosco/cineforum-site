<script lang="ts">
  import { goto } from '$app/navigation';
  import { api } from '$lib/api';
  
  let email = '';
  let password = '';
  let error = '';
  let loading = false;

  async function handleLogin() {
    error = '';
    loading = true;

    try {
      await api.login(email, password);
      goto('/dashboard');
    } catch (err: any) {
      error = err.response?.data?.error || 'Login failed. Please try again.';
    } finally {
      loading = false;
    }
  }
</script>

<style>
  .container {
    max-width: 450px;
    margin: 4rem auto;
    padding: 3rem;
    background: rgba(0, 0, 0, 0.75);
    border-radius: 8px;
  }

  h1 {
    font-size: 2rem;
    margin-bottom: 2rem;
    font-weight: 600;
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

  input {
    width: 100%;
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

  .error {
    background: #e87c03;
    color: #fff;
    padding: 1rem;
    border-radius: 4px;
    margin-bottom: 1rem;
    font-size: 0.9rem;
  }

  button {
    width: 100%;
    padding: 1rem;
    background: #e50914;
    border: none;
    border-radius: 4px;
    color: #fff;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
  }

  button:hover:not(:disabled) {
    background: #f40612;
  }

  button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .footer-text {
    margin-top: 1.5rem;
    color: #b3b3b3;
    font-size: 0.9rem;
  }

  .footer-text a {
    color: #fff;
    text-decoration: none;
  }

  .footer-text a:hover {
    text-decoration: underline;
  }
</style>

<div class="container">
  <h1>Sign In</h1>

  {#if error}
    <div class="error">{error}</div>
  {/if}

  <form on:submit|preventDefault={handleLogin}>
    <div class="form-group">
      <label for="email">Email</label>
      <input
        id="email"
        type="email"
        bind:value={email}
        required
        placeholder="Email address"
      />
    </div>

    <div class="form-group">
      <label for="password">Password</label>
      <input
        id="password"
        type="password"
        bind:value={password}
        required
        placeholder="Password"
      />
    </div>

    <button type="submit" disabled={loading}>
      {loading ? 'Signing in...' : 'Sign In'}
    </button>
  </form>

  <div class="footer-text">
    New to Cineforum? <a href="/register">Sign up now</a>
  </div>
</div>