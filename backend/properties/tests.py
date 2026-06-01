from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Property


class PropertyAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username='owner',
            email='owner@example.com',
            password='testpassword123',
        )
        self.other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='testpassword123',
        )
        self.property = Property.objects.create(
            owner=self.owner,
            title='Original Apartment',
            description='Original description',
            price='5000000.00',
            location='Hyderabad',
            property_type='apartment',
            listing_type='buy',
            bedrooms=2,
            bathrooms=2,
            area_sqft=1100,
            amenities='parking',
            furnished=False,
            status='available',
            approval_status='approved',
        )

    def test_owner_can_update_property_with_put(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.put(
            f'/api/properties/{self.property.pk}/',
            {
                'title': 'Updated Villa',
                'description': 'Updated description',
                'price': '7500000.00',
                'location': 'Bengaluru',
                'property_type': 'villa',
                'listing_type': 'rent',
                'bedrooms': 3,
                'bathrooms': 3,
                'area_sqft': 1800,
                'amenities': 'parking, garden',
                'furnished': True,
                'is_featured': False,
                'status': 'available',
                'category': None,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.property.refresh_from_db()
        self.assertEqual(self.property.title, 'Updated Villa')
        self.assertEqual(self.property.location, 'Bengaluru')
        self.assertEqual(self.property.property_type, 'villa')
        self.assertTrue(self.property.furnished)

    def test_owner_can_delete_property(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.delete(f'/api/properties/{self.property.pk}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Property.objects.filter(pk=self.property.pk).exists())

    def test_user_cannot_delete_another_users_property(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.delete(f'/api/properties/{self.property.pk}/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Property.objects.filter(pk=self.property.pk).exists())
