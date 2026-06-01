from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from properties.models import Agent, Category, Property


class Command(BaseCommand):
    help = 'Create Indian example listings for every property type.'

    def handle(self, *args, **options):
        owner, _ = User.objects.get_or_create(
            username='smartproperty_agent',
            defaults={
                'first_name': 'Sophia',
                'last_name': 'Laurent',
                'email': 'sophia@smartproperty.com',
            },
        )
        owner.first_name = 'Sophia'
        owner.last_name = 'Laurent'
        owner.email = 'sophia@smartproperty.com'
        owner.save()
        Agent.objects.update_or_create(
            user=owner,
            defaults={
                'phone': '+91 93461 93628',
                'bio': 'Verified Smart Property seller for premium Indian listings.',
            },
        )

        examples = [
            {
                'title': 'Whitefield Skyline Apartment',
                'property_type': 'apartment',
                'listing_type': 'rent',
                'price': Decimal('85000.00'),
                'location': 'Whitefield Main Road, Bengaluru, Karnataka, India',
                'bedrooms': 3,
                'bathrooms': 3,
                'area_sqft': 1850,
                'amenities': 'Clubhouse, Gym, Balcony, Covered Parking, Power Backup',
                'description': 'A bright high-rise apartment close to ITPL, metro access, schools, cafes, and daily essentials.',
                'furnished': True,
                'is_featured': True,
            },
            {
                'title': 'ECR Sea Breeze Villa',
                'property_type': 'villa',
                'listing_type': 'buy',
                'price': Decimal('48500000.00'),
                'location': 'East Coast Road, Chennai, Tamil Nadu, India',
                'bedrooms': 5,
                'bathrooms': 5,
                'area_sqft': 6200,
                'amenities': 'Private Pool, Garden, Home Theatre, Servant Room, Security',
                'description': 'A private coastal villa with landscaped gardens, large decks, premium interiors, and quick beach access.',
                'furnished': True,
                'is_featured': True,
            },
            {
                'title': 'Jubilee Hills Family House',
                'property_type': 'house',
                'listing_type': 'buy',
                'price': Decimal('32500000.00'),
                'location': 'Road No. 45, Jubilee Hills, Hyderabad, Telangana, India',
                'bedrooms': 4,
                'bathrooms': 4,
                'area_sqft': 4200,
                'amenities': 'Modular Kitchen, Terrace, Two Car Parking, Solar Water Heater',
                'description': 'A calm independent house near premium schools, hospitals, restaurants, and main city connectors.',
                'furnished': False,
                'is_featured': False,
            },
            {
                'title': 'BKC Signature Commercial Office',
                'property_type': 'commercial',
                'listing_type': 'rent',
                'price': Decimal('650000.00'),
                'location': 'Bandra Kurla Complex, Mumbai, Maharashtra, India',
                'bedrooms': 0,
                'bathrooms': 6,
                'area_sqft': 9800,
                'amenities': 'Private Elevator, Conference Rooms, Reception, Pantry, Basement Parking',
                'description': 'A plug-and-play commercial floor built for finance, consulting, and enterprise teams in Mumbai.',
                'furnished': True,
                'is_featured': True,
            },
            {
                'title': 'Sarjapur Growth Corridor Land',
                'property_type': 'land',
                'listing_type': 'buy',
                'price': Decimal('17500000.00'),
                'location': 'Sarjapur Road, Bengaluru, Karnataka, India',
                'bedrooms': 0,
                'bathrooms': 0,
                'area_sqft': 12000,
                'amenities': 'Clear Title, Road Access, Gated Layout, Water Connection',
                'description': 'A residential plot in a fast-growing corridor with clean access to schools and technology parks.',
                'furnished': False,
                'is_featured': False,
            },
            {
                'title': 'Koregaon Park Premium Apartment',
                'property_type': 'apartment',
                'listing_type': 'buy',
                'price': Decimal('22500000.00'),
                'location': 'Koregaon Park, Pune, Maharashtra, India',
                'bedrooms': 4,
                'bathrooms': 4,
                'area_sqft': 2850,
                'amenities': 'Sky Lounge, Gym, Clubhouse, Visitor Parking, Security',
                'description': 'A spacious premium apartment in one of Pune highest demand residential neighborhoods.',
                'furnished': True,
                'is_featured': True,
            },
        ]

        created = 0
        updated = 0
        for data in examples:
            category, _ = Category.objects.get_or_create(name=data['property_type'].title())
            prop, was_created = Property.objects.update_or_create(
                title=data['title'],
                defaults={
                    **data,
                    'owner': owner,
                    'category': category,
                    'approval_status': 'approved',
                    'status': 'available',
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(f'Example properties ready. Created {created}, updated {updated}.'))
