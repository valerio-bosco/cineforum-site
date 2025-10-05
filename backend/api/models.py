from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta
import uuid


class User(AbstractUser):
    """Extended user model with email verification"""
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.UUIDField(default=uuid.uuid4, editable=False)
    email_verification_sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def is_verification_expired(self):
        """Check if email verification is expired (24 hours)"""
        if self.email_verification_sent_at:
            return timezone.now() > self.email_verification_sent_at + timedelta(days=1)
        return False


class Group(models.Model):
    """Cineforum group"""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    administrator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='administered_groups')
    members = models.ManyToManyField(User, related_name='member_groups', through='GroupMembership')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_proposal_period_active = models.BooleanField(default=False)
    proposal_period_started_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


class GroupMembership(models.Model):
    """Group membership with join requests"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'group']
        ordering = ['-joined_at']

    def __str__(self):
        return f"{self.user.email} - {self.group.name} ({self.status})"


class Film(models.Model):
    """Film model with TMDB integration"""
    tmdb_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=500)
    original_title = models.CharField(max_length=500, blank=True)
    overview = models.TextField(blank=True)
    poster_path = models.CharField(max_length=500, blank=True)
    backdrop_path = models.CharField(max_length=500, blank=True)
    release_date = models.DateField(null=True, blank=True)
    runtime = models.IntegerField(null=True, blank=True)
    genres = models.JSONField(default=list)
    vote_average = models.FloatField(default=0)
    vote_count = models.IntegerField(default=0)
    streaming_services = models.JSONField(default=list)
    proposed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='proposed_films')
    groups = models.ManyToManyField(Group, related_name='films', through='GroupFilm')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class GroupFilm(models.Model):
    """Association between groups and films with proposal tracking"""
    STATUS_CHOICES = [
        ('proposed', 'Proposed'),
        ('watched', 'Watched'),
        ('rejected', 'Rejected'),
    ]

    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    proposed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_film_proposals')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='proposed')
    priority_weight = models.FloatField(default=1.0)
    proposed_at = models.DateTimeField(auto_now_add=True)
    watched_at = models.DateTimeField(null=True, blank=True)
    proposal_week_number = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['group', 'film']
        ordering = ['-priority_weight', '-proposed_at']

    def __str__(self):
        return f"{self.film.title} - {self.group.name} ({self.status})"


class CineforumSession(models.Model):
    """Records of cineforum sessions"""
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='sessions')
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name='sessions')
    selected_at = models.DateTimeField(auto_now_add=True)
    participants = models.ManyToManyField(User, related_name='participated_sessions')
    week_number = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-selected_at']

    def __str__(self):
        return f"{self.group.name} - {self.film.title} - {self.selected_at.date()}"


class Review(models.Model):
    """Film reviews by users"""
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    session = models.ForeignKey(CineforumSession, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['film', 'user', 'session']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.film.title} ({self.rating}/10)"