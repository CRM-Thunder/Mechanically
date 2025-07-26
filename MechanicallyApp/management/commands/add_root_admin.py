from django.core.management import BaseCommand

from MechanicallyApp.models import User
from MechanicallyApp.generators import generate_username

class Command(BaseCommand):

    def handle(self, *args, **options):
        User.objects.create_superuser(first_name="Jan", last_name="Kowalski", username=generate_username("Jan","Kowalski"), email="example@gmail.com", password="", role="admin", phone_number="123456789")
