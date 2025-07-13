from rest_framework import serializers

from .models import Manufacturer, User, Location
from .validators import manufacturer_name_validator, first_name_validator, last_name_validator, phone_number_validator, location_name_validator
from .generators import generate_username

class UserSerializer(serializers.ModelSerializer):
    #zastanowić się nad osobnym serializerem read only, który by zawierał username bo to info wrażliwe po części, a nie wszyscy muszą mieć do niego dostęp
    class Meta:
        model = User
        fields = ['id','username','first_name','last_name','email','phone_number', 'role']
        read_only_fields = ['id','username']

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

    def create(self, validated_data):
        first_name=validated_data.get('first_name')
        last_name=validated_data.get('last_name')
        generated_username=generate_username(first_name, last_name)
        while User.objects.filter(username=generated_username).exists():
            generated_username=generate_username(first_name, last_name)
        user=User.objects.create(username=generated_username, **validated_data)
        return user

    def update(self, instance, validated_data):
        instance.first_name=validated_data.get('first_name', instance.first_name)
        instance.last_name=validated_data.get('last_name', instance.last_name)
        instance.email=validated_data.get('email', instance.email)
        if instance.first_name != validated_data.get('first_name', instance.first_name) or instance.last_name != validated_data.get('last_name', instance.last_name):
            new_username=generate_username(instance.first_name, instance.last_name)
            while User.objects.filter(username=new_username).exists():
                new_username=generate_username(instance.first_name, instance.last_name)
            instance.username=new_username
        instance.save()
        #należy zająć się rolą, aby mechanik/standard nie mógł zmienić roli jeśli ma LocationUserAssignment
        return instance



class ManufacturerSerializer(serializers.ModelSerializer):
    id=serializers.UUIDField(read_only=True)
    class Meta:
        model = Manufacturer
        fields = ['id','name']

    def validate_name(self, value):
        manufacturer_name_validator(value)
        return value


class LocationSerializer(serializers.ModelSerializer):
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
            valid_location_types = [choice[0] for choice in Location.LocationTypeChoices.choices]
            if value not in valid_location_types:
                raise serializers.ValidationError('Location type must be one of the following: %s' % ', '.join(valid_location_types))
