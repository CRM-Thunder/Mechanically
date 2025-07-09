from django.core.validators import MinLengthValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
class User(AbstractUser):
    #odwzorować mechanizm tworzenia username jak na usosie, czyli 3 litery imienia 3 litery nazwiska i 4 cyfrowy kod
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
        petrol = 'P'
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
    manufacturer=models.CharField(max_length=20)
    vehicleModel=models.CharField(max_length=20)
    year=models.PositiveIntegerField()
    # noinspection PyUnresolvedReferences
    vehicleType=models.CharField(max_length=2, choices=VehicleTypeChoices.choices, default=VehicleTypeChoices.OTHER)
    # noinspection PyUnresolvedReferences
    fuelType=models.CharField(max_length=2, choices=FuelTypeChoices.choices, default=FuelTypeChoices.OTHER)
    # noinspection PyUnresolvedReferences
    availability=models.CharField(max_length=1, choices=AvailabilityChoices.choices, default=AvailabilityChoices.AVAILABLE)
    #musi być zabezpieczenie że może być przypisany tylko do brancha
    branchId=models.ForeignKey('Location',on_delete=models.CASCADE)

class Location(models.Model):
    class LocationTypeChoices(models.TextChoices):
        BRANCH='B'
        WORKSHOP='W'
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    #narazie jako pojedyncze pole, w razie czego można rozbudować
    address=models.CharField(max_length=50)
    # noinspection PyUnresolvedReferences
    locationType=models.CharField(max_length=1,choices=LocationTypeChoices.choices,default=LocationTypeChoices.BRANCH)

#należy wprowadzić zabezpieczenie, że do warsztatu może zostać przydzielony tylko mechanik, a do brancha tylko standardowy pracownik
class UserLocationAssignment(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    userId=models.ForeignKey(User,on_delete=models.CASCADE)
    locationId=models.ForeignKey(Location,on_delete=models.CASCADE)
    assignDate=models.DateTimeField(auto_now_add=True)

class FailureReport(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING='P'
        ASSIGNED='A'
        DISMISSED='D'
        RESOLVED='R'
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    vehicleId=models.ForeignKey(Vehicle,on_delete=models.CASCADE)
    description=models.TextField()
    reportDate=models.DateTimeField(auto_now_add=True)
    #zabezpieczyć aby tylko standardowy/menadżer mógł być autorem
    reportAuthor=models.ForeignKey(User,on_delete=models.CASCADE)
    # noinspection PyUnresolvedReferences
    status=models.CharField(max_length=1,choices=StatusChoices.choices,default=StatusChoices.PENDING)
    lastStatusChangeDate=models.DateTimeField(auto_now=True)

class RepairReport(models.Model):

    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    failureReportId=models.ForeignKey(FailureReport,on_delete=models.CASCADE)
    conditionAnalysis=models.TextField()
    repairAction=models.TextField()
    cost=models.DecimalField(max_digits=8,decimal_places=2)
    reportDate=models.DateTimeField(auto_now_add=True)
    readyForReview=models.BooleanField(default=False)
