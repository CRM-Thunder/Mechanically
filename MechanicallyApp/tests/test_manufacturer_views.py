from django.test import TestCase
from MechanicallyApp.models import User, Manufacturer
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient

class ManufacturerTestCase(TestCase):
    def setUp(self):
        User.objects.create_user(first_name="Piotr", last_name="Testowy", username="piotes1111", email="testowy@gmail.com", password="test1234", role="admin", phone_number="987654321", is_new_account=False)
        User.objects.create_user(first_name="Jan", last_name="Nowak", username="jannow1111", email="testowy2@gmail.com", password="test1234", role="standard", phone_number="987654322", is_new_account=False)
        Manufacturer.objects.create(name='DODGE')
        Manufacturer.objects.create(name='JAGUAR')
        Manufacturer.objects.create(name='HYUNDAI')

    def test_standard_user_can_list_manufacturers(self):
        user=User.objects.get(username="jannow1111")
        client=APIClient()
        client.force_authenticate(user)
        response=client.get(reverse('manufacturer-list'))
        assert response.status_code == status.HTTP_200_OK
        manufacturers=response.json()
        assert(len(manufacturers)==3)
        self.assertTrue(all(manufacturer['name'] in ('DODGE','JAGUAR','HYUNDAI') for manufacturer in manufacturers))

    def test_standard_user_can_retrieve_manufacturer(self):
        user=User.objects.get(username="jannow1111")
        client=APIClient()
        client.force_authenticate(user)
        manufacturer=Manufacturer.objects.get(name='DODGE')
        response=client.get(reverse('manufacturer-detail', kwargs={'pk': manufacturer.pk}))
        assert response.status_code == status.HTTP_200_OK
        manufacturers=response.json()
        assert(manufacturers['name']=='DODGE')

    def test_standard_user_cannot_create_manufacturer(self):
        user=User.objects.get(username="jannow1111")
        client=APIClient()
        client.force_authenticate(user)
        response=client.post(reverse('manufacturer-list'), {'name': 'FORD'})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_standard_user_cannot_update_manufacturer(self):
        user=User.objects.get(username="jannow1111")
        client=APIClient()
        client.force_authenticate(user)
        manufacturer=Manufacturer.objects.get(name='DODGE')
        response=client.put(reverse('manufacturer-detail', kwargs={'pk': manufacturer.pk}), {'name': 'FORD'})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_standard_user_cannot_delete_manufacturer(self):
        user=User.objects.get(username="jannow1111")
        client=APIClient()
        client.force_authenticate(user)
        manufacturer=Manufacturer.objects.get(name='DODGE')
        response=client.delete(reverse('manufacturer-detail', kwargs={'pk': manufacturer.pk}))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_user_can_create_manufacturer(self):
        user=User.objects.get(username="piotes1111")
        client=APIClient()
        client.force_authenticate(user)
        response=client.post(reverse('manufacturer-list'), {'name': 'FORD'})
        assert response.status_code == status.HTTP_201_CREATED

    def test_admin_user_can_update_manufacturer(self):
        user=User.objects.get(username="piotes1111")
        client=APIClient()
        client.force_authenticate(user)
        manufacturer=Manufacturer.objects.get(name='DODGE')
        response=client.put(reverse('manufacturer-detail', kwargs={'pk': manufacturer.pk}), {'name': 'FORD'})
        assert response.status_code == status.HTTP_200_OK
        response2=client.get(reverse('manufacturer-detail', kwargs={'pk': manufacturer.pk}))
        assert response2.status_code == status.HTTP_200_OK
        manufacturers=response2.json()
        assert(manufacturers['name']=='FORD')

    def test_admin_user_can_delete_manufacturer(self):
        user=User.objects.get(username="piotes1111")
        client=APIClient()
        client.force_authenticate(user)
        manufacturer=Manufacturer.objects.get(name='DODGE')
        response=client.delete(reverse('manufacturer-detail', kwargs={'pk': manufacturer.pk}))
        assert response.status_code == status.HTTP_204_NO_CONTENT
        response2=client.get(reverse('manufacturer-detail', kwargs={'pk': manufacturer.pk}))
        assert response2.status_code == status.HTTP_404_NOT_FOUND