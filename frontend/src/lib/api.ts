import { goto } from '$app/navigation';
import { browser } from '$app/environment';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

class ApiClient {
    private async request(endpoint: string, options: RequestInit = {}) {
        const url = `${API_URL}${endpoint}`;
        const headers: Record<string, string> = {
            'Content-Type': 'application/json',
            ...options.headers as Record<string, string>
        };

        if (browser) {
            const token = localStorage.getItem('access_token');
            if (token) {
                headers.Authorization = `Bearer ${token}`;
            }
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            if (response.status === 401 && !endpoint.includes('token/refresh')) {
                // Try to refresh token
                const refreshToken = browser ? localStorage.getItem('refresh_token') : null;
                if (refreshToken) {
                    try {
                        const refreshResponse = await fetch(`${API_URL}/token/refresh/`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ refresh: refreshToken })
                        });

                        if (refreshResponse.ok) {
                            const data = await refreshResponse.json();
                            if (browser) {
                                localStorage.setItem('access_token', data.access);
                            }

                            // Retry original request with new token
                            headers.Authorization = `Bearer ${data.access}`;
                            const retryResponse = await fetch(url, { ...options, headers });
                            return this.handleResponse(retryResponse);
                        }
                    } catch (e) {
                        this.logout();
                        throw e;
                    }
                } else {
                    this.logout();
                }
            }

            return this.handleResponse(response);
        } catch (error) {
            throw error;
        }
    }

    private async handleResponse(response: Response) {
        const contentType = response.headers.get('content-type');
        const isJson = contentType?.includes('application/json');

        const data = isJson ? await response.json() : await response.text();

        if (!response.ok) {
            throw {
                response: {
                    status: response.status,
                    data: data
                }
            };
        }

        return { data, status: response.status };
    }

    // Auth methods
    async register(email: string, username: string, password: string, password2: string) {
        return this.request('/users/register/', {
            method: 'POST',
            body: JSON.stringify({ email, username, password, password2 })
        });
    }

    async login(email: string, password: string) {
        const response = await this.request('/users/login/', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });

        if (browser && response.data) {
            localStorage.setItem('access_token', response.data.access);
            localStorage.setItem('refresh_token', response.data.refresh);
            localStorage.setItem('user', JSON.stringify(response.data.user));
        }
        return response;
    }

    async verifyEmail(token: string) {
        return this.request('/users/verify_email/', {
            method: 'POST',
            body: JSON.stringify({ token })
        });
    }

    async getMe() {
        return this.request('/users/me/');
    }

    logout() {
        if (browser) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user');
            goto('/login');
        }
    }

    // Group methods
    async getGroups() {
        return this.request('/groups/');
    }

    async getGroup(id: number) {
        return this.request(`/groups/${id}/`);
    }

    async createGroup(name: string, description: string) {
        return this.request('/groups/', {
            method: 'POST',
            body: JSON.stringify({ name, description })
        });
    }

    async joinGroup(groupId: number) {
        return this.request(`/groups/${groupId}/join_request/`, {
            method: 'POST'
        });
    }

    async approveMember(groupId: number, userId: number) {
        return this.request(`/groups/${groupId}/approve_member/`, {
            method: 'POST',
            body: JSON.stringify({ user_id: userId })
        });
    }

    async startProposalPeriod(groupId: number) {
        return this.request(`/groups/${groupId}/start_proposal_period/`, {
            method: 'POST'
        });
    }

    async endProposalPeriod(groupId: number) {
        return this.request(`/groups/${groupId}/end_proposal_period/`, {
            method: 'POST'
        });
    }

    async randomizeFilm(groupId: number) {
        return this.request(`/groups/${groupId}/randomize_film/`, {
            method: 'POST'
        });
    }

    async confirmFilmSelection(groupId: number, filmId: number) {
        return this.request(`/groups/${groupId}/confirm_film_selection/`, {
            method: 'POST',
            body: JSON.stringify({ film_id: filmId })
        });
    }

    // Film methods
    async searchTMDB(query: string) {
        return this.request(`/films/search_tmdb/?q=${encodeURIComponent(query)}`);
    }

    async proposeFilm(tmdbId: number, groupId: number) {
        return this.request('/films/propose_film/', {
            method: 'POST',
            body: JSON.stringify({ tmdb_id: tmdbId, group_id: groupId })
        });
    }

    async getFilms() {
        return this.request('/films/');
    }

    // Session methods
    async getSessions() {
        return this.request('/sessions/');
    }

    async getSession(id: number) {
        return this.request(`/sessions/${id}/`);
    }

    async markParticipation(sessionId: number) {
        return this.request(`/sessions/${sessionId}/mark_participation/`, {
            method: 'POST'
        });
    }

    // Review methods
    async getReviews() {
        return this.request('/reviews/');
    }

    async createReview(sessionId: number, rating: number, comment: string) {
        return this.request('/reviews/', {
            method: 'POST',
            body: JSON.stringify({
                session: sessionId,
                rating,
                comment
            })
        });
    }

    async updateReview(reviewId: number, rating: number, comment: string) {
        return this.request(`/reviews/${reviewId}/`, {
            method: 'PATCH',
            body: JSON.stringify({ rating, comment })
        });
    }

    async deleteReview(reviewId: number) {
        return this.request(`/reviews/${reviewId}/`, {
            method: 'DELETE'
        });
    }
}

export const api = new ApiClient();