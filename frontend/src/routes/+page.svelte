<script lang="ts">
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import { browser } from '$app/environment';

  let isLoggedIn = false;

  onMount(() => {
    if (browser) {
      const token = localStorage.getItem('access_token');
      isLoggedIn = !!token;
      
      // Redirect to dashboard if already logged in
      if (isLoggedIn) {
        goto('/dashboard');
      }
    }
  });
</script>

<style>
  .hero {
    min-height: 80vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    background: linear-gradient(180deg, #000 0%, #141414 100%);
    padding: 2rem;
  }

  h1 {
    font-size: 4rem;
    font-weight: 700;
    margin-bottom: 1rem;
    background: linear-gradient(90deg, #e50914 0%, #f40612 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .tagline {
    font-size: 1.5rem;
    color: #b3b3b3;
    margin-bottom: 3rem;
    max-width: 600px;
  }

  .cta-buttons {
    display: flex;
    gap: 1rem;
  }

  .btn {
    padding: 1rem 2.5rem;
    border: none;
    border-radius: 4px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
    text-decoration: none;
    display: inline-block;
  }

  .btn-primary {
    background: #e50914;
    color: #fff;
  }

  .btn-primary:hover {
    background: #f40612;
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(229, 9, 20, 0.3);
  }

  .btn-secondary {
    background: rgba(255, 255, 255, 0.1);
    color: #fff;
    border: 1px solid rgba(255, 255, 255, 0.2);
  }

  .btn-secondary:hover {
    background: rgba(255, 255, 255, 0.2);
    transform: translateY(-2px);
  }

  .features {
    padding: 4rem 2rem;
    max-width: 1200px;
    margin: 0 auto;
  }

  .features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 3rem;
    margin-top: 3rem;
  }

  .feature {
    text-align: center;
  }

  .feature-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
  }

  .feature h3 {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
    font-weight: 600;
  }

  .feature p {
    color: #b3b3b3;
    line-height: 1.6;
  }

  @media (max-width: 768px) {
    h1 {
      font-size: 2.5rem;
    }

    .tagline {
      font-size: 1.2rem;
    }

    .cta-buttons {
      flex-direction: column;
      width: 100%;
      max-width: 300px;
    }

    .btn {
      width: 100%;
    }
  }
</style>

<div class="hero">
  <h1>CINEFORUM</h1>
  <p class="tagline">
    Organize film screenings with friends. Propose, vote, and review films together.
  </p>
  
  <div class="cta-buttons">
    <a href="/register" class="btn btn-primary">Get Started</a>
    <a href="/login" class="btn btn-secondary">Sign In</a>
  </div>
</div>

<div class="features">
  <div class="features-grid">
    <div class="feature">
      <div class="feature-icon">👥</div>
      <h3>Create Groups</h3>
      <p>Form cineforum groups with your friends and movie enthusiasts</p>
    </div>

    <div class="feature">
      <div class="feature-icon">🎬</div>
      <h3>Propose Films</h3>
      <p>Search and propose films from The Movie Database for your next screening</p>
    </div>

    <div class="feature">
      <div class="feature-icon">🎲</div>
      <h3>Fair Selection</h3>
      <p>Smart randomizer with priority weights ensures everyone's films get picked</p>
    </div>

    <div class="feature">
      <div class="feature-icon">⭐</div>
      <h3>Rate & Review</h3>
      <p>Share your thoughts and ratings after each cineforum session</p>
    </div>

    <div class="feature">
      <div class="feature-icon">📊</div>
      <h3>Track History</h3>
      <p>Keep a record of all films watched and sessions attended</p>
    </div>

    <div class="feature">
      <div class="feature-icon">🔒</div>
      <h3>Secure & Private</h3>
      <p>Email verification and secure password hashing protect your account</p>
    </div>
  </div>
</div>