from django.test import TestCase
from MechanicallyApp.models import User, Location, UserLocationAssignment
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient

class UserLocationAssignmentTestCase(TestCase):
    def setUp(self):
        self.superuser=User.objects.create_superuser(first_name="Grzegorz", last_name="Kowalski", username="grzkow1111", email="testowy4@gmail.com", password="test1234", role="admin", phone_number="111111111", is_new_account=False)
        self.admin=User.objects.create_user(first_name="Piotr", last_name="Testowy", username="piotes1111",
                                 email="testowy@gmail.com", password="test1234", role="admin", phone_number="222222222", is_new_account=False)
        self.standard1=User.objects.create_user(first_name="Jan", last_name="Nowak", username="jannow1111", email="testowy2@gmail.com", password="test1234", role="standard", phone_number="333333333", is_new_account=False)
        self.standard2 = User.objects.create_user(first_name="Krzysztof", last_name="Pawlak", username="krzpaw1111",
                                             email="testowy22@gmail.com", password="test1234", role="standard",
                                             phone_number="444444444", is_new_account=False)
        self.manager=User.objects.create_user(first_name="Szymon", last_name="Chasowski", username="szycha1111", email="testowy3@gmail.com",password="test1234", role="manager", phone_number="666666666", is_new_account=False)
        self.mechanic1=User.objects.create_user(first_name="Karol", last_name="Nawrak", username="karnaw1111", email="testowy26@gmail.com",password="test1234", role="mechanic", phone_number="777777777", is_new_account=False)
        self.mechanic2=User.objects.create_user(first_name="Jimmy", last_name="Mcgill", username="jimmcg1111",email="testowy27@gmail.com", password="test1234", role="mechanic", phone_number="888888888", is_new_account=False)
        self.branch1=Location.objects.create(name='SIEDZIBA A',phone_number='123456789',email="test@gmail.com",address="Testowa 1 Gdynia", location_type='B')
        self.workshop1=Location.objects.create(name='WARSZTAT A', phone_number='133456789', email="test2@gmail.com",address="Testowa 2 Gdynia", location_type='W')
        self.branch2 = Location.objects.create(name='SIEDZIBA B', phone_number='123456489', email="test3@gmail.com",
                                               address="Testowa 3 Gdynia", location_type='B')
        self.workshop2 = Location.objects.create(name='WARSZTAT B', phone_number='133256789', email="test4@gmail.com",
                                                 address="Testowa 4 Gdynia", location_type='W')
        UserLocationAssignment.objects.create(user=self.standard1, location=self.branch1)
        UserLocationAssignment.objects.create(user=self.mechanic1, location=self.workshop1)
        
    def test_admin_can_assign_unassigned_standard_to_branch(self):
        client = APIClient()
        client.force_authenticate(self.admin)
        response = client.post(reverse('user-assign',kwargs={'pk':self.standard2.pk}),data={'location':self.branch2.pk})
        assert response.status_code == status.HTTP_200_OK

    def test_manager_can_assign_unassigned_standard_to_branch(self):
        client = APIClient()
        client.force_authenticate(self.manager)
        response = client.post(reverse('user-assign',kwargs={'pk':self.standard2.pk}), data={'location': self.branch2.pk})
        assert response.status_code == status.HTTP_200_OK

    def test_manager_cannot_be_assigned_to_location(self):
        client = APIClient()
        client.force_authenticate(self.admin)
        response = client.post(reverse('user-assign',kwargs={'pk':self.manager.pk}), data={'location': self.branch2.pk})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_admin_can_assign_unassigned_mechanic_to_workshop(self):
        client = APIClient()
        client.force_authenticate(self.admin)
        response = client.post(reverse('user-assign',kwargs={'pk':self.mechanic2.pk}),data={'location':self.workshop2.pk})
        assert response.status_code == status.HTTP_200_OK

    def test_manager_can_assign_unassigned_mechanic_to_workshop(self):
        client = APIClient()
        client.force_authenticate(self.manager)
        response = client.post(reverse('user-assign',kwargs={'pk':self.mechanic2.pk}), data={'location': self.workshop2.pk})
        assert response.status_code == status.HTTP_200_OK

    def test_standard_user_cannot_be_assigned_to_workshop(self):
        client = APIClient()
        client.force_authenticate(self.admin)
        response = client.post(reverse('user-assign',kwargs={'pk':self.standard2.pk}), data={'location': self.workshop2.pk})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        self.assertIn('Standard users can be assigned to branch locations only.',str(response.json()))

    def test_mechanic_cannot_be_assigned_to_branch(self):
        client = APIClient()
        client.force_authenticate(self.admin)
        response = client.post(reverse('user-assign',kwargs={'pk':self.mechanic2.pk}), data={'location': self.branch2.pk})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        self.assertIn('Mechanic users can be assigned to workshop locations only.', str(response.json()))

    def test_assigned_user_cannot_be_assigned_twice_to_same_location(self):
        client = APIClient()
        client.force_authenticate(self.admin)
        response = client.post(reverse('user-assign',kwargs={'pk':self.standard1.pk}), data={'location': self.branch1.pk})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        self.assertIn('This user is already assigned to a location', str(response.json()))
        response = client.post(reverse('user-assign',kwargs={'pk':self.mechanic1.pk}), data={'user': self.mechanic1.pk, 'location': self.workshop1.pk})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        self.assertIn('This user is already assigned to a location', str(response.json()))

    def test_assigned_user_cannot_be_assigned_twice_to_different_location(self):
        client = APIClient()
        client.force_authenticate(self.admin)
        response = client.post(reverse('user-assign',kwargs={'pk':self.standard1.pk}), data={'location': self.branch2.pk})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        self.assertIn('This user is already assigned to a location', str(response.json()))
        response = client.post(reverse('user-assign',kwargs={'pk':self.mechanic1.pk}), data={'user': self.mechanic1.pk, 'location': self.workshop2.pk})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        self.assertIn('This user is already assigned to a location', str(response.json()))

    def test_admin_can_unassign_assigned_standard_from_branch(self):
        client = APIClient()
        client.force_authenticate(self.admin)
        response = client.post(reverse('user-unassign',kwargs={'pk':self.standard1.pk}))
        assert response.status_code == status.HTTP_200_OK
        self.assertIn('User has been unassigned.',str(response.json()))
        self.assertEqual(UserLocationAssignment.objects.filter(user=self.standard1,location=self.branch1).count(),0)

    def test_admin_can_unassign_assigned_mechanic_from_workshop(self):
        client = APIClient()
        client.force_authenticate(self.admin)
        response = client.post(reverse('user-unassign',kwargs={'pk':self.mechanic1.pk}))
        assert response.status_code == status.HTTP_200_OK
        self.assertIn('User has been unassigned.',str(response.json()))
        self.assertEqual(UserLocationAssignment.objects.filter(user=self.mechanic1,location=self.workshop1).count(),0)

    def test_manager_can_unassign_assigned_standard_from_branch(self):
        client = APIClient()
        client.force_authenticate(self.manager)
        response = client.post(reverse('user-unassign',kwargs={'pk':self.standard1.pk}))
        assert response.status_code == status.HTTP_200_OK
        self.assertIn('User has been unassigned.',str(response.json()))
        self.assertEqual(UserLocationAssignment.objects.filter(user=self.standard1,location=self.branch1).count(),0)

    def test_manager_can_unassign_assigned_mechanic_from_workshop(self):
        client = APIClient()
        client.force_authenticate(self.manager)
        response = client.post(reverse('user-unassign',kwargs={'pk':self.mechanic1.pk}))
        assert response.status_code == status.HTTP_200_OK
        self.assertIn('User has been unassigned.',str(response.json()))
        self.assertEqual(UserLocationAssignment.objects.filter(user=self.mechanic1,location=self.workshop1).count(),0)

    def test_unassigned_standard_user_and_mechanic_user_cannot_be_unassigned(self):
        client = APIClient()
        client.force_authenticate(self.admin)
        response = client.post(reverse('user-unassign',kwargs={'pk':self.standard2.pk}))
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        self.assertIn('User is not assigned to any location.',str(response.json()))
        response = client.post(reverse('user-unassign', kwargs={'pk': self.mechanic2.pk}))
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        self.assertIn('User is not assigned to any location.', str(response.json()))

    def test_non_standard_non_mechanic_user_cannot_be_unassigned(self):
        client = APIClient()
        client.force_authenticate(self.admin)
        response = client.post(reverse('user-unassign',kwargs={'pk':self.manager.pk}))
        assert response.status_code == status.HTTP_404_NOT_FOUND
        self.assertIn('There is no standard user or mechanic user with provided ID.',str(response.json()))
        response = client.post(reverse('user-unassign',kwargs={'pk':self.superuser.pk}))
        assert response.status_code == status.HTTP_404_NOT_FOUND
        self.assertIn('There is no standard user or mechanic user with provided ID.',str(response.json()))
        response = client.post(reverse('user-unassign',kwargs={'pk':self.admin.pk}))
        assert response.status_code == status.HTTP_404_NOT_FOUND
        self.assertIn('There is no standard user or mechanic user with provided ID.', str(response.json()))