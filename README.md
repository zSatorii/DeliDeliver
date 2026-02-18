# 🛵 DeliDeliver

> Delideliver es una plataforma de delivery de comida y productos, desarrollada con Django.

[![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)
[![Firebase](https://img.shields.io/badge/firebase-ffca28?style=for-the-badge&logo=firebase&logoColor=black)](https://firebase.google.com/?hl=es-419)

---

## 📋 Tabla de contenidos

- [Descripcion](#-descripcion)
- [Caracteristicas](#-caracteristicas)
- [Instalacion](#-instalacion)
- [Arquitectura](#-arquitectura)

## 📦 Descripcion
**DeliDeliver** Es una plataforma de delivery diseñada en Django con una adicion de Firebase Permite a usuarios y empresas registrar pedidos, gestionar menús y repartidores manejar entregas en tiempo real.

El sistema cuenta con Dos roles principales: **Cliente**, **Empresa**, cada uno con su propio panel de control (Dashboard)

## ✨ Caracteristicas
- 🔐 **Autenticación** — Registro, login y manejo de sesiones con Firebase
- 🛠️ **Panel de administración** — Dashboard / Panel de control

## 🚀 Instalacion
```bash
# 1.Clona el repositorio :
Con el comando git clone https://github.com/tu-usuario/delideliver.git

# 2.Ahora crearas un entorno virtual y activarlo :
python -m venv venv
source venv/bin/activate # Linux/Mac
venv\Scripts\activate # Windows

# 3.Ahora instalaras dependencias : 
pip install -r requirements.txt

4.
```
## 🏗️ Arquitectura

```
delideliver/
├── delideliver/
│   ├── firebase_config.py          # Es la configuracion del firebase 
│   ├── setting.py         # La configuracion de Django
│   ├── urls.py       # Urls de Django
├── interfaz/             # Configuración del proyecto 
│   ├── templates/          # Son las Templates del proyecto
│   ├── urls.py             # Son las urls de la app 
│   ├── views.py            # Son las vistas del proyecto 
├── README.md
├── requirements.txt
└── manage.py
```