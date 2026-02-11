# create_sample_users.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nexustrustbank.settings')
django.setup()

from bankapp.models import User, AccountType
from django.db import transaction

@transaction.atomic
def create_sample_users():
    print("🚀 Creating Sample Users for NexusTrust Bank...\n")
    
    # Get or create account types
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
    
    # ============ 1. SUPERUSER (Full System Admin) ============
    # Access: Django Admin (/admin) + Bank Admin (/bank-admin)
    superuser, created = User.objects.get_or_create(
        email='ganesh@nexustrustbank.com',
        defaults={
            'full_name': 'Ganesh (System Administrator)',
            'phone': '9876543210',
            'address': 'Admin Office, Bandra Kurla Complex',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'pincode': '400001',
            'account_type': savings,
            'balance': 1000000.00,
            'is_staff': True,
            'is_superuser': True,
            'is_active': True,
            'is_frozen': False
        }
    )
    if created:
        superuser.set_password('Rohit.45')
        superuser.save()
        print("✅ SUPERUSER CREATED:")
        print("   📧 Email: ganesh@nexustrustbank.com")
        print("   🔑 Password: Rohit.45")
        print("   👑 Role: System Administrator (Full Access)")
        print("   🔓 Access: Django Admin + Bank Admin + User Dashboard\n")
    else:
        print("✅ Superuser already exists\n")
    
    # ============ 2. BANK ADMINISTRATOR ============
    # Access: Bank Admin (/bank-admin) ONLY - No Django Admin access
    bank_admin, created = User.objects.get_or_create(
        email='admin@nexustrustbank.com',
        defaults={
            'full_name': 'Priya Sharma (Bank Manager)',
            'phone': '9988776655',
            'address': 'NexusTrust Bank, Main Branch',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'pincode': '400051',
            'account_type': current,
            'balance': 500000.00,
            'is_staff': True,      # Can access bank admin
            'is_superuser': False,  # Cannot access Django admin
            'is_active': True,
            'is_frozen': False
        }
    )
    if created:
        bank_admin.set_password('Admin@123')
        bank_admin.save()
        print("✅ BANK ADMIN CREATED:")
        print("   📧 Email: admin@nexustrustbank.com")
        print("   🔑 Password: Admin@123")
        print("   👔 Role: Bank Manager")
        print("   🔓 Access: Bank Admin (/bank-admin) ONLY\n")
    
    # ============ 3. REGULAR CUSTOMERS ============
    # Access: User Dashboard only - No admin access
    
    # Customer 1: Savings Account
    customer1, created = User.objects.get_or_create(
        email='ravi.kumar@email.com',
        defaults={
            'full_name': 'Ravi Kumar',
            'phone': '9876543211',
            'aadhaar': '123412341234',
            'pan': 'ABCDE1234F',
            'address': '123 Green Park, Main Road',
            'city': 'Delhi',
            'state': 'Delhi',
            'pincode': '110001',
            'account_type': savings,
            'balance': 25000.00,
            'is_staff': False,
            'is_superuser': False,
            'is_active': True,
            'is_frozen': False
        }
    )
    if created:
        customer1.set_password('Ravi@123')
        customer1.save()
        print("✅ CUSTOMER CREATED:")
        print("   📧 Email: ravi.kumar@email.com")
        print("   🔑 Password: Ravi@123")
        print("   👤 Name: Ravi Kumar")
        print("   💰 Balance: ₹25,000\n")
    
    # Customer 2: Current Account
    customer2, created = User.objects.get_or_create(
        email='priya.patel@email.com',
        defaults={
            'full_name': 'Priya Patel',
            'phone': '9988776654',
            'aadhaar': '567856785678',
            'pan': 'FGHIJ5678K',
            'address': '456 Business Hub, SG Highway',
            'city': 'Ahmedabad',
            'state': 'Gujarat',
            'pincode': '380015',
            'account_type': current,
            'balance': 150000.00,
            'is_staff': False,
            'is_superuser': False,
            'is_active': True,
            'is_frozen': False
        }
    )
    if created:
        customer2.set_password('Priya@123')
        customer2.save()
        print("✅ CUSTOMER CREATED:")
        print("   📧 Email: priya.patel@email.com")
        print("   🔑 Password: Priya@123")
        print("   👤 Name: Priya Patel")
        print("   💰 Balance: ₹150,000\n")
    
    # Customer 3: Savings Account (Low Balance)
    customer3, created = User.objects.get_or_create(
        email='amit.singh@email.com',
        defaults={
            'full_name': 'Amit Singh',
            'phone': '8765432109',
            'address': '789 Lake View Apartments',
            'city': 'Bangalore',
            'state': 'Karnataka',
            'pincode': '560001',
            'account_type': savings,
            'balance': 5000.00,
            'is_staff': False,
            'is_superuser': False,
            'is_active': True,
            'is_frozen': False
        }
    )
    if created:
        customer3.set_password('Amit@123')
        customer3.save()
        print("✅ CUSTOMER CREATED:")
        print("   📧 Email: amit.singh@email.com")
        print("   🔑 Password: Amit@123")
        print("   👤 Name: Amit Singh")
        print("   💰 Balance: ₹5,000\n")
    
    # Customer 4: Frozen Account (For testing)
    customer4, created = User.objects.get_or_create(
        email='frozen.user@email.com',
        defaults={
            'full_name': 'Test Frozen Account',
            'phone': '7654321098',
            'address': '321 Test Colony',
            'city': 'Chennai',
            'state': 'Tamil Nadu',
            'pincode': '600001',
            'account_type': savings,
            'balance': 10000.00,
            'is_staff': False,
            'is_superuser': False,
            'is_active': True,
            'is_frozen': True  # Frozen account
        }
    )
    if created:
        customer4.set_password('Frozen@123')
        customer4.save()
        print("✅ TEST USER CREATED (FROZEN):")
        print("   📧 Email: frozen.user@email.com")
        print("   🔑 Password: Frozen@123")
        print("   ❄️ Status: FROZEN ACCOUNT\n")
    
    # ============ SUMMARY ============
    print("=" * 50)
    print("📊 USER ACCESS SUMMARY")
    print("=" * 50)
    print("\n🔷 SUPERUSER (Full System Access):")
    print("   - Email: ganesh@nexustrustbank.com")
    print("   - Access: Django Admin + Bank Admin + User Dashboard")
    print("   - URL: http://127.0.0.1:8000/admin/")
    print()
    print("🔶 BANK ADMINISTRATOR:")
    print("   - Email: admin@nexustrustbank.com")
    print("   - Access: Bank Admin ONLY")
    print("   - URL: http://127.0.0.1:8000/bank-admin/")
    print()
    print("👤 REGULAR CUSTOMERS:")
    print("   - Email: ravi.kumar@email.com (Password: Ravi@123)")
    print("   - Email: priya.patel@email.com (Password: Priya@123)")
    print("   - Email: amit.singh@email.com (Password: Amit@123)")
    print("   - Email: frozen.user@email.com (Password: Frozen@123) - FROZEN")
    print()
    print("🔐 Access URLs:")
    print("   • User Dashboard: http://127.0.0.1:8000/dashboard/")
    print("   • Bank Admin: http://127.0.0.1:8000/bank-admin/")
    print("   • Django Admin: http://127.0.0.1:8000/admin/")
    print("\n🚀 All users created successfully!")

if __name__ == '__main__':
    create_sample_users()