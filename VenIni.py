import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
from utils import centrar_ventana
from theme import (get_paleta, aplicar_estilos, crear_header, crear_boton,
                    crear_entry, crear_label, MODO_OSCURO)
import VenMenu

def acceder(serial, ventana):
    ventana.destroy()
    VenMenu.mostrar_ventana_menu()

def mostrar_ventana():
    cargar_config()
    paleta = get_paleta()

    ventana = tk.Tk()
    ventana.title("Drogs+")
    ventana.geometry("420x380")
    ventana.resizable(False, False)
    ventana.configure(bg=paleta["bg_principal"])

    icon_path = os.path.join("images", "cruz_azul.ico")
    if os.path.exists(icon_path):
        ventana.iconbitmap(icon_path)

    aplicar_estilos(ventana)
    centrar_ventana(ventana)

    crear_header(ventana, "Drogs+")

    body = tk.Frame(ventana, bg=paleta["bg_frame"])
    body.pack(fill="both", expand=True, padx=30, pady=20)

    try:
        image_path = os.path.join("images", "cruz_azul.png")
        image = Image.open(image_path)
        image = image.resize((80, 80), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        img_label = tk.Label(body, image=photo, bg=paleta["bg_frame"])
        img_label.image = photo
        img_label.pack(pady=(10, 5))
    except Exception:
        pass

    crear_label(body, "Sistema de Gestión para Droguería", "subtitle").pack(pady=(0, 15))
    crear_label(body, "Ingrese su serial de acceso", "info").pack()

    campo_frame = tk.Frame(body, bg=paleta["bg_frame"])
    campo_frame.pack(pady=15)

    campo_serial = crear_entry(campo_frame, width=25, font=("Segoe UI", 12))
    campo_serial.pack(padx=5)
    campo_serial.focus_set()

    btn_frame = tk.Frame(body, bg=paleta["bg_frame"])
    btn_frame.pack(pady=10)

    crear_boton(btn_frame, "Acceder", lambda: acceder(campo_serial.get(), ventana)).pack()

    campo_serial.bind("<Return>", lambda e: acceder(campo_serial.get(), ventana))

    ventana.mainloop()

from theme import cargar_config
cargar_config()
mostrar_ventana()
