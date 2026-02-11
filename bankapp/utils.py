from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import csv
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import calendar

# IMPORT THE MODELS - THIS IS THE FIX!
from .models import User, Transaction, AccountType, InterestHistory

def send_transaction_notification(user, transaction, transaction_type):
    """Send email notification for transactions"""
    subject = f'NexusTrust Bank - {transaction_type.capitalize()} Confirmation'
    message = f"""
    Dear {user.full_name},
    
    Your {transaction_type} of ₹{transaction.amount} has been processed successfully.
    
    Transaction ID: {transaction.transaction_id}
    Date: {transaction.created_at.strftime('%d-%m-%Y %H:%M:%S')}
    Amount: ₹{transaction.amount}
    Balance: ₹{transaction.balance_after}
    Description: {transaction.description or 'N/A'}
    
    Thank you for banking with NexusTrust Bank.
    
    Regards,
    NexusTrust Bank Team
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=True,
    )

def generate_csv_report(queryset, fields, filename):
    """Generate CSV report from queryset"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow([field.replace('_', ' ').title() for field in fields])
    
    # Write data
    for obj in queryset:
        row = []
        for field in fields:
            value = getattr(obj, field)
            if isinstance(value, Decimal):
                value = f"₹{value}"
            elif isinstance(value, datetime):
                value = value.strftime('%d-%m-%Y %H:%M:%S')
            elif isinstance(value, timezone.datetime):
                value = value.strftime('%d-%m-%Y %H:%M:%S')
            elif field == 'user' and hasattr(value, 'full_name'):
                value = value.full_name
            elif field == 'account_type' and hasattr(value, 'name'):
                value = value.name
            row.append(str(value))
        writer.writerow(row)
    
    return output.getvalue()

def generate_pdf_report(queryset, title, fields):
    """Generate PDF report from queryset"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = TA_CENTER
    
    elements = []
    
    # Title
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 0.25*inch))
    
    # Date
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        alignment=TA_RIGHT,
    )
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", date_style))
    elements.append(Spacer(1, 0.25*inch))
    
    # Table data
    data = []
    
    # Headers
    headers = [field.replace('_', ' ').title() for field in fields]
    data.append(headers)
    
    # Data rows
    for obj in queryset:
        row = []
        for field in fields:
            value = getattr(obj, field)
            if isinstance(value, Decimal):
                value = f"₹{value}"
            elif isinstance(value, datetime):
                value = value.strftime('%d-%m-%Y %H:%M:%S')
            elif isinstance(value, timezone.datetime):
                value = value.strftime('%d-%m-%Y %H:%M:%S')
            elif field == 'user' and hasattr(value, 'full_name'):
                value = value.full_name
            elif field == 'account_type' and hasattr(value, 'name'):
                value = value.name
            row.append(str(value)[:50])
        data.append(row)
    
    # Create table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer

def calculate_interest(user, months=1):
    """Calculate interest for savings account"""
    if not user.account_type:
        return 0
    
    if user.account_type.category != 'savings':
        return 0
    
    rate = float(user.account_type.interest_rate)
    balance = float(user.balance)
    time_years = months / 12
    
    # Simple interest calculation
    interest = (balance * rate * time_years) / 100
    
    # Round to 2 decimal places
    return round(interest, 2)

def apply_monthly_interest():
    """Apply monthly interest to all savings accounts"""
    from .models import User, Transaction, InterestHistory
    from datetime import date
    from dateutil.relativedelta import relativedelta
    
    savings_users = User.objects.filter(
        account_type__category='savings',
        is_active=True,
        is_frozen=False,
        balance__gt=0
    )
    
    today = date.today()
    last_month = today - relativedelta(months=1)
    
    for user in savings_users:
        interest = calculate_interest(user)
        if interest > 0:
            # Credit interest
            user.balance += Decimal(str(interest))
            user.save()
            
            # Create transaction record
            transaction = Transaction.objects.create(
                user=user,
                transaction_type='interest',
                amount=interest,
                balance_after=user.balance,
                description=f'Monthly interest credit @ {user.account_type.interest_rate}%',
                status='completed'
            )
            
            # Record interest history
            InterestHistory.objects.create(
                user=user,
                account_type=user.account_type,
                amount=interest,
                rate=user.account_type.interest_rate,
                period_start=last_month,
                period_end=today
            )
            
            # Send notification
            send_transaction_notification(user, transaction, 'interest credit')
    
    return savings_users.count()

def get_dashboard_stats(user):
    """Get dashboard statistics for user"""
    from django.db.models import Sum, Count, Q
    
    transactions = user.transactions.filter(status='completed')
    
    total_deposits = transactions.filter(transaction_type='deposit').aggregate(Sum('amount'))['amount__sum'] or 0
    total_withdrawals = transactions.filter(transaction_type='withdraw').aggregate(Sum('amount'))['amount__sum'] or 0
    total_transfers_sent = transactions.filter(transaction_type='transfer', user=user).aggregate(Sum('amount'))['amount__sum'] or 0
    total_transfers_received = user.received_transactions.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
    
    this_month = timezone.now().replace(day=1)
    monthly_transactions = transactions.filter(created_at__gte=this_month).count()
    
    return {
        'balance': user.balance,
        'available_balance': user.get_available_balance(),
        'total_deposits': total_deposits,
        'total_withdrawals': total_withdrawals,
        'total_transfers_sent': total_transfers_sent,
        'total_transfers_received': total_transfers_received,
        'total_transactions': transactions.count(),
        'monthly_transactions': monthly_transactions,
        'account_status': 'Active' if not user.is_frozen else 'Frozen',
    }

def get_chart_data(user, months=6):
    """Get chart data for user dashboard"""
    from django.db.models import Sum, Count
    from datetime import datetime, timedelta
    
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30*months)
    
    # Balance history (line chart)
    transactions = user.transactions.filter(
        created_at__gte=start_date,
        status='completed'
    ).order_by('created_at')
    
    balance_history_dates = []
    balance_history_values = []
    
    # Get daily closing balance
    current_date = start_date
    while current_date <= end_date:
        day_transactions = transactions.filter(
            created_at__date=current_date.date()
        ).order_by('-created_at')
        
        if day_transactions.exists():
            balance = day_transactions.first().balance_after
        else:
            # Get last known balance
            last_transaction = transactions.filter(
                created_at__lt=current_date + timedelta(days=1)
            ).order_by('-created_at').first()
            balance = last_transaction.balance_after if last_transaction else user.balance
        
        balance_history_dates.append(current_date.strftime('%d-%m-%Y'))
        balance_history_values.append(float(balance))
        current_date += timedelta(days=1)
    
    # Monthly transactions (bar chart)
    monthly_data = []
    monthly_labels = []
    
    for i in range(months):
        month_start = end_date.replace(day=1) - timedelta(days=30*i)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        month_transactions = transactions.filter(
            created_at__date__gte=month_start.date(),
            created_at__date__lte=month_end.date()
        )
        
        monthly_data.append(month_transactions.count())
        monthly_labels.append(month_start.strftime('%b %Y'))
    
    monthly_labels.reverse()
    monthly_data.reverse()
    
    # Transaction types (pie chart)
    type_data = []
    type_labels = []
    
    # FIXED: Transaction is now imported at the top
    for t_type, t_label in Transaction.TRANSACTION_TYPES:
        count = transactions.filter(transaction_type=t_type).count()
        if count > 0:
            type_labels.append(t_label)
            type_data.append(count)
    
    return {
        'balance_history': {
            'labels': balance_history_dates,
            'data': balance_history_values,
        },
        'monthly_transactions': {
            'labels': monthly_labels,
            'data': monthly_data,
        },
        'transaction_types': {
            'labels': type_labels,
            'data': type_data,
        },
    }