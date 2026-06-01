from django.urls import path
from . import views

urlpatterns = [
    path('', views.property_list, name='property_list'),
    path('buy/', views.buy_properties, name='buy_properties'),
    path('rent/', views.rent_properties, name='rent_properties'),
    path('villas/', views.villa_properties, name='villa_properties'),
    path('apartments/', views.apartment_properties, name='apartment_properties'),
    path('houses/', views.house_properties, name='house_properties'),
    path('commercials/', views.commercial_properties, name='commercial_properties'),
    path('lands/', views.land_properties, name='land_properties'),
    path('floor-plans/', views.floor_plans, name='floor_plans'),
    path('floor-plans/<slug:slug>/', views.floor_plans, name='floor_plan_detail'),
    path('property/<int:pk>/', views.property_detail, name='property_detail'),
    path('property/new/', views.property_create, name='property_create'),
    path('property/<int:pk>/edit/', views.property_update, name='property_update'),
    path('property/<int:pk>/delete/', views.property_delete, name='property_delete'),
    path('property/<int:pk>/add-image/', views.add_image, name='add_image'),
    path('my-properties/', views.my_properties, name='my_properties'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:pk>/', views.wishlist_toggle, name='wishlist_toggle'),
]
