import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uphirex.settings')
django.setup()

from authapp.models import User
from organizations.models import Team
from jobs.models import JobPost

def fix_hr_organizations():
    hrs = User.objects.filter(role='hr', organization_id__isnull=True)
    print(f"Found {hrs.count()} HR users without an organization_id.")
    
    for hr in hrs:
        # Find if they created a team
        team = Team.objects.filter(created_by=hr).first()
        if team:
            print(f"Linking HR {hr.username} to team {team.name}")
            hr.organization_id = team
            hr.save(update_fields=['organization_id'])
            
            # Also update existing job posts for this HR
            jobs = JobPost.objects.filter(posted_by=hr, organization_id__isnull=True)
            if jobs.exists():
                print(f"Updating {jobs.count()} job posts for {hr.username}")
                jobs.update(organization_id=team)
        else:
            print(f"HR {hr.username} has not created any teams yet.")

if __name__ == "__main__":
    fix_hr_organizations()
