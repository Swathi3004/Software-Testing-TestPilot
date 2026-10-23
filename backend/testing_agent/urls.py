from django.urls import path
from .views import health_check, generate_tests, suggest_fix

urlpatterns = [
    path('health/', health_check, name='health-check'),
    path('generate-tests/', generate_tests, name='generate-tests'),
    path('suggest-fix/', suggest_fix, name='suggest-fix'),
]