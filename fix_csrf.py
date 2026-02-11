import os
import re

# List of template files that need CSRF token
csrf_files = [
    'bankapp/templates/bankapp/deposit.html',
    'bankapp/templates/bankapp/withdraw.html',
    'bankapp/templates/bankapp/transfer.html',
    'bankapp/templates/bankapp/contact.html',
    'bankapp/templates/bankapp/signup.html',
    'bankapp/templates/bankapp/login.html',
    'bankapp/templates/bankapp/password_change.html',
    'bankapp/templates/bankapp/password_reset.html',
    'bankapp/templates/bankapp/edit_profile.html',
    'bankapp/templates/bankapp/download_report.html',
    'bankapp/templates/bankapp/manage_user_detail.html',
    'bankapp/templates/bankapp/add_account_type.html',
    'bankapp/templates/bankapp/edit_account_type.html',
    'bankapp/templates/bankapp/delete_account_type.html',
    'bankapp/templates/bankapp/rollback_transaction.html',
    'bankapp/templates/bankapp/edit_transaction.html',
    'bankapp/templates/bankapp/delete_transaction.html',
]

for file_path in csrf_files:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if form exists and csrf_token is missing
        if '<form' in content and '{% csrf_token %}' not in content:
            # Add csrf_token after form tag
            content = re.sub(
                r'(<form[^>]*>)',
                r'\1\n                        {% csrf_token %}',
                content
            )
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Added CSRF token to: {file_path}")
        else:
            print(f"⏭️  Already has CSRF token or no form: {file_path}")
    else:
        print(f"❌ File not found: {file_path}")

print("\n🎉 CSRF fix complete! Now run: python manage.py runserver")