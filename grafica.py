from tkinter import messagebox

from matplotlib import pyplot as plt

import estado_global as vg

from datos import obtener_datos_grafica
from seguridad import desencriptar


def ventana_grafica():

    import lector_serial

    # ---------------------------------------------------------
    # PAUSAR LECTURA
    # ---------------------------------------------------------
    vg.PAUSAR_LECTURA = True

    print("[INFO] Lectura pausada.")

    try:
        if lector_serial.ARDUINO:
            lector_serial.ARDUINO.write(b"B")

            print("[LED] AZUL")

    except Exception as e:
        print(f"[ERROR LED] {e}")

    try:
        datos_db = obtener_datos_grafica(vg.USUARIO_ACTUAL)

        if not datos_db:
            messagebox.showinfo("Info", "No hay datos para graficar.")

            return

        fechas = []

        pulsos = []

        spo2_lista = []

        contador_aux = 1

        # ---------------------------------------------------------
        # PROCESAR DATOS
        # ---------------------------------------------------------
        for fila in datos_db:
            try:
                pulso = desencriptar(str(fila[1]).strip())

                spo2 = desencriptar(str(fila[2]).strip())

                if fila[0] is not None:
                    fecha = fila[0].strftime("%H:%M:%S")

                else:
                    fecha = f"Histórico {contador_aux}"

                fechas.append(fecha)

                pulsos.append(float(pulso))

                spo2_lista.append(float(spo2))

                contador_aux += 1

            except Exception as e:
                print(f"[ERROR GRAFICA] {e}")

        if len(pulsos) == 0:
            messagebox.showwarning("Sin datos", "No hay datos válidos.")

            return

        # ---------------------------------------------------------
        # GRAFICA
        # ---------------------------------------------------------
        plt.figure("Monitoreo Médico", figsize=(9, 5))

        plt.clf()

        plt.plot(
            fechas,
            pulsos,
            "-o",
            label="Pulso BPM",
            color="red",
            linewidth=2,
        )

        plt.plot(
            fechas,
            spo2_lista,
            "-s",
            label="SpO2 %",
            color="blue",
            linewidth=2,
        )

        plt.xlabel("Hora")

        plt.ylabel("Valores")

        plt.title(f"Paciente: {vg.USUARIO_ACTUAL}")

        plt.grid(True)

        plt.legend()

        plt.xticks(rotation=45)

        plt.tight_layout()

        plt.show()

    except Exception as e:
        messagebox.showerror("Error", str(e))

    finally:
        # ---------------------------------------------------------
        # REANUDAR LECTURA
        # ---------------------------------------------------------
        vg.PAUSAR_LECTURA = False

        print("[INFO] Lectura reanudada.")

        try:
            if lector_serial.ARDUINO:
                lector_serial.ARDUINO.write(b"A")

                print("[LED] AMARILLO")

        except Exception as e:
            print(f"[ERROR LED] {e}")
