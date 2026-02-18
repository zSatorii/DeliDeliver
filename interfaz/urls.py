from django.urls import path
from . import  views

urlpatterns = [
    path('registro_usuario/', views.registro_usuario, name='registro_usuario'),
    path('registro_empresa/', views.registro_empresa, name='registro_empresa'),
    path('login_cliente/', views.iniciar_Sesion_cliente, name='login_cliente'),
    path('login_empresa/', views.iniciar_Sesion_empresa, name='login_empresa'),
    path('dashboard_empresa/', views.dashboard_empresa, name='dashboard_empresa'),
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),
]