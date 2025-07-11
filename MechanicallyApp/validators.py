from django.core.validators import RegexValidator

first_name_validator = RegexValidator(regex=r'^[A-Z][a-z]*$', message='First name must start with capital letter.')

last_name_validator = RegexValidator(regex=r'^[A-Z][a-z]*$', message='Last name must start with capital letter.')