from django.urls import path
from .views import StationCandidateView

urlpatterns = [
    path('appointments/<str:appointment_code>/recommendations', StationCandidateView.as_view(), name='station_candidates'),
]