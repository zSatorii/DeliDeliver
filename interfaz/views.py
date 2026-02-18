from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from firebase_admin import firestore, auth
from delideliver.firebase_config import initialize_firebase
from functools import wraps
import requests
import os
from datetime import datetime


def home(request):
    return render(request, 'main.html')

# Inicializar Firebase
db = initialize_firebase()

def registro_usuario(request):
    mensaje = None
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        username = request.POST.get('username')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        password = request.POST.get('password')
        try:
            # Vamos a crear en firebase auth
            user = auth.create_user(
                email = email,
                password = password
            )

            # Crear en firestore

            db.collection('clientes').document(user.uid).set({
                'nombre': nombre,
                'apellido': apellido,
                'telefono': telefono,
                'username': username,
                'fecha_nacimiento': fecha_nacimiento,
                'email' : email,
                'uid' : user.uid,
                'rol' : 'cliente',
                'fecha_registro' : firestore.SERVER_TIMESTAMP,
            })

            mensaje = f"Usuario registrado correctamente con UID: {user.uid}"

        except Exception as e:
            mensaje = f"Error: {e}"

    return render(request, 'register_user.html', {'mensaje': mensaje})

def registro_empresa(request):
    mensaje = None
    if request.method == 'POST':
        NIT = request.POST.get('nit'),
        telefono = request.POST.get('telefono'),
        direccion = request.POST.get('direccion'),
        ciudad = request.POST.get('ciudad'),
        departamento = request.POST.get('departamento'),
        descripcion = request.POST.get('descripcion'),
        nombre = request.POST.get('nombre'),
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            # Vamos a crear en firebase auth
            user = auth.create_user(
                email = email,
                password = password
            )

            # Crear en firestore

            db.collection('empresas').document(user.uid).set({
                'nombre': nombre,
                'email' : email,
                'NIT': NIT,
                'telefono': telefono,
                'direccion': direccion,
                'ciudad': ciudad,
                'departamento': departamento,
                'descripcion': descripcion,
                'uid' : user.uid,
                'rol' : 'Empresa',
                'fecha_registro' : firestore.SERVER_TIMESTAMP,
            })

            mensaje = f"Usuario registrado correctamente con UID: {user.uid}"

        except Exception as e:
            mensaje = f"Error: {e}"

    return render(request, 'register_emp.html', {'mensaje': mensaje})

def login_required_firebase(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        uid = request.session.get('uid')
        rol = request.session.get('rol')
        if not uid:
            messages.error(request, "❌ Debes iniciar sesión para acceder.")
            if rol == 'Empresa':
                return redirect('login_empresa')
            else:
                return redirect('login_cliente')
        return view_func(request, *args, **kwargs)
    return wrapper

def iniciar_Sesion_cliente(request):
    
    # Si ya esta loggeado, lo redirigimos al dashboard
    if 'uid' in request.session:
        return redirect('dashboard_cliente')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        api_key = os.getenv ('FIREBASE_WEB_API_KEY')

        #Endopoint oficial de google para el login
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"

        payload = {
            "email" : email,
            "password" : password,
            "returnSecureToken" : True
        }

        try:
            # Peticion http al servicio de autenticacion (endpoint)
            response = requests.post(url, json=payload)
            data = response.json()
            
            if response.status_code == 200:
                # ✅ Exito. Vamos a almacenar los datos en la sesion
                request.session['uid'] = data['localId']
                request.session['email'] = data['email']
                request.session['rol'] = 'cliente'
                request.session['password'] = data['password']
                messages.success(request, f"✅ Bienvenido a nuestro sistema")
                return redirect('dashboard_cliente')
            else:
                # Error: Analizamos el error
                error_msg = data.get('error', ()).get('message', 'UNKNOWN_ERROR')
                errores_comunes = {
                    'INVALID_LOGIN_CREDENTIALS' : 'La contraseña es incorrecta o el correo no es valido',
                    'EMAIL_NOT_FOUND' : 'Este correo no esta registrado en el sistema',
                    'USER_DISABLES' : 'Esta cuenta ha sido inhabilitada por el administrador.',
                    'TOO_MANY_ATTEMPTS_TRY_LATER' : 'Demasiados intentos fallidos espere unos minutos'
                }
                mensaje_usuario = errores_comunes.get(error_msg, "❌ Error de autenticacion, revise sus datos")
                messages.error(request, mensaje_usuario)
        except requests.exceptions.RequestException as e:
            messages.error(request, f"❌ Error de conexion en el servidor")
        except Exception as e:
            messages.error(request, f"❌ Error inesperado: {str(e)}")
    return render(request, 'login_cliente.html')

def iniciar_Sesion_empresa(request):
    
    # Si ya esta loggeado, lo redirigimos al dashboard
    if 'uid' in request.session:
        return redirect('dashboard_empresa')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        api_key = os.getenv ('FIREBASE_WEB_API_KEY')

        #Endopoint oficial de google para el login
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"

        payload = {
            "email" : email,
            "password" : password,
            "returnSecureToken" : True
        }

        try:
            # Peticion http al servicio de autenticacion (endpoint)
            response = requests.post(url, json=payload)
            data = response.json()
            
            if response.status_code == 200:
                # ✅ Exito. Vamos a almacenar los datos en la sesion
                request.session['uid'] = data['localId']
                request.session['email'] = data['email']
                request.session['rol'] = 'Empresa'
                request.session['password'] = data['password']
                messages.success(request, f"✅ Bienvenido a nuestro sistema")
                return redirect('dashboard_empresa')
            else:
                # Error: Analizamos el error
                error_msg = data.get('error', ()).get('message', 'UNKNOWN_ERROR')
                errores_comunes = {
                    'INVALID_LOGIN_CREDENTIALS' : 'La contraseña es incorrecta o el correo no es valido',
                    'EMAIL_NOT_FOUND' : 'Este correo no esta registrado en el sistema',
                    'USER_DISABLES' : 'Esta cuenta ha sido inhabilitada por el administrador.',
                    'TOO_MANY_ATTEMPTS_TRY_LATER' : 'Demasiados intentos fallidos espere unos minutos'
                }
                mensaje_usuario = errores_comunes.get(error_msg, "❌ Error de autenticacion, revise sus datos")
                messages.error(request, mensaje_usuario)
        except requests.exceptions.RequestException as e:
            messages.error(request, f"❌ Error de conexion en el servidor")
        except Exception as e:
            messages.error(request, f"❌ Error inesperado: {str(e)}")
    return render(request, 'login_empresa.html')

def cerrar_sesion(request):
    # Limpio sesion y redirijo
    request.session.flush()
    messages.info(request, "Has cerrado sesion correctamente")
    return redirect('home')

@login_required_firebase # Verifica que el usuario esta loggeado
def dashboard_empresa(request):
    """
    Panel principal. Solo es accesible si el decorador lo permite.
    Recuperamos los datos desde firestore
    """
    uid = request.session.get('uid')
    datos_usuario = {}

    try:
        #  Consultar firestore usando el SDK admin
        doc_ref = db.collection('empresas').document(uid)
        doc = doc_ref.get()

        if doc.exists:
            datos_usuario = doc.to_dict()
        else: 
            # Si entra en el auth pero no tiene un perfil en firestore, manejo el caso
            datos_usuario = {
                'email' : request.session.get('email'),
                'uid' : request.session.get('uid'),
                'rol' : request.session.get('rol'),
                'fecha_registro' : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
    except Exception as e:
        messages.error(request, f"Error al cargar los datos de la BD: (e)")
    return render(request, 'dashboardemp.html', {'datos': datos_usuario})

@login_required_firebase # Verifica que el usuario esta loggeado
def dashboard_cliente(request):
    """
    Panel principal. Solo es accesible si el decorador lo permite.
    Recuperamos los datos desde firestore
    """
    uid = request.session.get('uid')
    datos_usuario = {}

    try:
        #  Consultar firestore usando el SDK admin
        doc_ref = db.collection('clientes').document(uid)
        doc = doc_ref.get()

        if doc.exists:
            datos_usuario = doc.to_dict()
        else: 
            # Si entra en el auth pero no tiene un perfil en firestore, manejo el caso
            datos_usuario = {
                'email' : request.session.get('email'),
                'uid' : request.session.get('uid'),
                'rol' : request.session.get('rol'),
                'fecha_registro' : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
    except Exception as e:
        messages.error(request, f"Error al cargar los datos de la BD: (e)")
    return render(request, 'dashboarduser.html', {'datos': datos_usuario})


# CRUD para los artículos/Productos de las empresas/vendedores en el delivery

@login_required_firebase
def articulo(request):

    """
    READ: 
    """

    uid = request.session.get('uid')
    articulos = []

    try:
        #Filtrar por el uid del usuario
        docs = db.collection('articulos').stream()
        for doc in docs:
            articulo = doc.to_dict()
            articulo['id'] = doc.id
            articulos.append(articulo)
    except Exception as e:
        messages.error(request, f"❌Hubo un error al obtener los artículos {e}")
    return render(request, 'articulos/listar.html', {'articulos' : articulos})
    

@login_required_firebase
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
                'dirEmpresa' : nueva_dirEmpresa,
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

"""
READ DE PEDIDOS:
"""

@login_required_firebase
def listar_pedidos(request):

    pedidos = []
    uid = request.session.get('uid')

    try:
        docs = db.collection('pedidos').where('cliente_id', '==', uid).stream()

        for doc in docs:
            pedido = doc.to_dict()
            pedido['id'] = doc.id
            pedidos.append(pedido)

    except Exception as e:
        messages.error(request, f"❌ Error al obtener pedidos: {e}")

    return render(request, 'pedidos/listar.html', {
        'pedidos': pedidos
    })

"""
CREATE DE PEDIDOS
"""

@login_required_firebase
def crear_pedido(request):

    articulos = []

    try:
        docs = db.collection('articulos').stream()

        for doc in docs:
            articulo = doc.to_dict()
            articulo['id'] = doc.id
            articulos.append(articulo)

    except Exception as e:
        messages.error(request, f"❌ Error al cargar artículos: {e}")

    if request.method == 'POST':

        articulo_id = request.POST.get('articulo')
        cantidad = int(request.POST.get('cantidad'))
        direccion = request.POST.get('direccion')
        metodo_pago = request.POST.get('metodo_pago')
        uid = request.session.get('uid')

        try:
            articulo_ref = db.collection('articulos').document(articulo_id)
            articulo = articulo_ref.get()

            if not articulo.exists:
                messages.error(request, "❌ El artículo no existe")
                return redirect('crear_pedido')

            articulo_data = articulo.to_dict()
            precio = float(articulo_data.get('Total', 0))

            total = precio * cantidad

            db.collection('pedidos').add({
                'cliente_id': uid,
                'articulo_id': articulo_id,
                'nomArticulo': articulo_data.get('nomArticulo'),
                'precio_unitario': precio,
                'cantidad': cantidad,
                'total': total,
                'direccion': direccion,
                'metodo_pago': metodo_pago,
                'estado': 'Pendiente',
                'fecha_creacion': firestore.SERVER_TIMESTAMP
            })

            messages.success(request, "✅ Pedido realizado correctamente")
            return redirect('listar_pedidos')

        except Exception as e:
            messages.error(request, f"❌ Error al crear pedido: {e}")

    return render(request, 'pedidos/form.html', {
        'articulos': articulos
    })


"""
UPDATE DE PEDIDOS
"""

@login_required_firebase
def editar_pedido(request, pedido_id):

    pedido_ref = db.collection('pedidos').document(pedido_id)

    try:
        doc = pedido_ref.get()

        if not doc.exists:
            messages.error(request, "❌ El pedido no existe")
            return redirect('listar_pedidos')

        pedido_data = doc.to_dict()

        if request.method == 'POST':

            nueva_cantidad = int(request.POST.get('cantidad'))
            nueva_direccion = request.POST.get('direccion')
            nuevo_metodo_pago = request.POST.get('metodo_pago')

            precio = float(pedido_data.get('precio_unitario', 0))
            nuevo_total = precio * nueva_cantidad

            pedido_ref.update({
                'cantidad': nueva_cantidad,
                'total': nuevo_total,
                'direccion': nueva_direccion,
                'metodo_pago': nuevo_metodo_pago,
                'fecha_actualizacion': firestore.SERVER_TIMESTAMP
            })

            messages.success(request, "✅ Pedido actualizado correctamente")
            return redirect('listar_pedidos')

    except Exception as e:
        messages.error(request, f"❌ Error al editar pedido: {e}")
        return redirect('listar_pedidos')

    return render(request, 'pedidos/editar.html', {
        'pedido': pedido_data,
        'id': pedido_id
    })

"""
DELETE DE PEDIDOS
"""

@login_required_firebase
def eliminar_pedido(request, pedido_id):

    pedido_ref = db.collection('pedidos').document(pedido_id)

    try:
        doc = pedido_ref.get()

        if not doc.exists:
            messages.error(request, "❌ El pedido no existe")
            return redirect('listar_pedidos')

        pedido_ref.delete()

        messages.success(request, "✅ Pedido eliminado correctamente")

    except Exception as e:
        messages.error(request, f"❌ Error al eliminar pedido: {e}")

    return redirect('listar_pedidos')
