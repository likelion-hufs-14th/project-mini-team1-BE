from django.urls import path
from . import views

urlpatterns = [
    path('appointments/', views.appointment_create, name='appointment_create'),
    path('appointments/<str:appointment_code>/status/', views.appointment_status, name='appointment_status'),
    path('appointments/<str:appointment_code>/candidates/', views.appointment_candidates, name='appointment_candidates'),
]