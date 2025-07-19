from django.core.management import BaseCommand

from MechanicallyApp.models import User
from MechanicallyApp.generators import generate_username

class Command(BaseCommand):

    def handle(self, *args, **options):
        User.objects.create_user(first_name="Piotr", last_name="Nowak", username=generate_username("Piotr","Nowak"), email="example2@gmail.com", password="", role="standard", phone_number="223456789")
