from django.urls import path
from .views import health_check, generate_tests

urlpatterns = [
    path('health/', health_check, name='health-check'),
    path('generate-tests/', generate_tests, name='generate-tests'),
]