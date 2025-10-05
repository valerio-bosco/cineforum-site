from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from .models import User


@shared_task
def send_verification_email(user_id):
    """Send email verification link to user"""
    try:
        user = User.objects.get(id=user_id)
        verification_link = f"{settings.FRONTEND_URL}/verify-email/{user.email_verification_token}"
        
        subject = 'Verify Your Cineforum Account'
        message = f"""
        Hello {user.username},
        
        Thank you for registering with Cineforum!
        
        Please click the link below to verify your email address:
        {verification_link}
        
        This link will expire in 24 hours.
        
        If you didn't create this account, please ignore this email.
        
        Best regards,
        The Cineforum Team
        """
        
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        
        return f"Verification email sent to {user.email}"
    except User.DoesNotExist:
        return f"User with id {user_id} not found"


@shared_task
def delete_unverified_users():
    """Delete users who haven't verified their email within 24 hours"""
    cutoff_time = timezone.now() - timedelta(days=1)
    
    unverified_users = User.objects.filter(
        is_email_verified=False,
        email_verification_sent_at__lt=cutoff_time
    )
    
    count = unverified_users.count()
    unverified_users.delete()
    
    return f"Deleted {count} unverified users"


@shared_task
def send_group_notification(group_id, message):
    """Send notification to all group members"""
    from .models import Group, GroupMembership
    
    try:
        group = Group.objects.get(id=group_id)
        members = User.objects.filter(
            groupmembership__group=group,
            groupmembership__status='approved'
        )
        
        recipient_emails = [member.email for member in members]
        
        subject = f'Cineforum Update: {group.name}'
        
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            recipient_emails,
            fail_silently=False,
        )
        
        return f"Notification sent to {len(recipient_emails)} members of {group.name}"
    except Group.DoesNotExist:
        return f"Group with id {group_id} not found"