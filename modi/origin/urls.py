from django.urls import path
from . import views

urlpatterns = [
    path('appointments/<int:appointment_code>/origins', views.origin_list, name='origin_list'),
]