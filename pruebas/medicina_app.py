import mysql.connector

conexion = mysql.connector.connect(
    host="localhost", user="root", password="", database="medicina"
)

cursor = conexion.cursor()

print("=== REGISTRO DE USUARIO ===")
documento = input("Documento: ")
nombre = input("Nombre: ")
edad = int(input("Edad: "))

# Clasificación automática
if edad < 18:
    tipo = "joven"
elif edad < 60:
    tipo = "adulto"
else:
    tipo = "mayor"

# Insertar usuario
sql_usuario = "INSERT INTO usuarios (documento, nombre, edad, tipo_usuario) VALUES (%s, %s, %s, %s)"
cursor.execute(sql_usuario, (documento, nombre, edad, tipo))
conexion.commit()

print("Usuario registrado correctamente")

print("\n=== REGISTRO DE DATOS DEL RELOJ ===")
pulso = int(input("Pulso: "))
sueno = float(input("Horas de sueño: "))

sql_datos = "INSERT INTO datos_reloj (documento, pulso, horas_sueno, fecha) VALUES (%s, %s, %s, NOW())"
cursor.execute(sql_datos, (documento, pulso, sueno))
conexion.commit()

print("Datos guardados correctamente")

cursor.close()
conexion.close()
