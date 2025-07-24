from django.test import TestCase
from MechanicallyApp.models import User, Manufacturer, Vehicle, Location, UserLocationAssignment
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient

class VehicleTestCase(TestCase):
    def setUp(self):
        admin=User.objects.create_user(first_name="Piotr", last_name="Testowy", username="piotes1111", email="testowy@gmail.com", password="test1234", role="admin", phone_number="987654321")
        standard=User.objects.create_user(first_name="Jan", last_name="Nowak", username="jannow1111", email="testowy2@gmail.com", password="test1234", role="standard", phone_number="987654322")
        manager=User.objects.create_user(first_name="Szymon", last_name="Chasowski", username="szycha1111",
                                 email="testowy3@gmail.com", password="test1234", role="manager",
                                 phone_number="987654323")
        dodge=Manufacturer.objects.create(name='DODGE')
        man=Manufacturer.objects.create(name='MAN')
        branch=Location.objects.create(name='SIEDZIBA', phone_number='123456789', email="test@gmail.com",
                                address="Testowa 1 Gdynia", location_type='B')

        branch2 = Location.objects.create(name='SIEDZIBA B', phone_number='163456789', email="test3@gmail.com",
                                         address="Portowa 3 Szczecin", location_type='B')
        Location.objects.create(name='WARSZTAT', phone_number='133456789', email="test2@gmail.com",
                                address="Testowa 2 Gdynia", location_type='W')
        vehicle1=Vehicle.objects.create(vin='5GZCZ63B93S896664',kilometers=400,vehicle_type='PC',year=2018,vehicle_model="SRT Hellcat",fuel_type='P',availability='A',location=branch, manufacturer=dodge)
        vehicle2 = Vehicle.objects.create(vin='5GZCZ63B93S896564', kilometers=500, vehicle_type='CO', year=2019,
                                          vehicle_model="Lion City", fuel_type='D', availability='A', location=branch2,
                                          manufacturer=man)
        vehicle3 = Vehicle.objects.create(vin='5GZCZ63B94S896564', kilometers=52400, vehicle_type='TR', year=2016,
                                          vehicle_model="TGX Euro 6", fuel_type='D', availability='A',
                                          manufacturer=man)
        UserLocationAssignment.objects.create(user=standard, location=branch)


    def test_standard_user_can_list_his_branch_vehicles(self):
        user=User.objects.get(username="jannow1111")
        client=APIClient()
        client.force_authenticate(user)
        response=client.get(reverse('vehicle-list'))
        assert response.status_code == status.HTTP_200_OK
        vehicles=response.json()
        vehicle1=Vehicle.objects.get(vin='5GZCZ63B93S896664')
        assert(len(vehicles)==1) and str(vehicle1.id)==vehicles[0]['id']

    def test_admin_and_manager_can_list_vehicles(self):
        admin=User.objects.get(username="piotes1111")
        client=APIClient()
        client.force_authenticate(admin)
        response = client.get(reverse('vehicle-list'))
        assert response.status_code == status.HTTP_200_OK
        vehicles = response.json()
        assert len(vehicles)==3

        manager=User.objects.get(username="szycha1111")
        client = APIClient()
        client.force_authenticate(manager)
        response = client.get(reverse('vehicle-list'))
        assert response.status_code == status.HTTP_200_OK
        vehicles = response.json()
        assert len(vehicles) == 3

    def test_standard_can_retrieve_his_branch_vehicle(self):
        user = User.objects.get(username="jannow1111")
        client = APIClient()
        client.force_authenticate(user)
        vehicle1 = Vehicle.objects.get(vin='5GZCZ63B93S896664')
        response=client.get(reverse('vehicle-detail',kwargs={'pk':str(vehicle1.id)}))
        assert response.status_code==status.HTTP_200_OK
        vehicles=response.json()
        assert vehicles['id']==str(vehicle1.id)

    def test_standard_cannot_retrieve_other_branch_vehicle(self):
        user = User.objects.get(username="jannow1111")
        client = APIClient()
        client.force_authenticate(user)
        vehicle1 = Vehicle.objects.get(vin='5GZCZ63B93S896564')
        response=client.get(reverse('vehicle-detail',kwargs={'pk':str(vehicle1.id)}))
        assert response.status_code==status.HTTP_404_NOT_FOUND

    def test_admin_and_manager_can_retrieve_vehicle(self):
        admin = User.objects.get(username="piotes1111")
        client = APIClient()
        client.force_authenticate(admin)
        vehicle1 = Vehicle.objects.get(vin='5GZCZ63B93S896564')
        response = client.get(reverse('vehicle-detail', kwargs={'pk': str(vehicle1.id)}))
        assert response.status_code == status.HTTP_200_OK
        retrieved_vehicle1=response.json()
        assert retrieved_vehicle1['id']==str(vehicle1.id)

        manager = User.objects.get(username="szycha1111")
        client = APIClient()
        client.force_authenticate(manager)
        vehicle2 = Vehicle.objects.get(vin='5GZCZ63B94S896564')
        response = client.get(reverse('vehicle-detail', kwargs={'pk': str(vehicle2.id)}))
        assert response.status_code == status.HTTP_200_OK
        retrieved_vehicle2 = response.json()
        assert retrieved_vehicle2['id'] == str(vehicle2.id)

    def test_admin_and_manager_can_create_vehicle(self):
        admin = User.objects.get(username="piotes1111")
        client = APIClient()
        client.force_authenticate(admin)
        man1=Manufacturer.objects.get(name='MAN')
        response = client.post(reverse('vehicle-list'),data={
          "vin": "5GZCZ63B94S896964",
          "kilometers": 13,
          "vehicle_type": "TR",
          "year": 2016,
          "vehicle_model": "TGX Euro 7",
          "fuel_type": "D",
          "availability": "A",
          "manufacturer": str(man1.id)})
        assert response.status_code==status.HTTP_201_CREATED

        manager = User.objects.get(username="szycha1111")
        client = APIClient()
        client.force_authenticate(manager)
        man1 = Manufacturer.objects.get(name='MAN')
        response = client.post(reverse('vehicle-list'), data={
            "vin": "4GZCZ63B94S896964",
            "kilometers": 14,
            "vehicle_type": "TR",
            "year": 2016,
            "vehicle_model": "TGX Euro 8",
            "fuel_type": "D",
            "availability": "A",
            "manufacturer": str(man1.id)})
        assert response.status_code == status.HTTP_201_CREATED

    def test_standard_user_cannot_create_vehicle(self):
        user=User.objects.get(username="jannow1111")
        client=APIClient()
        client.force_authenticate(user)
        man1 = Manufacturer.objects.get(name='MAN')
        response = client.post(reverse('vehicle-list'), data={
            "vin": "5GZCZ63B94S896964",
            "kilometers": 13,
            "vehicle_type": "TR",
            "year": 2016,
            "vehicle_model": "TGX Euro 7",
            "fuel_type": "D",
            "availability": "A",
            "manufacturer": str(man1.id)})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_standard_user_cannot_update_vehicle(self):
        user=User.objects.get(username="jannow1111")
        client=APIClient()
        client.force_authenticate(user)
        vehicle=Vehicle.objects.get(vin='5GZCZ63B93S896664')
        response=client.patch(reverse('vehicle-detail', kwargs={'pk': str(vehicle.id)}), {'vehicle_model': 'Panda'})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_standard_user_cannot_delete_vehicle(self):
        user=User.objects.get(username="jannow1111")
        client=APIClient()
        client.force_authenticate(user)
        vehicle=Vehicle.objects.get(vin='5GZCZ63B93S896664')
        response=client.delete(reverse('vehicle-detail', kwargs={'pk': str(vehicle.id)}))
        assert response.status_code == status.HTTP_403_FORBIDDEN



    def test_admin_and_manager_can_update_vehicle(self):
        admin=User.objects.get(username="piotes1111")
        client=APIClient()
        client.force_authenticate(admin)
        vehicle=Vehicle.objects.get(vin='5GZCZ63B93S896664')
        response=client.patch(reverse('vehicle-detail', kwargs={'pk': str(vehicle.id)}), {'vehicle_model': 'Panda 1'})
        assert response.status_code == status.HTTP_200_OK
        response2=client.get(reverse('vehicle-detail', kwargs={'pk': str(vehicle.id)}))
        assert response2.status_code == status.HTTP_200_OK
        vehicle_r=response2.json()
        assert(vehicle_r['vehicle_model']=='Panda 1')

        manager = User.objects.get(username="szycha1111")
        client = APIClient()
        client.force_authenticate(manager)
        response = client.patch(reverse('vehicle-detail', kwargs={'pk': str(vehicle.id)}), {'vehicle_model': 'Panda 2'})
        assert response.status_code == status.HTTP_200_OK
        response2 = client.get(reverse('vehicle-detail', kwargs={'pk': str(vehicle.id)}))
        assert response2.status_code == status.HTTP_200_OK
        vehicle_r = response2.json()
        assert (vehicle_r['vehicle_model'] == 'Panda 2')

    def test_admin_and_manager_can_delete_vehicle(self):
        admin=User.objects.get(username="piotes1111")
        client=APIClient()
        client.force_authenticate(admin)
        vehicle1=Vehicle.objects.get(vin='5GZCZ63B93S896664')
        response=client.delete(reverse('vehicle-detail', kwargs={'pk': vehicle1.pk}))
        assert response.status_code == status.HTTP_204_NO_CONTENT
        response2=client.get(reverse('vehicle-detail', kwargs={'pk': vehicle1.pk}))
        assert response2.status_code == status.HTTP_404_NOT_FOUND

        manager = User.objects.get(username="szycha1111")
        client = APIClient()
        client.force_authenticate(manager)
        vehicle2 = Vehicle.objects.get(vin='5GZCZ63B93S896564')
        response = client.delete(reverse('vehicle-detail', kwargs={'pk': vehicle2.pk}))
        assert response.status_code == status.HTTP_204_NO_CONTENT
        response2 = client.get(reverse('vehicle-detail', kwargs={'pk': vehicle2.pk}))
        assert response2.status_code == status.HTTP_404_NOT_FOUND