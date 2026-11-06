import tkinter as tk
from tkinter import messagebox

from usuarios import validar_login
from registro import abrir_registro
from menu import abrir_menu_principal

from lector_serial import iniciar_hilo_serial

import estado_global as vg


def iniciar_login():

    # ------------------------------------------------
    # INICIAR HILO SERIAL
    # ------------------------------------------------
    iniciar_hilo_serial()

    # ------------------------------------------------
    # VENTANA PRINCIPAL
    # ------------------------------------------------
    root = tk.Tk()

    root.title("Sistema de Salud - VitalTrack")
    root.geometry("350x250")
    root.resizable(False, False)

    # ------------------------------------------------
    # TITULO
    # ------------------------------------------------
    tk.Label(
        root,
        text="Control de Acceso",
        font=("Arial", 14, "bold"),
    ).pack(pady=10)

    # ------------------------------------------------
    # DOCUMENTO
    # ------------------------------------------------
    tk.Label(
        root,
        text="Documento de Identidad:",
    ).pack(pady=2)

    entry_doc = tk.Entry(
        root,
        font=("Arial", 10),
    )

    entry_doc.pack()

    # ------------------------------------------------
    # CONTRASEÑA
    # ------------------------------------------------
    tk.Label(
        root,
        text="Contraseña:",
    ).pack(pady=2)

    entry_pass = tk.Entry(
        root,
        show="*",
        font=("Arial", 10),
    )

    entry_pass.pack()

    # ------------------------------------------------
    # LOGIN
    # ------------------------------------------------
    def ejecutar_login():

        doc = entry_doc.get().strip()
        passwd = entry_pass.get().strip()

        if doc == "" or passwd == "":
            messagebox.showwarning(
                "Campos Incompletos",
                "Por favor ingresa tus credenciales.",
            )

            return

        if validar_login(doc, passwd):
            vg.USUARIO_ACTUAL = doc

            abrir_menu_principal(
                root,
                entry_doc,
                entry_pass,
            )

        else:
            messagebox.showerror(
                "Acceso Denegado",
                "Documento o contraseña incorrectos.",
            )

    # ------------------------------------------------
    # FRAME BOTONES
    # ------------------------------------------------
    frame_botones = tk.Frame(root)

    frame_botones.pack(pady=15)

    # ------------------------------------------------
    # BOTON REGISTRO
    # ------------------------------------------------
    tk.Button(
        frame_botones,
        text="Registrarse",
        width=12,
        bg="#6c757d",
        fg="white",
        command=lambda: abrir_registro(root),
    ).pack(side="left", padx=5)

    # ------------------------------------------------
    # BOTON LOGIN
    # ------------------------------------------------
    tk.Button(
        frame_botones,
        text="Aceptar",
        width=12,
        bg="#007bff",
        fg="white",
        command=ejecutar_login,
    ).pack(side="left", padx=5)

    root.mainloop()
