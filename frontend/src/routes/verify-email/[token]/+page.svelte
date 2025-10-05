<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { api } from '$lib/api';
  
  let verifying = true;
  let success = false;
  let error = '';

  $: token = $page.params.token;

  onMount(async () => {
    try {
      await api.verifyEmail(token);
      success = true;
    } catch (err: any) {
      error = err.response?.data?.error || 'Verification failed. Please try again.';
    } finally {
      verifying = false;
    }
  });
</script>

<style>
  .container {
    max-width: 500px;
    margin: 4rem auto;
    padding: 3rem;
    background: rgba(0, 0, 0, 0.75);
    border-radius: 8px;
    text-align: center;
  }

  .icon {
    font-size: 4rem;
    margin-bottom: 1.5rem;
  }

  h1 {
    font-size: 2rem;
    margin-bottom: 1rem;
    font-weight: 600;
  }

  p {
    color: #b3b3b3;
    margin-bottom: 2rem;
    line-height: 1.6;
  }

  .btn {
    display: inline-block;
    padding: 0.75rem 2rem;
    background: #e50914;
    color: #fff;
    text-decoration: none;
    border-radius: 4px;
    font-weight: 600;
    transition: background 0.2s;
  }

  .btn:hover {
    background: #f40612;
  }

  .spinner {
    border: 4px solid rgba(255, 255, 255, 0.1);
    border-top: 4px solid #e50914;
    border-radius: 50%;
    width: 50px;
    height: 50px;
    animation: spin 1s linear infinite;
    margin: 2rem auto;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .error-box {
    background: #e87c03;
    color: #fff;
    padding: 1rem;
    border-radius: 4px;
    margin-bottom: 1.5rem;
  }
</style>

<div class="container">
  {#if verifying}
    <div class="icon">⏳</div>
    <h1>Verifying Email...</h1>
    <div class="spinner"></div>
  {:else if success}
    <div class="icon">✅</div>
    <h1>Email Verified!</h1>
    <p>Your email has been successfully verified. You can now log in to your account.</p>
    <a href="/login" class="btn">Go to Login</a>
  {:else}
    <div class="icon">❌</div>
    <h1>Verification Failed</h1>
    {#if error}
      <div class="error-box">{error}</div>
    {/if}
    <p>The verification link may have expired or is invalid.</p>
    <a href="/register" class="btn">Register Again</a>
  {/if}
</div>