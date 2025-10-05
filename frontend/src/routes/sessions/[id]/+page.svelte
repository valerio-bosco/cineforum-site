<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { api } from '$lib/api';
  import type { CineforumSession, Review } from '$lib/types';
  
  let session: CineforumSession | null = null;
  let reviews: Review[] = [];
  let loading = true;
  let currentUser: any = null;
  let hasParticipated = false;
  let showReviewForm = false;
  let rating = 5;
  let comment = '';
  let submitting = false;
  let error = '';

  $: sessionId = parseInt($page.params.id);

  onMount(async () => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      currentUser = JSON.parse(userStr);
    }
    await loadSessionData();
  });

  async function loadSessionData() {
    try {
      const [sessionRes, reviewsRes] = await Promise.all([
        api.getSession(sessionId),
        api.getReviews().then(res => res.data.results || res.data)
      ]);
      
      session = sessionRes.data;
      reviews = reviewsRes.filter((r: Review) => r.session === sessionId);
      
      if (session && currentUser) {
        hasParticipated = session.participants.some(p => p.id === currentUser.id);
      }
    } catch (err) {
      console.error('Failed to load session:', err);
    } finally {
      loading = false;
    }
  }

  async function markParticipation() {
    try {
      await api.markParticipation(sessionId);
      await loadSessionData();
    } catch (err: any) {
      alert(err.response?.data?.error || 'Failed to mark participation');
    }
  }

  async function submitReview() {
    if (!rating || rating < 1 || rating > 10) {
      error = 'Rating must be between 1 and 10';
      return;
    }

    submitting = true;
    error = '';

    try {
      await api.createReview(sessionId, rating, comment);
      showReviewForm = false;
      rating = 5;
      comment = '';
      await loadSessionData();
    } catch (err: any) {
      error = err.response?.data?.error || 'Failed to submit review';
    } finally {
      submitting = false;
    }
  }

  function getImageUrl(path: string) {
    return path ? `https://image.tmdb.org/t/p/w500${path}` : '/placeholder.jpg';
  }

  function getBackdropUrl(path: string) {
    return path ? `https://image.tmdb.org/t/p/original${path}` : '/placeholder.jpg';
  }
</script>

<style>
  .container {
    max-width: 1200px;
    margin: 0 auto;
  }

  .back-link {
    color: #b3b3b3;
    text-decoration: none;
    margin-bottom: 2rem;
    display: inline-block;
  }

  .back-link:hover {
    color: #fff;
  }

  .hero {
    position: relative;
    height: 500px;
    margin: 0 -4% 2rem;
    border-radius: 8px;
    overflow: hidden;
  }

  .backdrop {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .hero-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(180deg, transparent 0%, #141414 100%);
    padding: 4rem;
  }

  h1 {
    font-size: 3rem;
    font-weight: 700;
    margin-bottom: 1rem;
  }

  .meta {
    display: flex;
    gap: 2rem;
    color: #b3b3b3;
    font-size: 1.1rem;
    margin-bottom: 1.5rem;
  }

  .meta-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .section {
    margin-bottom: 3rem;
  }

  h2 {
    font-size: 1.75rem;
    margin-bottom: 1.5rem;
    font-weight: 600;
  }

  .overview {
    color: #b3b3b3;
    line-height: 1.8;
    font-size: 1.1rem;
    max-width: 900px;
  }

  .actions {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
  }

  .btn {
    padding: 0.75rem 2rem;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
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

  .participants {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
  }

  .participant-card {
    background: rgba(255, 255, 255, 0.05);
    padding: 1rem 1.5rem;
    border-radius: 8px;
    font-size: 0.95rem;
  }

  .reviews-grid {
    display: grid;
    gap: 1.5rem;
  }

  .review-card {
    background: rgba(255, 255, 255, 0.05);
    padding: 2rem;
    border-radius: 8px;
  }

  .review-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  .review-user {
    font-weight: 600;
    font-size: 1.1rem;
  }

  .review-rating {
    background: rgba(229, 9, 20, 0.2);
    color: #e50914;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-weight: 600;
    font-size: 1.1rem;
  }

  .review-comment {
    color: #b3b3b3;
    line-height: 1.6;
  }

  .review-date {
    color: #808080;
    font-size: 0.85rem;
    margin-top: 1rem;
  }

  .review-form {
    background: rgba(255, 255, 255, 0.05);
    padding: 2rem;
    border-radius: 8px;
    margin-bottom: 2rem;
  }

  .form-group {
    margin-bottom: 1.5rem;
  }

  label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 600;
  }

  .rating-input {
    display: flex;
    gap: 1rem;
    align-items: center;
  }

  input[type="number"] {
    width: 100px;
    padding: 0.75rem;
    background: #333;
    border: none;
    border-radius: 4px;
    color: #fff;
    font-size: 1.2rem;
    font-weight: 600;
    text-align: center;
  }

  input[type="number"]:focus {
    outline: 2px solid #e50914;
  }

  textarea {
    width: 100%;
    min-height: 150px;
    padding: 1rem;
    background: #333;
    border: none;
    border-radius: 4px;
    color: #fff;
    font-size: 1rem;
    font-family: inherit;
    resize: vertical;
  }

  textarea:focus {
    outline: 2px solid #e50914;
  }

  .error {
    background: #e87c03;
    color: #fff;
    padding: 1rem;
    border-radius: 4px;
    margin-bottom: 1rem;
  }

  .empty-state {
    text-align: center;
    padding: 3rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    color: #b3b3b3;
  }

  .loading {
    text-align: center;
    padding: 4rem;
    color: #b3b3b3;
  }

  @media (max-width: 768px) {
    h1 {
      font-size: 2rem;
    }

    .hero {
      height: 300px;
    }

    .hero-overlay {
      padding: 2rem;
    }

    .meta {
      flex-direction: column;
      gap: 0.5rem;
    }
  }
</style>

{#if loading}
  <div class="loading">Loading session...</div>
{:else if session}
  <div class="container">
    <a href="/sessions" class="back-link">← Back to Sessions</a>

    <div class="hero">
      <img 
        src={getBackdropUrl(session.film.backdrop_path || session.film.poster_path)} 
        alt={session.film.title}
        class="backdrop"
      />
      <div class="hero-overlay">
        <h1>{session.film.title}</h1>
        <div class="meta">
          <div class="meta-item">
            📅 {new Date(session.selected_at).toLocaleDateString('en-US', {
              year: 'numeric',
              month: 'long',
              day: 'numeric'
            })}
          </div>
          <div class="meta-item">
            🎬 {session.group.name}
          </div>
          <div class="meta-item">
            👥 {session.participants_count} participants
          </div>
        </div>
      </div>
    </div>

    <div class="actions">
      {#if !hasParticipated}
        <button class="btn btn-primary" on:click={markParticipation}>
          Mark Participation
        </button>
      {:else}
        <button class="btn btn-secondary" disabled>
          ✓ Participated
        </button>
        {#if !showReviewForm && !reviews.some(r => r.user.id === currentUser?.id)}
          <button class="btn btn-primary" on:click={() => showReviewForm = true}>
            Write Review
          </button>
        {/if}
      {/if}
    </div>

    {#if session.film.overview}
      <div class="section">
        <h2>Overview</h2>
        <p class="overview">{session.film.overview}</p>
      </div>
    {/if}

    <div class="section">
      <h2>Participants ({session.participants_count})</h2>
      {#if session.participants.length > 0}
        <div class="participants">
          {#each session.participants as participant}
            <div class="participant-card">
              {participant.username}
            </div>
          {/each}
        </div>
      {:else}
        <div class="empty-state">
          <p>No participants yet. Be the first to join!</p>
        </div>
      {/if}
    </div>

    {#if showReviewForm}
      <div class="section">
        <h2>Write Your Review</h2>
        <div class="review-form">
          {#if error}
            <div class="error">{error}</div>
          {/if}

          <form on:submit|preventDefault={submitReview}>
            <div class="form-group">
              <label for="rating">Rating (1-10)</label>
              <div class="rating-input">
                <input
                  id="rating"
                  type="number"
                  bind:value={rating}
                  min="1"
                  max="10"
                  required
                />
                <span style="color: #e50914; font-size: 1.5rem;">
                  {'⭐'.repeat(Math.ceil(rating / 2))}
                </span>
              </div>
            </div>

            <div class="form-group">
              <label for="comment">Your Review</label>
              <textarea
                id="comment"
                bind:value={comment}
                placeholder="Share your thoughts about this film..."
              ></textarea>
            </div>

            <div class="actions">
              <button type="submit" class="btn btn-primary" disabled={submitting}>
                {submitting ? 'Submitting...' : 'Submit Review'}
              </button>
              <button 
                type="button" 
                class="btn btn-secondary" 
                on:click={() => showReviewForm = false}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    {/if}

    <div class="section">
      <h2>Reviews ({reviews.length})</h2>
      {#if reviews.length > 0}
        <div class="reviews-grid">
          {#each reviews as review}
            <div class="review-card">
              <div class="review-header">
                <div class="review-user">{review.user.username}</div>
                <div class="review-rating">{review.rating}/10</div>
              </div>
              {#if review.comment}
                <p class="review-comment">{review.comment}</p>
              {/if}
              <div class="review-date">
                {new Date(review.created_at).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                })}
              </div>
            </div>
          {/each}
        </div>
      {:else}
        <div class="empty-state">
          <p>No reviews yet. Be the first to review this film!</p>
        </div>
      {/if}
    </div>
  </div>
{:else}
  <div class="container">
    <p style="text-align: center; color: #b3b3b3;">Session not found</p>
  </div>
{/if}