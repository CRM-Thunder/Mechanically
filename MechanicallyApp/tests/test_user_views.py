from django.test import TestCase
from MechanicallyApp.models import User, Location, UserLocationAssignment
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient


class UserTestCase(TestCase):
    def setUp(self):
        User.objects.create_superuser(first_name="Grzegorz", last_name="Kowalski", username="grzkow1111", email="testowy4@gmail.com", password="test1234", role="admin", phone_number="111111111")
        User.objects.create_user(first_name="Piotr", last_name="Testowy", username="piotes1111", email="testowy@gmail.com", password="test1234", role="admin", phone_number="222222222")
        standard1=User.objects.create_user(first_name="Jan", last_name="Nowak", username="jannow1111", email="testowy2@gmail.com", password="test1234", role="standard", phone_number="333333333")
        standard2=User.objects.create_user(first_name="Krzysztof", last_name="Pawlak", username="krzpaw1111", email="testowy22@gmail.com",password="test1234", role="standard", phone_number="444444444")
        User.objects.create_user(first_name="Kamil", last_name="Grosicki", username="kamgro1111", email="testowy23@gmail.com",password="test1234", role="standard", phone_number="555555555")
        User.objects.create_user(first_name="Szymon", last_name="Chasowski", username="szycha1111", email="testowy3@gmail.com",password="test1234", role="manager", phone_number="666666666")
        mechanic1=User.objects.create_user(first_name="Karol", last_name="Nawrak", username="karnaw1111", email="testowy26@gmail.com",password="test1234", role="mechanic", phone_number="777777777")
        mechanic2=User.objects.create_user(first_name="Jimmy", last_name="Mcgill", username="jimmcg1111",email="testowy27@gmail.com", password="test1234", role="mechanic", phone_number="888888888")
        User.objects.create_user(first_name="Lalo", last_name="Salamanca", username="lalsal1111",email="testowy28@gmail.com", password="test1234", role="mechanic",phone_number="999999999")
        branch=Location.objects.create(name='SIEDZIBA',phone_number='123456789',email="test@gmail.com",address="Testowa 1 Gdynia", location_type='B')
        workshop=Location.objects.create(name='WARSZTAT', phone_number='133456789', email="test2@gmail.com",address="Testowa 2 Gdynia", location_type='W')
        UserLocationAssignment.objects.create(user=standard1, location=branch)
        UserLocationAssignment.objects.create(user=standard2, location=branch)
        UserLocationAssignment.objects.create(user=mechanic1, location=workshop)
        UserLocationAssignment.objects.create(user=mechanic2, location=workshop)


    def test_standard_user_can_list_branch_coworkers_only(self):
        user=User.objects.get(username="jannow1111")
        client = APIClient()
        client.force_authenticate(user)
        response=client.get(reverse('user-list'))
        assert response.status_code==status.HTTP_200_OK
        users=response.json()
        assert len(users)==2
        self.assertTrue(all(user['first_name'] in ('Jan','Krzysztof') for user in users))

    def test_mechanic_can_list_branch_coworkers_only(self):
        user=User.objects.get(username="karnaw1111")
        client = APIClient()
        client.force_authenticate(user)
        response=client.get(reverse('user-list'))
        assert response.status_code==status.HTTP_200_OK
        users=response.json()
        assert len(users)==2
        self.assertTrue(all(user['first_name'] in ('Karol','Jimmy') for user in users))