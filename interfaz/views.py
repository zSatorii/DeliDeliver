from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from firebase_admin import firestore, auth
from delideliver.firebase_config import initialize_firebase
from functools import wraps
import requests
import os
from datetime import datetime

# Inicializar Firebase
db = initialize_firebase()

def registro_usuario(request):
    mensaje = None
    if request.method == 'POST':
        nombre = request.POST.get('nombre'),
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            # Vamos a crear en firebase auth
            user = auth.create_user(
                nombre = nombre,
                email = email,
                password = password
            )

            # Crear en firestore

            db.collection('clientes').document(user.uid).set({
                'nombre': nombre,
                'email' : email,
                'uid' : user.uid,
                'rol' : 'cliente',
                'fecha_registro' : firestore.SERVER_TIMESTAMP,
            })

            mensaje = f"Usuario registrado correctamente con UID: {user.uid}"

        except Exception as e:
            mensaje = f"Error: {e}"

    return render(request, 'registro_cliente.html', {'mensaje': mensaje})

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

def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'user_id' not in request.session:
            messages.error(request, "❌ Debes iniciar sesión para acceder a esta página.")
            return redirect('login')
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
                request.session['password'] = data['password']
                messages.success(request, f"✅ Bienvenido a nuestro sistema")
                return redirect('dashboard_usuario')
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

def cerrar_sesion(request):
    # Limpio sesion y redirijo
    request.session.flush()
    messages.info(request, "Has cerrado sesion correctamente")
    return redirect('login')