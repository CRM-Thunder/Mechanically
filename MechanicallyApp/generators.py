import random

def generate_username(first_name, last_name):
    random_number=random.randint(1,9999)
    random_number_str=str(random_number)
    random_number_str_2=(4-len(random_number_str))*'0'+random_number_str
    return (
        first_name[:3] + last_name[:3] + random_number_str_2
    )