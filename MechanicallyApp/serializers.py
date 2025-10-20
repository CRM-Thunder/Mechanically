from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, NotFound

from .models import Manufacturer, User, Location, UserLocationAssignment, Vehicle, FailureReport, RepairReport, \
    RepairReportRejection, City
from .validators import manufacturer_name_validator, first_name_validator, last_name_validator, phone_number_validator, \
    location_name_validator, vin_validator, vehicle_model_validator, vehicle_year_validator, natural_text_validator, \
    city_name_validator, street_name_validator
from .generators import generate_username, generate_random_password
from .mail_services import send_activation_email, send_reset_password_email

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields=['id','name']
        read_only_fields=['id']

    def validate_name(self,value):
        city_name_validator(value)
        return value


class LoginSerializer(serializers.Serializer):
    username=serializers.CharField(write_only=True)
    password=serializers.CharField(write_only=True)
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        if len(username) != 10 or len(password) >256:
            raise serializers.ValidationError('Username or password is incorrect.')
        return data

# serializer służący do wypisywania, dodawania oraz aktualizowania Location
class LocationCreateSerializer(serializers.ModelSerializer):
    location_type=serializers.CharField(max_length=1, required=True)
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
        # noinspection PyUnresolvedReferences
        valid_location_types = [choice[0] for choice in Location.LocationTypeChoices.choices]
        if value not in valid_location_types:
            raise serializers.ValidationError('Location type must be one of the following: %s' % ', '.join(valid_location_types))
        return value

    def validate_street_number(self,value):
        street_name_validator(value)
        return value

class LocationRetrieveSerializer(serializers.ModelSerializer):
    city=serializers.CharField(source='city.name',read_only=True)
    class Meta:
        model = Location
        fields = ['id','name', 'phone_number', 'email' ,'city', 'street_name','building_number','unit_number']
        read_only_fields = ['id','name', 'phone_number', 'email' ,'city', 'street_name','building_number','unit_number']

class LocationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id','name','location_type']
        read_only_fields = ['id','name','location_type']

class LocationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id','name','phone_number','email', 'city','street_name','building_number','unit_number']
        read_only_fields = ['id']

    def validate_name(self, value):
        location_name_validator(value)
        return value

    def validate_phone_number(self,value):
        phone_number_validator(value)
        return value

#serializer służący do wyświetlania informacji o przydziale z poziomu UserSerializer
class UserLocationAssignmentForUserSerializer(serializers.ModelSerializer):
    location=LocationCreateSerializer(read_only=True)
    class Meta:
        model = UserLocationAssignment
        fields = ['location','assign_date']
        read_only_fields = ['location','assign_date']

#serializer służący do tworzenia użytkownika
class UserCreateSerializer(serializers.ModelSerializer):
    role=serializers.CharField(max_length=8,required=True)
    class Meta:
        model = User
        fields = ['id','first_name','last_name','email','phone_number', 'role']
        read_only_fields = ['id']

    def validate_first_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError('First name must be at least 3 characters')
        first_name_validator(value)
        return value

    def validate_last_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError('Last name must be at least 3 characters')
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
        user=User.objects.create_user(username=generated_username, password=generated_password, is_active=False, is_new_account=True, **validated_data)
        token = default_token_generator.make_token(user)
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
        fields = ['id','first_name','last_name','email','phone_number', 'role']
        read_only_fields = ['id']

    def validate_first_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError('First name must be at least 3 characters')
        first_name_validator(value)
        return value

    def validate_last_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError('Last name must be at least 3 characters')
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
                raise serializers.ValidationError('Users with assigned locations cannot be changed to other roles.')

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
        is_user_profile_endpoint=self.context.get('user_profile_endpoint',False)
        fields=super().get_fields()
        if self.instance.role in ['standard','mechanic']:
            fields['user_location_assignment']=UserLocationAssignmentForUserSerializer(read_only=True)
        if request.user.is_superuser==False and is_user_profile_endpoint==False:
            fields.pop('is_superuser')
            fields.pop('is_active')
            fields.pop('username')
            fields.pop('date_joined')
        elif request.user.is_superuser==False and is_user_profile_endpoint==True:
            fields.pop('is_superuser')
            fields.pop('is_active')
        return fields

class AccountActivationSerializer(serializers.Serializer):
    user=serializers.UUIDField(write_only=True,required=True)
    token = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=256)
    confirm_password=serializers.CharField(max_length=256)
    _user_instance=None
    def validate(self, data):
        user_id = data.get('user')
        token = data.get('token')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        user=User.objects.filter(pk=user_id, is_active=False, is_new_account=True).first()
        if user is None or not default_token_generator.check_token(user, token):
            raise serializers.ValidationError({'detail':'Invalid user or token.'})

        if password != confirm_password:
            raise serializers.ValidationError({'detail':'Passwords do not match.'})

        try:
            validate_password(password, user)
        except DjangoValidationError as err:
            raise serializers.ValidationError({'password':err.messages})

        self._user_instance=user
        return data

    def save(self):
        user=self._user_instance
        user.set_password(self.validated_data.get('password'))
        user.is_active=True
        user.is_new_account=False
        user.save()
        return "Account has been activated."

class ResetPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def save(self):
        email = self.validated_data.get('email')
        user = User.objects.filter(email=email, is_active=True).first()
        print(user)
        if user is None:
            return "If an account with provided email exists, password reset link has been sent to provided email address."
        token = default_token_generator.make_token(user)
        send_reset_password_email(user, token=token)
        return "If an account with provided email exists, password reset link has been sent to provided email address."

class ResetPasswordSerializer(serializers.Serializer):
    user = serializers.UUIDField(write_only=True, required=True)
    token = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=256)
    confirm_password = serializers.CharField(max_length=256)
    _user_instance = None

    def validate(self, data):
        user_id = data.get('user')
        token = data.get('token')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        user = User.objects.filter(pk=user_id, is_active=True).first()
        if user is None or not default_token_generator.check_token(user, token):
            raise serializers.ValidationError({'detail':'Invalid user or token.'})
        try:
            validate_password(password, user)
        except DjangoValidationError as err:
            raise serializers.ValidationError({'password': err.messages})

        if password != confirm_password:
            raise serializers.ValidationError({'detail':'Passwords do not match.'})
        self._user_instance = user
        return data

    def save(self):
        user = self._user_instance
        user.set_password(self.validated_data.get('password'))
        user.save()
        return "Password has been changed."


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=256)
    new_password = serializers.CharField(max_length=256)
    confirm_password=serializers.CharField(max_length=256)

    def validate(self, data):
        user=self.context.get('user')
        old_password=data.get('old_password')
        new_password=data.get('new_password')
        confirm_password=data.get('confirm_password')
        user=authenticate(username=user.username, password=old_password)
        if user is None:
            raise serializers.ValidationError({'detail':'Invalid password.'})
        try:
            validate_password(new_password, user)
        except DjangoValidationError as err:
            raise serializers.ValidationError({'password': err.messages})

        if new_password == old_password:
            raise serializers.ValidationError({'detail':'This password is already used.'})
        if new_password != confirm_password:
            raise serializers.ValidationError({'detail':'Passwords do not match.'})
        return data

    def save(self, **kwargs):
        user=self.context.get('user')
        user.set_password(self.validated_data.get('new_password'))
        user.save()
        return "Password has been changed."


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
class UserLocationAssignmentSerializer(serializers.Serializer):
    location=serializers.PrimaryKeyRelatedField(queryset=Location.objects.all(),required=True)

    def validate(self, data):
        user = self.context.get('user')
        location = data.get('location')
        if user.role=='standard' and location.location_type!='B':
            raise serializers.ValidationError({'detail':'Standard users can be assigned to branch locations only.'})
        if user.role=='mechanic' and location.location_type!='W':
            raise serializers.ValidationError({'detail':'Mechanic users can be assigned to workshop locations only.'})
        return data

    def save(self, **kwargs):
        user = self.context.get('user')
        location = self.validated_data.get('location')
        UserLocationAssignment.objects.create(user_id=user.pk,location_id=location.pk)

#serializer służący do wypisania informacji o lokacji mechanika/standarda
class UserNestedLocationAssignmentSerializer(serializers.ModelSerializer):
    location=LocationCreateSerializer(read_only=True)
    class Meta:
        model = UserLocationAssignment
        fields = ['location','assign_date']
        read_only_fields = ['location','assign_date']

#serializer do wypisywania wszystkich informacji o pojeździe
class VehicleRetrieveSerializer(serializers.ModelSerializer):
    manufacturer=ManufacturerSerializer(read_only=True)
    branch=LocationCreateSerializer(read_only=True)
    class Meta:
        model=Vehicle
        fields='__all__'
        read_only_fields=['id','vin','kilometers','manufacturer','vehicle_model','year','vehicle_type','fuel_type','availability','branch']

#serializer do listowania informacji o pojeździe
class VehicleListSerializer(serializers.ModelSerializer):
    class Meta:
        model=Vehicle
        fields=['id','manufacturer','vehicle_type','fuel_type','vehicle_model','year','location','availability']
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
                'Availability type must be one of the following: %s' % ', '.join(availability_choices))
        return value

    def update(self, instance, validated_data):
        if FailureReport.objects.filter(vehicle_id=instance.id,status__in=['P','A','S']).exists() and validated_data.get('availability')=='A':
            raise serializers.ValidationError('Vehicle has been reported as failure. It cannot be set as available.')
        return super().update(instance, validated_data)

class FailureReportCreateSerializer(serializers.ModelSerializer):
    vehicle=serializers.UUIDField(required=True)
    class Meta:
        model=FailureReport
        fields=['vehicle','title','description']

    def validate_vehicle(self,value):
        value=Vehicle.objects.filter(pk=value).first()
        if value is None:
            raise NotFound('There is no vehicle with provided ID assigned to your branch.')
        user_location_id=UserLocationAssignment.objects.filter(user_id=self.context.get('request').user.id).values_list('location_id',flat=True).first()
        if user_location_id is None:
            raise NotFound('You are not assigned to any branch.')
        if value.location.id!=user_location_id:
            raise NotFound('There is no vehicle with provided ID assigned to your branch.')
        if FailureReport.objects.filter(vehicle_id=value.id,status__in=['P','A','S']).exists():
            raise serializers.ValidationError('Vehicle is already reported as failure.')
        return value

    def create(self, validated_data):
        vehicle=validated_data.get('vehicle')
        title = validated_data.get('title')
        description = validated_data.get('description')
        with transaction.atomic():
            vehicle.availability='U'
            vehicle.save()
            instance = FailureReport.objects.create(vehicle=vehicle,title=title,description=description,status='P', report_author=self.context.get('request').user)
            return instance


class FailureReportListSerializer(serializers.ModelSerializer):
    vehicle=VehicleRetrieveSerializer(read_only=True)
    class Meta:
        model=FailureReport
        fields=['id','title','vehicle','status','report_date','managed_by']
        read_only_fields=['id','title','vehicle','status','report_date','managed_by']

class FailureReportInfoForRepairReportSerializer(serializers.ModelSerializer):
    vehicle=VehicleRetrieveSerializer(read_only=True)
    class Meta:
        model=FailureReport
        fields=['id','title','vehicle','description','status','report_date']
        read_only_fields=['id','title','vehicle','description','status','report_date']

class FailureReportRetrieveSerializer(serializers.ModelSerializer):
    vehicle=VehicleRetrieveSerializer(read_only=True)
    workshop=LocationCreateSerializer(read_only=True)
    class Meta:
        model=FailureReport
        fields='__all__'
        read_only_fields=['id','title','vehicle','description','workshop','report_date','report_author','status','last_status_change_date']

class FailureReportAssignSerializer(serializers.Serializer):
    workshop=serializers.PrimaryKeyRelatedField(queryset=Location.objects.all(),required=True)

    def validate_workshop(self,value):
        if value.location_type!='W':
            raise serializers.ValidationError('Provided location is not a workshop.')
        return value

    def save(self):
        failure_report=self.context.get('failure_report')
        workshop=self.validated_data.get('workshop')
        with transaction.atomic():
            failure_report.workshop=workshop
            failure_report.status='A'
            failure_report.save()
            repair_report=RepairReport.objects.create(failure_report=failure_report,status='A',cost=0)
            return {'repair_report_id':repair_report.pk}


class FailureReportReassignSerializer(serializers.Serializer):
    workshop = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all(), required=True)
    def validate_workshop(self,value):
        if value.location_type!='W':
            raise serializers.ValidationError('Provided location is not a workshop.')
        elif value.id==self.context.get('failure_report').workshop.id:
            raise serializers.ValidationError('Provided workshop is the same as current workshop.')
        return value

    def save(self):
        failure_report = self.context.get('failure_report')
        workshop = self.validated_data.get('workshop')
        failure_report.workshop = workshop
        failure_report.status = 'A'
        failure_report.save()
        return "Report has been reassigned to provided workshop."

class RepairReportRetrieveUpdateSerializer(serializers.ModelSerializer):
    failure_report=FailureReportInfoForRepairReportSerializer(read_only=True)
    class Meta:
        model=RepairReport
        fields=['id','failure_report','condition_analysis','repair_action','cost','last_change_date','status']
        read_only_fields=['id','failure_report','last_change_date','status']

    def validate_cost(self,value):
        if value<0:
            raise serializers.ValidationError('Cost cannot be negative.')
        return value

    def validate(self,data):
        if self.instance.status!='A':
            raise serializers.ValidationError({'detail':'Repair report cannot be modified if not in ACTIVE status.'})
        return super().validate(data)

class RepairReportListSerializer(serializers.ModelSerializer):
    title=serializers.CharField(source='failure_report.title',read_only=True)
    vehicle=serializers.UUIDField(source='failure_report.vehicle_id',read_only=True)
    report_date=serializers.DateTimeField(source='failure_report.report_date',read_only=True)
    class Meta:
        model=RepairReport
        fields=['id','title','status','vehicle','report_date']
        read_only_fields=['id','title','status','vehicle','report_date']

class RepairReportRejectionListSerializer(serializers.ModelSerializer):
    class Meta:
        model=RepairReportRejection
        fields=['id','repair_report','title','rejection_date']
        read_only_fields=['id','repair_report','title','rejection_date']


class RepairReportRejectionRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model=RepairReportRejection
        fields=['id','repair_report','title','rejection_date','reason']
        read_only_fields=['id','repair_report','title','rejection_date','reason']


class RepairReportRejectionSerializer(serializers.ModelSerializer):
    class Meta:
        model=RepairReportRejection
        fields=['id','title','rejection_date','reason']
        read_only_fields=['id','rejection_date']

    def validate_title(self,value):
        natural_text_validator(value)
        return value

    def validate_reason(self,value):
        natural_text_validator(value)
        return value

    def save(self, **kwargs):
        title=self.validated_data.get('title')
        reason=self.validated_data.get('reason')
        repair_report=self.context.get('repair_report')
        rejection=RepairReportRejection.objects.create(title=title,repair_report=repair_report,reason=reason)
        rejection.save()
        return rejection