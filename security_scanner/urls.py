from django.urls import path
from . import views

app_name = 'security_scanner'

urlpatterns = [
    path('', views.security_dashboard, name='dashboard'),
    path('vulnerability-report/', views.vulnerability_report, name='vulnerability_report'),
    path('test-cases/', views.test_cases, name='test_cases'),
    path('run-tests/', views.run_security_tests, name='run_tests'),
]