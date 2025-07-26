from django.core.management import BaseCommand

from MechanicallyApp.models import User
from MechanicallyApp.generators import generate_username

class Command(BaseCommand):

    def handle(self, *args, **options):
        User.objects.create_user(first_name="Szymon", last_name="Chalski", username=generate_username("Szymon","Chalski"), email="example7@gmail.com", password="", role="manager", phone_number="203456789")
