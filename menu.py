import tkinter as tk

import estado_global as vg

from historial import ventana_historial
from grafica import ventana_grafica


def abrir_menu_principal(root, entry_doc, entry_pass):

    root.withdraw()

    menu = tk.Toplevel()

    menu.title("Panel Principal")

    menu.geometry("400x350")

    # ---------------------------------------------------------
    # CERRAR TODO EL SISTEMA
    # ---------------------------------------------------------
    def ordenar_cierre():

        import lector_serial

        print("[INFO] Cerrando sistema...")

        vg.PROGRAMA_ACTIVO = False

        try:
            if lector_serial.ARDUINO:
                lector_serial.ARDUINO.close()

                print("[SERIAL] Puerto cerrado.")

        except Exception as e:
            print(f"[ERROR SERIAL] {e}")

        menu.destroy()

        root.destroy()

    # ---------------------------------------------------------
    # CERRAR SESIÓN
    # ---------------------------------------------------------
    def cerrar_sesion():

        vg.USUARIO_ACTUAL = None

        menu.destroy()

        entry_doc.delete(0, tk.END)

        entry_pass.delete(0, tk.END)

        root.deiconify()

    # ---------------------------------------------------------
    # AL CERRAR LA VENTANA
    # ---------------------------------------------------------
    menu.protocol("WM_DELETE_WINDOW", ordenar_cierre)

    # ---------------------------------------------------------
    # TITULO
    # ---------------------------------------------------------
    tk.Label(menu, text="Bienvenido", font=("Arial", 16, "bold")).pack(pady=15)

    tk.Label(menu, text=f"Usuario: {vg.USUARIO_ACTUAL}", fg="blue").pack()

    # ---------------------------------------------------------
    # BOTONES
    # ---------------------------------------------------------
    tk.Button(
        menu, text="Ver Historial", width=25, command=lambda: ventana_historial(menu)
    ).pack(pady=10)

    tk.Button(menu, text="Ver Gráfica", width=25, command=ventana_grafica).pack(pady=10)

    tk.Button(
        menu,
        text="Cerrar Sesión",
        width=20,
        bg="#dc3545",
        fg="white",
        command=cerrar_sesion,
    ).pack(pady=30)
