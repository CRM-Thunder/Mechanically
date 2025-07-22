from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from .models import Manufacturer, User, Location, UserLocationAssignment, Vehicle, FailureReport
from .validators import manufacturer_name_validator, first_name_validator, last_name_validator, phone_number_validator, location_name_validator, vin_validator, vehicle_model_validator, vehicle_year_validator
from .generators import generate_username
from .mail_services import send_activation_email



#serializer służący do wyświetlania informacji o przydziale z poziomu UserSerializer
class UserLocationAssignmentForUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLocationAssignment
        fields = ['location','assign_date']
        read_only_fields = ['location','assign_date']



#TODO: Dokładnie zaprojektować serializery dla Usera, dla odpowiednich funkcjonalności i poziomów uprawnień
class UserSerializer(serializers.ModelSerializer):
    user_location_assignment=UserLocationAssignmentForUserSerializer(read_only=True)
    #zastanowić się nad osobnym serializerem read only, który by zawierał username, bo to info wrażliwe po części, a nie wszyscy muszą mieć do niego dostęp
    class Meta:
        model = User
        fields = ['id','username','first_name','last_name','email','phone_number', 'role', 'user_location_assignment']
        read_only_fields = ['id','username','user_location_assignment']

    def validate_first_name(self, value):
        first_name_validator(value)
        return value

    def validate_last_name(self, value):
        last_name_validator(value)
        return value

    def validate_phone_number(self,value):
        phone_number_validator(value)
        return value

    def validate_role(self, value):
        valid_roles = [choice[0] for choice in User.ROLE_CHOICES]
        if value not in valid_roles:
            raise serializers.ValidationError('Role must be one of the following: %s' % ', '.join(valid_roles))
        return value

    def create(self, validated_data):
        first_name=validated_data.get('first_name')
        last_name=validated_data.get('last_name')
        generated_username=generate_username(first_name, last_name)
        while User.objects.filter(username=generated_username).exists():
            generated_username=generate_username(first_name, last_name)
        user=User.objects.create_user(username=generated_username, **validated_data)
        return user
    def update(self, instance, validated_data):
        if instance.first_name != validated_data.get('first_name', instance.first_name) or instance.last_name != validated_data.get('last_name', instance.last_name):
            new_username=generate_username(instance.first_name, instance.last_name)
            while User.objects.filter(username=new_username).exists():
                new_username=generate_username(instance.first_name, instance.last_name)
            instance.username=new_username
        instance.first_name=validated_data.get('first_name', instance.first_name)
        instance.last_name=validated_data.get('last_name', instance.last_name)
        instance.email=validated_data.get('email', instance.email)
        instance.save()
        #należy zająć się rolą, aby mechanik/standard nie mógł zmienić roli jeśli ma LocationUserAssignment
        return instance

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name','last_name','email','phone_number', 'role']

    def validate_first_name(self, value):
        first_name_validator(value)
        return value

    def validate_last_name(self, value):
        last_name_validator(value)
        return value

    def validate_phone_number(self,value):
        phone_number_validator(value)
        return value

    def validate_role(self, value):
        valid_roles = [choice[0] for choice in User.ROLE_CHOICES]
        if value not in valid_roles:
            raise serializers.ValidationError('Role must be one of the following: %s' % ', '.join(valid_roles))
        return value

    def create(self, validated_data):
        first_name=validated_data.get('first_name')
        last_name=validated_data.get('last_name')
        generated_username=generate_username(first_name, last_name)
        while User.objects.filter(username=generated_username).exists():
            generated_username=generate_username(first_name, last_name)
        user=User.objects.create_user(username=generated_username, is_active=False, **validated_data)
        token = default_token_generator.make_token(user)
        send_activation_email(user, token=token)
        return user


#serializer służący do wypisywania, dodawania oraz aktualizowania Manufacturer
class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = '__all__'
        read_only_fields = ['id']

    def validate_name(self, value):
        manufacturer_name_validator(value)
        return value


#serializer do przypisywania użytkownika do danej lokalizacji
class UserLocationAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLocationAssignment
        fields = ['id','user','location','assign_date']
        read_only_fields = ['id','assign_date']

#serializer służący do wypisywania, dodawania oraz aktualizowania Location
class LocationSerializer(serializers.ModelSerializer):
    location_type=serializers.CharField(max_length=1)
    class Meta:
        model = Location
        fields = '__all__'
        read_only_fields = ['id']

    def validate_name(self, value):
        location_name_validator(value)
        return value

    def validate_phone_number(self,value):
        phone_number_validator(value)
        return value

    def validate_location_type(self, value):
        if self.instance and value!=self.instance.location_type:
            raise serializers.ValidationError('Location type cannot be changed')
        # noinspection PyUnresolvedReferences
        valid_location_types = [choice[0] for choice in Location.LocationTypeChoices.choices]
        if value not in valid_location_types:
            raise serializers.ValidationError('Location type must be one of the following: %s' % ', '.join(valid_location_types))
        return value



#serializer służący do wypisania informacji o lokacji mechanika/standarda
class UserNestedLocationAssignmentSerializer(serializers.ModelSerializer):
    location=LocationSerializer(read_only=True)
    class Meta:
        model = UserLocationAssignment
        fields = ['location','assign_date']
        read_only_fields = ['location','assign_date']

#serializer do wypisywania wszystkich informacji o pojeździe
class VehicleRetrieveSerializer(serializers.ModelSerializer):
    manufacturer=ManufacturerSerializer(read_only=True)
    branch=LocationSerializer(read_only=True)
    class Meta:
        model=Vehicle
        fields='__all__'
        read_only_fields=['id','vin','kilometers','manufacturer','vehicle_model','year','vehicle_type','fuel_type','availability','branch']

#serializer do listowania informacji o pojeździe
class VehicleListSerializer(serializers.ModelSerializer):
    class Meta:
        model=Vehicle
        fields=['id','manufacturer','vehicle_model','year','location','availability']
        read_only_fields=['id','manufacturer','vehicle_model','year','location','availability']

#serializer do dodawania i aktualizacji pojazdu
class VehicleCreateUpdateSerializer(serializers.ModelSerializer):
    vehicle_type = serializers.CharField(max_length=2)
    fuel_type = serializers.CharField(max_length=2)
    class Meta:
        model = Vehicle
        fields = ['id','vin','kilometers','manufacturer','vehicle_model','year','vehicle_type','fuel_type','location','availability']
        read_only_fields = ['id']

    def validate_vin(self,value):
        vin_validator(value)
        return value

    def validate_vehicle_model(self, value):
        vehicle_model_validator(value)
        return value

    def validate_year(self, value):
        vehicle_year_validator(value)
        return value

    def validate_vehicle_type(self,value):
        # noinspection PyUnresolvedReferences
        valid_vehicle_types = [choice[0] for choice in Vehicle.VehicleTypeChoices.choices]
        if value not in valid_vehicle_types:
            raise serializers.ValidationError('Vehicle type must be one of the following: %s' % ', '.join(valid_vehicle_types))
        return value

    def validate_fuel_type(self,value):
        # noinspection PyUnresolvedReferences
        valid_fuel_types = [choice[0] for choice in Vehicle.FuelTypeChoices.choices]
        if value not in valid_fuel_types:
            raise serializers.ValidationError(
                'Fuel type must be one of the following: %s' % ', '.join(valid_fuel_types))
        return value


    def validate_location(self,value):
        if value.location_type!='B':
            raise serializers.ValidationError('Vehicle can only be assigned to branch location.')
        return value

    def validate_availability(self,value):
        # noinspection PyUnresolvedReferences
        availability_choices = [choice[0] for choice in Vehicle.AvailabilityChoices.choices]
        if value not in availability_choices:
            raise serializers.ValidationError(
                'Location type must be one of the following: %s' % ', '.join(availability_choices))
        return value

    #TODO:należy przetestować po zaimplementowaniu widoków z FailureReport
    def update(self, instance, validated_data):
        if FailureReport.objects.filter(vehicle_id=instance.id,status__in=['P','A']).exists() and validated_data.get('availability')=='A':
            raise serializers.ValidationError('Vehicle has been reported as failure. It cannot be set as available.')
        instance.vin=validated_data.get('vin', instance.vin)
        instance.kilometers=validated_data.get('kilometers', instance.kilometers)
        instance.manufacturer=validated_data.get('manufacturer', instance.manufacturer)
        instance.vehicle_model=validated_data.get('vehicle_model', instance.vehicle_model)
        instance.year=validated_data.get('year', instance.year)
        instance.vehicle_type=validated_data.get('vehicle_type', instance.vehicle_type)
        instance.fuel_type=validated_data.get('fuel_type', instance.fuel_type)
        instance.location=validated_data.get('location', instance.location)
        instance.availability=validated_data.get('availability', instance.availability)
        instance.save()
        return instance

class AccountActivationSerializer(serializers.Serializer):
    id=serializers.UUIDField()
    token = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=128)
    confirm_password=serializers.CharField(max_length=128)

    def validate(self, data):
        user_id = data['id']
        user=get_object_or_404(User, id=user_id, is_active=False)
        token = data['token']
        password = data['password']
        confirm_password = data['confirm_password']
        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError('Invalid token.')

        try:
            validate_password(password, user)
        except DjangoValidationError as err:
            raise serializers.ValidationError({'passwords':err.messages})

        if password != confirm_password:
            raise serializers.ValidationError('Passwords do not match.')

        return data

    def save(self):
        user_id = self.validated_data['id']
        user=get_object_or_404(User, id=user_id, is_active=False)
        user.set_password(self.validated_data['password'])
        user.is_active=True
        user.save()
        return "Account has been activated."








