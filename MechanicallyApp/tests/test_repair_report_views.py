from django.test import TestCase
from MechanicallyApp.models import User, Manufacturer, Vehicle, Location, UserLocationAssignment, FailureReport, \
    RepairReport, RepairReportRejection, City
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient



class RepairReportTestCase(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            first_name="Grzegorz", last_name="Kowalski",
            username="grzkow1111", email="testowy76@gmail.com",
            password="test1234", role="admin", phone_number="111111111", is_new_account=False)

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

        self.manager = User.objects.create_user(
            first_name="Szymon",
            last_name="Chasowski",
            username="szycha1111",
            email="testowy3@gmail.com",
            password="test1234",
            role="manager",
            phone_number="987654323", is_new_account=False
        )
        self.manager2 = User.objects.create_user(
            first_name="Remek",
            last_name="Winnicki",
            username="remwin1111",
            email="testowy35512@gmail.com",
            password="test1234",
            role="manager",
            phone_number="313754323", is_new_account=False
        )
        self.mechanic = User.objects.create_user(
            first_name="Dawid",
            last_name="Zalucki",
            username="dawzal1111",
            email="testowy4@gmail.com",
            password="test1234",
            role="mechanic",
            phone_number="987654324", is_new_account=False
        )
        self.mechanic2 = User.objects.create_user(
            first_name="Jakub",
            last_name="Szejna",
            username="jaksze1111",
            email="testowy12524@gmail.com",
            password="test1234",
            role="mechanic",
            phone_number="441144114", is_new_account=False
        )

        self.mechanic3 = User.objects.create_user(
            first_name="Szymon",
            last_name="Wrobel",
            username="szywro1111",
            email="testowy12522324@gmail.com",
            password="test1234",
            role="mechanic",
            phone_number="452114114", is_new_account=False
        )

        self.man = Manufacturer.objects.create(name='MAN')
        self.city=City.objects.create(name='Szczecin')
        self.branch = Location.objects.create(
            name='SIEDZIBA',
            phone_number='123456789',
            email="test@gmail.com",
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

        self.workshop3 = Location.objects.create(
            name='WARSZTAT C',
            phone_number='544353222',
            email="test25324@gmail.com",
            city=self.city,
            street_name='Parkowa',
            building_number=1,
            location_type='W'
        )
        UserLocationAssignment.objects.create(user=self.standard, location=self.branch)
        UserLocationAssignment.objects.create(user=self.mechanic, location=self.workshop)
        UserLocationAssignment.objects.create(user=self.mechanic2, location=self.workshop2)
        UserLocationAssignment.objects.create(user=self.mechanic3, location=self.workshop3)

        self.vehicleA = Vehicle.objects.create(
            vin='5GZCZ63B93S896664',
            vehicle_type='PC',
            year=2018,
            vehicle_model="Lion City",
            fuel_type='P',
            availability='U',
            location=self.branch,
            manufacturer=self.man
        )

        self.vehicleB = Vehicle.objects.create(
            vin='5GZCZ63B93S896564',
            vehicle_type='CO',
            year=2019,
            vehicle_model="Lion City",
            fuel_type='D',
            availability='U',
            location=self.branch,
            manufacturer=self.man
        )

        self.vehicleC = Vehicle.objects.create(
            vin='5GZCZ63B94S896564',
            vehicle_type='TR',
            year=2016,
            vehicle_model="TGX Euro 6",
            fuel_type='D',
            availability='A',
            location=self.branch,
            manufacturer=self.man
        )

        self.vehicleD = Vehicle.objects.create(
            vin='5GZCZ63B94S891564',
            vehicle_type='TR',
            year=2020,
            vehicle_model="TGX Euro 61",
            fuel_type='D',
            availability='U',
            location=self.branch,
            manufacturer=self.man
        )
        self.vehicleE = Vehicle.objects.create(
            vin='5GZCZ63B93S896594',
            vehicle_type='CO',
            year=2020,
            vehicle_model="Lion Gate",
            fuel_type='D',
            availability='A',
            location=self.branch,
            manufacturer=self.man
        )

        self.failure_report1 = FailureReport.objects.create(
            vehicle=self.vehicleA,
            title="Engine failure",
            description="Engine is not starting properly",
            report_author=self.standard,
            status='A',
            workshop=self.workshop,
            managed_by=self.manager2
        )

        self.failure_report2 = FailureReport.objects.create(
            vehicle=self.vehicleA,
            title="Brake issue",
            description="Brakes are making noise",
            report_author=self.standard,
            status='R',
            workshop=self.workshop2,
            managed_by=self.manager
        )

        self.failure_report3 = FailureReport.objects.create(
            vehicle=self.vehicleB,
            title="title issue",
            description="This issue description",
            report_author=self.standard,
            workshop=self.workshop,
            status='A',
            managed_by=self.manager
        )

        self.failure_report4 = FailureReport.objects.create(
            vehicle=self.vehicleC,
            title="Engine failure",
            description="Engine is not starting properly",
            report_author=self.standard,
            status='R',
            workshop=self.workshop,
            managed_by=self.manager
        )

        self.failure_report5 = FailureReport.objects.create(
            vehicle=self.vehicleD,
            title="Brake issue",
            description="Brakes are making noise",
            report_author=self.standard,
            status='A',
            workshop=self.workshop3,
            managed_by=self.manager
        )

        self.failure_report6 = FailureReport.objects.create(
            vehicle=self.vehicleE,
            title=" issue",
            description="This issue description",
            report_author=self.standard,
            workshop=self.workshop3,
            status='R',
            managed_by=self.manager
        )

        self.repair_report1 = RepairReport.objects.create(
            failure_report=self.failure_report1,
            condition_analysis="Initial analysis",
            repair_action="repair action",
            cost=100.00,
            status='A'
        )

        self.repair_report2 = RepairReport.objects.create(
            failure_report=self.failure_report2,
            condition_analysis="Initial analysis",
            repair_action="repair action",
            cost=100.00,
            status='H'
        )

        self.repair_report3 = RepairReport.objects.create(
            failure_report=self.failure_report3,
            condition_analysis="Initial analysis",
            repair_action="repair action",
            cost=100.00,
            status='R'
        )

        self.repair_report4 = RepairReport.objects.create(
            failure_report=self.failure_report4,
            condition_analysis="Initial analysis",
            repair_action="repair action",
            cost=100.00,
            status='H'
        )

        self.repair_report5 = RepairReport.objects.create(
            failure_report=self.failure_report5,
            condition_analysis="Initial analysis",
            repair_action="repair action",
            cost=100.00,
            status='A'
        )

        self.repair_report6 = RepairReport.objects.create(
            failure_report=self.failure_report6,
            condition_analysis="Initial analysis",
            repair_action="repair action",
            cost=100.00,
            status='H'
        )

        self.rejection1=RepairReportRejection.objects.create(
            repair_report=self.repair_report5,
            title="rejection title",
            reason="rejection reason"
        )
        self.rejection2 = RepairReportRejection.objects.create(
            repair_report=self.repair_report5,
            title="rejection title2",
            reason="rejection reason2"
        )

    def test_mechanic_can_list_related_repair_reports(self):
        client=APIClient()
        client.force_authenticate(user=self.mechanic)
        response=client.get(reverse('related-repair-report-list',kwargs={'vehicle_id':self.vehicleA.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()),1)

        client = APIClient()
        client.force_authenticate(user=self.mechanic3)
        response = client.get(reverse('related-repair-report-list', kwargs={'vehicle_id': self.vehicleD.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 0)

    def test_mechanic_can_retrieve_related_repair_report(self):
        client=APIClient()
        client.force_authenticate(user=self.mechanic)
        response=client.get(reverse('repair-report-detail',kwargs={'pk':self.repair_report2.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['id'],str(self.repair_report2.pk))

    def test_mechanic_can_list_workshop_repair_reports(self):
        client=APIClient()
        client.force_authenticate(user=self.mechanic)
        response=client.get(reverse('workshop-repair-report-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()),3)

        client = APIClient()
        client.force_authenticate(user=self.mechanic2)
        response = client.get(reverse('workshop-repair-report-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

        client = APIClient()
        client.force_authenticate(user=self.mechanic3)
        response = client.get(reverse('workshop-repair-report-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)

    def test_mechanic_cannot_retrieve_unrelated_repair_reports(self):
        client = APIClient()
        client.force_authenticate(user=self.mechanic)
        response = client.get(reverse('repair-report-detail', kwargs={'pk': self.repair_report5.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = client.get(reverse('repair-report-detail', kwargs={'pk': self.repair_report6.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_mechanic_can_list_his_workshop_repair_report_rejections(self):
        client=APIClient()
        client.force_authenticate(user=self.mechanic3)
        response=client.get(reverse('repair-report-rejection-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()),2)

        client = APIClient()
        client.force_authenticate(user=self.mechanic2)
        response = client.get(reverse('repair-report-rejection-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 0)

        client = APIClient()
        client.force_authenticate(user=self.mechanic)
        response = client.get(reverse('repair-report-rejection-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 0)

    def test_mechanic_can_retrieve_his_workshop_repair_report_rejections(self):
        client=APIClient()
        client.force_authenticate(user=self.mechanic3)
        response=client.get(reverse('repair-report-rejection-detail', kwargs={'pk': self.rejection1.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['id'],str(self.rejection1.pk))

        response = client.get(reverse('repair-report-rejection-detail', kwargs={'pk': self.rejection2.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['id'], str(self.rejection2.pk))

    def test_mechanic_cannot_retrieve_other_workshop_repair_report_rejections(self):
        client=APIClient()
        client.force_authenticate(user=self.mechanic2)
        response=client.get(reverse('repair-report-rejection-detail', kwargs={'pk': self.rejection1.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = client.get(reverse('repair-report-rejection-detail', kwargs={'pk': self.rejection2.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        client = APIClient()
        client.force_authenticate(user=self.mechanic)
        response = client.get(reverse('repair-report-rejection-detail', kwargs={'pk': self.rejection1.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = client.get(reverse('repair-report-rejection-detail', kwargs={'pk': self.rejection2.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_mechanic_can_set_repair_report_as_ready(self):
        client=APIClient()
        client.force_authenticate(user=self.mechanic3)
        response=client.post(reverse('repair-report-status', kwargs={'pk': self.repair_report5.pk}),data={
            "status":"ready"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rr=RepairReport.objects.get(pk=self.repair_report5.pk)
        self.assertEqual(rr.status,'R')

    def test_manager_can_reject_repair_report(self):
        client=APIClient()
        client.force_authenticate(user=self.manager)
        response=client.post(reverse('repair-report-reject', kwargs={'pk': self.repair_report3.pk}),data={'title':'tytul','reason':'jakis powod'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rejections=RepairReportRejection.objects.all()
        self.assertEqual(len(rejections),3)
        response=client.get(reverse('repair-report-rejection-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()),3)

    def test_manager_cannot_reject_active_or_historic_repair_report(self):
        client=APIClient()
        client.force_authenticate(user=self.manager)
        response = client.post(reverse('repair-report-reject', kwargs={'pk': self.repair_report5.pk}),
                               data={'title': 'tytul', 'reason': 'jakis powod'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = client.post(reverse('repair-report-reject', kwargs={'pk': self.repair_report6.pk}),
                               data={'title': 'tytul', 'reason': 'jakis powod'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_manager_cannot_reject_repair_report_managed_by_other_manager(self):
        client=APIClient()
        client.force_authenticate(user=self.manager)
        response = client.post(reverse('repair-report-reject', kwargs={'pk': self.repair_report1.pk}),
                               data={'title': 'tytul', 'reason': 'jakis powod'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_can_list_all_repair_reports(self):
        client=APIClient()
        client.force_authenticate(user=self.admin)
        response = client.get(reverse('repair-report-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 6)

    def test_manager_can_list_all_repair_reports_he_manages(self):
        client=APIClient()
        client.force_authenticate(user=self.manager)
        response = client.get(reverse('repair-report-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 5)

        client = APIClient()
        client.force_authenticate(user=self.manager2)
        response = client.get(reverse('repair-report-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_manager_can_retrieve_repair_report_he_manages(self):
        client=APIClient()
        client.force_authenticate(user=self.manager2)
        response = client.get(reverse('repair-report-detail', kwargs={'pk': self.repair_report1.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['id'],str(self.repair_report1.pk))

    def test_manager_cannot_retrieve_repair_report_he_not_manages(self):
        client=APIClient()
        client.force_authenticate(user=self.manager2)
        response = client.get(reverse('repair-report-detail', kwargs={'pk': self.repair_report2.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_standard_cannot_list_repair_reports(self):
        client=APIClient()
        client.force_authenticate(user=self.standard)
        response = client.get(reverse('repair-report-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_standard_cannot_retrieve_repair_report(self):
        client=APIClient()
        client.force_authenticate(user=self.standard)
        response=client.get(reverse('repair-report-detail', kwargs={'pk': self.repair_report1.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_mechanic_can_update_active_repair_report_in_his_workshop(self):
        client=APIClient()
        client.force_authenticate(user=self.mechanic)
        response=client.patch(reverse('repair-report-detail', kwargs={'pk': self.repair_report1.pk}),data={'cost': "400"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(RepairReport.objects.get(pk=self.repair_report1.pk).cost,400)

    def test_mechanic_cannot_update_ready_repair_report_in_his_workshop(self):
        client=APIClient()
        client.force_authenticate(user=self.mechanic)
        response=client.patch(reverse('repair-report-detail', kwargs={'pk': self.repair_report3.pk}),data={'cost': "400"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_mechanic_cannot_update_historic_repair_report_in_his_workshop(self):
        client = APIClient()
        client.force_authenticate(user=self.mechanic)
        response = client.patch(reverse('repair-report-detail', kwargs={'pk': self.repair_report4.pk}),
                                data={'cost': "400"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_mechanic_cannot_update_active_repair_report_in_other_workshop(self):
        client = APIClient()
        client.force_authenticate(user=self.mechanic)
        response = client.patch(reverse('repair-report-detail', kwargs={'pk': self.repair_report5.pk}),
                                data={'cost': "400"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)