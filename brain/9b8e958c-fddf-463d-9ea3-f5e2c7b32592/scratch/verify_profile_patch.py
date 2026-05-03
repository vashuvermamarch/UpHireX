import os
import django
from django.core.files.uploadedfile import SimpleUploadedFile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uphirex.settings')
django.setup()

from authapp.models import User
from authapp.serializers import UserUpdateSerializer

def verify_update():
    # 1. Get or create a test user
    username = 'testuser_patch'
    user = User.objects.filter(username=username).first()
    if not user:
        user = User.objects.create_user(
            username=username,
            email='patch@test.com',
            password='OldPassword123',
            displayName='Old Name',
            phone='1234567890'
        )
    
    print(f"Initial Name: {user.displayName}")
    print(f"Initial Phone: {user.phone}")
    
    # 2. Prepare patch data
    data = {
        'displayName': 'New Name',
        'phone': '0987654321',
        'password': 'NewPassword123'
    }
    
    # Simulate a file upload for profile_photo
    small_gif = (
        b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
        b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
        b'\x02\x4c\x01\x00\x3b'
    )
    photo = SimpleUploadedFile("test.gif", small_gif, content_type="image/gif")
    data['profile_photo'] = photo
    
    # 3. Use serializer to update
    serializer = UserUpdateSerializer(user, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        print("Serializer update successful.")
    else:
        print("Serializer errors:", serializer.errors)
        return

    # 4. Verify changes
    user.refresh_from_db()
    print(f"Updated Name: {user.displayName}")
    print(f"Updated Phone: {user.phone}")
    print(f"Profile Photo URL: {user.profile_photo.url if user.profile_photo else 'None'}")
    
    # Verify password
    if user.check_password('NewPassword123'):
        print("Password updated successfully.")
    else:
        print("Password update FAILED.")

if __name__ == "__main__":
    verify_update()
