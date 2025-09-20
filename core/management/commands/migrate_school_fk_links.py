from django.core.management.base import BaseCommand
from core.models import User, Subject

class Command(BaseCommand):
    help = 'Obsolete: School model no longer exists. This command is now a placeholder.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('This migration command is obsolete. School model no longer exists.'))
