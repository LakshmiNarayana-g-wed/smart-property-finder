from django.shortcuts import render, get_object_or_404, redirect
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator
from rest_framework import permissions, status, viewsets
from rest_framework.views import APIView
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from .models import Agent, Category, ContactMessage, Property, PropertyImage, Wishlist
from .forms import PropertyForm, PropertyImageForm, ContactForm
from .serialization import (
    AgentSerializer,
    CategorySerializer,
    ContactMessageSerializer,
    CurrentUserSerializer,
    PasswordChangeSerializer,
    PropertyImageSerializer,
    PropertySerializer,
    WishlistSerializer,
)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_overview(request):
    property_payload = {
        'title': 'Modern Apartment',
        'description': 'A well connected apartment with parking and balcony.',
        'price': '7500000.00',
        'location': 'Hyderabad',
        'property_type': 'apartment',
        'listing_type': 'buy',
        'bedrooms': 2,
        'bathrooms': 2,
        'area_sqft': 1250,
        'amenities': 'parking, balcony, gym',
        'furnished': True,
        'is_featured': False,
        'status': 'available',
        'category': None,
    }

    def example_detail_url(path, model):
        object_id = model.objects.values_list('id', flat=True).first()
        if not object_id:
            return None
        return request.build_absolute_uri(path.format(id=object_id))

    return Response({
        'message': 'Smart Property Finder API',
        'auth': {
            'login': request.build_absolute_uri('/api-auth/login/'),
            'logout': request.build_absolute_uri('/api-auth/logout/'),
            'account': request.build_absolute_uri('/api/account/'),
            'change_password': request.build_absolute_uri('/api/account/change-password/'),
        },
        'account': {
            'profile': {
                'url': request.build_absolute_uri('/api/account/'),
                'methods': ['GET', 'PATCH', 'PUT'],
                'raw_data_examples': {
                    'PATCH': {
                        'username': 'new_username',
                        'email': 'user@example.com',
                        'first_name': 'First',
                        'last_name': 'Last',
                    },
                },
            },
            'password': {
                'url': request.build_absolute_uri('/api/account/change-password/'),
                'method': 'POST',
                'raw_data': {
                    'current_password': 'old-password',
                    'new_password': 'new-secure-password',
                    'new_password2': 'new-secure-password',
                },
            },
        },
        'endpoints': {
            'properties': {
                'list_create': request.build_absolute_uri('/api/properties/'),
                'detail_pattern': '/api/properties/<id>/',
                'example_detail': example_detail_url('/api/properties/{id}/', Property),
                'methods': {
                    'GET': 'List properties or retrieve one property.',
                    'POST': 'Create a property at /api/properties/.',
                    'POST_DETAIL': 'Partially update a property at /api/properties/{id}/.',
                    'PUT': 'Replace a property at /api/properties/{id}/.',
                    'PATCH': 'Partially update a property at /api/properties/{id}/.',
                    'DELETE': 'Delete a property at /api/properties/{id}/.',
                },
                'raw_data_examples': {
                    'POST': property_payload,
                    'PUT': property_payload,
                    'PATCH': {
                        'price': '7200000.00',
                        'status': 'available',
                    },
                    'DELETE': 'No raw body required.',
                },
                'extra_actions': {
                    'toggle_wishlist': {
                        'url_pattern': '/api/properties/<id>/toggle_wishlist/',
                        'method': 'POST',
                        'raw_data': 'No raw body required.',
                    },
                },
            },
            'property_images': {
                'list_create': request.build_absolute_uri('/api/property-images/'),
                'detail_pattern': '/api/property-images/<id>/',
                'example_detail': example_detail_url('/api/property-images/{id}/', PropertyImage),
                'methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
                'raw_data_examples': {
                    'POST': {
                        'property': 1,
                        'image': 'Upload file with multipart/form-data.',
                        'caption': 'Front view',
                    },
                    'PATCH': {
                        'caption': 'Updated front view',
                    },
                },
            },
            'wishlist': {
                'list_create': request.build_absolute_uri('/api/wishlist/'),
                'detail_pattern': '/api/wishlist/<id>/',
                'example_detail': example_detail_url('/api/wishlist/{id}/', Wishlist),
                'methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
                'raw_data_examples': {
                    'POST': {'property': 1},
                    'DELETE': 'No raw body required.',
                },
            },
            'contact_messages': {
                'list_create': request.build_absolute_uri('/api/contact-messages/'),
                'detail_pattern': '/api/contact-messages/<id>/',
                'example_detail': example_detail_url('/api/contact-messages/{id}/', ContactMessage),
                'methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
                'raw_data_examples': {
                    'POST': {
                        'property': 1,
                        'name': 'Your Name',
                        'email': 'you@example.com',
                        'phone': '9876543210',
                        'message': 'I am interested in this property.',
                    },
                },
            },
            'categories': {
                'list': request.build_absolute_uri('/api/categories/'),
                'detail_pattern': '/api/categories/<id>/',
                'example_detail': example_detail_url('/api/categories/{id}/', Category),
                'methods': ['GET'],
            },
            'agents': {
                'list': request.build_absolute_uri('/api/agents/'),
                'detail_pattern': '/api/agents/<id>/',
                'example_detail': example_detail_url('/api/agents/{id}/', Agent),
                'methods': ['GET'],
            },
        },
    })


class CurrentUserAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = CurrentUserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = CurrentUserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def put(self, request):
        serializer = CurrentUserSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class PasswordChangeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        update_session_auth_hash(request, request.user)
        return Response({'detail': 'Password changed successfully.'}, status=status.HTTP_200_OK)


class IsOwnerOrStaffOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        owner = getattr(obj, 'owner', None) or getattr(getattr(obj, 'property', None), 'owner', None)
        return request.user.is_authenticated and (request.user.is_staff or owner == request.user)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class AgentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Agent.objects.select_related('user').all()
    serializer_class = AgentSerializer
    permission_classes = [permissions.AllowAny]


class PropertyViewSet(viewsets.ModelViewSet):
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrStaffOrReadOnly]

    def get_queryset(self):
        queryset = Property.objects.select_related('owner', 'category').prefetch_related('images')
        user = self.request.user

        if not user.is_authenticated:
            queryset = queryset.filter(approval_status='approved')
        elif not user.is_staff:
            queryset = queryset.filter(Q(approval_status='approved') | Q(owner=user))

        q = self.request.query_params.get('q', '').strip()
        listing = self.request.query_params.get('listing_type', '').strip()
        property_type = self.request.query_params.get('property_type', '').strip()
        location = self.request.query_params.get('location', '').strip()
        min_price = self.request.query_params.get('min_price', '').strip()
        max_price = self.request.query_params.get('max_price', '').strip()
        bedrooms = self.request.query_params.get('bedrooms', '').strip()
        bathrooms = self.request.query_params.get('bathrooms', '').strip()
        furnished = self.request.query_params.get('furnished', '').strip()
        sort = self.request.query_params.get('sort', 'newest').strip()

        if q:
            queryset = queryset.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(location__icontains=q))
        if listing:
            queryset = queryset.filter(listing_type=listing)
        if property_type:
            queryset = queryset.filter(property_type=property_type)
        if location:
            queryset = queryset.filter(location__icontains=location)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if bedrooms:
            queryset = queryset.filter(bedrooms__gte=bedrooms)
        if bathrooms:
            queryset = queryset.filter(bathrooms__gte=bathrooms)
        if furnished == 'yes':
            queryset = queryset.filter(furnished=True)
        elif furnished == 'no':
            queryset = queryset.filter(furnished=False)

        if sort == 'price_low':
            return queryset.order_by('price')
        if sort == 'price_high':
            return queryset.order_by('-price')
        if sort == 'area':
            return queryset.order_by('-area_sqft')
        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        approval_status = 'approved' if self.request.user.is_staff else 'pending'
        serializer.save(owner=self.request.user, approval_status=approval_status)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def toggle_wishlist(self, request, pk=None):
        prop = self.get_object()
        item, created = Wishlist.objects.get_or_create(user=request.user, property=prop)
        if not created:
            item.delete()
            return Response({'saved': False}, status=status.HTTP_200_OK)
        return Response({'saved': True}, status=status.HTTP_201_CREATED)


class PropertyImageViewSet(viewsets.ModelViewSet):
    serializer_class = PropertyImageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrStaffOrReadOnly]

    def get_queryset(self):
        queryset = PropertyImage.objects.select_related('property', 'property__owner').order_by('id')
        user = self.request.user

        if not user.is_authenticated:
            queryset = queryset.filter(property__approval_status='approved')
        elif not user.is_staff:
            queryset = queryset.filter(Q(property__approval_status='approved') | Q(property__owner=user))

        property_id = self.request.query_params.get('property')
        if property_id:
            queryset = queryset.filter(property_id=property_id)
        return queryset

    def perform_create(self, serializer):
        prop = serializer.validated_data['property']
        if not (self.request.user.is_staff or prop.owner == self.request.user):
            raise PermissionDenied('You can only add images to your own properties.')
        serializer.save()


class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).select_related('property', 'property__owner')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ContactMessageViewSet(viewsets.ModelViewSet):
    serializer_class = ContactMessageSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        return ContactMessage.objects.select_related('property').all()

APARTMENT_PLAN_SHOWCASE = [
    {
        'area': '110,4 SQ.M.',
        'rooms': '3-BEDROOM',
        'title': 'A spacious, comfortable apartment with an open balcony',
        'summary': 'A clean top-down 2D floor plan view revealing room depth, circulation, balcony placement, and how the kitchen, living, and private rooms connect.',
        'image': 'img/apartments/apartment-plan-open-balcony-top.png',
        'alt': '2D apartment plan with open balcony',
    },
    {
        'area': '110,4 SQ.M.',
        'rooms': '3-BEDROOM',
        'title': 'Open balcony layout from a 3D angle',
        'summary': 'The angled 3D view reveals room depth, circulation, balcony placement, and how the kitchen, living, and private rooms connect.',
        'image': 'img/apartments/apartment-plan-open-balcony-3d.png',
        'alt': 'Three dimensional apartment plan with open balcony',
    },
    {
        'area': '123,8 SQ.M.',
        'rooms': '4-BEDROOM',
        'title': 'Comfortable apartment for large families',
        'summary': 'A complete top-down 2D floor plan cutaway showing the entry sequence, room scale, balcony volume, and furniture placement for everyday use.',
        'image': 'img/apartments/apartment-plan-family-top.png',
        'alt': '2D four bedroom apartment floor plan',
    },
    {
        'area': '123,8 SQ.M.',
        'rooms': '4-BEDROOM',
        'title': 'Comfortable apartment for large families',
        'summary': 'A detailed 3D cutaway showing the entry sequence, room scale, balcony volume, and furniture placement for everyday use.',
        'image': 'img/apartments/apartment-plan-family-3d.png',
        'alt': 'Three dimensional four bedroom apartment floor plan',
    },
]


def property_list(request, listing_preset='', property_type_preset='', page_title='Curated listings', page_kicker='Explore all property', show_apartment_plans=False):
    qs = Property.objects.filter(approval_status='approved')
    q = request.GET.get('q','').strip()
    listing = listing_preset or request.GET.get('listing_type','')
    ptype = property_type_preset or request.GET.get('property_type','')
    location = request.GET.get('location','').strip()
    min_price = request.GET.get('min_price','')
    max_price = request.GET.get('max_price','')
    bedrooms = request.GET.get('bedrooms','')
    bathrooms = request.GET.get('bathrooms','')
    furnished = request.GET.get('furnished','')
    sort = request.GET.get('sort','newest')

    if q:
        qs = qs.filter(Q(title__icontains=q)|Q(description__icontains=q)|Q(location__icontains=q))
    if listing: qs = qs.filter(listing_type=listing)
    if ptype: qs = qs.filter(property_type=ptype)
    if location: qs = qs.filter(location__icontains=location)
    if min_price: qs = qs.filter(price__gte=min_price)
    if max_price: qs = qs.filter(price__lte=max_price)
    if bedrooms: qs = qs.filter(bedrooms__gte=bedrooms)
    if bathrooms: qs = qs.filter(bathrooms__gte=bathrooms)
    if furnished == 'yes': qs = qs.filter(furnished=True)
    elif furnished == 'no': qs = qs.filter(furnished=False)
    if sort == 'price_low':
        qs = qs.order_by('price')
    elif sort == 'price_high':
        qs = qs.order_by('-price')
    elif sort == 'area':
        qs = qs.order_by('-area_sqft')
    else:
        qs = qs.order_by('-created_at')

    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = list(Wishlist.objects.filter(user=request.user).values_list('property_id', flat=True))

    featured = Property.objects.filter(approval_status='approved', is_featured=True)[:6]
    if not featured:
        featured = Property.objects.filter(approval_status='approved')[:6]
    paginator = Paginator(qs, 9)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'properties/list.html', {
        'properties': page_obj.object_list,
        'page_obj': page_obj,
        'featured_properties': featured,
        'total_properties': Property.objects.filter(approval_status='approved').count(),
        'filters': {
            **request.GET.dict(),
            'listing_type': listing,
            'property_type': ptype,
        },
        'wishlist_ids': wishlist_ids,
        'page_title': page_title,
        'page_kicker': page_kicker,
        'reset_url': request.path,
        'apartment_plan_showcase': APARTMENT_PLAN_SHOWCASE if show_apartment_plans else [],
    })

def buy_properties(request):
    return property_list(
        request,
        listing_preset='buy',
        page_title='Homes for sale',
        page_kicker='Buy properties',
    )

def rent_properties(request):
    return property_list(
        request,
        listing_preset='rent',
        page_title='Homes for rent',
        page_kicker='Rent properties',
    )

def villa_properties(request):
    return property_list(
        request,
        property_type_preset='villa',
        page_title='Villa collection',
        page_kicker='Villa properties',
    )

def apartment_properties(request):
    return property_list(
        request,
        property_type_preset='apartment',
        page_title='Apartment collection',
        page_kicker='Apartment properties',
        show_apartment_plans=True,
    )

def house_properties(request):
    return property_list(
        request,
        property_type_preset='house',
        page_title='House collection',
        page_kicker='House properties',
    )

def commercial_properties(request):
    return property_list(
        request,
        property_type_preset='commercial',
        page_title='Commercial collection',
        page_kicker='Commercial properties',
    )

def land_properties(request):
    return property_list(
        request,
        property_type_preset='land',
        page_title='Land collection',
        page_kicker='Land properties',
    )

FLOOR_PLANS = [
    {
        'slug': 'master-plan',
        'label': 'Master Plan',
        'kicker': 'Site layout',
        'title': 'Master Plan',
        'summary': 'A complete community-level view with entry court, residential blocks, clubhouse, pool, garden courts, visitor parking, and service access.',
        'kind': 'master',
        'stats': ['5.8 acre site', '4 residential blocks', 'Central clubhouse', 'Two entry points'],
    },
    {
        'slug': 'building-a',
        'label': 'Building A',
        'kicker': 'Floor layout',
        'title': 'Building A Floor Plan',
        'summary': 'Linear premium apartment block with two lift cores, wide shared corridor, east and west facing homes, and efficient service zones.',
        'kind': 'linear',
        'stats': ['2 lift cores', '12 homes per floor', '2 and 3 BHK mix', 'Double-loaded corridor'],
    },
    {
        'slug': 'building-b',
        'label': 'Building B',
        'kicker': 'Floor layout',
        'title': 'Building B Floor Plan',
        'summary': 'Compact cluster plan with central lift lobby, corner apartments, balanced daylight, and short walking distances to every unit.',
        'kind': 'cluster',
        'stats': ['Central lobby', '8 homes per floor', 'Corner balconies', 'Optimized circulation'],
    },
    {
        'slug': 'building-g',
        'label': 'Building G',
        'kicker': 'Floor layout',
        'title': 'Building G Floor Plan',
        'summary': 'Garden-facing apartment block with generous living rooms, repeated modular units, and direct access toward landscaped open space.',
        'kind': 'linear',
        'stats': ['Garden-facing homes', '10 homes per floor', 'Wide balconies', 'Service stair access'],
    },
    {
        'slug': 'building-l',
        'label': 'Building L',
        'kicker': 'Floor layout',
        'title': 'Building L Floor Plan',
        'summary': 'Large-format wing plan with two lift banks, long corridor spine, varied apartment sizes, and premium end units.',
        'kind': 'wing',
        'stats': ['2 lift banks', '14 homes per floor', 'Premium end units', 'Multiple unit sizes'],
    },
]

@login_required
def floor_plans(request, slug='master-plan'):
    active_plan = next((plan for plan in FLOOR_PLANS if plan['slug'] == slug), FLOOR_PLANS[0])
    return render(request, 'properties/floor_plans.html', {
        'floor_plans': FLOOR_PLANS,
        'active_plan': active_plan,
    })

@login_required
def property_detail(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    if prop.approval_status != 'approved':
        can_preview = request.user.is_authenticated and (prop.owner == request.user or request.user.is_staff)
        if not can_preview:
            return HttpResponseForbidden()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.property = prop
            msg.save()
            messages.success(request, 'Your inquiry has been sent to the agent.')
            return redirect('property_detail', pk=pk)
    else:
        form = ContactForm()
    in_wishlist = request.user.is_authenticated and Wishlist.objects.filter(user=request.user, property=prop).exists()
    similar = Property.objects.filter(approval_status='approved', property_type=prop.property_type).exclude(pk=prop.pk)[:3]
    agent_profile = getattr(prop.owner, 'agent_profile', None)
    seller_phone = (agent_profile.phone if agent_profile and agent_profile.phone else '+91 98765 43210')
    seller_address = prop.location if 'india' in prop.location.lower() else f'{prop.location}, India'
    return render(request, 'properties/detail.html', {
        'property': prop,
        'form': form,
        'in_wishlist': in_wishlist,
        'similar_properties': similar,
        'seller_phone': seller_phone,
        'seller_address': seller_address,
    })

@login_required
def property_create(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST)
        if form.is_valid():
            prop = form.save(commit=False)
            prop.owner = request.user
            if not request.user.is_staff:
                prop.approval_status = 'pending'
            prop.save()
            for f in request.FILES.getlist('images'):
                PropertyImage.objects.create(property=prop, image=f)
            messages.success(request, 'Property created.')
            return redirect('property_detail', pk=prop.pk)
    else:
        form = PropertyForm()
    return render(request, 'properties/form.html', {'form': form, 'title': 'Create Property'})

@login_required
def property_update(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    if prop.owner != request.user and not request.user.is_staff:
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = PropertyForm(request.POST, instance=prop)
        if form.is_valid():
            form.save()
            for f in request.FILES.getlist('images'):
                PropertyImage.objects.create(property=prop, image=f)
            messages.success(request, 'Property updated.')
            return redirect('property_detail', pk=prop.pk)
    else:
        form = PropertyForm(instance=prop)
    return render(request, 'properties/form.html', {'form': form, 'title': 'Edit Property', 'property': prop})

@login_required
def property_delete(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    if prop.owner != request.user and not request.user.is_staff:
        return HttpResponseForbidden()
    if request.method == 'POST':
        prop.delete()
        messages.success(request, 'Property deleted.')
        return redirect('my_properties')
    return render(request, 'properties/confirm_delete.html', {'property': prop})

@login_required
def add_image(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    if prop.owner != request.user and not request.user.is_staff:
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = PropertyImageForm(request.POST, request.FILES)
        if form.is_valid():
            img = form.save(commit=False)
            img.property = prop
            img.save()
            return redirect('property_detail', pk=pk)
    else:
        form = PropertyImageForm()
    return render(request, 'properties/add_image.html', {'form': form, 'property': prop})

@login_required
def my_properties(request):
    qs = Property.objects.filter(owner=request.user)
    return render(request, 'properties/my_properties.html', {'properties': qs})

@login_required
def wishlist_view(request):
    items = Wishlist.objects.filter(user=request.user).select_related('property', 'property__owner')
    saved_ids = list(items.values_list('property_id', flat=True))
    suggested_properties = Property.objects.filter(approval_status='approved').exclude(pk__in=saved_ids)[:3]
    return render(request, 'properties/wishlist.html', {
        'items': items,
        'saved_ids': saved_ids,
        'suggested_properties': suggested_properties,
    })

@login_required
def wishlist_toggle(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    w, created = Wishlist.objects.get_or_create(user=request.user, property=prop)
    if not created:
        w.delete()
        messages.info(request, 'Removed from wishlist.')
    else:
        messages.success(request, 'Added to wishlist.')
    return redirect(request.META.get('HTTP_REFERER', 'property_list'))
