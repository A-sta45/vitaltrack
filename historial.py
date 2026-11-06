import tkinter as tk
from tkinter import ttk, messagebox

import estado_global as vg

from datos import obtener_historial_por_documento
from seguridad import desencriptar


def ventana_historial(menu):

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

    # ---------------------------------------------------------
    # VENTANA
    # ---------------------------------------------------------
    win_hist = tk.Toplevel(menu)

    win_hist.title("Historial Clínico")

    win_hist.geometry("650x350")

    win_hist.grab_set()

    # ---------------------------------------------------------
    # AL CERRAR
    # ---------------------------------------------------------
    def al_cerrar_historial():

        vg.PAUSAR_LECTURA = False

        print("[INFO] Lectura reanudada.")

        try:
            if lector_serial.ARDUINO:
                lector_serial.ARDUINO.write(b"A")

                print("[LED] AMARILLO")

        except Exception as e:
            print(f"[ERROR LED] {e}")

        win_hist.destroy()

    win_hist.protocol("WM_DELETE_WINDOW", al_cerrar_historial)

    # ---------------------------------------------------------
    # TITULO
    # ---------------------------------------------------------
    tk.Label(
        win_hist,
        text=f"Historial de {vg.USUARIO_ACTUAL}",
        font=("Arial", 12, "bold"),
    ).pack(pady=10)

    # ---------------------------------------------------------
    # TABLA
    # ---------------------------------------------------------
    tabla = ttk.Treeview(
        win_hist, columns=("Nombre", "Pulso", "SpO2", "Fecha"), show="headings"
    )

    tabla.heading("Nombre", text="Nombre")

    tabla.heading("Pulso", text="Pulso")

    tabla.heading("SpO2", text="SpO2")

    tabla.heading("Fecha", text="Fecha")

    tabla.column("Nombre", width=150)

    tabla.column("Pulso", width=100, anchor="center")

    tabla.column("SpO2", width=100, anchor="center")

    tabla.column("Fecha", width=180, anchor="center")

    tabla.pack(fill="both", expand=True, padx=10, pady=5)

    # ---------------------------------------------------------
    # CARGAR DATOS
    # ---------------------------------------------------------
    try:
        datos_db = obtener_historial_por_documento(vg.USUARIO_ACTUAL)

        if not datos_db:
            tk.Label(win_hist, text="No hay registros guardados.", fg="red").pack()

        for fila in datos_db:
            try:
                nombre = desencriptar(str(fila[0]).strip())

                pulso = desencriptar(str(fila[1]).strip())

                spo2 = desencriptar(str(fila[2]).strip())

                fecha = fila[3].strftime("%d/%m/%Y %H:%M:%S")

                tabla.insert(
                    "",
                    "end",
                    values=(nombre, pulso, spo2, fecha),
                )

            except Exception as e:
                print(f"[ERROR HISTORIAL] {e}")

    except Exception as e:
        messagebox.showerror("Error", str(e))
