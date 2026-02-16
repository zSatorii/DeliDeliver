from django.urls import path
from .views import registro_usuario
from . import views

urlpatterns = [
    path('registroemp/', views., name='registro_empresa'),
    path('registrouser/', views., name='registro_usuario'),
    path('dashboardemp/', views., name='dashboard_empresa'),
    path('dashboarduser/', views., name='dashboard_usuario'),
]