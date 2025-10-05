from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count, Q, F
from django.conf import settings
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import random
import requests
from datetime import datetime

from .models import User, Group, GroupMembership, Film, GroupFilm, CineforumSession, Review
from .serializer import (
    UserRegistrationSerializer, UserSerializer, GroupSerializer,
    GroupMembershipSerializer, FilmSerializer, GroupFilmSerializer,
    CineforumSessionSerializer, ReviewSerializer, FilmProposalSerializer
)
from .tasks import send_verification_email, delete_unverified_users


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['register', 'verify_email', 'login']:
            return [permissions.AllowAny()]
        return super().get_permissions()

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.email_verification_sent_at = timezone.now()
            user.save()
            
            # Send verification email (using Celery task)
            send_verification_email.delay(user.id)
            
            return Response({
                'message': 'User created successfully. Please check your email to verify your account.',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def verify_email(self, request):
        token = request.data.get('token')
        try:
            user = User.objects.get(email_verification_token=token)
            if user.is_verification_expired():
                user.delete()
                return Response({
                    'error': 'Verification link expired. Please register again.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user.is_email_verified = True
            user.is_active = True
            user.save()
            
            return Response({
                'message': 'Email verified successfully. You can now log in.'
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({
                'error': 'Invalid verification token.'
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        try:
            user = User.objects.get(email=email)
            ph = PasswordHasher()
            
            if not user.is_email_verified:
                return Response({
                    'error': 'Please verify your email before logging in.'
                }, status=status.HTTP_403_FORBIDDEN)
            
            try:
                ph.verify(user.password, password)
                
                # Check if password needs rehashing (Argon2 updates)
                if ph.check_needs_rehash(user.password):
                    user.password = ph.hash(password)
                    user.save()
                
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': UserSerializer(user).data
                })
            except VerifyMismatchError:
                return Response({
                    'error': 'Invalid credentials.'
                }, status=status.HTTP_401_UNAUTHORIZED)
                
        except User.DoesNotExist:
            return Response({
                'error': 'Invalid credentials.'
            }, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Group.objects.filter(
            Q(members=user, groupmembership__status='approved') |
            Q(administrator=user)
        ).distinct()

    def perform_create(self, serializer):
        group = serializer.save(administrator=self.request.user)
        GroupMembership.objects.create(
            user=self.request.user,
            group=group,
            status='approved'
        )

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        group = self.get_object()
        memberships = GroupMembership.objects.filter(group=group, status='approved')
        serializer = GroupMembershipSerializer(memberships, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def pending_requests(self, request, pk=None):
        group = self.get_object()
        
        if group.administrator != request.user:
            return Response({
                'error': 'Only the administrator can view pending requests.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        memberships = GroupMembership.objects.filter(group=group, status='pending')
        serializer = GroupMembershipSerializer(memberships, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def join_request(self, request, pk=None):
        group = self.get_object()
        user = request.user
        
        membership, created = GroupMembership.objects.get_or_create(
            user=user,
            group=group,
            defaults={'status': 'pending'}
        )
        
        if not created:
            return Response({
                'message': f'You already have a {membership.status} request for this group.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'message': 'Join request sent successfully.'
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def approve_member(self, request, pk=None):
        group = self.get_object()
        
        if group.administrator != request.user:
            return Response({
                'error': 'Only the administrator can approve members.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        user_id = request.data.get('user_id')
        try:
            membership = GroupMembership.objects.get(
                group=group,
                user_id=user_id,
                status='pending'
            )
            membership.status = 'approved'
            membership.save()
            
            return Response({
                'message': 'Member approved successfully.'
            }, status=status.HTTP_200_OK)
        except GroupMembership.DoesNotExist:
            return Response({
                'error': 'Membership request not found.'
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def reject_member(self, request, pk=None):
        group = self.get_object()
        
        if group.administrator != request.user:
            return Response({
                'error': 'Only the administrator can reject members.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        user_id = request.data.get('user_id')
        try:
            membership = GroupMembership.objects.get(
                group=group,
                user_id=user_id,
                status='pending'
            )
            membership.status = 'rejected'
            membership.save()
            
            return Response({
                'message': 'Member request rejected.'
            }, status=status.HTTP_200_OK)
        except GroupMembership.DoesNotExist:
            return Response({
                'error': 'Membership request not found.'
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def proposed_films(self, request, pk=None):
        group = self.get_object()
        
        group_films = GroupFilm.objects.filter(
            group=group,
            status='proposed'
        ).select_related('film', 'proposed_by').order_by('-priority_weight', '-proposed_at')
        
        serializer = GroupFilmSerializer(group_films, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def start_proposal_period(self, request, pk=None):
        group = self.get_object()
        
        if group.administrator != request.user:
            return Response({
                'error': 'Only the administrator can start the proposal period.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        group.is_proposal_period_active = True
        group.proposal_period_started_at = timezone.now()
        group.save()
        
        return Response({
            'message': 'Proposal period started.'
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def end_proposal_period(self, request, pk=None):
        group = self.get_object()
        
        if group.administrator != request.user:
            return Response({
                'error': 'Only the administrator can end the proposal period.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        group.is_proposal_period_active = False
        group.save()
        
        return Response({
            'message': 'Proposal period ended. You can now randomize a film.'
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def randomize_film(self, request, pk=None):
        group = self.get_object()
        
        if group.administrator != request.user:
            return Response({
                'error': 'Only the administrator can randomize films.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if group.is_proposal_period_active:
            return Response({
                'error': 'Please end the proposal period before randomizing.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get all proposed films
        proposed_films = GroupFilm.objects.filter(
            group=group,
            status='proposed'
        ).select_related('film', 'proposed_by')
        
        if not proposed_films:
            return Response({
                'error': 'No films available for randomization.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create weighted list based on priority
        weighted_films = []
        for gf in proposed_films:
            weight = int(gf.priority_weight * 100)
            weighted_films.extend([gf] * weight)
        
        # Random selection
        selected_group_film = random.choice(weighted_films)
        
        return Response({
            'selected_film': GroupFilmSerializer(selected_group_film).data,
            'message': 'Film selected! Please confirm to create the session.'
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def confirm_film_selection(self, request, pk=None):
        group = self.get_object()
        
        if group.administrator != request.user:
            return Response({
                'error': 'Only the administrator can confirm film selection.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        film_id = request.data.get('film_id')
        group_film = get_object_or_404(GroupFilm, group=group, film_id=film_id, status='proposed')
        
        # Create session
        week_number = CineforumSession.objects.filter(group=group).count() + 1
        session = CineforumSession.objects.create(
            group=group,
            film=group_film.film,
            week_number=week_number
        )
        
        # Mark film as watched
        group_film.status = 'watched'
        group_film.watched_at = timezone.now()
        group_film.save()
        
        # Update priorities
        selected_user = group_film.proposed_by
        
        # Increase priority for other users' films
        GroupFilm.objects.filter(
            group=group,
            status='proposed'
        ).exclude(
            proposed_by=selected_user
        ).update(priority_weight=F('priority_weight') * 1.2)
        
        # Decrease priority for selected user's films
        GroupFilm.objects.filter(
            group=group,
            status='proposed',
            proposed_by=selected_user
        ).update(priority_weight=F('priority_weight') * 0.8)
        
        return Response({
            'session': CineforumSessionSerializer(session).data,
            'message': 'Session created successfully!'
        }, status=status.HTTP_201_CREATED)


class FilmViewSet(viewsets.ModelViewSet):
    queryset = Film.objects.all()
    serializer_class = FilmSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def search_tmdb(self, request):
        query = request.query_params.get('q', '')
        api_key = settings.TMDB_API_KEY
        
        if not query:
            return Response({
                'error': 'Query parameter "q" is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            headers = {
                "accept": "application/json",
                "Authorization": "Bearer " + api_key
            }
            response = requests.get(
                f'https://api.themoviedb.org/3/search/movie',
                params={ 'query': query, 'language': 'en-US' },
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return Response(response.json())
            return Response({
                'error': 'Failed to search films'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except requests.RequestException as e:
            return Response({
                'error': f'TMDB API error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def propose_film(self, request):
        serializer = FilmProposalSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        tmdb_id = serializer.validated_data['tmdb_id']
        group_id = serializer.validated_data['group_id']
        
        group = get_object_or_404(Group, id=group_id)
        
        # Check if user is a member
        if not GroupMembership.objects.filter(
            group=group, user=request.user, status='approved'
        ).exists():
            return Response({
                'error': 'You must be a member of this group to propose films.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Check if proposal period is active
        if not group.is_proposal_period_active:
            return Response({
                'error': 'Proposal period is not active for this group.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Fetch film from TMDB
        api_key = settings.TMDB_API_KEY
        try:
            response = requests.get(
                f'https://api.themoviedb.org/3/movie/{tmdb_id}',
                params={'append_to_response': 'watch/providers'},
                headers={
                    "accept": "application/json",
                    "Authorization": "Bearer " + api_key
                },
                timeout=10
            )
            
            if response.status_code != 200:
                return Response({
                    'error': 'Failed to fetch film from TMDB'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            film_data = response.json()
        except requests.RequestException as e:
            return Response({
                'error': f'TMDB API error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Get or create film
        film, created = Film.objects.get_or_create(
            tmdb_id=tmdb_id,
            defaults={
                'title': film_data.get('title', ''),
                'original_title': film_data.get('original_title', ''),
                'overview': film_data.get('overview', ''),
                'poster_path': film_data.get('poster_path', ''),
                'backdrop_path': film_data.get('backdrop_path', ''),
                'release_date': film_data.get('release_date') or None,
                'runtime': film_data.get('runtime'),
                'genres': [g['name'] for g in film_data.get('genres', [])],
                'vote_average': film_data.get('vote_average', 0),
                'vote_count': film_data.get('vote_count', 0),
                'streaming_services': film_data.get('watch/providers', {}).get('results', {}),
                'proposed_by': request.user
            }
        )
        
        # Check if film already proposed for this group
        if GroupFilm.objects.filter(group=group, film=film).exists():
            return Response({
                'error': 'This film has already been proposed for this group.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create group film association
        week_number = CineforumSession.objects.filter(group=group).count()
        group_film = GroupFilm.objects.create(
            group=group,
            film=film,
            proposed_by=request.user,
            status='proposed',
            priority_weight=1.0,
            proposal_week_number=week_number
        )
        
        return Response({
            'message': 'Film proposed successfully!',
            'group_film': GroupFilmSerializer(group_film).data
        }, status=status.HTTP_201_CREATED)


class CineforumSessionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CineforumSession.objects.all()
    serializer_class = CineforumSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return CineforumSession.objects.filter(
            group__members=user,
            group__groupmembership__status='approved'
        ).distinct().select_related('group', 'film').prefetch_related('participants')

    @action(detail=True, methods=['post'])
    def mark_participation(self, request, pk=None):
        session = self.get_object()
        
        # Check if user is a member of the group
        if not GroupMembership.objects.filter(
            group=session.group,
            user=request.user,
            status='approved'
        ).exists():
            return Response({
                'error': 'You must be a member of this group.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        session.participants.add(request.user)
        
        return Response({
            'message': 'Participation marked successfully.'
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def unmark_participation(self, request, pk=None):
        session = self.get_object()
        
        session.participants.remove(request.user)
        
        return Response({
            'message': 'Participation removed.'
        }, status=status.HTTP_200_OK)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Review.objects.filter(
            session__group__members=user,
            session__group__groupmembership__status='approved'
        ).distinct().select_related('film', 'user', 'session')
        
        # Filter by film if provided
        film_id = self.request.query_params.get('film_id')
        if film_id:
            queryset = queryset.filter(film_id=film_id)
        
        # Filter by session if provided
        session_id = self.request.query_params.get('session_id')
        if session_id:
            queryset = queryset.filter(session_id=session_id)
        
        return queryset

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            film=serializer.validated_data['session'].film
        )

    def perform_update(self, serializer):
        # Ensure user can only update their own reviews
        if serializer.instance.user != self.request.user:
            raise PermissionDenied("You can only edit your own reviews")
        serializer.save()

    def perform_destroy(self, instance):
        # Ensure user can only delete their own reviews
        if instance.user != self.request.user:
            raise PermissionDenied("You can only delete your own reviews")
        instance.delete()