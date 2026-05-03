import os
import django
from django.test import RequestFactory

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uphirex.settings')
django.setup()

from authapp.models import User
from authapp.views import AuthViewSet

def verify_get_photo():
    # 1. Get or create a test user
    username = 'testuser_patch' # This user was created in previous verification
    user = User.objects.filter(username=username).first()
    if not user:
        print("User not found. Please run the previous verification script first.")
        return

    # 2. Mock a GET request to /auth/me/photo/
    factory = RequestFactory()
    request = factory.get('/api/v1/auth/me/photo/')
    request.user = user
    request.META['HTTP_HOST'] = 'localhost:8000' # For build_absolute_uri
    
    viewset = AuthViewSet()
    viewset.request = request
    viewset.action = 'my_photo'
    
    response = viewset.my_photo(request)
    print("Response Status:", response.status_code)
    print("Response Data:", response.data)
    
    if response.status_code == 200:
        print("GET /auth/me/photo/ successful.")
    else:
        print("GET /auth/me/photo/ failed.")

    # 3. Test for specific user
    request_user = factory.get(f'/api/v1/auth/user/{user.id}/photo/')
    request_user.user = user # authenticated user viewing another (or same) user
    request_user.META['HTTP_HOST'] = 'localhost:8000'
    
    viewset.request = request_user
    viewset.action = 'user_photo'
    
    response_user = viewset.user_photo(request_user, user_id=str(user.id))
    print("User Photo Response Status:", response_user.status_code)
    print("User Photo Response Data:", response_user.data)

if __name__ == "__main__":
    verify_get_photo()
