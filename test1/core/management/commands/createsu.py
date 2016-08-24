from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

# This command sets up an admin user if none exists
class Command(BaseCommand):

    def handle(self, *args, **options):
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "globalheartbeat@umich.edu", "G1oba1Heartbeat")