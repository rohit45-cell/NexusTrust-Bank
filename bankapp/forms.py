from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError
from .models import User, AccountType, Contact, Transaction
from decimal import Decimal
import re

class SignUpForm(forms.ModelForm):
    """User registration form with Indian KYC validation"""
    
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}),
        help_text='Password must be at least 8 characters long'
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'})
    )
    
    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone', 'aadhaar', 'pan', 'address', 'city', 'state', 'pincode', 'account_type']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10-digit mobile number'}),
            'aadhaar': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12-digit Aadhaar number (optional)'}),
            'pan': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PAN card number (optional)'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter full address', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '6-digit pincode'}),
            'account_type': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def clean_password2(self):
        """Validate that passwords match"""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError('Passwords do not match')
        
        if password1 and len(password1) < 8:
            raise ValidationError('Password must be at least 8 characters long')
        
        return password2
    
    def clean_phone(self):
        """Validate Indian phone number (10 digits, starts with 6-9)"""
        phone = self.cleaned_data.get('phone')
        if phone and not re.match(r'^[6-9]\d{9}$', phone):
            raise ValidationError('Enter a valid Indian mobile number (10 digits starting with 6-9)')
        return phone
    
    def clean_pincode(self):
        """Validate 6-digit pincode"""
        pincode = self.cleaned_data.get('pincode')
        if pincode and not re.match(r'^\d{6}$', pincode):
            raise ValidationError('Enter a valid 6-digit pincode')
        return pincode
    
    def clean_aadhaar(self):
        """Validate 12-digit Aadhaar number (optional)"""
        aadhaar = self.cleaned_data.get('aadhaar')
        if aadhaar and not re.match(r'^\d{12}$', aadhaar):
            raise ValidationError('Enter a valid 12-digit Aadhaar number')
        return aadhaar
    
    def clean_pan(self):
        """Validate PAN card format (optional)"""
        pan = self.cleaned_data.get('pan')
        if pan and not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', pan):
            raise ValidationError('Enter a valid PAN card number (e.g., ABCDE1234F)')
        return pan
    
    def save(self, commit=True):
        """Create user with hashed password"""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        
        # Ensure account_type is set (fallback to Savings if none selected)
        if not user.account_type:
            from .models import AccountType
            default_account, _ = AccountType.objects.get_or_create(
                name='Savings Account',
                defaults={
                    'category': 'savings',
                    'minimum_balance': 1000,
                    'interest_rate': 3.5,
                    'overdraft_limit': 0
                }
            )
            user.account_type = default_account
        
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    """User login form"""
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'})
    )


class UserProfileForm(forms.ModelForm):
    """User profile edit form"""
    
    class Meta:
        model = User
        fields = ['full_name', 'phone', 'address', 'city', 'state', 'pincode', 'profile_picture']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def clean_phone(self):
        """Validate Indian phone number"""
        phone = self.cleaned_data.get('phone')
        if phone and not re.match(r'^[6-9]\d{9}$', phone):
            raise ValidationError('Enter a valid Indian mobile number')
        return phone


class DepositForm(forms.Form):
    """Deposit money form"""
    
    amount = forms.DecimalField(
        min_value=1,
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount'})
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Add note (optional)', 'rows': 2})
    )


class WithdrawForm(forms.Form):
    """Withdraw money form"""
    
    amount = forms.DecimalField(
        min_value=1,
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount'})
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Add note (optional)', 'rows': 2})
    )


class TransferForm(forms.Form):
    """Transfer money form"""
    
    receiver_account = forms.CharField(
        max_length=16,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter receiver account number'})
    )
    amount = forms.DecimalField(
        min_value=1,
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount'})
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Add note (optional)', 'rows': 2})
    )
    
    def clean_receiver_account(self):
        """Validate receiver account exists and is active"""
        account = self.cleaned_data.get('receiver_account')
        try:
            receiver = User.objects.get(account_number=account, is_active=True, is_frozen=False)
        except User.DoesNotExist:
            raise ValidationError('Invalid account number or account not active')
        return account


class ContactForm(forms.ModelForm):
    """Contact us form"""
    
    class Meta:
        model = Contact
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10-digit mobile number'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter subject'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter your message', 'rows': 5}),
        }
    
    def clean_phone(self):
        """Validate Indian phone number"""
        phone = self.cleaned_data.get('phone')
        if phone and not re.match(r'^[6-9]\d{9}$', phone):
            raise ValidationError('Enter a valid Indian mobile number')
        return phone


class CustomPasswordChangeForm(PasswordChangeForm):
    """Custom password change form with Bootstrap styling"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class AccountTypeForm(forms.ModelForm):
    """Admin form for managing account types"""
    
    class Meta:
        model = AccountType
        fields = ['name', 'category', 'minimum_balance', 'interest_rate', 'overdraft_limit', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Premium Savings'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'minimum_balance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'interest_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'overdraft_limit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AdminUserEditForm(forms.ModelForm):
    """Admin form for editing users"""
    
    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone', 'address', 'city', 'state', 'pincode', 
                 'account_type', 'balance', 'is_active', 'is_frozen', 'is_staff']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
            'account_type': forms.Select(attrs={'class': 'form-select'}),
            'balance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_frozen': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ReportDateRangeForm(forms.Form):
    """Form for selecting date range for reports"""
    
    date_from = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False
    )
    date_to = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False
    )
    transaction_type = forms.ChoiceField(
        choices=[('', 'All')] + Transaction.TRANSACTION_TYPES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False
    )
