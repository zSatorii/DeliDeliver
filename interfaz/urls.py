from django.urls import path
from . import  views

urlpatterns = [
    path('registro_usuario/', views.registro_usuario, name='registro_usuario'),
    path('registro_empresa/', views.registro_empresa, name='registro_empresa'),
    path('login/', views.iniciar_Sesion_cliente, name='login'),
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),
]