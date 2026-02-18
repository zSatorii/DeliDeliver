from django.urls import path
from . import views

urlpatterns = [

    # vendedores de los artículos
    path('articulos/', views.articulo, name='listar_articulos'),
    path('articulos/crear/', views.crear_articulo, name='crear_articulo'),
    path('articulos/editar/<str:articulo_id>/', views.editar_articulo, name='editar_articulo'),
    path('articulos/eliminar/<str:articulo_id>/', views.eliminar_Venta, name='eliminar_articulo'),

    # clientes
    path('compradores/', views.listar_compradores, name='listar_compradores'),
    path('compradores/crear/', views.crear_comprador, name='crear_comprador'),
    path('compradores/editar/<str:comprador_id>/', views.editar_comprador, name='editar_comprador'),
    path('compradores/eliminar/<str:comprador_id>/', views.eliminar_comprador, name='eliminar_comprador'),

    #Pedidos
    path('pedidos/', views.listar_pedidos, name='listar_pedidos'),
    path('pedidos/crear/', views.crear_pedido, name='crear_pedido'),
    path('pedidos/editar/<str:pedido_id>/', views.editar_pedido, name='editar_pedido'),
    path('pedidos/eliminar/<str:pedido_id>/', views.eliminar_pedido, name='eliminar_pedido'),

]
