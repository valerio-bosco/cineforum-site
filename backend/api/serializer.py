from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from argon2 import PasswordHasher
from .models import User, Group, GroupMembership, Film, GroupFilm, CineforumSession, Review


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        ph = PasswordHasher()
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.password = ph.hash(password)
        user.is_active = False  # Will be activated after email verification
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'is_email_verified', 'created_at')
        read_only_fields = ('id', 'is_email_verified', 'created_at')


class GroupMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = GroupMembership
        fields = ('id', 'user', 'status', 'joined_at')


class GroupSerializer(serializers.ModelSerializer):
    administrator = UserSerializer(read_only=True)
    members_count = serializers.SerializerMethodField()
    membership_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Group
        fields = ('id', 'name', 'description', 'administrator', 'members_count', 
                  'is_proposal_period_active', 'proposal_period_started_at', 
                  'created_at', 'membership_status')
        read_only_fields = ('id', 'created_at', 'administrator')

    def get_members_count(self, obj):
        return obj.members.filter(groupmembership__status='approved').count()

    def get_membership_status(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            membership = GroupMembership.objects.filter(
                group=obj, user=request.user
            ).first()
            return membership.status if membership else None
        return None


class FilmSerializer(serializers.ModelSerializer):
    proposed_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Film
        fields = ('id', 'tmdb_id', 'title', 'original_title', 'overview', 
                  'poster_path', 'backdrop_path', 'release_date', 'runtime',
                  'genres', 'vote_average', 'vote_count', 'streaming_services',
                  'proposed_by', 'created_at')
        read_only_fields = ('id', 'created_at', 'proposed_by')


class GroupFilmSerializer(serializers.ModelSerializer):
    film = FilmSerializer(read_only=True)
    proposed_by = UserSerializer(read_only=True)
    
    class Meta:
        model = GroupFilm
        fields = ('id', 'film', 'proposed_by', 'status', 'priority_weight',
                  'proposed_at', 'watched_at', 'proposal_week_number')
        read_only_fields = ('id', 'proposed_at', 'watched_at')


class CineforumSessionSerializer(serializers.ModelSerializer):
    film = FilmSerializer(read_only=True)
    group = GroupSerializer(read_only=True)
    participants = UserSerializer(many=True, read_only=True)
    participants_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CineforumSession
        fields = ('id', 'group', 'film', 'selected_at', 'participants',
                  'participants_count', 'week_number')
        read_only_fields = ('id', 'selected_at')

    def get_participants_count(self, obj):
        return obj.participants.count()


class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    film = FilmSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = ('id', 'film', 'user', 'session', 'rating', 'comment',
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at', 'user', 'film')

    def validate_rating(self, value):
        if not 1 <= value <= 10:
            raise serializers.ValidationError("Rating must be between 1 and 10")
        return value

    def validate(self, attrs):
        request = self.context.get('request')
        session = attrs.get('session')
        
        # Check if user participated in the session
        if not session.participants.filter(id=request.user.id).exists():
            raise serializers.ValidationError(
                "You can only review films from sessions you participated in."
            )
        
        return attrs


class FilmProposalSerializer(serializers.Serializer):
    tmdb_id = serializers.IntegerField()
    group_id = serializers.IntegerField()