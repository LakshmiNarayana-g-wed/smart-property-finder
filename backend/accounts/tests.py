from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
import datetime
from .models import EmailOTP

class OTPModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword123')
        
    def test_otp_creation_and_expiration(self):
        # Generate an OTP
        otp_record = EmailOTP.objects.create(user=self.user, otp='123456')
        
        # Verify fields
        self.assertEqual(otp_record.user, self.user)
        self.assertEqual(otp_record.otp, '123456')
        self.assertFalse(otp_record.is_verified)
        self.assertFalse(otp_record.is_expired())
        
        # Simulate time passage of 6 minutes (beyond 5 minute limit)
        otp_record.created_at = timezone.now() - datetime.timedelta(minutes=6)
        otp_record.save()
        
        # Verify expiration behavior
        self.assertTrue(otp_record.is_expired())


class AccountAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
        )
        self.client.force_authenticate(user=self.user)

    def test_user_can_change_username(self):
        response = self.client.patch('/api/account/', {'username': 'newuser'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'newuser')
        self.assertEqual(response.data['username'], 'newuser')

    def test_user_can_change_password(self):
        response = self.client.post(
            '/api/account/change-password/',
            {
                'current_password': 'testpassword123',
                'new_password': 'newpassword456',
                'new_password2': 'newpassword456',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword456'))

    def test_password_change_requires_current_password(self):
        response = self.client.post(
            '/api/account/change-password/',
            {
                'current_password': 'wrong-password',
                'new_password': 'newpassword456',
                'new_password2': 'newpassword456',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('testpassword123'))
