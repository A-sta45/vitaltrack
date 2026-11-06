import tkinter as tk
from tkinter import ttk, messagebox
import threading
import serial
import time

# Importaciones de tus módulos de lógica y base de datos
from usuarios import insertar_usuario, validar_login
from datos import insertar_datos, obtener_historial_por_documento, obtener_datos_grafica
from seguridad import desencriptar

# Variables globales de control
USUARIO_ACTUAL = None
PAUSAR_LECTURA = False


def iniciar_app():
    from matplotlib import pyplot as plt

    root = tk.Tk()
    root.title("Sistema de Salud - VitalTrack")
    root.geometry("350x250")
    root.resizable(False, False)

    # -------------------------------------------------------------------------
    # HILO DE LECTURA SERIAL CORREGIDO (ROJO -> AMARILLO -> VERDE -> AMARILLO)
    # -------------------------------------------------------------------------
    def escuchar_pico():
        global USUARIO_ACTUAL, PAUSAR_LECTURA
        PUERTO_SERIAL = "COM7"
        ultimo_guardado = None
        estado_actual_led = None

        print(f"[SERIAL] Intentando conectar al puerto {PUERTO_SERIAL}...")

        # Bucle de conexión inicial seguro
        while True:
            try:
                arduino = serial.Serial(
                    port=PUERTO_SERIAL,
                    baudrate=115200,
                    timeout=0.1,
                    rtscts=True,
                    dsrdtr=True,
                )
                arduino.reset_input_buffer()
                arduino.reset_output_buffer()
                print(
                    f"[CONECTADO CON ÉXITO] ¡Puerto {PUERTO_SERIAL} listo con control de estados!"
                )
                break
            except Exception as e_conexion:
                print(
                    f"[ERROR PUERTO] Esperando dispositivo en {PUERTO_SERIAL}... Reintentando. Motivo: {e_conexion}"
                )
                time.sleep(2)

        # Bucle principal de lectura y envío de comandos de luz
        while True:
            if USUARIO_ACTUAL is None or PAUSAR_LECTURA:
                time.sleep(0.1)
                continue

            try:
                if arduino.in_waiting > 0:
                    linea_raw = arduino.readline()
                    linea = linea_raw.decode("utf-8", errors="ignore").strip()

                    if not linea:
                        continue

                    print(f"[DEBUG SERIAL] Llegó de la Pico: {linea}")

                    if "," in linea:
                        partes = linea.split(",")
                        if len(partes) == 3:
                            try:
                                v_pulso = float(partes[1])
                                v_spo2 = float(partes[2])

                                # ESTADO 1: No está el dedo (Valores en 0.0) -> LED ROJO
                                if v_pulso == 0.0 or v_spo2 == 0.0:
                                    ultimo_guardado = None  # Reiniciamos el cronómetro si saca el dedo
                                    if estado_actual_led != "R":
                                        arduino.write(b"R")
                                        estado_actual_led = "R"
                                        print("[ESTADO] Sin dedo. LED -> ROJO")
                                else:
                                    tiempo_actual = time.time()

                                    # Si es la primera lectura válida con el dedo puesto, iniciamos el conteo
                                    if ultimo_guardado is None:
                                        ultimo_guardado = tiempo_actual
                                        print(
                                            "[ESTADO] Dedo detectado. Iniciando conteo de 30s..."
                                        )

                                    # ESTADO 3: Se cumplen los 30 segundos -> LED VERDE Y GUARDAR
                                    if tiempo_actual - ultimo_guardado >= 30.0:
                                        try:
                                            arduino.write(b"V")
                                            estado_actual_led = "V"
                                            print(
                                                "[ESTADO] ¡Tiempo cumplido! LED -> VERDE"
                                            )

                                            insertar_datos(
                                                USUARIO_ACTUAL, v_pulso, v_spo2
                                            )
                                            print(
                                                f"[Auto-Guardado] Registro exitoso en BD para el usuario {USUARIO_ACTUAL}."
                                            )

                                            # CORRECCIÓN: Reseteamos el conteo y limpiamos el estado para permitir el Amarillo de nuevo
                                            ultimo_guardado = tiempo_actual
                                            estado_actual_led = None
                                            time.sleep(
                                                1.0
                                            )  # Pausa para mantener el color verde visible un momento
                                        except Exception as err:
                                            print("Error en guardado automático:", err)

                                    # ESTADO 2: Dedo puesto, midiendo (Segundos 0 al 29) -> LED AMARILLO
                                    else:
                                        tiempo_restante = int(
                                            30 - (tiempo_actual - ultimo_guardado)
                                        )
                                        print(
                                            f"[INFO] Próximo guardado en {tiempo_restante}s... (Pulso: {v_pulso} BPM | SpO2: {v_spo2}%)"
                                        )

                                        # CORRECCIÓN: Quitamos el candado restrictivo de 'V' para regresar de Verde a Amarillo de forma fluida
                                        if estado_actual_led != "A":
                                            arduino.write(b"A")
                                            estado_actual_led = "A"
                                            print(
                                                "[ESTADO] Midiendo... LED -> AMARILLO"
                                            )

                            except ValueError:
                                pass

            except Exception as e_bucle:
                print(f"[AVISO] Error leyendo ráfaga serial: {e_bucle}")

            time.sleep(0.1)

    # Lanzamos el hilo serial en segundo plano
    hilo_sensor = threading.Thread(target=escuchar_pico, daemon=True)
    hilo_sensor.start()

    # -------------------------------------------------------------------------
    # VENTANA DE REGISTRO DE USUARIOS
    # -------------------------------------------------------------------------
    def abrir_registro():
        win_reg = tk.Toplevel(root)
        win_reg.title("Registrar Nuevo Usuario")
        win_reg.geometry("300x320")
        win_reg.grab_set()

        tk.Label(win_reg, text="Documento / ID:", font=("Arial", 10)).pack(pady=2)
        entry_doc = tk.Entry(win_reg)
        entry_doc.pack()

        tk.Label(win_reg, text="Nombre Completo:", font=("Arial", 10)).pack(pady=2)
        entry_nombre = tk.Entry(win_reg)
        entry_nombre.pack()

        tk.Label(win_reg, text="Edad:", font=("Arial", 10)).pack(pady=2)
        entry_edad = tk.Entry(win_reg)
        entry_edad.pack()

        tk.Label(win_reg, text="Contraseña:", font=("Arial", 10)).pack(pady=2)
        entry_pass = tk.Entry(win_reg, show="*")
        entry_pass.pack()

        def guardar_nuevo_usuario():
            doc = entry_doc.get().strip()
            nom = entry_nombre.get().strip()
            edad_str = entry_edad.get().strip()
            passwd = entry_pass.get().strip()

            if not doc or not nom or not edad_str or not passwd:
                messagebox.showwarning(
                    "Advertencia", "Todos los campos son obligatorios"
                )
                return

            try:
                insertar_usuario(doc, nom, int(edad_str), passwd)
                messagebox.showinfo("Éxito", "Usuario registrado correctamente.")
                win_reg.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo registrar: {e}")

        tk.Button(
            win_reg,
            text="Registrar Cuenta",
            bg="#28a745",
            fg="white",
            width=18,
            command=guardar_nuevo_usuario,
        ).pack(pady=15)

    # -------------------------------------------------------------------------
    # PANEL PRINCIPAL (POST-LOGIN)
    # -------------------------------------------------------------------------
    def abrir_menu_principal():
        global USUARIO_ACTUAL, PAUSAR_LECTURA
        root.withdraw()

        menu = tk.Toplevel()
        menu.title("Sistema de Salud - Panel Principal")
        menu.geometry("400x350")

        def ordenar_cierre():
            root.destroy()

        menu.protocol("WM_DELETE_WINDOW", ordenar_cierre)

        tk.Label(menu, text="Bienvenido al Sistema", font=("Arial", 16, "bold")).pack(
            pady=15
        )
        tk.Label(
            menu,
            text=f"Sesión Activa ID: {USUARIO_ACTUAL}",
            font=("Arial", 10, "italic"),
            fg="blue",
        ).pack(pady=5)

        # ---- VENTANA HISTORIAL CLINICO ----
        def ventana_historial():
            global PAUSAR_LECTURA
            PAUSAR_LECTURA = True
            print("[INFO] Lectura serial pausada por apertura de Historial.")

            win_hist = tk.Toplevel(menu)
            win_hist.title("Mi Historial Clínico")
            win_hist.geometry("650x350")
            win_hist.grab_set()

            def al_cerrar_historial():
                global PAUSAR_LECTURA
                PAUSAR_LECTURA = False
                print("[INFO] Lectura serial reanudada.")
                win_hist.destroy()

            win_hist.protocol("WM_DELETE_WINDOW", al_cerrar_historial)

            tk.Label(
                win_hist,
                text=f"Historial Clínico del Usuario: {USUARIO_ACTUAL}",
                font=("Arial", 12, "bold"),
            ).pack(pady=10)

            tabla = ttk.Treeview(
                win_hist, columns=("Nombre", "Pulso", "SpO2", "Fecha"), show="headings"
            )
            tabla.heading("Nombre", text="Nombre Paciente")
            tabla.heading("Pulso", text="Pulso (BPM)")
            tabla.heading("SpO2", text="SpO2 (%)")
            tabla.heading("Fecha", text="Fecha y Hora de Captura")

            tabla.column("Nombre", width=150)
            tabla.column("Pulso", width=100, anchor="center")
            tabla.column("SpO2", width=100, anchor="center")
            tabla.column("Fecha", width=180, anchor="center")
            tabla.pack(fill="both", expand=True, padx=10, pady=5)

            try:
                datos_db = obtener_historial_por_documento(USUARIO_ACTUAL)
                if not datos_db:
                    tk.Label(
                        win_hist,
                        text="No tienes registros médicos guardados aún.",
                        fg="red",
                    ).pack()

                for fila in datos_db:
                    try:
                        nombre_visual = desencriptar(str(fila[0]).strip())
                        pulso_des = desencriptar(str(fila[1]).strip())
                        spo2_des = desencriptar(str(fila[2]).strip())

                        if fila[3] is not None:
                            fecha_visual = fila[3].strftime("%d/%m/%Y %H:%M:%S")
                        else:
                            fecha_visual = "Sin fecha"

                        tabla.insert(
                            "",
                            "end",
                            values=(nombre_visual, pulso_des, spo2_des, fecha_visual),
                        )
                    except Exception as e_des:
                        print(f"[DEBUG HISTORIAL] Error interpretando fila: {e_des}")
                        tabla.insert(
                            "", "end", values=(fila[0], fila[1], fila[2], fila[3])
                        )
            except Exception as e:
                messagebox.showerror("Error al cargar historial", str(e))

        # ---- VENTANA GRÁFICA DE TENDENCIAS ----
        def ventana_grafica():
            global PAUSAR_LECTURA
            PAUSAR_LECTURA = True
            print("[INFO] Lectura serial pausada por apertura de Gráfica.")

            try:
                datos_db = obtener_datos_grafica(USUARIO_ACTUAL)

                if not datos_db:
                    messagebox.showinfo(
                        "Info", "No tienes datos suficientes para generar una gráfica."
                    )
                    PAUSAR_LECTURA = False
                    return

                fechas = []
                pulsos = []
                spo2_lista = []
                contador_aux = 1

                for fila in datos_db:
                    try:
                        p_texto = desencriptar(str(fila[1]).strip())
                        s_texto = desencriptar(str(fila[2]).strip())

                        if fila[0] is not None:
                            fecha_str = fila[0].strftime("%H:%M:%S")
                        else:
                            fecha_str = f"Histórico {contador_aux}"

                        fechas.append(fecha_str)
                        pulsos.append(float(p_texto))
                        spo2_lista.append(float(s_texto))
                        contador_aux += 1
                    except Exception as e_conv:
                        print(f"[DEBUG GRAFICA] Ignorando registro dañado: {e_conv}")
                        pass

                if len(pulsos) == 0:
                    messagebox.showwarning(
                        "Sin datos válidos", "Toma lecturas nuevas antes de graficar."
                    )
                    return

                plt.figure("Monitoreo en Tiempo Real", figsize=(9, 5))
                plt.clf()

                plt.plot(
                    fechas,
                    pulsos,
                    "-o",
                    label="Ritmo Cardíaco (BPM)",
                    color="red",
                    linewidth=2,
                )
                plt.plot(
                    fechas,
                    spo2_lista,
                    "-s",
                    label="Oxigenación (SpO2 %)",
                    color="blue",
                    linewidth=2,
                )

                plt.xlabel("Hora Exacta del Sensado")
                plt.ylabel("Constantes Vitales")
                plt.title(f"Evolución Médica - ID Paciente: {USUARIO_ACTUAL}")
                plt.grid(True, linestyle="--", alpha=0.6)
                plt.legend()
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.show()

            except Exception as e:
                messagebox.showerror("Error al graficar", str(e))
            finally:
                PAUSAR_LECTURA = False
                print("[INFO] Lectura serial reanudada tras cerrar gráfica.")

        def cerrar_sesion():
            global USUARIO_ACTUAL
            USUARIO_ACTUAL = None
            menu.destroy()
            entry_doc.delete(0, tk.END)
            entry_pass.delete(0, tk.END)
            root.deiconify()

        tk.Button(
            menu,
            text="Visualizar Mi Historial",
            width=25,
            font=("Arial", 11),
            command=ventana_historial,
        ).pack(pady=8)
        tk.Button(
            menu,
            text="Ver Gráfica de Tendencia",
            width=25,
            font=("Arial", 11),
            command=ventana_grafica,
        ).pack(pady=8)
        tk.Button(
            menu,
            text="Cerrar Sesión",
            width=15,
            bg="#dc3545",
            fg="white",
            command=cerrar_sesion,
        ).pack(pady=25)

    # -------------------------------------------------------------------------
    # LOGIN PRINCIPAL INDEPENDIENTE
    # -------------------------------------------------------------------------
    tk.Label(root, text="Control de Acceso", font=("Arial", 14, "bold")).pack(pady=10)

    tk.Label(root, text="Documento de Identidad:").pack(pady=2)
    entry_doc = tk.Entry(root, font=("Arial", 10))
    entry_doc.pack()

    tk.Label(root, text="Contraseña:").pack(pady=2)
    entry_pass = tk.Entry(root, show="*", font=("Arial", 10))
    entry_pass.pack()

    def ejecutar_login():
        global USUARIO_ACTUAL
        doc = entry_doc.get().strip()
        passwd = entry_pass.get().strip()

        if doc == "" or passwd == "":
            messagebox.showwarning(
                "Campos Incompletos", "Por favor ingresa tus credenciales."
            )
            return

        if validar_login(doc, passwd):
            USUARIO_ACTUAL = doc
            abrir_menu_principal()
        else:
            messagebox.showerror(
                "Acceso Denegado", "Documento o contraseña incorrectos."
            )

    frame_botones = tk.Frame(root)
    frame_botones.pack(pady=15)

    tk.Button(
        frame_botones,
        text="Registrarse",
        width=12,
        bg="#6c757d",
        fg="white",
        command=abrir_registro,
    ).pack(side="left", padx=5)
    tk.Button(
        frame_botones,
        text="Aceptar",
        width=12,
        bg="#007bff",
        fg="white",
        command=ejecutar_login,
    ).pack(side="left", padx=5)

    root.mainloop()


if __name__ == "__main__":
    iniciar_app()
