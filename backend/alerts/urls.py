from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.HealthView.as_view(), name='health'),
    path('alerts/', views.AlertListView.as_view(), name='alert-list'),
    path('alerts/<int:pk>/', views.AlertDetailView.as_view(), name='alert-detail'),
    path('devices/register/', views.RegisterDeviceView.as_view(), name='device-register'),
    path('weather/', views.WeatherAlertView.as_view(), name='weather'),
]
