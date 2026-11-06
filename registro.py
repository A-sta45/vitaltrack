import tkinter as tk
from tkinter import messagebox

from usuarios import insertar_usuario


def abrir_registro(root):

    win_reg = tk.Toplevel(root)

    win_reg.title("Registrar Usuario")

    win_reg.geometry("300x320")

    win_reg.grab_set()

    # ---------------------------------------------------------
    # CAMPOS
    # ---------------------------------------------------------
    tk.Label(win_reg, text="Documento").pack()

    entry_doc = tk.Entry(win_reg)

    entry_doc.pack()

    tk.Label(win_reg, text="Nombre").pack()

    entry_nombre = tk.Entry(win_reg)

    entry_nombre.pack()

    tk.Label(win_reg, text="Edad").pack()

    entry_edad = tk.Entry(win_reg)

    entry_edad.pack()

    tk.Label(win_reg, text="Contraseña").pack()

    entry_pass = tk.Entry(win_reg, show="*")

    entry_pass.pack()

    # ---------------------------------------------------------
    # GUARDAR
    # ---------------------------------------------------------
    def guardar_usuario():

        doc = entry_doc.get().strip()

        nom = entry_nombre.get().strip()

        edad = entry_edad.get().strip()

        passwd = entry_pass.get().strip()

        if not doc or not nom or not edad or not passwd:
            messagebox.showwarning("Advertencia", "Todos los campos son obligatorios.")

            return

        try:
            insertar_usuario(doc, nom, int(edad), passwd)

            messagebox.showinfo("Éxito", "Usuario registrado.")

            win_reg.destroy()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------------------------------------------------------
    # BOTÓN
    # ---------------------------------------------------------
    tk.Button(
        win_reg, text="Registrar", bg="#28a745", fg="white", command=guardar_usuario
    ).pack(pady=20)
