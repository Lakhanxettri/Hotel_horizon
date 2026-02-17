from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('rooms/', views.rooms, name='rooms'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('booking/', views.booking_view, name='booking'),  # key!
    path('admin-bookings/', views.admin_booking_list, name='admin-bookings'),
    path('booking/<int:booking_id>/<str:action>/', views.update_booking_status, name='update-booking-status'),
    path('owner/bookings/', views.owner_bookings, name='owner_bookings'),
    
]

