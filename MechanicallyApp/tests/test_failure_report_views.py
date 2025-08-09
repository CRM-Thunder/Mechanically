from django.test import TestCase
from MechanicallyApp.models import User, Manufacturer, Vehicle, Location, UserLocationAssignment, FailureReport, \
    RepairReport
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient


class FailureReportTestCase(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            first_name="Grzegorz", last_name="Kowalski",
            username="grzkow1111", email="testowy76@gmail.com",
            password="test1234", role="admin", phone_number="111111111")
        # Create users with different roles
        self.admin = User.objects.create_user(
            first_name="Piotr",
            last_name="Testowy",
            username="piotes1111",
            email="testowy@gmail.com",
            password="test1234",
            role="admin",
            phone_number="987654321"
        )

        self.standard = User.objects.create_user(
            first_name="Jan",
            last_name="Nowak",
            username="jannow1111",
            email="testowy2@gmail.com",
            password="test1234",
            role="standard",
            phone_number="987654322"
        )
        self.standard2 = User.objects.create_user(first_name="Krzysztof", last_name="Pawlak", username="krzpaw1111",
                                                  email="testowy22@gmail.com", password="test1234", role="standard",
                                                  phone_number="444444444")

        self.manager = User.objects.create_user(
            first_name="Szymon",
            last_name="Chasowski",
            username="szycha1111",
            email="testowy3@gmail.com",
            password="test1234",
            role="manager",
            phone_number="987654323"
        )

        self.mechanic = User.objects.create_user(
            first_name="Karol",
            last_name="Nawrak",
            username="karnaw1111",
            email="testowy4@gmail.com",
            password="test1234",
            role="mechanic",
            phone_number="987654324"
        )

        # Create manufacturers
        self.dodge = Manufacturer.objects.create(name='DODGE')
        self.man = Manufacturer.objects.create(name='MAN')

        # Create locations
        self.branch = Location.objects.create(
            name='SIEDZIBA',
            phone_number='123456789',
            email="test@gmail.com",
            address="Testowa 1 Gdynia",
            location_type='B'
        )

        self.branch2 = Location.objects.create(
            name='SIEDZIBA B',
            phone_number='163456789',
            email="test3@gmail.com",
            address="Portowa 3 Szczecin",
            location_type='B'
        )

        self.workshop = Location.objects.create(
            name='WARSZTAT',
            phone_number='133456789',
            email="test2@gmail.com",
            address="Testowa 2 Gdynia",
            location_type='W'
        )

        # Create vehicles
        self.vehicle1 = Vehicle.objects.create(
            vin='5GZCZ63B93S896664',
            kilometers=400,
            vehicle_type='PC',
            year=2018,
            vehicle_model="SRT Hellcat",
            fuel_type='P',
            availability='A',
            location=self.branch,
            manufacturer=self.dodge
        )

        self.vehicle2 = Vehicle.objects.create(
            vin='5GZCZ63B93S896564',
            kilometers=500,
            vehicle_type='CO',
            year=2019,
            vehicle_model="Lion City",
            fuel_type='D',
            availability='A',
            location=self.branch,
            manufacturer=self.man
        )

        self.vehicle3 = Vehicle.objects.create(
            vin='5GZCZ63B94S896564',
            kilometers=52400,
            vehicle_type='TR',
            year=2016,
            vehicle_model="TGX Euro 6",
            fuel_type='D',
            availability='A',
            location=self.branch,
            manufacturer=self.man
        )

        self.vehicle4 = Vehicle.objects.create(
            vin='5GZCZ63B94S891564',
            kilometers=82400,
            vehicle_type='TR',
            year=2020,
            vehicle_model="TGX Euro 61",
            fuel_type='D',
            availability='A',
            location=self.branch2,
            manufacturer=self.man
        )
        self.vehicle5 = Vehicle.objects.create(
            vin='5GZCZ63B93S896594',
            kilometers=5070,
            vehicle_type='CO',
            year=2020,
            vehicle_model="Lion Gate",
            fuel_type='D',
            availability='U',
            location=self.branch,
            manufacturer=self.man
        )

        # Assign users to locations
        UserLocationAssignment.objects.create(user=self.standard, location=self.branch)
        UserLocationAssignment.objects.create(user=self.mechanic, location=self.workshop)

        # Create failure reports
        self.failure_report1 = FailureReport.objects.create(
            vehicle=self.vehicle1,
            title="Engine failure",
            description="Engine is not starting properly",
            report_author=self.standard,
            status='P'  # PENDING
        )

        self.failure_report2 = FailureReport.objects.create(
            vehicle=self.vehicle3,
            title="Brake issue",
            description="Brakes are making noise",
            report_author=self.standard,
            status='A'  # ASSIGNED
        )

        self.failure_report3 = FailureReport.objects.create(
            vehicle=self.vehicle3,
            title="Assigned issue",
            description="This issue is already assigned",
            report_author=self.standard,
            workshop=self.workshop,
            status='R' # RESOLVED
        )

        # Create repair report for the assigned failure
        self.repair_report1 = RepairReport.objects.create(
            failure_report=self.failure_report2,
            condition_analysis="Initial analysis",
            repair_action="Pending repair",
            cost=100.00,
            status='A'  # ACTIVE
        )
        self.repair_report2 = RepairReport.objects.create(
            failure_report=self.failure_report3,
            condition_analysis="Historical analysis",
            repair_action="Historical repair",
            cost=1200.00,
            status='H'  # HISTORIC
        )

    def test_standard_user_can_create_failure_report(self):
        client = APIClient()
        client.force_authenticate(self.standard)
        response = client.post(reverse('failure-report-list'), data={
            "vehicle": self.vehicle2.pk,
            "description": "Test failure description"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Check that vehicle availability was updated to Unavailable
        vehicle = Vehicle.objects.get(id=self.vehicle2.id)
        self.assertEqual(vehicle.availability, 'U')

    def test_failure_report_cannot_be_created_for_non_existing_vehicle(self):
        client = APIClient()
        client.force_authenticate(self.standard)
        response = client.post(reverse('failure-report-list'), data={
            "vehicle": 'b54d7467-2eaa-4e1b-8be2-3fb091d7639e',
            "description": "Test failure description"
        })
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('There is no vehicle with provided ID assigned to your branch.',str(response.json()))

    def test_standard_user_can_create_failure_report_for_unavailable_vehicle_but_without_current_failure_report(self):
        client = APIClient()
        client.force_authenticate(self.standard)
        response = client.post(reverse('failure-report-list'), data={
            "vehicle": self.vehicle5.pk,
            "description": "Test failure description"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Check that vehicle availability was updated to Unavailable
        vehicle = Vehicle.objects.get(id=self.vehicle5.id)
        self.assertEqual(vehicle.availability, 'U')


    def test_unassigned_standard_cannot_create_failure_report(self):
        client = APIClient()
        client.force_authenticate(self.standard2)
        response = client.post(reverse('failure-report-list'), data={
            "vehicle": self.vehicle2.pk,
            "description": "Test failure description"
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_standard_user_cannot_create_failure_report(self):
        client = APIClient()
        client.force_authenticate(self.mechanic)
        response = client.post(reverse('failure-report-list'), data={
            "vehicle": self.vehicle2.pk,
            "description": "Test failure description"
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


        client = APIClient()
        client.force_authenticate(self.manager)
        response = client.post(reverse('failure-report-list'), data={
            "vehicle": self.vehicle2.pk,
            "description": "Test failure description"
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        client = APIClient()
        client.force_authenticate(self.admin)
        response = client.post(reverse('failure-report-list'), data={
            "vehicle": self.vehicle2.pk,
            "description": "Test failure description"
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        client = APIClient()
        client.force_authenticate(self.superuser)
        response = client.post(reverse('failure-report-list'), data={
            "vehicle": self.vehicle2.pk,
            "description": "Test failure description"
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_standard_user_cannot_create_failure_report_for_other_branch_vehicle(self):
        client = APIClient()
        client.force_authenticate(self.standard)

        response = client.post(reverse('failure-report-list'), data={
            "vehicle":self.vehicle4.pk,  # Vehicle from branch2
            "description": "Test failure description"
        })
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('There is no vehicle with provided ID assigned to your branch.',str(response.json()))

    def test_standard_user_cannot_create_failure_report_for_already_reported_vehicle(self):
        client = APIClient()
        client.force_authenticate(self.standard)

        response = client.post(reverse('failure-report-list'), data={
            "vehicle": self.vehicle1.pk,
            "description": "Test failure description"
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Vehicle is already reported as failure.', str(response.json()))

        response = client.post(reverse('failure-report-list'), data={
            "vehicle": self.vehicle3.pk,
            "description": "Test failure description"
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Vehicle is already reported as failure.', str(response.json()))

    def test_standard_user_cannot_list_failure_reports(self):
        client = APIClient()
        client.force_authenticate(self.standard)

        response = client.get(reverse('failure-report-list'))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_mechanic_cannot_list_failure_reports(self):
        client = APIClient()
        client.force_authenticate(self.mechanic)

        response = client.get(reverse('failure-report-list'))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_can_list_failure_reports(self):
        client = APIClient()
        client.force_authenticate(self.manager)

        response = client.get(reverse('failure-report-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        failure_reports = response.json()
        self.assertEqual(len(failure_reports), 3)

    def test_admin_can_list_failure_reports(self):
        client = APIClient()
        client.force_authenticate(self.admin)

        response = client.get(reverse('failure-report-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        failure_reports = response.json()
        self.assertEqual(len(failure_reports), 3)

    def test_manager_can_retrieve_failure_report(self):
        client = APIClient()
        client.force_authenticate(self.manager)

        response = client.get(reverse('failure-report-detail', kwargs={'pk': str(self.failure_report1.id)}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        failure_report = response.json()
        self.assertEqual(failure_report['id'], str(self.failure_report1.id))
        self.assertEqual(failure_report['title'], self.failure_report1.title)

    def test_admin_can_retrieve_failure_report(self):
        client = APIClient()
        client.force_authenticate(self.admin)

        response = client.get(reverse('failure-report-detail', kwargs={'pk': str(self.failure_report1.id)}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        failure_report = response.json()
        self.assertEqual(failure_report['id'], str(self.failure_report1.id))
        self.assertEqual(failure_report['title'], self.failure_report1.title)

    def test_standard_user_cannot_retrieve_failure_report(self):
        client = APIClient()
        client.force_authenticate(self.standard)

        response = client.get(reverse('failure-report-detail', kwargs={'pk': str(self.failure_report1.id)}))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_mechanic_cannot_retrieve_failure_report(self):
        client = APIClient()
        client.force_authenticate(self.mechanic)

        response = client.get(reverse('failure-report-detail', kwargs={'pk': str(self.failure_report1.id)}))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#nie działa
    def test_manager_can_assign_failure_report(self):
        client = APIClient()
        client.force_authenticate(self.manager)
        response = client.post(reverse('failure-report-assign'), data={
            "failure_report": self.failure_report1.pk,
            "workshop": self.workshop.pk
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        failure_report = FailureReport.objects.get(id=self.failure_report1.id)
        self.assertEqual(failure_report.status, 'A')  # ASSIGNED
        self.assertEqual(failure_report.workshop, self.workshop)
        self.assertTrue(RepairReport.objects.filter(failure_report=failure_report).exists())

    def test_standard_user_cannot_assign_failure_report(self):
        client = APIClient()
        client.force_authenticate(self.standard)

        response = client.post(reverse('failure-report-assign'), data={
            "failure_report": str(self.failure_report1.id),
            "workshop": str(self.workshop.id)
        })

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#nie działa
    def test_manager_can_dismiss_failure_report(self):
        client = APIClient()
        client.force_authenticate(self.manager)
        response = client.post(reverse('failure-report-dismiss'), data={
            "failure_report": self.failure_report1.pk
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that failure report was updated
        failure_report = FailureReport.objects.get(id=self.failure_report1.id)
        self.assertEqual(failure_report.status, 'D')  # DISMISSED

    def test_standard_user_cannot_dismiss_failure_report(self):
        client = APIClient()
        client.force_authenticate(self.standard)

        response = client.post(reverse('failure-report-dismiss'), data={
            "failure_report": str(self.failure_report1.id)
        })

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_can_reassign_failure_report(self):
        # Create another workshop
        workshop2 = Location.objects.create(
            name='WARSZTAT 2',
            phone_number='143456789',
            email="test4@gmail.com",
            address="Testowa 3 Gdynia",
            location_type='W'
        )

        client = APIClient()
        client.force_authenticate(self.manager)

        response = client.post(reverse('failure-report-reassign'), data={
            "failure_report": str(self.failure_report2.id),
            "workshop": str(workshop2.id)
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that failure report was updated
        failure_report = FailureReport.objects.get(id=self.failure_report2.id)
        self.assertEqual(failure_report.status, 'A')  # ASSIGNED
        self.assertEqual(failure_report.workshop, workshop2)

    def test_standard_user_cannot_reassign_failure_report(self):
        # Create another workshop
        workshop2 = Location.objects.create(
            name='WARSZTAT 2',
            phone_number='143456789',
            email="test4@gmail.com",
            address="Testowa 3 Gdynia",
            location_type='W'
        )

        client = APIClient()
        client.force_authenticate(self.standard)

        response = client.post(reverse('failure-report-reassign'), data={
            "failure_report": str(self.failure_report2.id),
            "workshop": str(workshop2.id)
        })

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
