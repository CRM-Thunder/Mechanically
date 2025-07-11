from django.core.validators import MinLengthValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
class User(AbstractUser):
    #odwzorować mechanizm tworzenia username jak na usosie, czyli 3 litery imienia 3 litery nazwiska i 4 cyfrowy kod, dodać do tego regex jak się uda zaimplementować
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    username = models.CharField(max_length=10, unique=True,
    validators=[
        MinLengthValidator(10)
    ])
    email=models.EmailField(unique=True)
    first_name = models.CharField(max_length=20,validators=[MinLengthValidator(3)])
    last_name = models.CharField(max_length=30,validators=[MinLengthValidator(3)])
    REQUIRED_FIELDS = ['email','first_name','last_name']
    def __str__(self):
        return self.username

    def get_full_name(self):
        return self.first_name + " " + self.last_name

    def get_short_name(self):
        return self.first_name

#dodać walidator dla formatu VIN
class Vehicle(models.Model):

    class VehicleTypeChoices(models.TextChoices):
        #samochód osobowy
        PASSENGER_CAR = 'PC'
        # samochód ciężarowy
        TRUCK = 'TR'
        # autobus
        COACH = 'CO'
        # motocykl
        MOTORBIKE = 'MO'
        # ciągnik siodłowy
        TRACTOR_UNIT = 'TU'
        #inne pojazdy
        OTHER = 'OT'

    class FuelTypeChoices(models.TextChoices):
        #benzyna
        PETROL = 'P'
        # diesel
        DIESEL = 'D'
        #elektryczność
        ELECTRIC = 'E'
        #wodór
        HYDROGEN = 'H2'
        #hybryda elektryczno-dieslowa
        HYBRID_DIESEL='HD'
        #hybryda elektryczno-benzynowa
        HYBRID_PETROL='HP'
        #inne
        OTHER = 'OT'

    class AvailabilityChoices(models.TextChoices):
        AVAILABLE = 'A'
        UNAVAILABLE='U'
        REPAIR = 'R'
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    vin=models.CharField(max_length=17,unique=True, validators=[MinLengthValidator(17)])
    kilometers=models.PositiveIntegerField()
    manufacturer=models.ForeignKey('Manufacturer',on_delete=models.CASCADE, related_name='vehicles')
    vehicle_model=models.CharField(max_length=20)
    year=models.PositiveIntegerField()
    # noinspection PyUnresolvedReferences
    vehicle_type=models.CharField(max_length=2, choices=VehicleTypeChoices.choices, default=VehicleTypeChoices.OTHER)
    # noinspection PyUnresolvedReferences
    fuel_type=models.CharField(max_length=2, choices=FuelTypeChoices.choices, default=FuelTypeChoices.OTHER)
    # noinspection PyUnresolvedReferences
    availability=models.CharField(max_length=1, choices=AvailabilityChoices.choices, default=AvailabilityChoices.AVAILABLE)
    #musi być zabezpieczenie że może być przypisany tylko do brancha
    branch=models.ForeignKey('Location',on_delete=models.CASCADE, related_name='vehicles')


class Manufacturer(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    name=models.CharField(max_length=20,unique=True, validators=[MinLengthValidator(3)])
    def __str__(self):
        return self.name


class Location(models.Model):
    class LocationTypeChoices(models.TextChoices):
        BRANCH='B'
        WORKSHOP='W'

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=9, blank=True)
    email = models.EmailField(blank=True)
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    #narazie jako pojedyncze pole, w razie czego można rozbudować
    address=models.CharField(max_length=50)
    # noinspection PyUnresolvedReferences
    location_type=models.CharField(max_length=1,choices=LocationTypeChoices.choices,default=LocationTypeChoices.BRANCH)

#należy wprowadzić zabezpieczenie, że do warsztatu może zostać przydzielony tylko mechanik, a do brancha tylko standardowy pracownik
class UserLocationAssignment(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    location=models.ForeignKey(Location,on_delete=models.CASCADE)
    assign_date=models.DateTimeField(auto_now_add=True)

class FailureReport(models.Model):
    class FailureStatusChoices(models.TextChoices):
        PENDING='P'
        ASSIGNED='A'
        DISMISSED='D'
        RESOLVED='R'
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    vehicle=models.ForeignKey(Vehicle,on_delete=models.CASCADE, related_name='failure_reports')
    description=models.TextField()
    workshop=models.ForeignKey('Location',on_delete=models.CASCADE, null=True, blank=True, related_name='failure_reports')
    report_date=models.DateTimeField(auto_now_add=True)
    #zabezpieczyć aby tylko standardowy/menadżer mógł być autorem
    report_author=models.ForeignKey(User,on_delete=models.CASCADE, related_name='failure_reports')
    # noinspection PyUnresolvedReferences
    status=models.CharField(max_length=1,choices=FailureStatusChoices.choices,default=FailureStatusChoices.PENDING)
    last_status_change_date=models.DateTimeField(auto_now=True)

class RepairReport(models.Model):
    class RepairStatusChoices(models.TextChoices):
        ACTIVE='A'
        READY='R'
        HISTORIC='H'
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    failure_report=models.OneToOneField(FailureReport,on_delete=models.CASCADE, related_name='repair_report')
    condition_analysis=models.TextField()
    repair_action=models.TextField()
    cost=models.DecimalField(max_digits=8,decimal_places=2)
    report_date=models.DateTimeField(auto_now_add=True)
    ready_for_review=models.BooleanField(default=False)
    # noinspection PyUnresolvedReferences
    status=models.CharField(max_length=1,choices=RepairStatusChoices.choices,default=RepairStatusChoices.ACTIVE)