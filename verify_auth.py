import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uphirex.settings')
django.setup()

from django.test import Client
from authapp.models import User
from django.core.cache import cache

def test_flows():
    client = Client()
    
    # Cleanup
    User.objects.filter(username__in=["user1", "mgr1"]).delete()
    cache.clear()
    
    # 1. Sign up as a normal user
    print("Testing Normal User Signup...")
    signup_data = {
        "username": "user1",
        "password": "password123",
        "phone_number": "1234567890",
        "email": "user1@example.com",
        "user_type": "USER"
    }
    resp = client.post('/api/auth/signup/', data=signup_data)
    print(f"Signup response: {resp.status_code}")
    print(resp.json())
    
    otp = resp.json()['data']['otp']
    
    # 2. Verify Signup
    print("\nTesting Verify Signup...")
    verify_data = {
        "phone_number": "1234567890",
        "otp": otp
    }
    resp = client.post('/api/auth/verify_signup/', data=verify_data, content_type='application/json')
    print(f"Verify response: {resp.status_code}")
    v_data = resp.json()['data']
    print(v_data)
    signup_token = v_data['signup_token']
    
    # 3. Login as Normal User
    print("\nTesting Normal User Login...")
    login_data = {
        "username": "user1",
        "password": "password123",
        "signup_token": signup_token
    }
    resp = client.post('/api/auth/login/', data=login_data, content_type='application/json')
    print(f"Login response: {resp.status_code}")
    print(resp.json())
    
    # 4. Sign up as a Manager
    print("\nTesting Manager Signup...")
    signup_data_mgr = {
        "username": "mgr1",
        "password": "password123",
        "phone_number": "0987654321",
        "email": "mgr1@example.com",
        "user_type": "MANAGER"
    }
    resp = client.post('/api/auth/signup/', data=signup_data_mgr)
    print(f"Manager Signup response: {resp.status_code}")
    otp_mgr = resp.json()['data']['otp']
    
    # Verify Manager Signup
    resp = client.post('/api/auth/verify_signup/', data={"phone_number": "0987654321", "otp": otp_mgr}, content_type='application/json')
    print(f"Manager Verify response: {resp.status_code}")
    mgr = User.objects.get(username="mgr1")
    print(f"Manager is_active: {mgr.is_active}") # Should be False
    
    # Try Login as Manager (Should fail)
    print("\nTesting Manager Login (before activation)...")
    resp = client.post('/api/auth/login/', data={"username": "mgr1", "password": "password123"}, content_type='application/json')
    print(f"Manager login response (expected 403): {resp.status_code}")
    print(resp.json())
    
    # Activate Manager
    print("\nActivating Manager...")
    mgr.is_active = True
    mgr.save()
    
    # Try Login as Manager (Should succeed)
    print("\nTesting Manager Login (after activation)...")
    resp = client.post('/api/auth/login/', data={"username": "mgr1", "password": "password123"}, content_type='application/json')
    print(f"Manager login response (expected 200): {resp.status_code}")
    print(resp.json())

if __name__ == "__main__":
    test_flows()
