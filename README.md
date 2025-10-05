# Cineforum Application

A complete cineforum management platform built with Django (Backend), Svelte (Frontend), and MySQL (Database), fully containerized with Docker and ready for Kubernetes deployment.

## Features

- **User Authentication**: Secure registration with email verification and Argon2 password hashing
- **Group Management**: Create and join cineforum groups
- **Film Proposals**: Propose films using TMDB API integration
- **Smart Randomizer**: Weighted film selection with priority system
- **Reviews & Ratings**: Rate and review films from attended sessions
- **Material UI Design**: Netflix/Prime Video inspired interface
- **Scalable Architecture**: Docker containers with Kubernetes support

## Architecture

- **Backend**: Django 5.0 + Django REST Framework
- **Frontend**: SvelteKit + TypeScript
- **Database**: MySQL 8.0
- **Cache/Queue**: Redis + Celery
- **Web Server**: Nginx
- **Orchestration**: Docker Compose / Kubernetes

## Prerequisites

- Docker & Docker Compose
- (Optional) Kubernetes cluster with kubectl
- TMDB API Key (get from https://www.themoviedb.org/settings/api)
- Email account for verification emails (Gmail recommended)

## Quick Start with Docker Compose

1. **Clone the repository and set up environment variables**

```bash
# Create backend/.env file
cat > backend/.env << EOF
SECRET_KEY=your-super-secret-key-change-this
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,backend
DATABASE_HOST=db
DATABASE_NAME=cineforum
DATABASE_USER=cineforum_user
DATABASE_PASSWORD=cineforum_pass
TMDB_API_KEY=your-tmdb-api-key-here
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
FRONTEND_URL=http://localhost:3000
EOF

# Create frontend/.env file
cat > frontend/.env << EOF
VITE_API_URL=http://localhost:8000/api
EOF
```

2. **Build and run the application**

```bash
docker-compose up --build
```

3. **Access the application**

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api
- Django Admin: http://localhost:8000/admin

4. **Create Django superuser (optional)**

```bash
docker-compose exec backend python manage.py createsuperuser
```

## Kubernetes Deployment

1. **Build and push Docker images**

```bash
# Build backend
cd backend
docker build -t cineforum-backend:latest .

# Build frontend
cd ../frontend
docker build -t cineforum-frontend:latest .
```

2. **Update secrets in kubernetes/deployment.yaml**

Edit the `cineforum-secrets` Secret with your actual values:
- mysql-root-password
- mysql-password
- django-secret-key
- tmdb-api-key
- email-password

3. **Deploy to Kubernetes**

```bash
kubectl apply -f kubernetes/deployment.yaml
```

4. **Verify deployment**

```bash
kubectl get pods -n cineforum
kubectl get services -n cineforum
```

5. **Access the application**

Add to `/etc/hosts`:
```
127.0.0.1 cineforum.local
```

Then access: http://cineforum.local

## Project Structure

```
cineforum/
├── docker-compose.yml
├── nginx/
│   └── nginx.conf
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── cineforum/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── celery.py
│   │   └── wsgi.py
│   └── api/
│       ├── models.py
│       ├── serializers.py
│       ├── views.py
│       └── tasks.py
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── svelte.config.js
│   ├── src/
│   │   ├── routes/
│   │   │   ├── +layout.svelte
│   │   │   ├── login/+page.svelte
│   │   │   ├── register/+page.svelte
│   │   │   └── dashboard/+page.svelte
│   │   └── lib/
│   │       ├── api.ts
│   │       └── types.ts
└── kubernetes/
    └── deployment.yaml
```

## API Endpoints

### Authentication
- `POST /api/users/register/` - Register new user
- `POST /api/users/login/` - Login
- `POST /api/users/verify_email/` - Verify email
- `GET /api/users/me/` - Get current user

### Groups
- `GET /api/groups/` - List user's groups
- `POST /api/groups/` - Create group
- `POST /api/groups/{id}/join_request/` - Request to join
- `POST /api/groups/{id}/approve_member/` - Approve member (admin)
- `POST /api/groups/{id}/start_proposal_period/` - Start proposals (admin)
- `POST /api/groups/{id}/end_proposal_period/` - End proposals (admin)
- `POST /api/groups/{id}/randomize_film/` - Randomize film (admin)
- `POST /api/groups/{id}/confirm_film_selection/` - Confirm selection (admin)

### Films
- `GET /api/films/search_tmdb/?q=query` - Search TMDB
- `POST /api/films/propose_film/` - Propose film to group
- `GET /api/films/` - List films

### Sessions
- `GET /api/sessions/` - List sessions
- `GET /api/sessions/{id}/` - Session details
- `POST /api/sessions/{id}/mark_participation/` - Mark participation

### Reviews
- `GET /api/reviews/` - List reviews
- `POST /api/reviews/` - Create review
- `PATCH /api/reviews/{id}/` - Update review
- `DELETE /api/reviews/{id}/` - Delete review

## User Flow

1. **Registration**: User registers with email and password
2. **Email Verification**: User receives email and verifies within 24 hours
3. **Create/Join Group**: User creates a new group or requests to join existing ones
4. **Proposal Period**: Group admin starts proposal period
5. **Propose Films**: Members search TMDB and propose films
6. **End Proposals**: Admin ends proposal period
7. **Randomize**: Admin randomizes from proposed films (with priority weights)
8. **Confirm**: Admin confirms selected film, creating a session
9. **Participate**: Members mark participation in session
10. **Review**: Participants leave ratings and reviews

## Priority System

The film selection uses a weighted priority system:

- New proposals start with priority weight 1.0
- When a user's film is selected:
  - Their other proposals get weight × 0.8 (decrease)
  - Other users' proposals get weight × 1.2 (increase)
- Older proposals from previous weeks maintain higher priority
- Randomizer considers weights when selecting

## Security Features

- **Argon2 Password Hashing**: Industry-standard password security
- **JWT Authentication**: Secure token-based auth with refresh tokens
- **Email Verification**: Prevents fake accounts
- **Auto-deletion**: Unverified accounts deleted after 24 hours
- **CORS Protection**: Configured allowed origins
- **SQL Injection Protection**: Django ORM
- **XSS Protection**: React/Svelte auto-escaping

## Scaling

The application is designed for horizontal scaling:

- **Backend**: Stateless Django instances (scale with HPA)
- **Frontend**: Stateless Svelte instances (scale with HPA)
- **Database**: MySQL with persistent volume
- **Redis**: Shared cache/queue for Celery tasks

Kubernetes HPA is configured to auto-scale based on CPU/memory usage.

## Celery Tasks

Background tasks handled by Celery:

- `send_verification_email`: Sends email verification links
- `delete_unverified_users`: Runs every 6 hours to clean up
- `send_group_notification`: Sends notifications to group members

## Environment Variables

### Backend
- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (False in production)
- `ALLOWED_HOSTS`: Comma-separated allowed hosts
- `DATABASE_HOST`: MySQL host
- `DATABASE_NAME`: Database name
- `DATABASE_USER`: Database user
- `DATABASE_PASSWORD`: Database password
- `TMDB_API_KEY`: TMDB API key
- `EMAIL_HOST`: SMTP host
- `EMAIL_PORT`: SMTP port
- `EMAIL_HOST_USER`: Email address
- `EMAIL_HOST_PASSWORD`: Email password
- `FRONTEND_URL`: Frontend URL for email links

### Frontend
- `VITE_API_URL`: Backend API URL

## Troubleshooting

### Email verification not working
- Check EMAIL_HOST_PASSWORD is an App Password (for Gmail)
- Ensure "Less secure app access" is enabled or use App Passwords
- Check spam folder

### TMDB API errors
- Verify TMDB_API_KEY is correct
- Check API rate limits

### Database connection issues
- Wait for MySQL to fully initialize (can take 30-60 seconds)
- Check DATABASE_HOST matches service name

### Frontend can't connect to backend
- Verify VITE_API_URL is correct
- Check CORS settings in Django

## License

MIT License

## Support

For issues and questions, please open a GitHub issue.