from django.test import TestCase
from MechanicallyApp.models import User, Location, City
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient

class LocationTestCase(TestCase):
    def setUp(self):
        self.city=City.objects.create(name='Szczecin')
        self.admin=User.objects.create_user(first_name="Piotr", last_name="Testowy", username="piotes1111", email="testowy@gmail.com", password="test1234", role="admin", phone_number="987654321", is_new_account=False)
        self.standard=User.objects.create_user(first_name="Jan", last_name="Nowak", username="jannow1111", email="testowy2@gmail.com", password="test1234", role="standard", phone_number="987654322", is_new_account=False)
        self.manager=User.objects.create_user(first_name="Szymon", last_name="Chasowski", username="szycha1111", email="testowy3@gmail.com",password="test1234", role="manager", phone_number="987654323", is_new_account=False)
        self.branch=Location.objects.create(name='SIEDZIBA',phone_number='123456789',email="test@gmail.com", city=self.city,
            street_name='Parkowa',
            building_number=1, location_type='B')
        self.workshop=Location.objects.create(name='WARSZTAT', phone_number='133456789', email="test2@gmail.com", city=self.city,
            street_name='Parkowa',
            building_number=1, location_type='W')

    def test_standard_user_can_list_locations(self):
        client = APIClient()
        client.force_authenticate(self.standard)
        response = client.get(reverse('location-list'))
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(len(response.json()),2)

    def test_standard_user_cannot_retrieve_location(self):
        client = APIClient()
        client.force_authenticate(self.standard)
        response = client.get(reverse('location-detail', kwargs={'pk': self.branch.pk}))
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        locations = response.json()
        assert (locations['name'] == 'SIEDZIBA')

    def test_standard_user_cannot_create_location(self):
        user=User.objects.get(username="jannow1111")
        client=APIClient()
        client.force_authenticate(user)
        response=client.post(reverse('location-list'), {'name': 'SIEDZIBA 2', 'phone_number': 321432542, 'email':'test3@gmail.com','address':'Piaskowa 3 Sopot','location_type': 'B'})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_standard_user_cannot_update_location(self):
        user = User.objects.get(username="jannow1111")
        client = APIClient()
        client.force_authenticate(user)
        location = Location.objects.get(name='SIEDZIBA')
        response=client.patch(reverse('location-detail', kwargs={'pk': location.pk}), {'name': 'SIEDZIBA B'})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_standard_user_cannot_delete_location(self):
        user = User.objects.get(username="jannow1111")
        client = APIClient()
        client.force_authenticate(user)
        location = Location.objects.get(name='SIEDZIBA')
        response=client.delete(reverse('location-detail', kwargs={'pk': location.pk}))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_and_manager_users_can_list_locations(self):
        user = User.objects.get(username="piotes1111")
        client = APIClient()
        client.force_authenticate(user)
        response=client.get(reverse('location-list'))
        assert response.status_code==status.HTTP_200_OK
        locations=response.json()
        assert(len(locations)==2)
        self.assertTrue(all(location['name'] in ('SIEDZIBA','WARSZTAT') for location in locations))

        user2 = User.objects.get(username="szycha1111")
        client = APIClient()
        client.force_authenticate(user2)
        response = client.get(reverse('location-list'))
        assert response.status_code == status.HTTP_200_OK
        locations = response.json()
        assert (len(locations) == 2)
        self.assertTrue(all(location['name'] in ('SIEDZIBA', 'WARSZTAT') for location in locations))

    def test_admin_and_manager_users_can_retrieve_location(self):
        user = User.objects.get(username="piotes1111")
        client = APIClient()
        client.force_authenticate(user)
        location = Location.objects.get(name='SIEDZIBA')
        response = client.get(reverse('location-detail', kwargs={'pk': location.pk}))
        assert response.status_code == status.HTTP_200_OK
        locations = response.json()
        assert (locations['name'] == 'SIEDZIBA')

        user2 = User.objects.get(username="szycha1111")
        client = APIClient()
        client.force_authenticate(user2)
        location = Location.objects.get(name='SIEDZIBA')
        response = client.get(reverse('location-detail', kwargs={'pk': location.pk}))
        assert response.status_code == status.HTTP_200_OK
        locations = response.json()
        assert (locations['name'] == 'SIEDZIBA')

    def test_admin_user_can_create_location(self):
        user = User.objects.get(username="piotes1111")
        client = APIClient()
        client.force_authenticate(user)
        response = client.post(reverse('location-list'),
                               {'name': 'SIEDZIBA C', 'phone_number': 321432542, 'email': 'test3@gmail.com',
                                'city': str(self.city.pk),'street_name':'Parkowa','building_number':1, 'location_type': 'B'})
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)


    def test_admin_user_can_update_location(self):
        user = User.objects.get(username="piotes1111")
        client = APIClient()
        client.force_authenticate(user)
        location = Location.objects.get(name='SIEDZIBA')
        response = client.patch(reverse('location-detail', kwargs={'pk': location.pk}),
                                data={'name': 'SIEDZIBA B'})
        assert response.status_code == status.HTTP_200_OK
        response2 = client.get(reverse('location-detail', kwargs={'pk': location.pk}))
        assert response2.status_code == status.HTTP_200_OK
        locations = response2.json()
        assert (locations['name'] == 'SIEDZIBA B')

    def test_admin_user_can_delete_location(self):
        user = User.objects.get(username="piotes1111")
        client = APIClient()
        client.force_authenticate(user)
        location = Location.objects.get(name='SIEDZIBA')
        response = client.delete(reverse('location-detail', kwargs={'pk': location.pk}))
        assert response.status_code == status.HTTP_204_NO_CONTENT
        response2 = client.get(reverse('location-detail', kwargs={'pk': location.pk}))
        assert response2.status_code == status.HTTP_404_NOT_FOUND
