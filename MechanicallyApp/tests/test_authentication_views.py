from django.test import TestCase
from MechanicallyApp.models import User
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient
class AuthenticationTestCase(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(first_name="Piotr", last_name="Testowy", username="piotes1111",
                                               email="testowy@gmail.com", password="test123456789", role="admin",
                                               phone_number="222222222")

        self.fresh_account = User.objects.create_user(first_name="Sebastian", last_name="Wrobel", username="sebwro",
                                                      email="durango@gmail.com",
                                                      password="test123456789",
                                                      role="standard", phone_number="313731377", is_active=False)

    def test_user_can_obtain_tokens(self):
        client = APIClient()
        response=client.post(reverse('obtain-token-pair'),data={'username':self.admin.username,'password':'test123456789'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', str(response.json()))
        self.assertIn('access', str(response.json()))

    def test_user_can_refresh_token(self):
        client = APIClient()
        response = client.post(reverse('obtain-token-pair'), data={'username': self.admin.username, 'password': 'test123456789'})
        refresh=response.json()['refresh']
        response = client.post(reverse('refresh-token'),data={'refresh':refresh})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', str(response.json()))

    def test_inactive_user_cannot_obtain_tokens(self):
        client = APIClient()
        response = client.post(reverse('obtain-token-pair'),
                               data={'username': self.fresh_account.username, 'password': 'test123456789'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('No active account found with the given credentials',str(response.json()))

    def test_user_can_blacklist_refresh_token(self):
        client = APIClient()
        response = client.post(reverse('obtain-token-pair'),
                               data={'username': self.admin.username, 'password': 'test123456789'})
        refresh = response.json()['refresh']
        response = client.post(reverse('refresh-token'), data={'refresh': refresh})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response=client.post(reverse('blacklist-refresh-token'), data={'refresh': refresh})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = client.post(reverse('refresh-token'), data={'refresh': refresh})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('Token is blacklisted',str(response.json()))

