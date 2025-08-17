from django.test import TestCase
from MechanicallyApp.models import User, Location, UserLocationAssignment
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient
from django.core import mail

class UserTestCase(TestCase):
    def setUp(self):
        self.superuser=User.objects.create_superuser(first_name="Grzegorz", last_name="Kowalski", username="grzkow1111", email="testowy4@gmail.com", password="test1234", role="admin", phone_number="111111111")
        self.admin1=User.objects.create_user(first_name="Piotr", last_name="Testowy", username="piotes1111", email="testowy@gmail.com", password="test1234", role="admin", phone_number="222222222")
        self.admin2=User.objects.create_user(first_name="Albrecht", last_name="Entrati", username="albent1111",email="testowy75@gmail.com", password="test1234", role="admin", phone_number="121212121")
        self.standard1=User.objects.create_user(first_name="Jan", last_name="Nowak", username="jannow1111", email="testowy2@gmail.com", password="test1234", role="standard", phone_number="333333333")
        self.standard2=User.objects.create_user(first_name="Krzysztof", last_name="Pawlak", username="krzpaw1111", email="testowy22@gmail.com",password="test1234", role="standard", phone_number="444444444")
        self.standard3=User.objects.create_user(first_name="Kamil", last_name="Grosicki", username="kamgro1111", email="testowy23@gmail.com",password="test1234", role="standard", phone_number="555555555")
        self.manager=User.objects.create_user(first_name="Szymon", last_name="Chasowski", username="szycha1111", email="testowy3@gmail.com",password="test1234", role="manager", phone_number="666666666")
        self.mechanic1=User.objects.create_user(first_name="Karol", last_name="Nawrak", username="karnaw1111", email="testowy26@gmail.com",password="test1234", role="mechanic", phone_number="777777777")
        self.mechanic2=User.objects.create_user(first_name="Jimmy", last_name="Mcgill", username="jimmcg1111",email="testowy27@gmail.com", password="test1234", role="mechanic", phone_number="888888888")
        self.mechanic3=User.objects.create_user(first_name="Lalo", last_name="Salamanca", username="lalsal1111",email="testowy28@gmail.com", password="test1234", role="mechanic",phone_number="999999999")
        self.branch=Location.objects.create(name='SIEDZIBA',phone_number='123456789',email="test@gmail.com",address="Testowa 1 Gdynia", location_type='B')
        self.workshop=Location.objects.create(name='WARSZTAT', phone_number='133456789', email="test2@gmail.com",address="Testowa 2 Gdynia", location_type='W')
        UserLocationAssignment.objects.create(user=self.standard1, location=self.branch)
        UserLocationAssignment.objects.create(user=self.standard2, location=self.branch)
        UserLocationAssignment.objects.create(user=self.mechanic1, location=self.workshop)
        UserLocationAssignment.objects.create(user=self.mechanic2, location=self.workshop)

    def test_superuser_can_retrieve_own_account_with_additional_fields(self):

        client=APIClient()
        client.force_authenticate(self.superuser)
        response=client.get(reverse('user-profile'))
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.json()['username'],self.superuser.username)
        self.assertEqual(response.json()['is_active'],self.superuser.is_active)


    def test_non_standard_or_mechanic_user_can_retrieve_own_account_without_location_field(self):

        client=APIClient()
        client.force_authenticate(self.manager)
        response=client.get(reverse('user-profile'))
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.json()['id'],str(self.manager.pk))
        self.assertEqual(response.json().get('user_location_assignment',None),None)

    def test_assigned_user_can_retrieve_own_account_with_location_field(self):

        client=APIClient()
        client.force_authenticate(self.standard1)
        response=client.get(reverse('user-profile'))
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.json()['id'],str(self.standard1.pk))
        self.assertEqual(response.json()['user_location_assignment']['location']['name'],'SIEDZIBA')

    def test_unassigned_standard_can_retrieve_own_account_with_empty_location_field(self):
        client=APIClient()
        client.force_authenticate(self.standard3)
        response=client.get(reverse('user-profile'))
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.json()['id'],str(self.standard3.pk))
        self.assertEqual(response.json()['user_location_assignment'],None)

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

    def test_manager_can_list_standards_and_mechanics_and_managers_only(self):
        user=User.objects.get(username="szycha1111")
        client = APIClient()
        client.force_authenticate(user)
        response=client.get(reverse('user-list'))
        assert response.status_code==status.HTTP_200_OK
        users=response.json()
        assert len(users)==7
        self.assertTrue(all(user['first_name'] in ('Jan','Krzysztof','Kamil','Lalo','Szymon','Karol','Jimmy') for user in users))

    def test_admin_can_list_all_users_without_superuser(self):
        user = User.objects.get(username="piotes1111")
        client = APIClient()
        client.force_authenticate(user)
        response = client.get(reverse('user-list'))
        assert response.status_code == status.HTTP_200_OK
        users = response.json()
        assert len(users) == 9
        self.assertTrue(all(user['first_name']!='Grzegorz' for user in users))

    def test_superuser_can_list_all_users(self):
        user = User.objects.get(username="grzkow1111")
        client = APIClient()
        client.force_authenticate(user)
        response = client.get(reverse('user-list'))
        assert response.status_code == status.HTTP_200_OK
        users = response.json()
        assert len(users) == 10

    def test_not_admin_users_cannot_create_users(self):
        standard=User.objects.get(username="jannow1111")
        mechanic=User.objects.get(username="karnaw1111")
        manager=User.objects.get(username="szycha1111")

        client = APIClient()
        client.force_authenticate(standard)
        response = client.post(reverse('user-list'),data={
            "first_name": "Jakub",
            "last_name": "Tackowski",
            "email":"delivered@resend.dev",
            "phone_number":"628327263",
            "role":"mechanic"
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN
        client = APIClient()
        client.force_authenticate(mechanic)
        response = client.post(reverse('user-list'), data={
            "first_name": "Jakub",
            "last_name": "Tackowski",
            "email": "delivered@resend.dev",
            "phone_number": "628327263",
            "role": "mechanic"
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN
        client = APIClient()
        client.force_authenticate(manager)
        response = client.post(reverse('user-list'), data={
            "first_name": "Jakub",
            "last_name": "Tackowski",
            "email": "delivered@resend.dev",
            "phone_number": "628327263",
            "role": "mechanic"
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN
        self.assertEqual(len(mail.outbox), 0)

    def test_admin_can_create_standard(self):
        user = User.objects.get(username="piotes1111")
        client = APIClient()
        client.force_authenticate(user)
        response = client.post(reverse('user-list'), data={
            "first_name": "Jakub",
            "last_name": "Tackowski",
            "email": "delivered@resend.dev",
            "phone_number": "628327263",
            "role": "standard"
        })
        assert response.status_code == status.HTTP_201_CREATED
        created_account=User.objects.get(first_name="Jakub")
        assert created_account.role=="standard" and created_account.is_active==False
        self.assertEqual(len(mail.outbox), 1)

    def test_admin_can_create_mechanic(self):
        user = User.objects.get(username="piotes1111")
        client = APIClient()
        client.force_authenticate(user)
        response = client.post(reverse('user-list'), data={
            "first_name": "Jakub",
            "last_name": "Tackowski",
            "email": "delivered@resend.dev",
            "phone_number": "628327263",
            "role": "mechanic"
        })
        assert response.status_code == status.HTTP_201_CREATED
        created_account=User.objects.get(first_name="Jakub")
        assert created_account.role=="mechanic" and created_account.is_active==False
        self.assertEqual(len(mail.outbox), 1)

    def test_admin_can_create_manager(self):
        user = User.objects.get(username="piotes1111")
        client = APIClient()
        client.force_authenticate(user)
        response = client.post(reverse('user-list'), data={
            "first_name": "Jakub",
            "last_name": "Tackowski",
            "email": "delivered@resend.dev",
            "phone_number": "628327263",
            "role": "manager"
        })
        assert response.status_code == status.HTTP_201_CREATED
        created_account=User.objects.get(first_name="Jakub")
        assert created_account.role=="manager" and created_account.is_active==False
        self.assertEqual(len(mail.outbox), 1)

    def test_admin_cannot_create_admin(self):
        user = User.objects.get(username="piotes1111")
        client = APIClient()
        client.force_authenticate(user)
        response = client.post(reverse('user-list'), data={
            "first_name": "Jakub",
            "last_name": "Tackowski",
            "email": "delivered@resend.dev",
            "phone_number": "628327263",
            "role": "admin"
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN
        self.assertEqual(len(mail.outbox), 0)

    def test_superuser_can_create_admin(self):
        user = User.objects.get(username="grzkow1111")
        client = APIClient()
        client.force_authenticate(user)
        response = client.post(reverse('user-list'), data={
            "first_name": "Jakub",
            "last_name": "Tackowski",
            "email": "vaworo8022@7tul.com",
            "phone_number": "628327263",
            "role": "admin"
        })
        assert response.status_code == status.HTTP_201_CREATED
        created_account = User.objects.get(first_name="Jakub")
        assert created_account.role == "admin" and created_account.is_active == False
        self.assertEqual(len(mail.outbox), 1)

    def test_standard_can_retrieve_own_account_and_branch_coworkers(self):
        user=User.objects.get(username="jannow1111")
        client=APIClient()
        client.force_authenticate(user)
        response=client.get(reverse('user-detail',kwargs={'pk':user.pk}))
        assert response.status_code==status.HTTP_200_OK
        assert response.json()['id']==str(user.id)
        user2=User.objects.get(username="krzpaw1111")
        response=client.get(reverse('user-detail',kwargs={'pk':user2.pk}))
        assert response.status_code==status.HTTP_200_OK
        assert response.json()['id']==str(user2.id)

    def test_standard_cannot_retrieve_unrelated_users(self):
        user = User.objects.get(username="jannow1111")
        client = APIClient()
        client.force_authenticate(user)
        standard3=User.objects.get(username="kamgro1111")
        mechanic=User.objects.get(username="jimmcg1111")
        manager=User.objects.get(username="szycha1111")
        admin=User.objects.get(username="piotes1111")
        superuser=User.objects.get(username="grzkow1111")
        response = client.get(reverse('user-detail', kwargs={'pk': standard3.pk}))
        assert response.status_code == status.HTTP_404_NOT_FOUND
        response = client.get(reverse('user-detail', kwargs={'pk': mechanic.pk}))
        assert response.status_code == status.HTTP_404_NOT_FOUND
        response = client.get(reverse('user-detail', kwargs={'pk': manager.pk}))
        assert response.status_code == status.HTTP_404_NOT_FOUND
        response = client.get(reverse('user-detail', kwargs={'pk': admin.pk}))
        assert response.status_code == status.HTTP_404_NOT_FOUND
        response = client.get(reverse('user-detail', kwargs={'pk': superuser.pk}))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_mechanic_can_retrieve_own_account_and_workshop_coworkers(self):
        user=User.objects.get(username="karnaw1111")
        client=APIClient()
        client.force_authenticate(user)
        response=client.get(reverse('user-detail',kwargs={'pk':user.pk}))
        assert response.status_code==status.HTTP_200_OK
        assert response.json()['id']==str(user.id)
        user2=User.objects.get(username="jimmcg1111")
        response=client.get(reverse('user-detail',kwargs={'pk':user2.pk}))
        assert response.status_code==status.HTTP_200_OK
        assert response.json()['id']==str(user2.id)

    def test_mechanic_cannot_retrieve_unrelated_users(self):
        user = User.objects.get(username="karnaw1111")
        client = APIClient()
        client.force_authenticate(user)
        standard=User.objects.get(username="jannow1111")
        mechanic3=User.objects.get(username="lalsal1111")
        manager=User.objects.get(username="szycha1111")
        admin=User.objects.get(username="piotes1111")
        superuser=User.objects.get(username="grzkow1111")
        response = client.get(reverse('user-detail', kwargs={'pk': standard.pk}))
        assert response.status_code == status.HTTP_404_NOT_FOUND
        response = client.get(reverse('user-detail', kwargs={'pk': mechanic3.pk}))
        assert response.status_code == status.HTTP_404_NOT_FOUND
        response = client.get(reverse('user-detail', kwargs={'pk': manager.pk}))
        assert response.status_code == status.HTTP_404_NOT_FOUND
        response = client.get(reverse('user-detail', kwargs={'pk': admin.pk}))
        assert response.status_code == status.HTTP_404_NOT_FOUND
        response = client.get(reverse('user-detail', kwargs={'pk': superuser.pk}))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_manager_can_retrieve_own_account_and_standards_and_mechanics(self):
        user=User.objects.get(username="szycha1111")
        client=APIClient()
        client.force_authenticate(user)
        response=client.get(reverse('user-detail',kwargs={'pk':user.pk}))
        assert response.status_code==status.HTTP_200_OK
        assert response.json()['id']==str(user.id)
        standard=User.objects.get(username="kamgro1111")
        response=client.get(reverse('user-detail',kwargs={'pk':standard.pk}))
        assert response.status_code==status.HTTP_200_OK
        assert response.json()['id'] == str(standard.id)
        mechanic=User.objects.get(username="jimmcg1111")
        response=client.get(reverse('user-detail',kwargs={'pk':mechanic.pk}))
        assert response.status_code==status.HTTP_200_OK
        assert response.json()['id'] == str(mechanic.id)

    def test_admin_can_retrieve_all_users_without_superuser(self):
        user = User.objects.get(username="piotes1111")
        standard = User.objects.get(username="jannow1111")
        mechanic = User.objects.get(username="karnaw1111")
        manager = User.objects.get(username="szycha1111")
        admin=User.objects.get(username="albent1111")
        client = APIClient()
        client.force_authenticate(user)
        response = client.get(reverse('user-detail', kwargs={'pk': user.pk}))
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['id'] == str(user.id)
        response = client.get(reverse('user-detail', kwargs={'pk': standard.pk}))
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['id'] == str(standard.id)
        response = client.get(reverse('user-detail', kwargs={'pk': mechanic.pk}))
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['id'] == str(mechanic.id)
        response = client.get(reverse('user-detail', kwargs={'pk': admin.pk}))
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['id'] == str(admin.id)
        response = client.get(reverse('user-detail', kwargs={'pk': manager.pk}))
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['id'] == str(manager.id)

    def test_admin_cannot_retrieve_superuser(self):
        user = User.objects.get(username="piotes1111")
        client = APIClient()
        client.force_authenticate(user)
        superuser=User.objects.get(username="grzkow1111")
        response = client.get(reverse('user-detail', kwargs={'pk': superuser.pk}))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_superuser_can_retrieve_all_users(self):
        user = User.objects.get(username="grzkow1111")
        standard = User.objects.get(username="jannow1111")
        mechanic = User.objects.get(username="karnaw1111")
        manager = User.objects.get(username="szycha1111")
        admin=User.objects.get(username="albent1111")
        client = APIClient()
        client.force_authenticate(user)
        response = client.get(reverse('user-detail', kwargs={'pk': user.pk}))
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['username'] == user.username
        response = client.get(reverse('user-detail', kwargs={'pk': standard.pk}))
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['username'] == standard.username
        response = client.get(reverse('user-detail', kwargs={'pk': mechanic.pk}))
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['username'] == mechanic.username
        response = client.get(reverse('user-detail', kwargs={'pk': admin.pk}))
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['username'] == admin.username
        response = client.get(reverse('user-detail', kwargs={'pk': manager.pk}))
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['username'] == manager.username

    def test_not_admin_users_cannot_update_users(self):
        standard=User.objects.get(username="jannow1111")
        mechanic=User.objects.get(username="karnaw1111")
        manager=User.objects.get(username="szycha1111")
        target=User.objects.get(username="krzpaw1111")
        client=APIClient()
        client.force_authenticate(standard)
        response=client.patch(reverse('user-detail',kwargs={'pk': target.pk}),data={'phone_number':321321321})
        assert response.status_code==status.HTTP_403_FORBIDDEN
        client=APIClient()
        client.force_authenticate(mechanic)
        response=client.patch(reverse('user-detail',kwargs={'pk': target.pk}),data={'phone_number':321321321})
        assert response.status_code==status.HTTP_403_FORBIDDEN
        client=APIClient()
        client.force_authenticate(manager)
        response=client.patch(reverse('user-detail',kwargs={'pk': target.pk}),data={'phone_number':321321321})
        assert response.status_code==status.HTTP_403_FORBIDDEN

    def test_admin_can_update_lower_role_users_personal_data_field(self):
        user=User.objects.get(username="piotes1111")
        standard=User.objects.get(username="jannow1111")
        mechanic=User.objects.get(username="karnaw1111")
        manager=User.objects.get(username="szycha1111")
        client=APIClient()
        client.force_authenticate(user)
        response=client.patch(reverse('user-detail',kwargs={'pk': standard.pk}),data={'phone_number':321321321})
        assert response.status_code==status.HTTP_200_OK
        standard = User.objects.get(username="jannow1111")
        assert "321321321"==str(standard.phone_number)
        response=client.patch(reverse('user-detail',kwargs={'pk': mechanic.pk}),data={'phone_number':321321322})
        assert response.status_code == status.HTTP_200_OK
        mechanic = User.objects.get(username="karnaw1111")
        assert "321321322" == str(mechanic.phone_number)
        response=client.patch(reverse('user-detail',kwargs={'pk': manager.pk}),data={'phone_number':321321323})
        assert response.status_code == status.HTTP_200_OK
        manager = User.objects.get(username="szycha1111")
        assert "321321323" == str(manager.phone_number)

    def test_admin_can_update_standard_and_mechanic_role_when_unassigned(self):
        user=User.objects.get(username="piotes1111")
        standard=User.objects.get(username="kamgro1111")
        mechanic=User.objects.get(username="lalsal1111")
        client=APIClient()
        client.force_authenticate(user)
        response=client.patch(reverse('user-detail',kwargs={'pk': standard.pk}),data={'role':'manager'})
        assert response.status_code==status.HTTP_200_OK
        old_standard=User.objects.get(username="kamgro1111")
        assert old_standard.role=="manager"
        response=client.patch(reverse('user-detail',kwargs={'pk': mechanic.pk}),data={'role':'manager'})
        assert response.status_code==status.HTTP_200_OK
        old_mechanic=User.objects.get(username="lalsal1111")
        assert old_mechanic.role=="manager"

    def test_admin_cannot_update_standard_and_mechanic_role_when_assigned(self):
        user=User.objects.get(username="piotes1111")
        standard=User.objects.get(username="jannow1111")
        mechanic=User.objects.get(username="karnaw1111")
        client=APIClient()
        client.force_authenticate(user)
        response=client.patch(reverse('user-detail',kwargs={'pk': standard.pk}),data={'role':'manager'})
        assert response.status_code==status.HTTP_400_BAD_REQUEST
        response=client.patch(reverse('user-detail',kwargs={'pk': mechanic.pk}),data={'role':'manager'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_admin_can_update_manager_role(self):
        user = User.objects.get(username="piotes1111")
        manager=User.objects.get(username="szycha1111")
        client = APIClient()
        client.force_authenticate(user)
        response = client.patch(reverse('user-detail', kwargs={'pk': manager.pk}), data={'role': 'standard'})
        assert response.status_code == status.HTTP_200_OK
        manager = User.objects.get(username="szycha1111")
        assert manager.role == "standard"

    def test_admin_cannot_update_admin_user(self):
        user = User.objects.get(username="piotes1111")
        admin=User.objects.get(username="albent1111")
        client = APIClient()
        client.force_authenticate(user)
        response = client.patch(reverse('user-detail', kwargs={'pk': admin.pk}), data={'first_name': 'Chuck'})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_cannot_update_non_existent_user(self):
        client = APIClient()
        client.force_authenticate(self.admin1)
        response = client.patch(reverse('user-detail', kwargs={'pk': 'b54d7467-2eaa-4e1b-8be2-3fb091d7639e'}), data={'first_name': 'Chuck'})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_admin_cannot_enumerate_superuser(self):
        client = APIClient()
        client.force_authenticate(self.admin1)
        response = client.patch(reverse('user-detail', kwargs={'pk': 'b54d7467-2eaa-4e1b-8be2-3fb091d7639e'}), data={'first_name': 'Chuck'})
        response2 = client.patch(reverse('user-detail', kwargs={'pk': self.superuser.pk}), data={'first_name': 'Chuck'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response2.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(str(response.data), str(response2.data))

    def test_manager_cannot_update_admin_user(self):
        client = APIClient()
        client.force_authenticate(self.manager)
        response = client.patch(reverse('user-detail', kwargs={'pk': self.admin1.pk}), data={'first_name': 'Chuck'})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_cannot_promote_user_to_admin(self):
        user = User.objects.get(username="piotes1111")
        standard=User.objects.get(username="kamgro1111")
        client = APIClient()
        client.force_authenticate(user)
        response = client.patch(reverse('user-detail', kwargs={'pk': standard.pk}), data={'role': 'admin'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_superuser_cannot_demote_admin_user(self):
        user = User.objects.get(username="grzkow1111")
        admin=User.objects.get(username="albent1111")
        client = APIClient()
        client.force_authenticate(user)
        response = client.patch(reverse('user-detail', kwargs={'pk': admin.pk}), data={'role': 'standard'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_superuser_can_update_admin_user(self):
        user = User.objects.get(username="grzkow1111")
        admin=User.objects.get(username="albent1111")
        client = APIClient()
        client.force_authenticate(user)
        response = client.patch(reverse('user-detail', kwargs={'pk': admin.pk}), data={'first_name': 'Chuck'})
        assert response.status_code == status.HTTP_200_OK
        admin_updated=User.objects.get(id=admin.id)
        assert admin_updated.first_name=="Chuck"

    def test_non_admin_users_cannot_delete_users(self):
        standard=User.objects.get(username="jannow1111")
        mechanic=User.objects.get(username="karnaw1111")
        manager=User.objects.get(username="szycha1111")
        target=User.objects.get(username="krzpaw1111")
        client=APIClient()
        client.force_authenticate(standard)
        response=client.delete(reverse('user-detail',kwargs={'pk': target.pk}))
        assert response.status_code==status.HTTP_403_FORBIDDEN
        client=APIClient()
        client.force_authenticate(mechanic)
        response=client.delete(reverse('user-detail',kwargs={'pk': target.pk}))
        assert response.status_code==status.HTTP_403_FORBIDDEN
        client=APIClient()
        client.force_authenticate(manager)
        response=client.delete(reverse('user-detail',kwargs={'pk': target.pk}))
        assert response.status_code==status.HTTP_403_FORBIDDEN

    def test_admin_can_delete_lower_role_users(self):
        user=User.objects.get(username="piotes1111")
        standard=User.objects.get(username="jannow1111")
        mechanic=User.objects.get(username="karnaw1111")
        manager=User.objects.get(username="szycha1111")
        client=APIClient()
        client.force_authenticate(user)
        response=client.delete(reverse('user-detail',kwargs={'pk': standard.pk}))
        assert response.status_code==status.HTTP_204_NO_CONTENT
        assert User.objects.filter(username="jannow1111").exists()==False
        response=client.delete(reverse('user-detail',kwargs={'pk': mechanic.pk}))
        assert response.status_code==status.HTTP_204_NO_CONTENT
        assert User.objects.filter(username="karnaw1111").exists()==False
        response=client.delete(reverse('user-detail',kwargs={'pk': manager.pk}))
        assert response.status_code==status.HTTP_204_NO_CONTENT
        assert User.objects.filter(username="szycha1111").exists()==False

    def test_admin_cannot_delete_admin_user(self):
        user=User.objects.get(username="piotes1111")
        admin=User.objects.get(username="albent1111")
        client=APIClient()
        client.force_authenticate(user)
        response=client.delete(reverse('user-detail',kwargs={'pk': admin.pk}))
        assert response.status_code==status.HTTP_403_FORBIDDEN

    def test_superuser_can_delete_admin_user(self):
        user=User.objects.get(username="grzkow1111")
        admin=User.objects.get(username="albent1111")
        client=APIClient()
        client.force_authenticate(user)
        response=client.delete(reverse('user-detail',kwargs={'pk': admin.pk}))
        assert response.status_code==status.HTTP_204_NO_CONTENT
        assert User.objects.filter(username="albent1111").exists()==False

