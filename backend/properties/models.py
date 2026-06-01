from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    def __str__(self): return self.name
    class Meta: verbose_name_plural = 'Categories'

class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agent_profile')
    phone = models.CharField(max_length=30, blank=True)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='agents/', blank=True, null=True)
    def __str__(self): return self.user.get_full_name() or self.user.username

PROPERTY_TYPES = [
    ('apartment', 'Apartment'),
    ('villa', 'Villa'),
    ('house', 'House'),
    ('commercial', 'Commercial'),
    ('land', 'Land'),
]
LISTING_TYPES = [('buy', 'Buy'), ('rent', 'Rent')]
STATUS = [('available', 'Available'), ('sold', 'Sold'), ('rented', 'Rented')]
APPROVAL_STATUS = [('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')]

class Property(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    location = models.CharField(max_length=200)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES, default='apartment')
    listing_type = models.CharField(max_length=10, choices=LISTING_TYPES, default='buy')
    bedrooms = models.PositiveIntegerField(default=1)
    bathrooms = models.PositiveIntegerField(default=1)
    area_sqft = models.PositiveIntegerField(default=0)
    amenities = models.CharField(max_length=500, blank=True, help_text='Comma-separated')
    furnished = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS, default='approved')
    status = models.CharField(max_length=20, choices=STATUS, default='available')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Properties'

    def __str__(self): return self.title
    def get_absolute_url(self): return reverse('property_detail', args=[self.pk])
    def amenity_list(self):
        return [a.strip() for a in self.amenities.split(',') if a.strip()]
    def default_image_url(self):
        images = {
            'apartment': 'https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&w=1200&q=85',
            'villa': 'https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?auto=format&fit=crop&w=1200&q=85',
            'house': 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=85',
            'commercial': 'https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=1200&q=85',
            'land': 'https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1200&q=85',
        }
        return images.get(self.property_type, images['house'])

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='properties/')
    caption = models.CharField(max_length=120, blank=True)
    def __str__(self): return f'{self.property.title} image'

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user', 'property')

class ContactMessage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='messages')
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f'Inquiry: {self.name} -> {self.property.title}'
