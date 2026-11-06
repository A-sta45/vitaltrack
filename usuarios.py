from db import conectar
from seguridad import encriptar, desencriptar


def insertar_usuario(documento, nombre, edad, password):
    if edad < 18:
        tipo = "joven"
    elif edad < 60:
        tipo = "adulto"
    else:
        tipo = "mayor"

    # Encriptamos TODO por seguridad, incluida la contraseña
    nombre_enc = encriptar(nombre)
    edad_enc = encriptar(str(edad))
    password_enc = encriptar(password)

    con = conectar()
    cursor = con.cursor()

    sql = "INSERT INTO usuarios (documento, nombre, edad, tipo_usuario, password) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(sql, (documento, nombre_enc, edad_enc, tipo, password_enc))
    con.commit()

    cursor.close()
    con.close()


def validar_login(documento, password_ingresada):
    con = conectar()
    cursor = con.cursor()

    # Buscamos al usuario por su documento
    sql = "SELECT password FROM usuarios WHERE documento = %s"
    cursor.execute(sql, (documento,))
    resultado = cursor.fetchone()

    cursor.close()
    con.close()

    if resultado:
        password_guardada_enc = resultado[0]
        # Desencriptamos la contraseña de la BD para compararla con la que escribió el usuario
        try:
            password_real = desencriptar(password_guardada_enc)
            return password_real == password_ingresada
        except:
            return False
    return False
