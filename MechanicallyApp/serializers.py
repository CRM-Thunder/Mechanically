from rest_framework import serializers

from .models import Manufacturer, User
from .validators import manufacturer_name_validator, first_name_validator, last_name_validator
from .generators import generate_username

# noinspection PyMethodMayBeStatic
class ManufacturerCreateReadSerializer(serializers.ModelSerializer):
    id=serializers.UUIDField(read_only=True)
    class Meta:
        model = Manufacturer
        fields = ['id','name']

    def validate_name(self, value):
        manufacturer_name_validator(value)
        return value


# noinspection PyMethodMayBeStatic
class UserCreateReadSerializer(serializers.ModelSerializer):
    id=serializers.UUIDField(read_only=True)
    username=serializers.CharField(read_only=True)
    class Meta:
        model = User
        fields = ['id','username','first_name','last_name','email', 'role']

    def validate_first_name(self, value):
        first_name_validator(value)
        return value

    def validate_last_name(self, value):
        last_name_validator(value)
        return value

    def create(self, validated_data):
        first_name=validated_data.get('first_name', None)
        last_name=validated_data.get('last_name', None)
        generated_username=generate_username(first_name, last_name)
        while User.objects.filter(username=generated_username).exists():
            generated_username=generate_username(first_name, last_name)
        user=User.objects.create(username=generated_username, **validated_data)
        return user