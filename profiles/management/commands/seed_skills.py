from django.core.management.base import BaseCommand
from profiles.models import Skill

class Command(BaseCommand):
    help = 'Seed the database with technical and non-technical skills.'

    def handle(self, *args, **options):
        tech_skills = [
            ('Python', 'Technical'),
            ('Django', 'Technical'),
            ('JavaScript', 'Technical'),
            ('React', 'Technical'),
            ('Java', 'Technical'),
            ('Spring Boot', 'Technical'),
            ('SQL', 'Technical'),
            ('PostgreSQL', 'Technical'),
            ('Docker', 'Technical'),
            ('Kubernetes', 'Technical'),
            ('AWS', 'Technical'),
            ('Git', 'Technical'),
            ('Machine Learning', 'Technical'),
            ('Data Analysis', 'Technical'),
            ('C++', 'Technical'),
            ('Node.js', 'Technical'),
            ('TypeScript', 'Technical'),
            ('HTML/CSS', 'Technical'),
        ]

        non_tech_skills = [
            ('Communication', 'Non-Technical'),
            ('Leadership', 'Non-Technical'),
            ('Problem Solving', 'Non-Technical'),
            ('Time Management', 'Non-Technical'),
            ('Teamwork', 'Non-Technical'),
            ('Adaptability', 'Non-Technical'),
            ('Public Speaking', 'Non-Technical'),
            ('Project Management', 'Non-Technical'),
            ('Critical Thinking', 'Non-Technical'),
            ('Conflict Resolution', 'Non-Technical'),
            ('Creativity', 'Non-Technical'),
            ('Emotional Intelligence', 'Non-Technical'),
            ('Negotiation', 'Non-Technical'),
            ('Customer Service', 'Non-Technical'),
        ]

        all_skills = tech_skills + non_tech_skills

        count = 0
        for name, category in all_skills:
            skill, created = Skill.objects.get_or_create(
                name=name,
                defaults={'category': category}
            )
            if created:
                count += 1
                self.stdout.write(self.style.SUCCESS(f'Created skill: {name} ({category})'))
            else:
                self.stdout.write(self.style.WARNING(f'Skill already exists: {name}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {count} new skills.'))
