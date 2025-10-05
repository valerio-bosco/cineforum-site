<script lang="ts">
  import { goto } from '$app/navigation';
  import { api } from '$lib/api';
  
  let email = '';
  let username = '';
  let password = '';
  let password2 = '';
  let error = '';
  let success = false;
  let loading = false;

  async function handleRegister() {
    error = '';
    loading = true;

    if (password !== password2) {
      error = 'Passwords do not match';
      loading = false;
      return;
    }

    try {
      await api.register(email, username, password, password2);
      success = true;
    } catch (err: any) {
      error = err.response?.data?.error || 'Registration failed. Please try again.';
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

  .success {
    background: #46d369;
    color: #fff;
    padding: 1.5rem;
    border-radius: 4px;
    text-align: center;
  }

  .success h2 {
    margin-bottom: 0.5rem;
    font-size: 1.5rem;
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

  .info-text {
    font-size: 0.85rem;
    color: #b3b3b3;
    margin-top: 0.5rem;
  }
</style>

<div class="container">
  {#if success}
    <div class="success">
      <h2>Registration Successful!</h2>
      <p>Please check your email to verify your account.</p>
      <p style="margin-top: 1rem;">You have 24 hours to verify your email.</p>
    </div>
    <div class="footer-text" style="text-align: center;">
      <a href="/login">Go to Login</a>
    </div>
  {:else}
    <h1>Sign Up</h1>

    {#if error}
      <div class="error">{error}</div>
    {/if}

    <form on:submit|preventDefault={handleRegister}>
      <div class="form-group">
        <label for="email">Email</label>
        <input
          id="email"
          type="email"
          bind:value={email}
          required
          placeholder="Email address"
        />
        <div class="info-text">You'll need to verify this email</div>
      </div>

      <div class="form-group">
        <label for="username">Username</label>
        <input
          id="username"
          type="text"
          bind:value={username}
          required
          placeholder="Username"
        />
      </div>

      <div class="form-group">
        <label for="password">Password</label>
        <input
          id="password"
          type="password"
          bind:value={password}
          required
          placeholder="Password (min 8 characters)"
          minlength="8"
        />
      </div>

      <div class="form-group">
        <label for="password2">Confirm Password</label>
        <input
          id="password2"
          type="password"
          bind:value={password2}
          required
          placeholder="Confirm password"
        />
      </div>

      <button type="submit" disabled={loading}>
        {loading ? 'Creating account...' : 'Sign Up'}
      </button>
    </form>

    <div class="footer-text">
      Already have an account? <a href="/login">Sign in</a>
    </div>
  {/if}
</div>