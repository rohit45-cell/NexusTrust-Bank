from django.db import migrations
from django.contrib.auth.hashers import make_password

def create_admin(apps, schema_editor):
    User = apps.get_model("bankapp", "User")

    email = "admin@nexustrustbank.com"

    if User.objects.filter(email=email).exists():
        return

    User.objects.create(
        email=email,
        full_name="System Admin",
        phone="9876543210",
        address="NexusTrust HQ",
        city="Bangalore",
        state="Karnataka",
        pincode="560001",
        password=make_password("admin@123"),
        is_staff=True,
        is_superuser=True,
        is_active=True,
    )

class Migration(migrations.Migration):

    dependencies = [
        ("bankapp", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_admin),
    ]
