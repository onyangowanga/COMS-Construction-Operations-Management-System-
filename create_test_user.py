#!/usr/bin/env python
"""
Create test user for testing JWT authentication
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.authentication.models import User, Organization, SystemRole

# First, get or create admin user without organization
try:
    user = User.objects.get(email='admin@test.com')
    user_created = False
    print(f"User exists: {user.email}")
except User.DoesNotExist:
    user = User.objects.create(
        email='admin@test.com',
        username='testadmin',  # Unique username
        first_name='Admin',
        last_name='User',
        system_role=SystemRole.SUPER_ADMIN,
        is_staff=True,
        is_superuser=True,
        is_verified=True,
        organization=None
    )
    user_created = True
    print(f"User created: {user.email}")

# Set password
user.set_password('TestPass123!')
user.save()

print(f"User {'created' if user_created else 'exists'}: {user.email}")

# Then create organization with user as owner
org, org_created = Organization.objects.get_or_create(
    name='Test Organization',
    defaults={
        'is_active': True,
        'owner': user
    }
)
print(f"Organization {'created' if org_created else 'exists'}: {org.name}")

# Update user with organization
if not user.organization:
    user.organization = org
    user.save()
    print(f"User updated with organization: {org.name}")

print(f"\nUser Details:")
print(f"  - Email: {user.email}")
print(f"  - Username: {user.username}")
print(f"  - System Role: {user.system_role}")
print(f"  - Is Staff: {user.is_staff}")
print(f"  - Is Superuser: {user.is_superuser}")
print(f"  - Organization: {user.organization.name if user.organization else 'None'}")
print("\nYou can now login with:")
print("  Email: admin@test.com")
print("  Password: TestPass123!")
print("\nTest endpoints:")
print("  - http://localhost:8000/admin/ (Django admin)")
print("  - http://localhost:8000/api/auth/login/ (API login)")

