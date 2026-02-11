import os
import django
import random
import string

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nexustrustbank.settings')
django.setup()

from bankapp.models import User, AccountType, Transaction
from django.db import transaction
from django.utils import timezone

@transaction.atomic
def setup_complete_system():
    print("=" * 70)
    print("🏦 NEXUSTRUST BANK - COMPLETE SYSTEM SETUP")
    print("=" * 70)
    print("\n📋 SETTING UP DATABASE...\n")
    
    # ============ 1. CREATE ACCOUNT TYPES ============
    savings, _ = AccountType.objects.get_or_create(
        name='Savings Account',
        defaults={
            'category': 'savings',
            'minimum_balance': 1000.00,
            'interest_rate': 3.50,
            'overdraft_limit': 0.00,
            'is_active': True
        }
    )
    print("✅ Savings Account Type")
    
    current, _ = AccountType.objects.get_or_create(
        name='Current Account',
        defaults={
            'category': 'current',
            'minimum_balance': 5000.00,
            'interest_rate': 1.00,
            'overdraft_limit': 25000.00,
            'is_active': True
        }
    )
    print("✅ Current Account Type")
    
    # ============ 2. DELETE ALL EXISTING USERS ============
    print("\n🗑️  Cleaning up existing users...")
    User.objects.all().delete()
    print("✅ Database cleared")
    
    # ============ 3. CREATE SUPERUSER ============
    superuser = User.objects.create_superuser(
        email='ganesh@nexustrustbank.com',
        password='Rohit.45',
        full_name='Ganesh (System Administrator)',
        phone='9876543210',
        address='Admin Office, Bandra Kurla Complex',
        city='Mumbai',
        state='Maharashtra',
        pincode='400001',
        account_type=savings,
        balance=1000000.00,
        is_staff=True,
        is_superuser=True,
        is_active=True,
        is_frozen=False
    )
    print("\n✅ SUPERUSER CREATED:")
    print("   📧 Email: ganesh@nexustrustbank.com")
    print("   🔑 Password: Rohit.45")
    print("   👑 Role: System Administrator")
    print("   🔓 Access: Django Admin + Bank Staff Portal")
    print("   🌐 Django Admin: http://127.0.0.1:8000/django-admin/")
    
    # ============ 4. CREATE BANK STAFF ============
    staff = User.objects.create_user(
        email='staff@nexustrustbank.com',
        password='Staff@123',
        full_name='Rajesh Kumar (Bank Manager)',
        phone='9988776655',
        address='NexusTrust Bank, Main Branch',
        city='Mumbai',
        state='Maharashtra',
        pincode='400051',
        account_type=current,
        balance=500000.00,
        is_staff=True,
        is_superuser=False,
        is_active=True,
        is_frozen=False
    )
    print("\n✅ BANK STAFF CREATED:")
    print("   📧 Email: staff@nexustrustbank.com")
    print("   🔑 Password: Staff@123")
    print("   👔 Role: Bank Manager")
    print("   🔓 Access: Bank Staff Portal ONLY")
    print("   🌐 Staff Portal: http://127.0.0.1:8000/bank-staff/")
    print("   ❌ Cannot access: Django Admin, Customer Dashboard")
    
    # ============ 5. CREATE REGULAR CUSTOMERS ============
    customers = [
        {
            'email': 'ravi.kumar@email.com',
            'password': 'Ravi@123',
            'name': 'Ravi Kumar',
            'phone': '9876543211',
            'city': 'Delhi',
            'balance': 25000.00,
            'type': savings
        },
        {
            'email': 'priya.patel@email.com',
            'password': 'Priya@123',
            'name': 'Priya Patel',
            'phone': '9988776654',
            'city': 'Ahmedabad',
            'balance': 150000.00,
            'type': current
        },
        {
            'email': 'amit.singh@email.com',
            'password': 'Amit@123',
            'name': 'Amit Singh',
            'phone': '8765432109',
            'city': 'Bangalore',
            'balance': 5000.00,
            'type': savings
        },
        {
            'email': 'frozen.user@email.com',
            'password': 'Frozen@123',
            'name': 'Test Frozen Account',
            'phone': '7654321098',
            'city': 'Chennai',
            'balance': 10000.00,
            'type': savings,
            'frozen': True
        }
    ]
    
    print("\n👤 CREATING REGULAR CUSTOMERS:")
    for cust in customers:
        user = User.objects.create_user(
            email=cust['email'],
            password=cust['password'],
            full_name=cust['name'],
            phone=cust['phone'],
            address=f'123 {cust["city"]} Main Road',
            city=cust['city'],
            state='Maharashtra' if cust['city'] == 'Mumbai' else cust['city'],
            pincode='400001' if cust['city'] == 'Mumbai' else '560001',
            account_type=cust['type'],
            balance=cust['balance'],
            is_staff=False,
            is_superuser=False,
            is_active=True,
            is_frozen=cust.get('frozen', False)
        )
        print(f"   ✅ {cust['name']}: {cust['email']} / {cust['password']}")
        if cust.get('frozen'):
            print(f"      ❄️  ACCOUNT FROZEN")
    
    # ============ 6. CREATE SAMPLE TRANSACTIONS ============
    print("\n💰 CREATING SAMPLE TRANSACTIONS...")
    
    # Get customers for transactions
    ravi = User.objects.get(email='ravi.kumar@email.com')
    priya = User.objects.get(email='priya.patel@email.com')
    amit = User.objects.get(email='amit.singh@email.com')
    
    # Deposit for Ravi
    Transaction.objects.create(
        user=ravi,
        transaction_type='deposit',
        amount=50000.00,
        balance_after=75000.00,
        description='Salary deposit',
        status='completed',
        ip_address='127.0.0.1'
    )
    
    # Withdrawal for Ravi
    Transaction.objects.create(
        user=ravi,
        transaction_type='withdraw',
        amount=10000.00,
        balance_after=65000.00,
        description='ATM withdrawal',
        status='completed',
        ip_address='127.0.0.1'
    )
    
    # Transfer from Priya to Ravi
    Transaction.objects.create(
        user=priya,
        transaction_type='transfer',
        amount=5000.00,
        balance_after=145000.00,
        description=f'Transfer to Ravi Kumar',
        status='completed',
        receiver=ravi,
        ip_address='127.0.0.1'
    )
    
    Transaction.objects.create(
        user=ravi,
        transaction_type='transfer',
        amount=5000.00,
        balance_after=70000.00,
        description=f'Transfer from Priya Patel',
        status='completed',
        receiver=priya,
        ip_address='127.0.0.1'
    )
    
    print("   ✅ 4 sample transactions created")
    
    # ============ 7. FINAL SUMMARY ============
    print("\n" + "=" * 70)
    print("📊 SYSTEM ACCESS SUMMARY - COMPLETE SEPARATION")
    print("=" * 70)
    
    print("\n🔷 SUPERUSER (Full System Access):")
    print("   📧 ganesh@nexustrustbank.com / Rohit.45")
    print("   ✅ Django Admin: http://127.0.0.1:8000/django-admin/")
    print("   ✅ Bank Staff: http://127.0.0.1:8000/bank-staff/")
    print("   ✅ CAN access customer dashboard (for testing)")
    
    print("\n🔶 BANK STAFF (Staff Portal Only):")
    print("   📧 staff@nexustrustbank.com / Staff@123")
    print("   ✅ Bank Staff: http://127.0.0.1:8000/bank-staff/")
    print("   ❌ Django Admin: BLOCKED")
    print("   ❌ Customer Dashboard: BLOCKED")
    
    print("\n👤 REGULAR CUSTOMERS (Customer Portal Only):")
    print("   📧 ravi.kumar@email.com / Ravi@123")
    print("   📧 priya.patel@email.com / Priya@123")
    print("   📧 amit.singh@email.com / Amit@123")
    print("   ✅ Customer Dashboard: http://127.0.0.1:8000/my-banking/")
    print("   ❌ Bank Staff Portal: BLOCKED")
    print("   ❌ Django Admin: BLOCKED")
    
    print("\n❄️  FROZEN ACCOUNT (Cannot Login):")
    print("   📧 frozen.user@email.com / Frozen@123")
    print("   ❌ Account Frozen - Login Disabled")
    
    print("\n" + "=" * 70)
    print(f"✅ TOTAL USERS: {User.objects.count()}")
    print(f"✅ TOTAL TRANSACTIONS: {Transaction.objects.count()}")
    print("=" * 70)
    print("\n🚀 Setup complete! Run: python manage.py runserver")
    print("=" * 70)

if __name__ == '__main__':
    setup_complete_system()