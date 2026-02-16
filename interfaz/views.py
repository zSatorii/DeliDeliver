from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from firebase_admin import auth, firestore
from delideliver.firebase_config import initialize_firebase
from functools import wraps
import requests
import os
from datetime import datetime
from django.views.decorators.http import require_POST

db = initialize_firebase()

def registro_usuario(request):
    mensaje = None
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            #creamos un firestore auth
            user = auth.create_user(
                email=email,
                password=password
            )
            #crear en firestore

            db.collection('empresas').document(user.uid).set({
                'email' : email,
                'uid' : user.uid,
                'rol' : 'empresa',
                'fecha_registro' : firestore.SERVER_TIMESTAMP,
            })

            mensaje = f"👍🟩Usuario registrado correctamente con UID {user.uid}"
        except Exception as e:
            mensaje = f"❌❌❌Error {e}"
    return render(request, 'registro.html', {'mensaje' : mensaje})  
# logica para el inicio de sesion

def login_required_firebase(view_func):
    #este decorador personalizado va a proteger las vistas si el usuario no ha iniciado sesion si no existe le UID, lo enviara a iniciar sesion
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'uid' not in request.session:
            messages.warning(request, "Acceso denegado, no has iniciado sesion ❌")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def iniciar_sesion(request):

    #Si ya esta logueado, se redirige al dashboard

    if 'uid' in request.session:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        api_key = os.getenv ('FIREBASE_WEB_API_KEY')

        #EndPoint oficial de google para el login
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"

        payload = {
            "email" : email,
            "password" : password,
            "returnSecureToken" : True
        }


        try:
            #Petición HTTP
            response = requests.post(url, json=payload)
            data = response.json()
            # 👇 AGREGA ESTO TEMPORALMENTE
            print("STATUS:", response.status_code)
            print("DATA:", data)
            print("API KEY:", api_key)
            if response.status_code == 200:
                #✅ Exito: Vamos a almacenar los datos en la sesión
                request.session['uid'] = data['localId']
                request.session['email'] = data['email']
                request.session['idToken'] = data['idToken']
                
                messages.success(request, f"✅Bienvenido a nuestro sistema")
                return redirect('dashboard')
            else:
                #ERROR analizamos el error
                error_msg = data.get('error', {}).get('message', 'UNKNOW_ERROR')

                errores_comunes = {
                    'INVALID_LOGIN_CREDENTIALS': 'La contraseña es incorrecta o el correo no es válido.',
                    'EMAIL_NOT_FOUND': 'Este correo no está registrado en el sistema.',
                    'USER_DISABLED': 'Esta cuenta ha sido inhabilitada por el administrador.',
                    'TOO_MANY_ATTEMPTS_TRY_LATER': 'Demasiados intentos fallidos. Espere unos minutos.'
                }
            
                mensaje_usuario = errores_comunes.get(error_msg, "❌❌Error de autentificación, revise sus datos")
                messages.error(request, mensaje_usuario)
        except requests.exceptions.RequestException as e:
            messages.error(request, f"❌Error de conexión con el servidor")
        except Exception as e:
            messages.error(request, f"Error inesperado {str(e)}")
    return render(request, "login.html")
    
def cerrar_sesion(request):
    # Limpio sesión y redirijo
    request.session.flush()
    messages.info(request, f"✅Has cerrado sesión correctamente")
    return redirect('login')
