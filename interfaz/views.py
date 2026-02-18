from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from firebase_admin import auth, firestore
from delideliver.firebase_config import initialize_firebase
from functools import wraps
import requests
import os
from datetime import datetime


db = initialize_firebase()

# logica para el inicio de sesión del cliente

def login_required_firebase(view_func):
    #este decorador personalizado va a proteger las vistas si el usuario no ha iniciado sesion si no existe le UID, lo enviara a iniciar sesion
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'uid' not in request.session:
            messages.warning(request, "Acceso denegado, no has iniciado sesion ❌")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


# CRUD para los artículos/Productos de las empresas/vendedores en el delivery

@login_required_firebase #Verifica que el usuario este logueado
def articulo(request):

    """
    READ: 
    """

    uid = request.session.get('uid')
    articulos = []

    try:
        #Filtrar por el uid del usuario
        docs = db.collection('articulos').where()
        for doc in docs:
            articulo = doc.to_dict()
            articulo['id'] = doc.id
            articulos.append(articulo)
    except Exception as e:
        messages.error(request, f"❌Hubo un error al obtener los artículos {e}")
    return render(request, 'articulos/listar.html', {'articulos' : articulos})
    
@login_required_firebase #Verifica que este logueado
def crear_articulo(request):
    """
    CREATE: Recibimos los datos del formulario anterior y lo almacenamos según la info del artículo
    """
    if (request.method == 'POST'):
        nomArticulo = request.POST.get('nomArticulo')
        descripcion = request.POST.get('descripcion')
        dirEmpresa = request.POST.get('dirEmpresa')
        descuento = request.POST.get('descuento')
        total = request.POST.get('total')
        uid = request.session.get('uid')

        try:
            db.collection('articulos').add({
                'nomArticulo' : nomArticulo,
                'descripcion': descripcion,
                'estado' : 'Unidades disponibles',
                'dirEmpresa' : dirEmpresa,
                'descuento' : descuento,
                'Total' : total,
                'usuario_id' : uid,
                'fecha_creacion' : firestore.SERVER_TIMESTAMP
            })
            messages.success(request, "✅Artículo a comercializar añadido con éxito")
        except Exception as e:
            messages.error(request, f"Eror al añadir el artículo {e}")
    return render(request, 'articulos/form.html')
    
@login_required_firebase
def eliminar_Venta(request, articulo_id):
    """
    DELETE: Eliminar artículos
    """
    uid = request.session.get('uid')

    try:
        # Referencia al documento
        articulo_ref = db.collection('articulos').document(articulo_id)
        articulo = articulo_ref.get()

        # Verificamos que exista
        if not articulo.exists:
            messages.error(request, "❌El artículo no existe o no fue añadido.")
            return redirect('listar_articulos')

        # Verificamos que el artículo pertenezca a la empresa/vendedor
        if articulo.to_dict().get('usuario_id') != uid:
            messages.error(request, "❌No tienes permiso para eliminar este artículo.")
            return redirect('listar_articulos')

        # Eliminamos la tarea
        articulo_ref.delete()
        messages.success(request, "✅🤑Artículo eliminado correctamente.")

    except Exception as e:
        messages.error(request, f"❌Error al eliminar el artículo: {e}")

    return redirect('listar_articulos')

@login_required_firebase
def editar_articulo(request, articulo_id):
    """
    UPDATE: Va a recuperar los datos de la tarea especifica y actualiza los campos en Firebase
    """
    uid = request.session.get('uid')
    articulo_ref = db.collection('articulos').document(articulo_id)

    try:
        doc = articulo_ref.get()
        if not doc.exists:
            messages.error(request, "El artículo no existe")
            return redirect('listar_articulos')
        articulo_data = doc.to_dict()
        if articulo_data.get('usuario_id') != uid:
            messages.error(request, "❌No tienes permiso para editar la información de este producto")
            return redirect('listar_articulos')

        if request.method == 'POST':
            nuevo_nomArticulo = request.POST.get('nomArticulo')
            nueva_descripcion = request.POST.get('descripcion')
            nuevo_estado = request.POST.get('estado')
            nueva_dirEmpresa = request.POST.get('dirEmpresa')
            nuevo_desc = request.POST.get('descuento')
            nuevo_Total = request.POST.get('total')

            articulo_ref.update({
                'nomArticulo' : nuevo_nomArticulo,
                'descripcion' : nueva_descripcion,
                'estado' : nuevo_estado,
                'nueva_dirEmpresa' : nueva_dirEmpresa,
                'nuevo_desc' : nuevo_desc,
                'nuevo_total' : nuevo_Total,
                'fecha_actualizacion' : firestore.SERVER_TIMESTAMP
            })

            messages.success(request, "✅🤑Artículo actualizado correctamente")
            return redirect('listar_articulos')
    except Exception as e:
        messages.error(request, f"❌Error al editar el artículo: {e}")
        return redirect('listar_articulos')
    return render(request, 'articulos/editar.html', {
        'articulo': articulo_data, 
        'id': articulo_id})


"""
CRUD CLIENTE:

READ: El cliente va a confirmar los articulos a comprar y se va a mandar al firebase
"""

@login_required_firebase
def listar_compradores(request):

    compradores = []

    try:
        docs = db.collection('compradores').stream()

        for doc in docs:
            comprador = doc.to_dict()
            comprador['id'] = doc.id
            compradores.append(comprador)

    except Exception as e:
        messages.error(request, f"❌ Error al obtener compradores: {e}")

    return render(request, 'compradores/listar.html', {
        'compradores': compradores
    })

"""
CREATE: Recibimos los datos del formulario anterior y lo almacenamos según la info del artículo
"""

@login_required_firebase
def crear_comprador(request):

    if request.method == 'POST':

        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        telefono = request.POST.get('telefono')
        direccion = request.POST.get('direccion')
        uid = request.session.get('uid')

        try:
            db.collection('compradores').add({
                'nombre': nombre,
                'correo': correo,
                'telefono': telefono,
                'direccion': direccion,
                'usuario_id': uid,
                'fecha_creacion': firestore.SERVER_TIMESTAMP
            })

            messages.success(request, "✅ Comprador registrado correctamente")
            return redirect('listar_compradores')

        except Exception as e:
            messages.error(request, f"❌ Error al crear comprador: {e}")

    return render(request, 'compradores/form.html')

"""
UPDATE CLIENTE:
"""

@login_required_firebase
def editar_comprador(request, comprador_id):

    comprador_ref = db.collection('compradores').document(comprador_id)

    try:
        doc = comprador_ref.get()

        if not doc.exists:
            messages.error(request, "❌ El comprador no existe")
            return redirect('listar_compradores')

        comprador_data = doc.to_dict()

        if request.method == 'POST':

            nuevo_nombre = request.POST.get('nombre')
            nuevo_correo = request.POST.get('correo')
            nuevo_telefono = request.POST.get('telefono')
            nueva_direccion = request.POST.get('direccion')

            comprador_ref.update({
                'nombre': nuevo_nombre,
                'correo': nuevo_correo,
                'telefono': nuevo_telefono,
                'direccion': nueva_direccion,
                'fecha_actualizacion': firestore.SERVER_TIMESTAMP
            })

            messages.success(request, "✅ Comprador actualizado correctamente")
            return redirect('listar_compradores')

    except Exception as e:
        messages.error(request, f"❌ Error al editar comprador: {e}")
        return redirect('listar_compradores')

    return render(request, 'compradores/editar.html', {
        'comprador': comprador_data,
        'id': comprador_id
    })

"""
DELETE CLIENTE:
"""

@login_required_firebase
def eliminar_comprador(request, comprador_id):

    comprador_ref = db.collection('compradores').document(comprador_id)

    try:
        doc = comprador_ref.get()

        if not doc.exists:
            messages.error(request, "❌ El comprador no existe")
            return redirect('listar_compradores')

        comprador_ref.delete()

        messages.success(request, "✅ Comprador eliminado correctamente")

    except Exception as e:
        messages.error(request, f"❌ Error al eliminar comprador: {e}")

    return redirect('listar_compradores')
