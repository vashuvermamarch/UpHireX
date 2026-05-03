import os
import django
from unittest.mock import patch

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uphirex.settings')
django.setup()

from authapp.models import User
from jobs.models import JobPost
from applications.models import JobApplication
from applications.views import JobApplicationViewSet
from rest_framework.test import APIRequestFactory

def verify_status_email():
    # 1. Setup test data
    hr_user, _ = User.objects.get_or_create(username='test_hr', email='hr@test.com', role='hr')
    applicant, _ = User.objects.get_or_create(username='test_applicant', email='applicant@test.com', role='job_seeker')
    job, _ = JobPost.objects.get_or_create(title='Software Engineer', posted_by=hr_user)
    application, _ = JobApplication.objects.get_or_create(user=applicant, job=job)
    
    application.status = 'pending'
    application.save()

    # 2. Mock PATCH request to update_status
    factory = APIRequestFactory()
    raw_request = factory.patch(f'/api/v1/applications/{application.id}/update_status/', {'status': 'shortlisted'}, format='json')
    raw_request.user = hr_user
    
    from rest_framework.request import Request
    request = Request(raw_request)
    request._request.user = hr_user
    request.user = hr_user
    
    viewset = JobApplicationViewSet()
    viewset.request = request
    viewset.action = 'update_status'
    viewset.kwargs = {'pk': str(application.id)}
    viewset.format_kwarg = None
    
    # Use a patch to catch the send_mail call
    with patch('django.core.mail.send_mail') as mocked_send_mail:
        response = viewset.update_status(request, pk=str(application.id))
        
        print("Response Status:", response.status_code)
        print("Response Data:", response.data)
        
        if response.status_code == 200:
            print("Status updated successfully.")
            if mocked_send_mail.called:
                print("Email was sent!")
                subject = mocked_send_mail.call_args[0][0]
                recipient = mocked_send_mail.call_args[0][3]
                print(f"Subject: {subject}")
                print(f"Recipient: {recipient}")
            else:
                print("Email was NOT sent.")
        else:
            print("Status update failed.")

if __name__ == "__main__":
    verify_status_email()
