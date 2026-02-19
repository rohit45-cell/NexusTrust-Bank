from django.db import migrations

def create_admin(apps, schema_editor):
    User = apps.get_model("bankapp", "User")

    email = "admin@nexustrustbank.com"

    if User.objects.filter(email=email).exists():
        return

    admin = User.objects.create(
        email=email,
        full_name="System Admin",
        phone="9876543210",
        address="NexusTrust HQ",
        city="Bangalore",
        state="Karnataka",
        pincode="560001",
        is_staff=True,
        is_superuser=True,
        is_active=True,
    )
    admin.set_password("admin@123")
    admin.save()


class Migration(migrations.Migration):

    dependencies = [
        ("bankapp", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_admin),
    ]
