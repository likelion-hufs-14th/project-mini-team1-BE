from django.urls import path
from . import views

urlpatterns = [
    path('appointments/<str:appointment_code>/origins', views.origin_list, name='origin_list'),
]