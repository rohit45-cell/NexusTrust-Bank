from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator, MinValueValidator
from django.utils import timezone
import random
import string
from datetime import datetime, timedelta




# Indian Phone Number Validator
phone_validator = RegexValidator(
    regex=r'^[6-9]\d{9}$',
    message="Enter a valid Indian mobile number (10 digits starting with 6-9)"
)

# PAN Card Validator
pan_validator = RegexValidator(
    regex=r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$',
    message="Enter a valid PAN Card number"
)

# Aadhaar Validator
aadhaar_validator = RegexValidator(
    regex=r'^\d{12}$',
    message="Enter a valid 12-digit Aadhaar number"
)

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)

class AccountType(models.Model):
    ACCOUNT_CATEGORIES = [
        ('savings', 'Savings Account'),
        ('current', 'Current Account'),
        ('fixed', 'Fixed Deposit'),
        ('recurring', 'Recurring Deposit'),
    ]
    
    name = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=20, choices=ACCOUNT_CATEGORIES, default='savings')
    minimum_balance = models.DecimalField(max_digits=12, decimal_places=2, default=1000.00)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=3.50)
    overdraft_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.get_category_display()}"
    
    class Meta:
        verbose_name = "Account Type"
        verbose_name_plural = "Account Types"

class User(AbstractBaseUser, PermissionsMixin):
    # Personal Information
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=10, validators=[phone_validator])
    
    # Optional Indian KYC
    aadhaar = models.CharField(max_length=12, validators=[aadhaar_validator], blank=True, null=True, unique=True)
    pan = models.CharField(max_length=10, validators=[pan_validator], blank=True, null=True, unique=True)
    
    # Address
    address = models.TextField(max_length=500)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pincode = models.CharField(max_length=6, validators=[RegexValidator(r'^\d{6}$')])
    
    # Banking Details
    account_number = models.CharField(max_length=16, unique=True, blank=True, null=True)
    ifsc_code = models.CharField(max_length=11, unique=True, blank=True, null=True)
    account_type = models.ForeignKey(AccountType, on_delete=models.SET_NULL, null=True, related_name='users')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Profile
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_frozen = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    # Timestamps
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'phone', 'address', 'city', 'state', 'pincode']
    
    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = self.generate_account_number()
        if not self.ifsc_code:
            self.ifsc_code = self.generate_ifsc_code()
        super().save(*args, **kwargs)
    
    def generate_account_number(self):
        prefix = "NTB"  # NexusTrust Bank
        timestamp = datetime.now().strftime("%y%m%d%H%M%S")
        random_digits = ''.join(random.choices(string.digits, k=4))
        return f"{prefix}{timestamp}{random_digits}"[:16]
    
    def generate_ifsc_code(self):
        return f"NTB{random.choice(string.digits)}{random.choice(string.ascii_uppercase)}{random.choice(string.ascii_uppercase)}{random.choice(string.ascii_uppercase)}{random.choice(string.digits)}"[:11]
    
    def get_account_type_name(self):
        """Safely get account type name"""
        return self.account_type.name if self.account_type else "Savings Account"
    
    def get_account_type_category(self):
        """Safely get account type category"""
        return self.account_type.category if self.account_type else "savings"
    
    def get_minimum_balance(self):
        """Safely get minimum balance"""
        return float(self.account_type.minimum_balance) if self.account_type else 1000.0
    
    def get_interest_rate(self):
        """Safely get interest rate"""
        return float(self.account_type.interest_rate) if self.account_type else 3.5
    
    def get_overdraft_limit(self):
        """Safely get overdraft limit"""
        return float(self.account_type.overdraft_limit) if self.account_type else 0.0
    
    def can_withdraw(self, amount):
        """Check if withdrawal is allowed"""
        if self.is_frozen:
            return False, "Account is frozen"
        
        if not self.account_type:
            # If no account type, just check sufficient balance
            if float(self.balance) >= float(amount):
                return True, "Approved"
            else:
                return False, "Insufficient balance"
        
        amount = float(amount)
        balance = float(self.balance)
        
        if self.account_type.category == 'savings':
            min_balance = float(self.account_type.minimum_balance)
            if balance - amount < min_balance:
                return False, f"Cannot withdraw below minimum balance of ₹{min_balance}"
        elif self.account_type.category == 'current':
            overdraft = float(self.account_type.overdraft_limit)
            if balance - amount < -overdraft:
                return False, f"Overdraft limit of ₹{overdraft} exceeded"
        
        if amount > balance and not (self.account_type.category == 'current' and balance + overdraft >= amount):
            return False, "Insufficient balance"
        
        return True, "Approved"
    
    def get_available_balance(self):
        """Get available balance considering account type rules"""
        if not self.account_type:
            return float(self.balance)
        
        if self.account_type.category == 'current':
            return float(self.balance) + float(self.account_type.overdraft_limit)
        return float(self.balance)
    
    def __str__(self):
        return f"{self.full_name} - {self.account_number}"
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdraw', 'Withdrawal'),
        ('transfer', 'Transfer'),
        ('rollback', 'Rollback'),
        ('interest', 'Interest Credit'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('rolled_back', 'Rolled Back'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    transaction_id = models.CharField(max_length=20, unique=True, blank=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(1)])
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_rolled_back = models.BooleanField(default=False)
    
    # For transfer transactions
    receiver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_transactions')
    
    # Metadata
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()
        super().save(*args, **kwargs)
    
    def generate_transaction_id(self):
        timestamp = datetime.now().strftime("%y%m%d%H%M%S")
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"TXN{timestamp}{random_str}"
    
    def __str__(self):
        return f"{self.transaction_id} - {self.user.full_name} - ₹{self.amount} - {self.transaction_type}"
    
    class Meta:
        ordering = ['-created_at']

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=10, validators=[phone_validator])
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.subject}"
    
    class Meta:
        ordering = ['-created_at']

class AuditLog(models.Model):
    ACTION_TYPES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('rollback', 'Rollback'),
        ('freeze', 'Freeze Account'),
        ('unfreeze', 'Unfreeze Account'),
        ('password_reset', 'Password Reset'),
    ]
    
    admin_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    target_model = models.CharField(max_length=50)
    target_object_id = models.PositiveIntegerField()
    target_object_repr = models.CharField(max_length=200)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.timestamp} - {self.admin_user} - {self.action_type} - {self.target_model}"
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"

class InterestHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interest_history')
    account_type = models.ForeignKey(AccountType, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    period_start = models.DateField()
    period_end = models.DateField()
    credited_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.full_name} - ₹{self.amount} - {self.period_end}"
    
    class Meta:
        ordering = ['-credited_at']