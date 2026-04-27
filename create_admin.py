import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uphirex.settings')
django.setup()

from authapp.models import User

username = 'admin'
email = 'admin@uphirex.com'
password = 'AdminPassword123'

user = User.objects.filter(username=username).first()
if user:
    user.set_password(password)
    user.role = 'admin'
    user.is_active = True
    user.is_staff = True
    user.is_superuser = True
    user.email_verified = True
    user.save()
    print(f"Superuser '{username}' password updated successfully!")
else:
    User.objects.create_superuser(username=username, email=email, password=password, role='admin', email_verified=True)
    print(f"Superuser '{username}' created successfully!")
