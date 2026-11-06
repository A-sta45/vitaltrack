import serial
import threading
import time

from datos import insertar_datos

import estado_global as vg

ARDUINO = None


# ---------------------------------------------------------
# FUNCIÓN PRINCIPAL
# ---------------------------------------------------------
def escuchar_pico_dinamico():

    PUERTO_SERIAL = "COM7"

    ultimo_guardado = None

    estado_actual_led = None

    ultimo_tiempo_restante = None

    ultima_lectura_valida = time.time()

    try:
        global ARDUINO

        ARDUINO = serial.Serial(PUERTO_SERIAL, 115200, timeout=1)

        time.sleep(2)

        print("[SERIAL] Conectado correctamente.")

        while vg.PROGRAMA_ACTIVO:
            # ---------------------------------------------------------
            # SIN LOGIN
            # ---------------------------------------------------------
            if vg.USUARIO_ACTUAL is None:
                time.sleep(1)

                continue

            # ---------------------------------------------------------
            # PAUSA DE LECTURA
            # ---------------------------------------------------------
            if vg.PAUSAR_LECTURA:
                time.sleep(0.2)

                continue

            # ---------------------------------------------------------
            # LEER SERIAL
            # ---------------------------------------------------------
            if ARDUINO.in_waiting > 0:
                linea = ARDUINO.readline().decode("utf-8", errors="ignore").strip()

                print(f"[SERIAL] {linea}")

                if "," in linea:
                    partes = linea.split(",")

                    if len(partes) == 3:
                        try:
                            _, pulso, spo2 = partes

                            v_pulso = float(pulso)

                            v_spo2 = float(spo2)

                            # ---------------------------------------------------------
                            # VALIDAR SI LA LECTURA ES REAL
                            # ---------------------------------------------------------
                            lectura_valida = v_pulso > 0.0 and v_spo2 > 0.0

                            # ---------------------------------------------------------
                            # SIN LECTURA VÁLIDA
                            # ---------------------------------------------------------
                            if not lectura_valida:
                                tiempo_sin_dedo = time.time() - ultima_lectura_valida

                                print(
                                    f"[INFO] Sin lectura válida: {tiempo_sin_dedo:.1f}s"
                                )

                                # ---------------------------------------------------------
                                # DEDO RETIRADO
                                # ---------------------------------------------------------
                                if tiempo_sin_dedo >= 2:
                                    print("[INFO] Dedo retirado confirmado.")

                                    ultimo_guardado = None

                                    ultimo_tiempo_restante = None

                                    if estado_actual_led != "R":
                                        ARDUINO.write(b"R")

                                        estado_actual_led = "R"

                                        print("[LED] ROJO")

                            # ---------------------------------------------------------
                            # CON LECTURA VÁLIDA
                            # ---------------------------------------------------------
                            else:
                                tiempo_actual = time.time()

                                ultima_lectura_valida = time.time()

                                # ---------------------------------------------------------
                                # INICIO DEL CONTEO
                                # ---------------------------------------------------------
                                if ultimo_guardado is None:
                                    ultimo_guardado = tiempo_actual

                                    print("[INFO] Conteo iniciado.")

                                # ---------------------------------------------------------
                                # TIEMPO RESTANTE
                                # ---------------------------------------------------------
                                tiempo_restante = int(
                                    30 - (tiempo_actual - ultimo_guardado)
                                )

                                # Evitar negativos
                                if tiempo_restante < 0:
                                    tiempo_restante = 0

                                print(f"[INFO] Guardado en {tiempo_restante}s")

                                # ---------------------------------------------------------
                                # DETECCIÓN EXTRA
                                # SI EL CONTADOR SUBE
                                # ---------------------------------------------------------
                                if ultimo_tiempo_restante is not None:
                                    if tiempo_restante > ultimo_tiempo_restante:
                                        print("[ALERTA] Reinicio detectado.")

                                        ultimo_guardado = None

                                        ultimo_tiempo_restante = None

                                        ARDUINO.write(b"R")

                                        estado_actual_led = "R"

                                        continue

                                ultimo_tiempo_restante = tiempo_restante

                                # ---------------------------------------------------------
                                # GUARDAR DATOS
                                # ---------------------------------------------------------
                                if (tiempo_actual - ultimo_guardado) >= 30:
                                    try:
                                        ARDUINO.write(b"V")

                                        estado_actual_led = "V"

                                        print("[LED] VERDE")

                                        insertar_datos(
                                            vg.USUARIO_ACTUAL, v_pulso, v_spo2
                                        )

                                        print(
                                            f"[BD] Guardado para: {vg.USUARIO_ACTUAL}"
                                        )

                                        ultimo_guardado = time.time()

                                        ultimo_tiempo_restante = None

                                        time.sleep(1)

                                    except Exception as err:
                                        print(f"[ERROR BD] {err}")

                                # ---------------------------------------------------------
                                # MIDIENDO
                                # ---------------------------------------------------------
                                else:
                                    if estado_actual_led != "A":
                                        ARDUINO.write(b"A")

                                        estado_actual_led = "A"

                                        print("[LED] AMARILLO")

                        except Exception as err:
                            print(f"[ERROR] {err}")

            time.sleep(0.1)

    except Exception as e:
        print(f"[ERROR SERIAL] {e}")


# ---------------------------------------------------------
# INICIAR HILO
# ---------------------------------------------------------
def iniciar_hilo_serial():

    hilo = threading.Thread(target=escuchar_pico_dinamico, daemon=True)

    hilo.start()

    print("[HILO] Serial iniciado.")
