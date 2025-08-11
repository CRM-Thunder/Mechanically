from django.core.validators import MinLengthValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
class User(AbstractUser):
    ROLE_CHOICES=(
        ('standard','standard'),
        ('mechanic','mechanic'),
        ('manager','manager'),
        ('admin','administrator')
    )
    role=models.CharField(max_length=10,choices=ROLE_CHOICES,default='standard')
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    username = models.CharField(max_length=10, unique=True,
    validators=[
        MinLengthValidator(10)
    ])
    email=models.EmailField(unique=True)
    first_name = models.CharField(max_length=20,validators=[MinLengthValidator(3)])
    last_name = models.CharField(max_length=30,validators=[MinLengthValidator(3)])
    phone_number=models.CharField(max_length=9, unique=True, validators=[MinLengthValidator(9)])
    REQUIRED_FIELDS = ['email','first_name','last_name']
    def __str__(self):
        return self.username

    def get_full_name(self):
        return self.first_name + " " + self.last_name

    def get_short_name(self):
        return self.first_name

class Location(models.Model):
    class LocationTypeChoices(models.TextChoices):
        BRANCH='B'
        WORKSHOP='W'

    name = models.CharField(max_length=100, unique=True, validators=[MinLengthValidator(3)])
    phone_number = models.CharField(max_length=9, unique=True, validators=[MinLengthValidator(9)])
    email = models.EmailField()
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    #narazie jako pojedyncze pole, w razie czego można rozbudować
    address=models.CharField(max_length=50)
    # noinspection PyUnresolvedReferences
    location_type=models.CharField(max_length=1,choices=LocationTypeChoices.choices)


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
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    vin=models.CharField(max_length=17,unique=True, validators=[MinLengthValidator(17)])
    kilometers=models.PositiveIntegerField()
    manufacturer=models.ForeignKey('Manufacturer',on_delete=models.PROTECT, related_name='vehicles')
    vehicle_model=models.CharField(max_length=20)
    year=models.PositiveIntegerField()
    # noinspection PyUnresolvedReferences
    vehicle_type=models.CharField(max_length=2, choices=VehicleTypeChoices.choices, default=VehicleTypeChoices.OTHER)
    # noinspection PyUnresolvedReferences
    fuel_type=models.CharField(max_length=2, choices=FuelTypeChoices.choices, default=FuelTypeChoices.OTHER)
    # noinspection PyUnresolvedReferences
    availability=models.CharField(max_length=1, choices=AvailabilityChoices.choices, default=AvailabilityChoices.AVAILABLE)
    #musi być zabezpieczenie, że może być przypisany tylko do brancha, na poziomie Serializera lub stworzyć własny trigger
    location=models.ForeignKey('Location',on_delete=models.SET_NULL, related_name='vehicles', null=True, blank=True)


class Manufacturer(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    name=models.CharField(max_length=20,unique=True, validators=[MinLengthValidator(3)])
    def __str__(self):
        return self.name



class UserLocationAssignment(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user=models.OneToOneField('User',on_delete=models.CASCADE, related_name='user_location_assignment')
    location=models.ForeignKey('Location',on_delete=models.CASCADE, related_name='user_location_assignment')
    assign_date=models.DateTimeField(auto_now_add=True)

class FailureReport(models.Model):
    class FailureStatusChoices(models.TextChoices):
        PENDING='P'
        ASSIGNED='A'
        STOPPED='S'
        DISMISSED='D'
        RESOLVED='R'
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    vehicle=models.ForeignKey('Vehicle',on_delete=models.CASCADE, related_name='failure_reports')
    title=models.CharField(max_length=100)
    description=models.TextField()
    workshop=models.ForeignKey('Location',on_delete=models.SET_NULL, null=True, blank=True, related_name='failure_reports')
    report_date=models.DateTimeField(auto_now_add=True)
    report_author=models.ForeignKey('User',on_delete=models.SET_NULL, related_name='failure_reports',null=True)
    # noinspection PyUnresolvedReferences
    status=models.CharField(max_length=1,choices=FailureStatusChoices.choices,default=FailureStatusChoices.PENDING)
    last_status_change_date=models.DateTimeField(auto_now=True)

class RepairReport(models.Model):
    class RepairStatusChoices(models.TextChoices):
        ACTIVE='A'
        READY='R'
        HISTORIC='H'
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    failure_report=models.OneToOneField('FailureReport',on_delete=models.CASCADE, related_name='repair_report')
    condition_analysis=models.TextField()
    repair_action=models.TextField()
    cost=models.DecimalField(max_digits=8,decimal_places=2)
    last_change_date=models.DateTimeField(auto_now=True)
    # noinspection PyUnresolvedReferences
    status=models.CharField(max_length=1,choices=RepairStatusChoices.choices,default=RepairStatusChoices.ACTIVE)