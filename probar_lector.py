import serial
import time

# Importamos tu función original para guardar en XAMPP
from datos import insertar_datos

# CONFIGURACIÓN DEL PUERTO:
# Cambia 'COM3' por el puerto exacto que usa tu Pico en Thonny
PUERTO_SERIAL = "COM7"
BAUD_RATE = 115200

print("==================================================")
print("  INICIANDO PRUEBA DEL LECTOR SERIAL Y ENCRIPTACIÓN")
print("==================================================")

try:
    # Intentamos abrir el puerto USB
    arduino = serial.Serial(PUERTO_SERIAL, BAUD_RATE, timeout=1)
    print(f" -> Puerto {PUERTO_SERIAL} abierto con éxito.")
    print(" -> Esperando 2 segundos para estabilizar la línea...")
    time.sleep(2)
    print("\n -> ¡Listo! Pon el dedo en el sensor para ver los datos...\n")

    while True:
        if arduino.in_waiting > 0:
            # Leer la línea que manda la Pico (ej: "12345678,74.35,98.12")
            linea = arduino.readline().decode("utf-8").strip()

            # Verificamos si la línea tiene el formato de comas esperado
            if "," in linea:
                partes = linea.split(",")
                if len(partes) == 3:
                    documento, pulso, spo2 = partes

                    # Convertimos a float para mantener los decimales que propusiste
                    v_pulso = float(pulso)
                    v_spo2 = float(spo2)

                    # Si el dedo está puesto (valores mayores a zero)
                    if v_pulso > 0.0 and v_spo2 > 0.0:
                        print(
                            f"[Pico USB] -> Doc: {documento} | Pulso: {v_pulso} | SpO2: {v_spo2}"
                        )

                        try:
                            # Ejecuta tu lógica: cifra los datos y los mete a MySQL de XAMPP
                            insertar_datos(documento, v_pulso, v_spo2)
                            print(
                                "   [✓] Guardado y encriptado en la base de datos con éxito."
                            )
                        except Exception as error_db:
                            print(
                                f"   [X] Error al insertar en la base de datos: {error_db}"
                            )
                    else:
                        print("[Aviso] Coloca el dedo en el sensor...")

        time.sleep(0.3)  # Escucha rápido el puerto

except KeyboardInterrupt:
    print("\nPrueba detenida por el usuario.")
except Exception as e:
    print(f"\n[X] Error crítico de conexión: {e}")
    print("Asegúrate de que:")
    print(f" 1. La Pico esté conectada en el puerto {PUERTO_SERIAL}.")
    print(" 2. THONNY ESTÉ COMPLETAMENTE CERRADO.")
    print(" 3. Tu panel de XAMPP (Apache y MySQL) esté encendido.")
