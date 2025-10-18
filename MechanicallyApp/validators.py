from datetime import date
import re
from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError

def first_name_validator(first_name):
    if not re.match('^[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]{2,}$', first_name):
        raise serializers.ValidationError('First name must start with capital letter and contain only letters.')


def last_name_validator(last_name):
    if not re.match(r"^[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]{2,}(?:[-' ][A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+)*$", last_name):
        raise serializers.ValidationError('Last name must start with capital letter and contain only letters, spaces, apostrophes, hyphens.')


def vin_validator(vin):
    if not re.match(r'^[A-HJ-NPR-Z0-9]{17}$', vin):
        raise serializers.ValidationError('VIN must be in correct format.')

def phone_number_validator(phone_number):
    if not re.match(r'^\d{9}$', phone_number):
        raise serializers.ValidationError('Phone number must be in correct format: XXXXXXXXX')

def manufacturer_name_validator(manufacturer_name):
    if not re.match(r'^[A-Z][a-zA-Z]*(?:[ -][A-Z][a-zA-Z]*)*$', manufacturer_name):
        raise serializers.ValidationError('Manufacturer name must start with capital letter and may contain letters, single spaces or hyphens.')

def location_name_validator(location_name):
    if not re.match(r'^[A-ZĄĆĘŁŃÓŚŹŻ]+(?:[ -][A-ZĄĆĘŁŃÓŚŹŻ]+)*$', location_name):
        raise serializers.ValidationError('Location name must consist of capital letters and may contain single spaces or hyphens.')

def vehicle_year_validator(vehicle_year):
    current_year=date.today().year
    if vehicle_year < 1900 or vehicle_year > current_year:
        raise serializers.ValidationError('Vehicle production year must be between 1900 and current year.')

def vehicle_model_validator(vehicle_model):
    if not re.match(r'^[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?(?: [A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?)*$', vehicle_model):
        raise serializers.ValidationError('Vehicle model may contain letters, numbers, hyphens, dots, and single spaces between words. It cannot start or end with a space, hyphen, or dot.')

def natural_text_validator(text):
    if not re.match(r'^[A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż0-9\s.,:!?\'"\-()@]*$', text):
        raise serializers.ValidationError('"Only letters, numbers, spaces, and basic punctuation are allowed."')

class MaximumLengthValidator:
    def __init__(self, max_length=256):
        self.max_length = max_length

    def validate(self, password, user=None):
        if len(password) > self.max_length:
           raise DjangoValidationError(f'Password must be less than {self.max_length} characters.', code='password_to_long', params={'max_length': self.max_length})
