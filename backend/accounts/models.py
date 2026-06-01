from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
import datetime


class Profile(models.Model):
    ROLE_CHOICES = [
        ('buyer', 'Buyer / Renter'),
        ('agent', 'Property Agent'),
        ('admin', 'Admin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='buyer')

    def __str__(self):
        return f'{self.user.username} - {self.get_role_display()}'


class EmailOTP(models.Model):
    """
    Model to temporarily store 6-digit OTPs sent to the user for email verification
    during the forgot password flow.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def is_expired(self):
        """
        Check if the OTP has expired (validity is 5 minutes).
        """
        return timezone.now() > self.created_at + datetime.timedelta(minutes=5)

    def __str__(self):
        return f"OTP {self.otp} for {self.user.email} (Expired: {self.is_expired()})"

