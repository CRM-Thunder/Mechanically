from django.test import TestCase
from MechanicallyApp.models import User, Manufacturer, Vehicle, Location, UserLocationAssignment, FailureReport, \
    RepairReport, City
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient

class VehicleTestCase(TestCase):
    def setUp(self):
        self.city=City.objects.create(name='Szczecin')
        self.admin=User.objects.create_user(first_name="Piotr", last_name="Testowy", username="piotes1111", email="testowy@gmail.com", password="test1234", role="admin", phone_number="987654321", is_new_account=False)
        self.standard=User.objects.create_user(first_name="Jan", last_name="Nowak", username="jannow1111", email="testowy2@gmail.com", password="test1234", role="standard", phone_number="987654322", is_new_account=False)
        self.mechanic = User.objects.create_user(first_name="Test", last_name="Testow", username="testes1111",
                                                 email="testowy2131232@gmail.com", password="test1234", role="mechanic",
                                                 phone_number="917614312", is_new_account=False)
        self.manager=User.objects.create_user(first_name="Szymon", last_name="Chasowski", username="szycha1111",
                                 email="testowy3@gmail.com", password="test1234", role="manager",
                                 phone_number="987654323", is_new_account=False)
        self.dodge=Manufacturer.objects.create(name='DODGE')
        self.man=Manufacturer.objects.create(name='MAN')
        self.branch=Location.objects.create(name='SIEDZIBA', phone_number='123456789', email="test@gmail.com",
                                            city=self.city,
                                            street_name='Parkowa',
                                            building_number=1, location_type='B')

        self.branch2 = Location.objects.create(name='SIEDZIBA B', phone_number='163456789', email="test3@gmail.com",
                                               city=self.city,
                                               street_name='Parkowa',
                                               building_number=1, location_type='B')
        self.workshop=Location.objects.create(name='WARSZTAT', phone_number='133456789', email="test2@gmail.com",
                                              city=self.city,
                                              street_name='Parkowa',
                                              building_number=1, location_type='W')
        self.workshop2 = Location.objects.create(name='WARSZTAT B', phone_number='133456719', email="test643@gmail.com",
                                                 city=self.city,
                                                 street_name='Parkowa',
                                                 building_number=1, location_type='W')
        self.vehicle1=Vehicle.objects.create(vin='5GZCZ63B93S896664',vehicle_type='PC',year=2018,vehicle_model="SRT Hellcat",fuel_type='P',availability='A',location=self.branch, manufacturer=self.dodge)
        self.vehicle2 = Vehicle.objects.create(vin='5GZCZ63B93S896564', vehicle_type='CO', year=2019,
                                          vehicle_model="Lion City", fuel_type='D', availability='A', location=self.branch2,
                                          manufacturer=self.man)
        self.vehicle3 = Vehicle.objects.create(vin='5GZCZ63B94S896564',  vehicle_type='TR', year=2016,
                                          vehicle_model="TGX Euro 6", fuel_type='D', availability='A',
                                          manufacturer=self.man)

        self.vehicle4 = Vehicle.objects.create(
            vin='5GZCZ63B94S891564',
            vehicle_type='TR',
            year=2020,
            vehicle_model="TGX Euro 61",
            fuel_type='D',
            availability='A',
            location=self.branch,
            manufacturer=self.man
        )

        self.vehicle5 = Vehicle.objects.create(
            vin='1GZCZ63B94S891564',
            vehicle_type='TR',
            year=2021,
            vehicle_model="TGX Euro 62",
            fuel_type='D',
            availability='U',
            location=self.branch2,
            manufacturer=self.man
        )
        self.vehicle6 = Vehicle.objects.create(
            vin='3GZCZ63B94S891564',
            vehicle_type='TR',
            year=2025,
            vehicle_model="TGX Euro 63",
            fuel_type='D',
            availability='U',
            location=self.branch2,
            manufacturer=self.man
        )
        self.failure_report1 = FailureReport.objects.create(
            vehicle=self.vehicle4,
            title="Engine failure",
            description="Engine is not starting properly",
            report_author=self.standard,
            status='P'  # PENDING
        )
        self.failure_report2 = FailureReport.objects.create(
            vehicle=self.vehicle5,
            title="Engine failure",
            description="Engine is not starting properly",
            report_author=None,
            workshop=self.workshop,
            status='A'  # ASSIGNED
        )
        self.failure_report3 = FailureReport.objects.create(
            vehicle=self.vehicle6,
            title="Engine failure",
            description="Engine is not starting properly",
            report_author=None,
            workshop=self.workshop2,
            status='A'  # ASSIGNED
        )
        self.repair_report1 = RepairReport.objects.create(
            failure_report=self.failure_report2,
            condition_analysis="Initial analysis",
            repair_action="Pending repair",
            cost=100.00,
            status='A'  # ACTIVE
        )
        self.repair_report1 = RepairReport.objects.create(
            failure_report=self.failure_report3,
            condition_analysis="Initial analysis",
            repair_action="Pending repair",
            cost=200.00,
            status='A'  # ACTIVE
        )
        UserLocationAssignment.objects.create(user=self.standard, location=self.branch)
        UserLocationAssignment.objects.create(user=self.mechanic, location=self.workshop)


    def test_standard_user_can_list_his_branch_vehicles(self):
        user=User.objects.get(username="jannow1111")
        client=APIClient()
        client.force_authenticate(user)
        response=client.get(reverse('vehicle-list'))
        assert response.status_code == status.HTTP_200_OK
        vehicles=response.json()
        assert(len(vehicles)==2)

    def test_mechanic_can_list_vehicles_which_have_failure_reports_related_to_his_workshop(self):
        client=APIClient()
        client.force_authenticate(self.mechanic)
        response=client.get(reverse('vehicle-list'))
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(len(response.json()),1)

    def test_mechanic_can_retrieve_vehicle_which_has_failure_reports_related_to_his_workshop(self):
        client=APIClient()
        client.force_authenticate(self.mechanic)
        response=client.get(reverse('vehicle-detail',kwargs={'pk':self.vehicle5.pk}))
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.json()['id'],str(self.vehicle5.pk))

    def test_mechanic_cannot_retrieve_vehicle_which_has_failure_reports_related_only_to_other_workshops(self):
        client=APIClient()
        client.force_authenticate(self.mechanic)
        response=client.get(reverse('vehicle-detail',kwargs={'pk':self.vehicle6.pk}))
        self.assertEqual(response.status_code,status.HTTP_404_NOT_FOUND)
        self.assertIn('No Vehicle matches the given query.',str(response.json()))


    def test_admin_and_manager_can_list_vehicles(self):
        admin=User.objects.get(username="piotes1111")
        client=APIClient()
        client.force_authenticate(admin)
        response = client.get(reverse('vehicle-list'))
        assert response.status_code == status.HTTP_200_OK
        vehicles = response.json()
        assert len(vehicles)==6

        manager=User.objects.get(username="szycha1111")
        client = APIClient()
        client.force_authenticate(manager)
        response = client.get(reverse('vehicle-list'))
        assert response.status_code == status.HTTP_200_OK
        vehicles = response.json()
        assert len(vehicles) == 6

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
        client = APIClient()
        client.force_authenticate(self.standard)
        response=client.get(reverse('vehicle-detail',kwargs={'pk':self.vehicle2.pk}))
        self.assertEqual(response.status_code,status.HTTP_404_NOT_FOUND)
        self.assertIn('No Vehicle matches the given query.',str(response.json()))

    def test_standard_cannot_retrieve_non_existent_vehicle(self):
        client = APIClient()
        client.force_authenticate(self.standard)
        response=client.get(reverse('vehicle-detail',kwargs={'pk':'b54d7467-2eaa-4e1b-8be2-3fb091d7639e'}))
        self.assertEqual(response.status_code,status.HTTP_404_NOT_FOUND)
        self.assertIn('No Vehicle matches the given query.',str(response.json()))

    def test_standard_cannot_enumerate_other_branch_vehicles(self):
        client = APIClient()
        client.force_authenticate(self.standard)
        response=client.get(reverse('vehicle-detail',kwargs={'pk':self.vehicle2.pk}))
        response2 = client.get(reverse('vehicle-detail', kwargs={'pk': 'b54d7467-2eaa-4e1b-8be2-3fb091d7639e'}))
        self.assertEqual(response.status_code,status.HTTP_404_NOT_FOUND)
        self.assertEqual(response2.status_code, response.status_code)
        self.assertIn('No Vehicle matches the given query.', str(response.json()))
        self.assertIn(str(response.json()), str(response2.json()))

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
            "vehicle_type": "TR",
            "year": 2016,
            "vehicle_model": "TGX Euro 7",
            "fuel_type": "D",
            "availability": "A",
            "manufacturer": str(man1.id)})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_vehicle_cannot_be_created_with_non_existent_manufacturer(self):
        user=User.objects.get(username="piotes1111")
        client=APIClient()
        client.force_authenticate(user)
        response = client.post(reverse('vehicle-list'), data={
            "vin": "5GZCZ63B94S896964",
            "vehicle_type": "TR",
            "year": 2016,
            "vehicle_model": "TGX Euro 7",
            "fuel_type": "D",
            "availability": "A",
            "manufacturer": 'b54d7467-2eaa-4e1b-8be2-3fb091d7639e'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

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

    def test_unavailable_vehicle_with_pending_failure_report_cannot_be_updated_as_available(self):
        admin = User.objects.get(username="piotes1111")
        client = APIClient()
        client.force_authenticate(admin)
        response = client.patch(reverse('vehicle-detail', kwargs={'pk': self.vehicle4.pk}), {'availability': 'A'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        self.assertIn('Vehicle has been reported as failure. It cannot be set as available.',response.json())

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