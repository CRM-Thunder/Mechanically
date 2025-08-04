from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.validators import UniqueValidator

from .models import Manufacturer, User, Location, UserLocationAssignment, Vehicle, FailureReport, RepairReport
from .validators import manufacturer_name_validator, first_name_validator, last_name_validator, phone_number_validator, location_name_validator, vin_validator, vehicle_model_validator, vehicle_year_validator
from .generators import generate_username, generate_random_password
from .mail_services import send_activation_email, send_reset_password_email

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



#serializer służący do wyświetlania informacji o przydziale z poziomu UserSerializer
class UserLocationAssignmentForUserSerializer(serializers.ModelSerializer):
    location=LocationSerializer(read_only=True)
    class Meta:
        model = UserLocationAssignment
        fields = ['location','assign_date']
        read_only_fields = ['location','assign_date']

#serializer służący do tworzenia użytkownika
class UserCreateSerializer(serializers.ModelSerializer):
    role=serializers.CharField(max_length=8)
    class Meta:
        model = User
        fields = ['id','first_name','last_name','email','phone_number', 'role']
        read_only_fields = ['id']

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
        is_superuser=self.context.get('is_superuser',False)
        roles = [choice[0] for choice in User.ROLE_CHOICES]
        if is_superuser:
            valid_roles=roles
        else:
            valid_roles=('standard','manager','mechanic')

        if value not in valid_roles:
            if value not in roles:
                raise serializers.ValidationError('Role must be one of the following: %s' % ', '.join(valid_roles))
            else:
                raise PermissionDenied("You do not have permission to perform this action.")
        return value

    def create(self, validated_data):
        first_name=validated_data.get('first_name')
        last_name=validated_data.get('last_name')
        generated_username=generate_username(first_name, last_name)
        while User.objects.filter(username=generated_username).exists():
            generated_username=generate_username(first_name, last_name)
        generated_password=generate_random_password()
        while validate_password(generated_password) is not None:
            generated_password=generate_random_password()
        user=User.objects.create_user(username=generated_username, password=generated_password, is_active=False, **validated_data)
        token = default_token_generator.make_token(user)
        #TODO: przejść na asynchroniczne wysyłanie maila
        send_activation_email(user, token=token)
        return user

class UserListSerializer(serializers.ModelSerializer):
    location=serializers.UUIDField(source='user_location_assignment.location.id', read_only=True)
    class Meta:
        model = User
        fields = ['id','first_name','last_name','email','phone_number','role','location']
        read_only_fields = ['id','first_name','last_name','email','phone_number', 'role','location']

    def to_representation(self,instance):
        rep=super().to_representation(instance)
        if instance.role not in ('standard','mechanic'):
            rep.pop('location')
        return rep

class UserUpdateSerializer(serializers.ModelSerializer):
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

    def validate_role(self,value):
        valid_roles = ('standard', 'manager', 'mechanic')
        if value not in valid_roles:
            raise serializers.ValidationError('Updated role must be one of the following: %s' % ', '.join(valid_roles))
        return value

    def update(self, instance, validated_data):
        if validated_data.get('role', instance.role)!=instance.role:
            if instance.role=='admin':
                raise serializers.ValidationError('Admin users cannot be changed to other roles.')

            if UserLocationAssignment.objects.filter(user=instance).exists():
                raise serializers.ValidationError('Users with assigned locations cannot be changed to other roles. Please unassign user from location first.')

        if instance.first_name != validated_data.get('first_name', instance.first_name) or instance.last_name != validated_data.get('last_name', instance.last_name):
            instance.first_name = validated_data.get('first_name', instance.first_name)
            instance.last_name = validated_data.get('last_name', instance.last_name)
            new_username=generate_username(instance.first_name, instance.last_name)

            while User.objects.filter(username=new_username).exists():
                new_username=generate_username(instance.first_name, instance.last_name)
            instance.username=new_username

        instance.email=validated_data.get('email', instance.email)
        instance.phone_number=validated_data.get('phone_number', instance.phone_number)
        instance.role=validated_data.get('role', instance.role)
        instance.save()
        return instance

class UserRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','first_name','last_name','email','phone_number', 'role', 'is_superuser','is_active','date_joined']
        read_only_fields = ['id','username','first_name','last_name','email','phone_number', 'role', 'is_superuser','is_active','date_joined']

    def get_fields(self):
        request=self.context.get('request')
        fields=super().get_fields()
        if self.instance.role in ['standard','mechanic']:
            fields['user_location_assignment']=UserLocationAssignmentForUserSerializer(read_only=True)
        #TODO: ewentualnie zamienić na dodawanie pól, trzeba sprawdzić jak podawać źródło danych dla nich
        if not request.user.is_superuser:
            fields.pop('is_superuser')
            fields.pop('is_active')
            fields.pop('username')
            fields.pop('date_joined')
        return fields

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

class ResetPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def save(self):
        email = self.validated_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return "If an account with provided email exists, password reset link has been sent to provided email address."
        token = default_token_generator.make_token(user)
        send_reset_password_email(user, token=token)
        return "If an account with provided email exists, password reset link has been sent to provided email address."

class ResetPasswordSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    token = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=128)
    confirm_password = serializers.CharField(max_length=128)

    def validate(self, data):
        user_id = data['id']
        user = get_object_or_404(User, id=user_id, is_active=True)
        token = data['token']
        password = data['password']
        confirm_password = data['confirm_password']
        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError('Invalid token.')

        try:
            validate_password(password, user)
        except DjangoValidationError as err:
            raise serializers.ValidationError({'passwords': err.messages})

        if password != confirm_password:
            raise serializers.ValidationError('Passwords do not match.')

        return data

    def save(self):
        user_id = self.validated_data['id']
        user = get_object_or_404(User, id=user_id, is_active=True)
        user.set_password(self.validated_data['password'])
        user.save()
        return "Password has been successfully changed. You can now login with your new credentials."


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
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        validators=[
            UniqueValidator(
                queryset=UserLocationAssignment.objects.all(),
                message="This user is already assigned to a location."
            )
        ]
    )
    class Meta:
        model = UserLocationAssignment
        fields = ['user','location','assign_date']
        read_only_fields = ['assign_date']

    def validate_user(self,value):
        if value.role not in ('standard','mechanic'):
            raise serializers.ValidationError('Only standard users and mechanic users can be assigned to locations.')
        return value

    def validate(self, data):
        user = data['user']
        location = data['location']
        if user.role=='standard' and location.location_type!='B':
            raise serializers.ValidationError('Standard users can be assigned to branch locations only.')
        if user.role=='mechanic' and location.location_type!='W':
            raise serializers.ValidationError('Mechanic users can be assigned to workshop locations only.')
        return data

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

class FailureReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model=FailureReport
        fields=['vehicle','description']

    def validate_vehicle(self,value):
        author_branch=UserLocationAssignment.objects.get(user=self.context.get('request').user).location
        if value.location!=author_branch:
            raise NotFound('There is no vehicle with provided ID assigned to your branch.')
        if FailureReport.objects.filter(vehicle_id=value.id,status__in=['P','A','S']).exists():
            raise serializers.ValidationError('Vehicle is already reported as failure.')
        return value

    def create(self, validated_data):
        vehicle=validated_data.get('vehicle')
        vehicle.availability='U'
        description=validated_data.get('description')
        vehicle.save()
        FailureReport.objects.create(vehicle=vehicle,description=description,status='P', report_author=self.context.get('request').user)
        return "Report has been successfully created. Technical staff will take care of the vehicle as soon as possible."


class FailureReportListSerializer(serializers.ModelSerializer):
    vehicle=VehicleRetrieveSerializer(read_only=True)
    class Meta:
        model=FailureReport
        fields=['id','title','vehicle','status','report_date']
        read_only_fields=['id','title','vehicle','status','report_date']

class FailureReportRetrieveSerializer(serializers.ModelSerializer):
    vehicle=VehicleRetrieveSerializer(read_only=True)
    report_author=UserRetrieveSerializer(read_only=True)
    workshop=LocationSerializer(read_only=True)
    class Meta:
        model=FailureReport
        fields='__all__'
        read_only_fields=['id','title','vehicle','description','workshop','report_date','report_author','status','last_status_change_date']

class FailureReportAssignWorkshopSerializer(serializers.Serializer):
    failure_report=serializers.PrimaryKeyRelatedField(queryset=FailureReport.objects.filter(workshop=None),required=True)
    workshop=serializers.PrimaryKeyRelatedField(queryset=Location.objects.filter(location_type='W'),required=True)

    def validate_failure_report(self,value):
        if value.status!='P':
            raise serializers.ValidationError('Selected failure report is not in pending status.')

    def save(self):
        failure_report=self.validated_data['failure_report']
        workshop=self.validated_data['workshop']
        failure_report.workshop=workshop
        failure_report.status='A'
        failure_report.save()
        #TODO: zmienić warunek uwzględniając osobny status dla rozpoczętego RepairReport ale bez warsztatu
        if RepairReport.objects.filter(failure_report=failure_report, status__in=['A','R']).exists():
            repair_report=RepairReport.objects.get(failure_report=failure_report)
        else:
            repair_report=RepairReport.objects.create(failure_report=failure_report,status='A',cost=0)
        return {'failure_report':failure_report,'repair_report':repair_report}
