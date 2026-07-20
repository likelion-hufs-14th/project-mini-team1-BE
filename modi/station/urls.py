from django.urls import path
from .views import StationCandidateView

urlpatterns = [
    path('candidates/', StationCandidateView.as_view(), name='station_candidates'),
]