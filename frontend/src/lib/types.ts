export interface User {
    id: number;
    email: string;
    username: string;
    is_email_verified: boolean;
    created_at: string;
}

export interface Group {
    id: number;
    name: string;
    description: string;
    administrator: User;
    members_count: number;
    is_proposal_period_active: boolean;
    proposal_period_started_at: string | null;
    created_at: string;
    membership_status: 'pending' | 'approved' | 'rejected' | null;
}

export interface Film {
    id: number;
    tmdb_id: number;
    title: string;
    original_title: string;
    overview: string;
    poster_path: string;
    backdrop_path: string;
    release_date: string;
    runtime: number;
    genres: string[];
    vote_average: number;
    vote_count: number;
    streaming_services: any;
    proposed_by: User;
    created_at: string;
}

export interface GroupFilm {
    id: number;
    film: Film;
    proposed_by: User;
    status: 'proposed' | 'watched' | 'rejected';
    priority_weight: number;
    proposed_at: string;
    watched_at: string | null;
    proposal_week_number: number;
}

export interface CineforumSession {
    id: number;
    group: Group;
    film: Film;
    selected_at: string;
    participants: User[];
    participants_count: number;
    week_number: number;
}

export interface Review {
    id: number;
    film: Film;
    user: User;
    session: number;
    rating: number;
    comment: string;
    created_at: string;
    updated_at: string;
}

export interface TMDBMovie {
    id: number;
    title: string;
    original_title: string;
    overview: string;
    poster_path: string | null;
    backdrop_path: string | null;
    release_date: string;
    vote_average: number;
    vote_count: number;
}