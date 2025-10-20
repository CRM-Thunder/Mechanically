from django.test import TestCase
from MechanicallyApp.models import User, Manufacturer, Vehicle, Location, UserLocationAssignment, FailureReport, \
    RepairReport, City
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient


class FailureReportTestCase(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            first_name="Grzegorz", last_name="Kowalski",
            username="grzkow1111", email="testowy76@gmail.com",
            password="test1234", role="admin", phone_number="111111111", is_new_account=False)
        # Create users with different roles
        self.admin = User.objects.create_user(
            first_name="Piotr",
            last_name="Testowy",
            username="piotes1111",
            email="testowy@gmail.com",
            password="test1234",
            role="admin",
            phone_number="987654321", is_new_account=False
        )

        self.standard = User.objects.create_user(
            first_name="Jan",
            last_name="Nowak",
            username="jannow1111",
            email="testowy2@gmail.com",
            password="test1234",
            role="standard",
            phone_number="987654322", is_new_account=False
        )
        self.standard2 = User.objects.create_user(first_name="Krzysztof", last_name="Pawlak", username="krzpaw1111",
                                                  email="testowy22@gmail.com", password="test1234", role="standard",
                                                  phone_number="444444444", is_new_account=False)
        self.standard3 = User.objects.create_user(first_name="Arnold", last_name="Wasp", username="arnwas1111",
                                                  email="testowy2123122@gmail.com", password="test1234", role="standard",
                                                  phone_number="444414444", is_new_account=False)

        self.manager = User.objects.create_user(
            first_name="Szymon",
            last_name="Chasowski",
            username="szycha1111",
            email="testowy3@gmail.com",
            password="test1234",
            role="manager",
            phone_number="987654323", is_new_account=False
        )

        self.manager2=User.objects.create_user(
            first_name="Johnny",
            last_name="Silverhand",
            username="johsil1111",
            email="testowy2077@gmail.com",
            password="test1234",
            role="manager",
            phone_number="987654377", is_new_account=False

        )

        self.mechanic = User.objects.create_user(
            first_name="Karol",
            last_name="Nawrak",
            username="karnaw1111",
            email="testowy4@gmail.com",
            password="test1234",
            role="mechanic",
            phone_number="987654324", is_new_account=False
        )
        self.mechanic2 = User.objects.create_user(
            first_name="Donald",
            last_name="Kaczynski",
            username="donkac1111",
            email="testowy12524@gmail.com",
            password="test1234",
            role="mechanic",
            phone_number="441144114", is_new_account=False
        )

        # Create manufacturers
        self.dodge = Manufacturer.objects.create(name='DODGE')
        self.man = Manufacturer.objects.create(name='MAN')
        self.city = City.objects.create(name='Szczecin')
        # Create locations
        self.branch = Location.objects.create(
            name='SIEDZIBA',
            phone_number='123456789',
            email="test@gmail.com",
            city=self.city,
            street_name='Parkowa',
            building_number=1,
            location_type='B'
        )

        self.branch2 = Location.objects.create(
            name='SIEDZIBA B',
            phone_number='163456789',
            email="test3@gmail.com",
            city=self.city,
            street_name='Parkowa',
            building_number=1,
            location_type='B'
        )

        self.workshop = Location.objects.create(
            name='WARSZTAT',
            phone_number='133456789',
            email="test2@gmail.com",
            city=self.city,
            street_name='Parkowa',
            building_number=1,
            location_type='W'
        )
        self.workshop2 = Location.objects.create(
            name='WARSZTAT B',
            phone_number='544333222',
            email="test25323@gmail.com",
            city=self.city,
            street_name='Parkowa',
            building_number=1,
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
        self.vehicle6 = Vehicle.objects.create(
            vin='8GZCZ63B93S896564',
            kilometers=500,
            vehicle_type='CO',
            year=2019,
            vehicle_model="Lion City",
            fuel_type='D',
            availability='U',
            location=self.branch,
            manufacturer=self.man
        )
        self.failure_report4 = FailureReport.objects.create(
            vehicle=self.vehicle6,
            title="Brake issue",
            description="Brakes are making noise",
            report_author=self.standard,
            status='A',
            workshop=self.workshop2,
            managed_by=self.manager
        )
        self.repair_report3 = RepairReport.objects.create(
            failure_report=self.failure_report4,
            condition_analysis="Wheelbrakes are deceased",
            repair_action="New wheelbrakes have been installed",
            cost=1500.00,
            status='R'
        )

        # Assign users to locations
        UserLocationAssignment.objects.create(user=self.standard, location=self.branch)
        UserLocationAssignment.objects.create(user=self.mechanic, location=self.workshop)
        UserLocationAssignment.objects.create(user=self.mechanic2, location=self.workshop2)

        # Create failure reports
        self.failure_report1 = FailureReport.objects.create(
            vehicle=self.vehicle1,
            title="Engine failure",
            description="Engine is not starting properly",
            report_author=self.standard,
            status='P',  # PENDING
            managed_by=self.manager
        )

        self.failure_report2 = FailureReport.objects.create(
            vehicle=self.vehicle3,
            title="Brake issue",
            description="Brakes are making noise",
            report_author=self.standard,
            status='A',  # ASSIGNED
            workshop=self.workshop2,
            managed_by = self.manager
        )

        self.failure_report3 = FailureReport.objects.create(
            vehicle=self.vehicle3,
            title="Resolved issue",
            description="This issue is already resolved",
            report_author=self.standard,
            workshop=self.workshop,
            status='R', # RESOLVED
            managed_by=self.manager
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
            "title":'zero tituli',
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
            "title": 'zero tituli',
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
        self.assertEqual(len(failure_reports), 4)


    def test_admin_can_list_failure_reports(self):
        client = APIClient()
        client.force_authenticate(self.admin)

        response = client.get(reverse('failure-report-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        failure_reports = response.json()
        self.assertEqual(len(failure_reports), 4)

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

    def test_manager_can_assign_failure_report(self):
        client = APIClient()
        client.force_authenticate(self.manager)
        response = client.post(reverse('failure-report-action',kwargs={'pk':self.failure_report1.pk}), data={
            "workshop": self.workshop.pk,
            "action":"assign"
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        failure_report = FailureReport.objects.get(id=self.failure_report1.id)
        self.assertEqual(failure_report.status, 'A')  # ASSIGNED
        self.assertEqual(failure_report.workshop, self.workshop)
        self.assertTrue(RepairReport.objects.filter(failure_report=failure_report).exists())

    def test_manager_cannot_assign_failure_report_not_managed_by_himself(self):
        client = APIClient()
        client.force_authenticate(self.manager2)
        response = client.post(reverse('failure-report-action', kwargs={'pk': self.failure_report1.pk}), data={
            "workshop": self.workshop.pk,
            "action":"assign"
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_standard_user_cannot_assign_failure_report(self):
        client = APIClient()
        client.force_authenticate(self.standard)

        response = client.post(reverse('failure-report-action', kwargs={'pk': self.failure_report1.pk}), data={
            "workshop": self.workshop.pk,
            "action":"assign"
        })

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_assigned_failure_report_cannot_be_assigned_again(self):
        client = APIClient()
        client.force_authenticate(self.manager)
        response = client.post(reverse('failure-report-action',kwargs={'pk':self.failure_report2.pk}), data={
            "workshop": self.workshop.pk,
            "action": "assign"
        })
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertIn('Failure report is not in PENDING status.',str(response.json()))


    def test_manager_can_dismiss_failure_report(self):
        client = APIClient()
        client.force_authenticate(self.manager)
        response = client.post(reverse('failure-report-action',kwargs={'pk':self.failure_report1.pk}),data={
            "action":"dismiss"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that failure report was updated
        failure_report = FailureReport.objects.get(id=self.failure_report1.id)
        self.assertEqual(failure_report.status, 'D')  # DISMISSED

    def test_manager_cannot_dismiss_failure_report_not_managed_by_himself(self):
        client = APIClient()
        client.force_authenticate(self.manager2)
        response = client.post(reverse('failure-report-action', kwargs={'pk': self.failure_report1.pk}), data={
            "workshop": self.workshop.pk,
            "action":"dismiss"
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_standard_user_cannot_dismiss_failure_report(self):
        client = APIClient()
        client.force_authenticate(self.standard)

        response = client.post(reverse('failure-report-action',kwargs={'pk':self.failure_report1.pk}),data={
            "action":"dismiss"
        })

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_can_resolve_assigned_failure_report_with_ready_repair_report(self):
        client = APIClient()
        client.force_authenticate(self.manager)

        response = client.post(reverse('failure-report-action',kwargs={'pk':self.failure_report4.pk}),data={
            "action":"resolve"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        fr=FailureReport.objects.get(id=self.failure_report4.id)
        rr=RepairReport.objects.get(id=self.repair_report3.id)
        veh=Vehicle.objects.get(id=self.vehicle6.id)
        self.assertEqual(fr.status, 'R')
        self.assertEqual(rr.status, 'H')
        self.assertEqual(veh.availability,'A')
        self.assertIn('Failure report has been resolved.',str(response.json()))

    def test_manager_cannot_resolve_failure_report_managed_by_other_manager(self):
        client = APIClient()
        client.force_authenticate(self.manager2)
        response=client.post(reverse('failure-report-action',kwargs={'pk':self.failure_report4.pk}),data={
            "action":"resolve"
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_cannot_resolve_pending_failure_report(self):
        client = APIClient()
        client.force_authenticate(self.manager)
        response=client.post(reverse('failure-report-action',kwargs={'pk':self.failure_report1.pk}),data={
            "action":"resolve"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Failure report is not in ASSIGNED status.',str(response.json()))

    def test_manager_cannot_resolve_failure_report_with_not_ready_repair_report(self):
        self.repair_report3.status = 'A'
        self.repair_report3.save()
        client = APIClient()
        client.force_authenticate(self.manager)
        response = client.post(reverse('failure-report-action', kwargs={'pk': self.failure_report4.pk}),data={"action":"resolve"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Repair report is not in READY status.', str(response.json()))
        self.repair_report3.status = 'R'
        self.repair_report3.save()


    def test_manager_can_reassign_failure_report(self):
        client = APIClient()
        client.force_authenticate(self.manager)

        response = client.post(reverse('failure-report-action',kwargs={'pk':self.failure_report2.pk}), data={
            "workshop": str(self.workshop.id),
            "action":"reassign"
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        failure_report = FailureReport.objects.get(id=self.failure_report2.id)
        self.assertEqual(failure_report.status, 'A')  # ASSIGNED
        self.assertEqual(failure_report.workshop, self.workshop)

    def test_manager_cannot_reassign_failure_report_not_managed_by_himself(self):
        client = APIClient()
        client.force_authenticate(self.manager2)
        response = client.post(reverse('failure-report-action', kwargs={'pk': self.failure_report2.pk}), data={
            "workshop": self.workshop.pk,
            "action":"reassign"
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_standard_user_cannot_reassign_failure_report(self):

        client = APIClient()
        client.force_authenticate(self.standard)

        response = client.post(reverse('failure-report-action', kwargs={'pk': self.failure_report2.pk}), data={
            "workshop": str(self.workshop2.id),
            "action":"reassign"
        })

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_manager_cannot_reassign_pending_failure_report(self):
        client=APIClient()
        client.force_authenticate(self.manager)
        response = client.post(reverse('failure-report-action', kwargs={'pk': self.failure_report1.pk}), data={
            "workshop": str(self.workshop2.id),
            "action":"reassign"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Failure report is not in ASSIGNED or STOPPED status.', str(response.json()))

    def test_manager_cannot_reassign_non_existent_failure_report(self):
        client=APIClient()
        client.force_authenticate(self.manager)
        response = client.post(reverse('failure-report-action',kwargs={'pk':'5f35a175-73bb-44ac-b007-bb1d7ff3f13b'}), data={
            "workshop": str(self.workshop2.id),
            "action":"reassign"
        })
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_manager_can_manage_unmanaged_failure_report(self):
        client = APIClient()
        client.force_authenticate(self.manager2)
        failure_report=FailureReport.objects.create(
            vehicle=self.vehicle2,
            title="Engine failure",
            description="Engine is not starting properly",
            report_author=self.standard,
            status='P')
        response=client.post(reverse('failure-report-management',kwargs={'pk':failure_report.pk}), data={
            "action":"obtain"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        failure_report = FailureReport.objects.get(id=failure_report.id)
        self.assertEqual(failure_report.managed_by, self.manager2)

    def test_manager_cannot_manage_managed_failure_report(self):
        client = APIClient()
        client.force_authenticate(self.manager2)
        response = client.post(reverse('failure-report-management', kwargs={'pk': self.failure_report1.pk}),data={
            "action":"obtain"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Failure report is already managed by another manager.', str(response.json()))

    def test_manager_cannot_manage_resolved_failure_report(self):
        client = APIClient()
        client.force_authenticate(self.manager2)
        failure_report = FailureReport.objects.create(
            vehicle=self.vehicle2,
            title="Engine failure",
            description="Engine is not starting properly",
            report_author=self.standard,
            status='R')
        response=client.post(reverse('failure-report-management', kwargs={'pk': failure_report.pk}),data={
            "action":"obtain"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Failure report is not in PENDING, ASSIGNED or STOPPED status.', str(response.json()))

    def test_manager_cannot_manage_dismissed_failure_report(self):
        client = APIClient()
        client.force_authenticate(self.manager2)
        failure_report = FailureReport.objects.create(
            vehicle=self.vehicle2,
            title="Engine failure",
            description="Engine is not starting properly",
            report_author=self.standard,
            status='D')
        response=client.post(reverse('failure-report-management', kwargs={'pk': failure_report.pk}),data={
            "action":"obtain"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Failure report is not in PENDING, ASSIGNED or STOPPED status.', str(response.json()))

    def test_manager_cannot_manage_failure_report_already_managed_by_himself(self):
        client = APIClient()
        client.force_authenticate(self.manager)
        response = client.post(reverse('failure-report-management', kwargs={'pk': self.failure_report1.pk}),data={
            "action":"obtain"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Failure report is already managed by you.', str(response.json()))

    def test_manager_can_release_failure_report_he_manages_himself(self):
        client = APIClient()
        client.force_authenticate(self.manager)
        response=client.post(reverse('failure-report-management', kwargs={'pk': self.failure_report1.pk}),data={
            "action":"release"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        failure=FailureReport.objects.get(pk=self.failure_report1.pk)
        self.assertEqual(failure.managed_by, None)

    def test_manager_cannot_release_failure_report_that_is_not_managed(self):
        client = APIClient()
        client.force_authenticate(self.manager2)
        failure_report = FailureReport.objects.create(
            vehicle=self.vehicle2,
            title="Engine failure",
            description="Engine is not starting properly",
            report_author=self.standard,
            status='P')
        response=client.post(reverse('failure-report-management', kwargs={'pk': failure_report.pk}),data={
            'action':'release'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('You do not have permission to perform this action.', str(response.json()))

    def test_manager_cannot_release_failure_report_managed_by_other_manager(self):
        client = APIClient()
        client.force_authenticate(self.manager2)
        response=client.post(reverse('failure-report-management', kwargs={'pk': self.failure_report1.pk}),data={
            "action":"release"
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('You do not have permission to perform this action.', str(response.json()))

    def test_manager_cannot_release_resolved_failure_report(self):
        client = APIClient()
        client.force_authenticate(self.manager)
        response=client.post(reverse('failure-report-management', kwargs={'pk': self.failure_report3.pk}),data={"action":"release"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Failure report is not in PENDING, ASSIGNED or STOPPED status.', str(response.json()))

    def test_manager_cannot_release_dismissed_failure_report(self):
        client = APIClient()
        client.force_authenticate(self.manager)
        failure_report = FailureReport.objects.create(
            vehicle=self.vehicle2,
            title="Engine failure",
            description="Engine is not starting properly",
            report_author=self.standard,
            status='D',
            managed_by=self.manager
        )
        response=client.post(reverse('failure-report-management', kwargs={'pk': failure_report.pk}),data={
            "action":"release"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Failure report is not in PENDING, ASSIGNED or STOPPED status.', str(response.json()))


