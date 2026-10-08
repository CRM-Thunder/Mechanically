import random
from django.utils.crypto import get_random_string
def generate_username(first_name, last_name):
    first_name=first_name.lower()
    last_name=last_name.lower()
    random_number=random.randint(1,9999)
    random_number_str=str(random_number)
    random_number_str_2=(4-len(random_number_str))*'0'+random_number_str
    return (
        first_name[:3] + last_name[:3] + random_number_str_2
    )

def generate_random_password():
    random_string_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!#$%&()*+,-./:;<=>?@[]^_`{|}~"
    return get_random_string(length=256, allowed_chars=random_string_chars)