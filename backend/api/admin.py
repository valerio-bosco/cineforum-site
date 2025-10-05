from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Group, GroupMembership, Film, GroupFilm, CineforumSession, Review


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'is_email_verified', 'is_active', 'created_at')
    list_filter = ('is_email_verified', 'is_active', 'is_staff', 'created_at')
    search_fields = ('email', 'username')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Verification', {'fields': ('is_email_verified', 'email_verification_token', 'email_verification_sent_at')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'email_verification_token')


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'administrator', 'is_proposal_period_active', 'created_at')
    list_filter = ('is_proposal_period_active', 'created_at')
    search_fields = ('name', 'administrator__username', 'administrator__email')
    raw_id_fields = ('administrator',)
    date_hierarchy = 'created_at'


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'status', 'joined_at')
    list_filter = ('status', 'joined_at')
    search_fields = ('user__username', 'user__email', 'group__name')
    raw_id_fields = ('user', 'group')
    date_hierarchy = 'joined_at'


@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_date', 'vote_average', 'proposed_by', 'created_at')
    list_filter = ('release_date', 'created_at')
    search_fields = ('title', 'original_title', 'tmdb_id')
    raw_id_fields = ('proposed_by',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Info', {'fields': ('tmdb_id', 'title', 'original_title', 'overview')}),
        ('Media', {'fields': ('poster_path', 'backdrop_path')}),
        ('Details', {'fields': ('release_date', 'runtime', 'genres', 'vote_average', 'vote_count')}),
        ('Streaming', {'fields': ('streaming_services',)}),
        ('Metadata', {'fields': ('proposed_by', 'created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(GroupFilm)
class GroupFilmAdmin(admin.ModelAdmin):
    list_display = ('film', 'group', 'proposed_by', 'status', 'priority_weight', 'proposed_at')
    list_filter = ('status', 'proposed_at')
    search_fields = ('film__title', 'group__name', 'proposed_by__username')
    raw_id_fields = ('group', 'film', 'proposed_by')
    date_hierarchy = 'proposed_at'


@admin.register(CineforumSession)
class CineforumSessionAdmin(admin.ModelAdmin):
    list_display = ('group', 'film', 'week_number', 'selected_at', 'participant_count')
    list_filter = ('selected_at',)
    search_fields = ('group__name', 'film__title')
    raw_id_fields = ('group', 'film')
    filter_horizontal = ('participants',)
    date_hierarchy = 'selected_at'
    
    def participant_count(self, obj):
        return obj.participants.count()
    participant_count.short_description = 'Participants'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('film', 'user', 'rating', 'session', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('film__title', 'user__username', 'user__email', 'comment')
    raw_id_fields = ('film', 'user', 'session')
    date_hierarchy = 'created_at'
    
    readonly_fields = ('created_at', 'updated_at')