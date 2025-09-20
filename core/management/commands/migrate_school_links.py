from django.core.management.base import BaseCommand
from core.models import User, School, Subject

class Command(BaseCommand):
    help = 'Migrate existing school_id fields to new School model and link users/subjects.'

    def handle(self, *args, **options):
        # Migrate Users
        for user in User.objects.exclude(school_id__isnull=True).exclude(school_id__exact=''):
            school, created = School.objects.get_or_create(name=user.school_id)
            user.school = school
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Linked user {user.username} to school {school.name}'))

        # Migrate Subjects
        for subject in Subject.objects.exclude(school_id__isnull=True).exclude(school_id__exact=''):
            school, created = School.objects.get_or_create(name=subject.school_id)
            subject.school = school
            subject.save()
            self.stdout.write(self.style.SUCCESS(f'Linked subject {subject.name} to school {school.name}'))

        self.stdout.write(self.style.SUCCESS('Migration complete.'))
