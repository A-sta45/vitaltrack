from db import conectar
from seguridad import encriptar


def insertar_datos(documento, pulso, spo2):
    con = conectar()
    cursor = con.cursor()
    pulso_enc = encriptar(str(pulso))
    spo2_enc = encriptar(str(spo2))

    sql = "INSERT INTO datos_reloj (documento, pulso, spo2) VALUES (%s, %s, %s)"
    cursor.execute(sql, (documento, pulso_enc, spo2_enc))
    con.commit()
    cursor.close()
    con.close()


# ◄--- ESTA ES LA FUNCIÓN QUE CAMBIA CON EL INNER JOIN
def obtener_historial_por_documento(documento):
    con = conectar()
    cursor = con.cursor()

    # Esta consulta busca el nombre en 'usuarios' usando el documento de 'datos_reloj'
    sql = """
        SELECT usuarios.nombre, datos_reloj.pulso, datos_reloj.spo2, datos_reloj.fecha 
        FROM datos_reloj 
        INNER JOIN usuarios ON datos_reloj.documento = usuarios.documento 
        WHERE datos_reloj.documento = %s 
        ORDER BY datos_reloj.fecha DESC
    """
    cursor.execute(sql, (documento,))
    resultados = cursor.fetchall()

    cursor.close()
    con.close()
    return resultados


def obtener_datos_grafica(documento):
    con = conectar()
    cursor = con.cursor()
    sql = "SELECT fecha, pulso, spo2 FROM datos_reloj WHERE documento = %s ORDER BY fecha ASC"
    cursor.execute(sql, (documento,))
    resultados = cursor.fetchall()
    cursor.close()
    con.close()
    return resultados
