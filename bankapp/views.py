from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction as db_transaction
from django.db.models import Q, Sum, Count
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json

from .models import User, AccountType, Transaction, Contact, AuditLog, InterestHistory
from .forms import (
    SignUpForm, LoginForm, UserProfileForm, DepositForm, WithdrawForm,
    TransferForm, ContactForm, CustomPasswordChangeForm, AccountTypeForm,
    AdminUserEditForm, ReportDateRangeForm
)
from .decorators import customer_required, admin_required, superuser_required, account_frozen_check, account_active_required
from .utils import (
    send_transaction_notification, generate_csv_report, generate_pdf_report,
    get_dashboard_stats, get_chart_data, calculate_interest
)

# ============ PUBLIC VIEWS ============

def home(request):
    try:
        total_users = User.objects.filter(is_active=True).count()
        total_transactions = Transaction.objects.count()
        total_account_types = AccountType.objects.filter(is_active=True).count()
    except Exception:
        total_users = 0
        total_transactions = 0
        total_account_types = 0

    context = {
        'total_users': total_users,
        'total_transactions': total_transactions,
        'total_account_types': total_account_types,
    }
    return render(request, 'bankapp/home.html', context)


def about(request):
    """About page"""
    return render(request, 'bankapp/about.html')

def services(request):
    """Services page"""
    account_types = AccountType.objects.filter(is_active=True)
    return render(request, 'bankapp/services.html', {'account_types': account_types})

def contact(request):
    """Contact page"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent. We will contact you soon.')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'bankapp/contact.html', {'form': form})

def terms(request):
    """Terms and conditions"""
    return render(request, 'bankapp/terms.html')

def privacy(request):
    """Privacy policy"""
    return render(request, 'bankapp/privacy.html')

# ============ AUTHENTICATION VIEWS ============

def signup(request):
    """User registration"""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = True
            user.save()
            login(request, user)
            messages.success(request, f'Welcome to NexusTrust Bank, {user.full_name}! Your account has been created successfully.')
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'bankapp/signup.html', {'form': form})

def user_login(request):
    """User login"""
    if request.user.is_authenticated:
        # Redirect based on user type
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                if user.is_active:
                    if not user.is_frozen:
                        login(request, user)
                        messages.success(request, f'Welcome back, {user.full_name}!')
                        # Redirect based on user type
                        if user.is_staff:
                            return redirect('admin_dashboard')
                        return redirect('dashboard')
                    else:
                        messages.error(request, 'Your account is frozen. Please contact customer support.')
                else:
                    messages.error(request, 'Your account is inactive. Please contact support.')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    return render(request, 'bankapp/login.html', {'form': form})

def user_logout(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

class CustomPasswordChangeView(auth_views.PasswordChangeView):
    """Custom password change view"""
    template_name = 'bankapp/password_change.html'
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy('profile')
    
    def form_valid(self, form):
        messages.success(self.request, 'Your password was changed successfully.')
        return super().form_valid(form)

# ============ USER DASHBOARD VIEWS - CUSTOMERS ONLY ============
# Staff members CANNOT access these views

@customer_required
@account_active_required
@account_frozen_check
def dashboard(request):
    """User dashboard - CUSTOMERS ONLY"""
    stats = get_dashboard_stats(request.user)
    chart_data = get_chart_data(request.user)
    recent_transactions = request.user.transactions.filter(status='completed')[:10]
    
    context = {
        'stats': stats,
        'chart_data': json.dumps(chart_data),
        'recent_transactions': recent_transactions,
        'user': request.user,
    }
    return render(request, 'bankapp/dashboard.html', context)

@customer_required
@account_active_required
def profile(request):
    """User profile - CUSTOMERS ONLY"""
    return render(request, 'bankapp/profile.html', {'user': request.user})

@customer_required
@account_active_required
@account_frozen_check
def edit_profile(request):
    """Edit user profile - CUSTOMERS ONLY"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'bankapp/edit_profile.html', {'form': form})

@customer_required
@account_active_required
@account_frozen_check
@db_transaction.atomic
def deposit(request):
    """Deposit money - CUSTOMERS ONLY"""
    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            description = form.cleaned_data['description']
            
            request.user.balance += amount
            request.user.save()
            
            transaction = Transaction.objects.create(
                user=request.user,
                transaction_type='deposit',
                amount=amount,
                balance_after=request.user.balance,
                description=description,
                status='completed',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            send_transaction_notification(request.user, transaction, 'deposit')
            messages.success(request, f'Successfully deposited ₹{amount}.')
            return redirect('transaction_detail', transaction_id=transaction.transaction_id)
    else:
        form = DepositForm()
    return render(request, 'bankapp/deposit.html', {'form': form})

@customer_required
@account_active_required
@account_frozen_check
@db_transaction.atomic
def withdraw(request):
    """Withdraw money - CUSTOMERS ONLY"""
    if request.method == 'POST':
        form = WithdrawForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            description = form.cleaned_data['description']
            
            can_withdraw, message = request.user.can_withdraw(amount)
            if not can_withdraw:
                messages.error(request, message)
                return redirect('withdraw')
            
            request.user.balance -= amount
            request.user.save()
            
            transaction = Transaction.objects.create(
                user=request.user,
                transaction_type='withdraw',
                amount=amount,
                balance_after=request.user.balance,
                description=description,
                status='completed',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            send_transaction_notification(request.user, transaction, 'withdrawal')
            messages.success(request, f'Successfully withdrew ₹{amount}.')
            return redirect('transaction_detail', transaction_id=transaction.transaction_id)
    else:
        form = WithdrawForm()
    return render(request, 'bankapp/withdraw.html', {'form': form})

@customer_required
@account_active_required
@account_frozen_check
@db_transaction.atomic
def transfer(request):
    """Transfer money - CUSTOMERS ONLY"""
    if request.method == 'POST':
        form = TransferForm(request.POST)
        if form.is_valid():
            receiver_account = form.cleaned_data['receiver_account']
            amount = form.cleaned_data['amount']
            description = form.cleaned_data['description']
            
            receiver = get_object_or_404(User, account_number=receiver_account, is_active=True, is_frozen=False)
            
            if receiver == request.user:
                messages.error(request, 'Cannot transfer to your own account.')
                return redirect('transfer')
            
            can_withdraw, message = request.user.can_withdraw(amount)
            if not can_withdraw:
                messages.error(request, message)
                return redirect('transfer')
            
            request.user.balance -= amount
            request.user.save()
            receiver.balance += amount
            receiver.save()
            
            sender_transaction = Transaction.objects.create(
                user=request.user,
                transaction_type='transfer',
                amount=amount,
                balance_after=request.user.balance,
                description=f'Transfer to {receiver.full_name} ({receiver.account_number}) - {description}',
                status='completed',
                receiver=receiver,
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            receiver_transaction = Transaction.objects.create(
                user=receiver,
                transaction_type='transfer',
                amount=amount,
                balance_after=receiver.balance,
                description=f'Transfer from {request.user.full_name} ({request.user.account_number}) - {description}',
                status='completed',
                receiver=request.user,
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            send_transaction_notification(request.user, sender_transaction, 'transfer sent')
            send_transaction_notification(receiver, receiver_transaction, 'transfer received')
            
            messages.success(request, f'Successfully transferred ₹{amount} to {receiver.full_name}.')
            return redirect('transaction_detail', transaction_id=sender_transaction.transaction_id)
    else:
        form = TransferForm()
    return render(request, 'bankapp/transfer.html', {'form': form})

@customer_required
@account_active_required
def transaction_history(request):
    """View transaction history - CUSTOMERS ONLY"""
    transactions = request.user.transactions.filter(status='completed').order_by('-created_at')
    
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    t_type = request.GET.get('type')
    
    if date_from:
        transactions = transactions.filter(created_at__date__gte=date_from)
    if date_to:
        transactions = transactions.filter(created_at__date__lte=date_to)
    if t_type:
        transactions = transactions.filter(transaction_type=t_type)
    
    search = request.GET.get('search')
    if search:
        transactions = transactions.filter(
            Q(transaction_id__icontains=search) |
            Q(description__icontains=search) |
            Q(amount__icontains=search)
        )
    
    paginator = Paginator(transactions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'transactions': page_obj,
        'transaction_types': Transaction.TRANSACTION_TYPES,
    }
    return render(request, 'bankapp/transaction_history.html', context)

@customer_required
@account_active_required
def transaction_detail(request, transaction_id):
    """View transaction details - CUSTOMERS ONLY"""
    transaction = get_object_or_404(Transaction, transaction_id=transaction_id)
    
    if transaction.user != request.user:
        messages.error(request, 'You do not have permission to view this transaction.')
        return redirect('transaction_history')
    
    return render(request, 'bankapp/transaction_detail.html', {'transaction': transaction})

@customer_required
@account_active_required
def download_report(request):
    """Download transaction report - CUSTOMERS ONLY"""
    transactions = request.user.transactions.filter(status='completed')
    
    if request.method == 'POST':
        form = ReportDateRangeForm(request.POST)
        if form.is_valid():
            date_from = form.cleaned_data['date_from']
            date_to = form.cleaned_data['date_to']
            t_type = form.cleaned_data['transaction_type']
            
            if date_from:
                transactions = transactions.filter(created_at__date__gte=date_from)
            if date_to:
                transactions = transactions.filter(created_at__date__lte=date_to)
            if t_type:
                transactions = transactions.filter(transaction_type=t_type)
            
            fields = ['transaction_id', 'transaction_type', 'amount', 'balance_after', 'description', 'created_at']
            
            if request.POST.get('format') == 'csv':
                csv_data = generate_csv_report(transactions, fields, f'transaction_report_{request.user.account_number}')
                response = HttpResponse(csv_data, content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="transaction_report_{datetime.now().strftime("%Y%m%d")}.csv"'
                return response
            else:
                pdf_buffer = generate_pdf_report(transactions, f'Transaction Report - {request.user.full_name}', fields)
                response = HttpResponse(pdf_buffer, content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="transaction_report_{datetime.now().strftime("%Y%m%d")}.pdf"'
                return response
    else:
        form = ReportDateRangeForm()
    
    return render(request, 'bankapp/download_report.html', {'form': form})

# ============ BANK ADMINISTRATOR VIEWS - STAFF ONLY ============
# Regular customers CANNOT access these views

@admin_required
def admin_dashboard(request):
    """Admin dashboard - STAFF ONLY"""
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    frozen_users = User.objects.filter(is_frozen=True).count()
    
    total_transactions = Transaction.objects.count()
    total_deposits = Transaction.objects.filter(transaction_type='deposit').aggregate(Sum('amount'))['amount__sum'] or 0
    total_withdrawals = Transaction.objects.filter(transaction_type='withdraw').aggregate(Sum('amount'))['amount__sum'] or 0
    
    total_contacts = Contact.objects.count()
    pending_contacts = Contact.objects.filter(is_resolved=False).count()
    
    recent_transactions = Transaction.objects.order_by('-created_at')[:10]
    recent_users = User.objects.order_by('-date_joined')[:10]
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'frozen_users': frozen_users,
        'total_transactions': total_transactions,
        'total_deposits': total_deposits,
        'total_withdrawals': total_withdrawals,
        'total_contacts': total_contacts,
        'pending_contacts': pending_contacts,
        'recent_transactions': recent_transactions,
        'recent_users': recent_users,
    }
    return render(request, 'bankapp/admin_dashboard.html', context)

@admin_required
def manage_users(request):
    """Manage users - STAFF ONLY"""
    users = User.objects.all().order_by('-date_joined')
    
    status = request.GET.get('status')
    if status == 'active':
        users = users.filter(is_active=True, is_frozen=False)
    elif status == 'frozen':
        users = users.filter(is_frozen=True)
    elif status == 'inactive':
        users = users.filter(is_active=False)
    
    search = request.GET.get('search')
    if search:
        users = users.filter(
            Q(account_number__icontains=search) |
            Q(full_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )
    
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'bankapp/manage_users.html', {'users': page_obj})

@admin_required
def manage_user_detail(request, user_id):
    """Manage individual user - STAFF ONLY"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = AdminUserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            
            AuditLog.objects.create(
                admin_user=request.user,
                action_type='update',
                target_model='User',
                target_object_id=user.id,
                target_object_repr=str(user),
                description=f'User updated by admin: {user.full_name}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f'User {user.full_name} updated successfully.')
            return redirect('manage_users')
    else:
        form = AdminUserEditForm(instance=user)
    
    transactions = user.transactions.order_by('-created_at')[:20]
    
    return render(request, 'bankapp/manage_user_detail.html', {
        'form': form,
        'target_user': user,
        'transactions': transactions
    })

@admin_required
def toggle_freeze_account(request, user_id):
    """Freeze/Unfreeze user account - STAFF ONLY"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.is_frozen = not user.is_frozen
        user.save()
        
        AuditLog.objects.create(
            admin_user=request.user,
            action_type='freeze' if user.is_frozen else 'unfreeze',
            target_model='User',
            target_object_id=user.id,
            target_object_repr=str(user),
            description=f'Account {"frozen" if user.is_frozen else "unfrozen"} by admin',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, f'Account for {user.full_name} has been {"frozen" if user.is_frozen else "unfrozen"}.')
    
    return redirect('manage_user_detail', user_id=user.id)

@admin_required
def admin_reset_password(request, user_id):
    """Admin reset user password - STAFF ONLY"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        import random
        import string
        new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        
        user.set_password(new_password)
        user.save()
        
        AuditLog.objects.create(
            admin_user=request.user,
            action_type='password_reset',
            target_model='User',
            target_object_id=user.id,
            target_object_repr=str(user),
            description=f'Password reset by admin',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, f'Password reset successful. New password: {new_password}')
        
    return redirect('manage_user_detail', user_id=user.id)

@admin_required
def manage_account_types(request):
    """Manage account types - STAFF ONLY"""
    account_types = AccountType.objects.all()
    return render(request, 'bankapp/manage_account_types.html', {'account_types': account_types})

@admin_required
def add_account_type(request):
    """Add new account type - STAFF ONLY"""
    if request.method == 'POST':
        form = AccountTypeForm(request.POST)
        if form.is_valid():
            account_type = form.save()
            
            AuditLog.objects.create(
                admin_user=request.user,
                action_type='create',
                target_model='AccountType',
                target_object_id=account_type.id,
                target_object_repr=str(account_type),
                description=f'Account type created: {account_type.name}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f'Account type {account_type.name} created successfully.')
            return redirect('manage_account_types')
    else:
        form = AccountTypeForm()
    
    return render(request, 'bankapp/add_account_type.html', {'form': form})

@admin_required
def edit_account_type(request, pk):
    """Edit account type - STAFF ONLY"""
    account_type = get_object_or_404(AccountType, pk=pk)
    
    if request.method == 'POST':
        form = AccountTypeForm(request.POST, instance=account_type)
        if form.is_valid():
            form.save()
            
            AuditLog.objects.create(
                admin_user=request.user,
                action_type='update',
                target_model='AccountType',
                target_object_id=account_type.id,
                target_object_repr=str(account_type),
                description=f'Account type updated: {account_type.name}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f'Account type {account_type.name} updated successfully.')
            return redirect('manage_account_types')
    else:
        form = AccountTypeForm(instance=account_type)
    
    return render(request, 'bankapp/edit_account_type.html', {'form': form, 'account_type': account_type})

@admin_required
def delete_account_type(request, pk):
    """Delete account type - STAFF ONLY"""
    account_type = get_object_or_404(AccountType, pk=pk)
    
    if account_type.users.exists():
        messages.error(request, f'Cannot delete {account_type.name} as it has users assigned.')
        return redirect('manage_account_types')
    
    if request.method == 'POST':
        AuditLog.objects.create(
            admin_user=request.user,
            action_type='delete',
            target_model='AccountType',
            target_object_id=account_type.id,
            target_object_repr=str(account_type),
            description=f'Account type deleted: {account_type.name}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        account_type.delete()
        messages.success(request, 'Account type deleted successfully.')
        return redirect('manage_account_types')
    
    return render(request, 'bankapp/delete_account_type.html', {'account_type': account_type})

@admin_required
def manage_transactions(request):
    """Manage all transactions - STAFF ONLY"""
    transactions = Transaction.objects.all().order_by('-created_at')
    
    status = request.GET.get('status')
    if status:
        transactions = transactions.filter(status=status)
    
    t_type = request.GET.get('type')
    if t_type:
        transactions = transactions.filter(transaction_type=t_type)
    
    search = request.GET.get('search')
    if search:
        transactions = transactions.filter(
            Q(transaction_id__icontains=search) |
            Q(user__full_name__icontains=search) |
            Q(user__account_number__icontains=search) |
            Q(description__icontains=search)
        )
    
    paginator = Paginator(transactions, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'transactions': page_obj,
        'transaction_types': Transaction.TRANSACTION_TYPES,
        'status_choices': Transaction.STATUS_CHOICES,
    }
    return render(request, 'bankapp/manage_transactions.html', context)

@admin_required
@db_transaction.atomic
def rollback_transaction(request, transaction_id):
    """Rollback a transaction - STAFF ONLY"""
    transaction = get_object_or_404(Transaction, id=transaction_id)
    
    if transaction.is_rolled_back:
        messages.error(request, 'This transaction has already been rolled back.')
        return redirect('manage_transactions')
    
    if transaction.transaction_type == 'rollback':
        messages.error(request, 'Cannot rollback a rollback transaction.')
        return redirect('manage_transactions')
    
    if request.method == 'POST':
        user = transaction.user
        
        if transaction.transaction_type in ['deposit', 'transfer']:
            if transaction.transaction_type == 'deposit':
                user.balance -= transaction.amount
                description = f'Rollback of deposit: {transaction.transaction_id}'
            else:
                user.balance -= transaction.amount
                description = f'Rollback of received transfer: {transaction.transaction_id}'
        else:
            user.balance += transaction.amount
            description = f'Rollback of {transaction.transaction_type}: {transaction.transaction_id}'
        
        user.save()
        
        transaction.is_rolled_back = True
        transaction.status = 'rolled_back'
        transaction.save()
        
        rollback = Transaction.objects.create(
            user=user,
            transaction_type='rollback',
            amount=transaction.amount,
            balance_after=user.balance,
            description=description,
            status='completed',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        AuditLog.objects.create(
            admin_user=request.user,
            action_type='rollback',
            target_model='Transaction',
            target_object_id=transaction.id,
            target_object_repr=str(transaction),
            description=f'Transaction rolled back: {transaction.transaction_id}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, f'Transaction {transaction.transaction_id} rolled back successfully.')
        return redirect('manage_transactions')
    
    return render(request, 'bankapp/rollback_transaction.html', {'transaction': transaction})

@admin_required
def edit_transaction(request, transaction_id):
    """Edit transaction details - STAFF ONLY"""
    transaction = get_object_or_404(Transaction, id=transaction_id)
    
    if request.method == 'POST':
        transaction.description = request.POST.get('description', transaction.description)
        transaction.status = request.POST.get('status', transaction.status)
        transaction.save()
        
        AuditLog.objects.create(
            admin_user=request.user,
            action_type='update',
            target_model='Transaction',
            target_object_id=transaction.id,
            target_object_repr=str(transaction),
            description=f'Transaction updated by admin: {transaction.transaction_id}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, 'Transaction updated successfully.')
        return redirect('manage_transactions')
    
    return render(request, 'bankapp/edit_transaction.html', {'transaction': transaction})

@admin_required
def delete_transaction(request, transaction_id):
    """Delete transaction - STAFF ONLY"""
    transaction = get_object_or_404(Transaction, id=transaction_id)
    
    if request.method == 'POST':
        AuditLog.objects.create(
            admin_user=request.user,
            action_type='delete',
            target_model='Transaction',
            target_object_id=transaction.id,
            target_object_repr=str(transaction),
            description=f'Transaction deleted by admin: {transaction.transaction_id}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        transaction.delete()
        messages.success(request, 'Transaction deleted successfully.')
        return redirect('manage_transactions')
    
    return render(request, 'bankapp/delete_transaction.html', {'transaction': transaction})

@admin_required
def audit_logs(request):
    """View audit logs - STAFF ONLY"""
    logs = AuditLog.objects.all().order_by('-timestamp')
    
    action = request.GET.get('action')
    if action:
        logs = logs.filter(action_type=action)
    
    user = request.GET.get('user')
    if user:
        logs = logs.filter(admin_user__email__icontains=user)
    
    date_from = request.GET.get('date_from')
    if date_from:
        logs = logs.filter(timestamp__date__gte=date_from)
    
    date_to = request.GET.get('date_to')
    if date_to:
        logs = logs.filter(timestamp__date__lte=date_to)
    
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'logs': page_obj,
        'action_types': AuditLog.ACTION_TYPES,
    }
    return render(request, 'bankapp/audit_logs.html', context)

@admin_required
def reports(request):
    """Generate reports - STAFF ONLY"""
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if not date_to:
        date_to = timezone.now().date()
    if not date_from:
        date_from = date_to - timedelta(days=30)
    
    total_users = User.objects.filter(date_joined__date__gte=date_from, date_joined__date__lte=date_to).count()
    new_users = User.objects.filter(date_joined__date__gte=date_from, date_joined__date__lte=date_to).count()
    
    transactions = Transaction.objects.filter(
        created_at__date__gte=date_from,
        created_at__date__lte=date_to,
        status='completed'
    )
    
    transaction_summary = []
    for t_type, t_label in Transaction.TRANSACTION_TYPES:
        type_transactions = transactions.filter(transaction_type=t_type)
        total = type_transactions.aggregate(Sum('amount'))['amount__sum'] or 0
        count = type_transactions.count()
        transaction_summary.append({
            'type': t_label,
            'count': count,
            'total': total
        })
    
    account_distribution = []
    for account_type in AccountType.objects.all():
        count = User.objects.filter(account_type=account_type).count()
        total_balance = User.objects.filter(account_type=account_type).aggregate(Sum('balance'))['balance__sum'] or 0
        account_distribution.append({
            'name': account_type.name,
            'count': count,
            'total_balance': total_balance
        })
    
    context = {
        'date_from': date_from,
        'date_to': date_to,
        'total_users': total_users,
        'new_users': new_users,
        'transaction_summary': transaction_summary,
        'account_distribution': account_distribution,
        'total_transactions': transactions.count(),
        'total_deposits': transactions.filter(transaction_type='deposit').aggregate(Sum('amount'))['amount__sum'] or 0,
        'total_withdrawals': transactions.filter(transaction_type='withdraw').aggregate(Sum('amount'))['amount__sum'] or 0,
        'total_transfers': transactions.filter(transaction_type='transfer').count(),
    }
    return render(request, 'bankapp/reports.html', context)

@admin_required
def export_csv(request):
    """Export data as CSV - STAFF ONLY"""
    data_type = request.GET.get('type', 'transactions')
    
    if data_type == 'users':
        queryset = User.objects.all()
        fields = ['account_number', 'full_name', 'email', 'phone', 'account_type', 'balance', 'is_active', 'date_joined']
        filename = 'users_report'
    elif data_type == 'transactions':
        queryset = Transaction.objects.all()
        fields = ['transaction_id', 'user', 'transaction_type', 'amount', 'balance_after', 'status', 'created_at']
        filename = 'transactions_report'
    elif data_type == 'contacts':
        queryset = Contact.objects.all()
        fields = ['name', 'email', 'phone', 'subject', 'is_resolved', 'created_at']
        filename = 'contacts_report'
    else:
        return redirect('reports')
    
    csv_data = generate_csv_report(queryset, fields, filename)
    response = HttpResponse(csv_data, content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}_{datetime.now().strftime("%Y%m%d")}.csv"'
    return response

@admin_required
def export_pdf(request):
    """Export data as PDF - STAFF ONLY"""
    data_type = request.GET.get('type', 'transactions')
    
    if data_type == 'users':
        queryset = User.objects.all()
        fields = ['account_number', 'full_name', 'email', 'phone', 'account_type', 'balance', 'is_active', 'date_joined']
        title = 'Users Report'
    elif data_type == 'transactions':
        queryset = Transaction.objects.all()
        fields = ['transaction_id', 'user', 'transaction_type', 'amount', 'balance_after', 'status', 'created_at']
        title = 'Transactions Report'
    elif data_type == 'contacts':
        queryset = Contact.objects.all()
        fields = ['name', 'email', 'phone', 'subject', 'is_resolved', 'created_at']
        title = 'Contact Submissions Report'
    else:
        return redirect('reports')
    
    pdf_buffer = generate_pdf_report(queryset, title, fields)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{data_type}_{datetime.now().strftime("%Y%m%d")}.pdf"'
    return response
