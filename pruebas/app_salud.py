import tkinter as tk
from tkinter import messagebox
import mysql.connector


# Conexión a la base de datos
def conectar():
    return mysql.connector.connect(
        host="localhost", user="root", password="", database="medicina"
    )


# -------------------------------
# REGISTRAR USUARIO
# -------------------------------
def guardar_usuario():
    doc = entry_doc.get()
    nombre = entry_nombre.get()
    edad = int(entry_edad.get())

    if edad < 18:
        tipo = "joven"
    elif edad < 60:
        tipo = "adulto"
    else:
        tipo = "mayor"

    try:
        con = conectar()
        cursor = con.cursor()

        sql = "INSERT INTO usuarios (documento, nombre, edad, tipo_usuario) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (doc, nombre, edad, tipo))
        con.commit()

        messagebox.showinfo("Éxito", "Usuario registrado")

        cursor.close()
        con.close()

    except Exception as e:
        messagebox.showerror("Error", str(e))


# -------------------------------
# REGISTRAR DATOS
# -------------------------------
def guardar_datos():
    doc = entry_doc_datos.get()
    pulso = int(entry_pulso.get())
    sueno = float(entry_sueno.get())

    try:
        con = conectar()
        cursor = con.cursor()

        sql = "INSERT INTO datos_reloj (documento, pulso, horas_sueno, fecha) VALUES (%s, %s, %s, NOW())"
        cursor.execute(sql, (doc, pulso, sueno))
        con.commit()

        messagebox.showinfo("Éxito", "Datos guardados")

        cursor.close()
        con.close()

    except Exception as e:
        messagebox.showerror("Error", str(e))


# -------------------------------
# INTERFAZ
# -------------------------------
ventana = tk.Tk()
ventana.title("Sistema de Salud")

# --- Usuario ---
tk.Label(ventana, text="Registro de Usuario").pack()

tk.Label(ventana, text="Documento").pack()
entry_doc = tk.Entry(ventana)
entry_doc.pack()

tk.Label(ventana, text="Nombre").pack()
entry_nombre = tk.Entry(ventana)
entry_nombre.pack()

tk.Label(ventana, text="Edad").pack()
entry_edad = tk.Entry(ventana)
entry_edad.pack()

tk.Button(ventana, text="Guardar Usuario", command=guardar_usuario).pack()

# --- Datos ---
tk.Label(ventana, text="\nDatos del Reloj").pack()

tk.Label(ventana, text="Documento").pack()
entry_doc_datos = tk.Entry(ventana)
entry_doc_datos.pack()

tk.Label(ventana, text="Pulso").pack()
entry_pulso = tk.Entry(ventana)
entry_pulso.pack()

tk.Label(ventana, text="Horas de sueño").pack()
entry_sueno = tk.Entry(ventana)
entry_sueno.pack()

tk.Button(ventana, text="Guardar Datos", command=guardar_datos).pack()

ventana.mainloop()
