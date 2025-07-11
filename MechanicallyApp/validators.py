from datetime import date
import re
from rest_framework import serializers

def first_name_validator(first_name):
    if not re.match(r'^[A-Z][a-z]*$', first_name):
        raise serializers.ValidationError('First name must start with capital letter.')



def last_name_validator(last_name):
    if not re.match(r'^[A-Z][a-z]*$', last_name):
        raise serializers.ValidationError('Last name must start with capital letter.')


def vin_validator(vin):
    if not re.match(r'^[A-HJ-NPR-Z0-9]{17}$', vin):
        raise serializers.ValidationError('VIN must be in correct format.')

def vehicle_year_validator(vehicle_year):
    current_year=date.today().year
    if vehicle_year < 1900 or vehicle_year > current_year:
        raise serializers.ValidationError('Vehicle production year must be between 1900 and current year.')