from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.utils import timezone
from .models import User, AccountType, Transaction, AuditLog
import json

@receiver(post_save, sender=User)
def create_audit_log_on_user_save(sender, instance, created, **kwargs):
    if not kwargs.get('raw', False):  # Skip for fixtures
        action = 'create' if created else 'update'
        AuditLog.objects.create(
            admin_user=instance if instance.is_staff else None,
            action_type=action,
            target_model='User',
            target_object_id=instance.id,
            target_object_repr=str(instance),
            description=f'User {"created" if created else "updated"}: {instance.full_name} ({instance.email})'
        )

@receiver(post_save, sender=AccountType)
def create_audit_log_on_account_type_save(sender, instance, created, **kwargs):
    if not kwargs.get('raw', False):
        action = 'create' if created else 'update'
        AuditLog.objects.create(
            admin_user=None,  # Will be set in view
            action_type=action,
            target_model='AccountType',
            target_object_id=instance.id,
            target_object_repr=str(instance),
            description=f'Account Type {"created" if created else "updated"}: {instance.name}'
        )

@receiver(post_save, sender=Transaction)
def create_audit_log_on_transaction(sender, instance, created, **kwargs):
    if created and not kwargs.get('raw', False):
        AuditLog.objects.create(
            admin_user=None,
            action_type='create',
            target_model='Transaction',
            target_object_id=instance.id,
            target_object_repr=str(instance),
            description=f'Transaction created: {instance.transaction_id} - ₹{instance.amount} - {instance.transaction_type}'
        )

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    AuditLog.objects.create(
        admin_user=user if user.is_staff else None,
        action_type='login',
        target_model='User',
        target_object_id=user.id,
        target_object_repr=str(user),
        description=f'User logged in: {user.email}',
        ip_address=request.META.get('REMOTE_ADDR')
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    if user:
        AuditLog.objects.create(
            admin_user=user if user.is_staff else None,
            action_type='logout',
            target_model='User',
            target_object_id=user.id,
            target_object_repr=str(user),
            description=f'User logged out: {user.email}',
            ip_address=request.META.get('REMOTE_ADDR')
        )

# Initialize signals
def ready(self):
    import bankapp.signals