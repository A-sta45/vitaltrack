# VitalTrack

Aplicación de escritorio (**Tkinter**) para registrar y consultar signos vitales (pulso y SpO2) leídos desde un dispositivo conectado por **puerto serial** (ej. un smartwatch/Arduino), con los datos guardados cifrados en **MySQL**.

## Características

- **Login y registro de usuarios** (`login.py`, `registro.py`, `usuarios.py`), con contraseña y datos personales cifrados antes de guardarse.
- **Lectura en segundo plano del puerto serial** (`lector_serial.py`) en un hilo separado, controlable (pausar/reanudar) desde el resto de la interfaz vía `estado_global.py`.
- **Cifrado de datos sensibles** con `cryptography.Fernet` (`seguridad.py`): nombre, edad, contraseña, pulso y SpO2 se cifran antes de insertarse en la base de datos y se descifran al consultarlos.
- **Historial** (`historial.py`) y **gráficas** (`grafica.py`) de las mediciones guardadas por documento de usuario.
- **Menú principal** (`menu.py`) desde el que se accede a historial, gráfica y cierre ordenado del sistema (incluye cerrar el puerto serial).

## Estructura

- `main.py` — punto de entrada, abre la ventana de login.
- `db.py` — conexión a MySQL.
- `seguridad.py` — funciones `encriptar`/`desencriptar`.
- `datos.py`, `usuarios.py` — acceso a datos (lecturas y usuarios).
- `config.py` — puerto serial, baudrate y tiempo de guardado.
- `pruebas/` — prototipos/pruebas sueltas (`app_salud.py`, `medicina_app.py`).

## Configuración

Ajusta en `config.py` el puerto serial de tu dispositivo (por defecto `COM7`) y en `db.py` los datos de conexión a tu MySQL local.

La base de datos necesita al menos las tablas `usuarios` y `datos_reloj` (ver las consultas en `datos.py` y `usuarios.py` para los campos esperados).

## Instalación y ejecución

```bash
python -m venv venv
source venv/bin/activate  # en Windows: venv\Scripts\activate
pip install cryptography mysql-connector-python pyserial matplotlib
python main.py
```
