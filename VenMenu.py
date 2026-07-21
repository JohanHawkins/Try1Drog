import tkinter as tk
from tkinter import ttk
import os
from utils import centrar_ventana
from theme import (get_paleta, aplicar_estilos, crear_header, crear_boton,
                    crear_label)
import Inventario.Inventario as Inventario
import Ventas.Ventas as Ventas
import Registro
import Clientes.Clientes as Clientes
import Reportes.Reportes as Reportes
from Facturacion.facturacion import mostrar_ventana_facturacion
from Facturacion.config_empresa import mostrar_ventana_config

def crear_ventana_menu():
    paleta = get_paleta()
    ventana_menu = tk.Tk()
    ventana_menu.title("Drogs+ - Menú Principal")
    ventana_menu.resizable(True, True)
    ventana_menu.minsize(300, 200)
    ventana_menu.configure(bg=paleta["bg_principal"])

    icon_path = os.path.join("images", "cruz_azul.ico")
    if os.path.exists(icon_path):
        ventana_menu.iconbitmap(icon_path)

    aplicar_estilos(ventana_menu)
    centrar_ventana(ventana_menu)

    return ventana_menu

def abrir_inventario(ventana):
    ventana.destroy()
    Inventario.mostrar_ventana_inventario()

def abrir_ventas(ventana):
    ventana.destroy()
    Ventas.mostrar_ventana_ventas()

def abrir_registro(ventana):
    ventana.destroy()
    Registro.mostrar_ventana_registro()

def abrir_clientes(ventana):
    ventana.destroy()
    Clientes.mostrar_ventana_clientes()

def abrir_reportes(ventana):
    ventana.destroy()
    Reportes.mostrar_ventana_reportes()

def abrir_facturacion(ventana):
    ventana.destroy()
    mostrar_ventana_facturacion()

def abrir_config_dian(ventana):
    ventana.destroy()
    mostrar_ventana_config()

def mostrar_ventana_menu():
    ventana_menu = crear_ventana_menu()
    paleta = get_paleta()

    crear_header(ventana_menu, "Menú Principal")

    body = tk.Frame(ventana_menu, bg=paleta["bg_principal"])
    body.pack(fill="both", expand=True, padx=20, pady=15)

    crear_label(body, "Seleccione un módulo", "info").pack(pady=(0, 15))

    modulos = [
        ("📦  Gestión de Inventario", lambda: abrir_inventario(ventana_menu)),
        ("🛒  Punto de Venta", lambda: abrir_ventas(ventana_menu)),
        ("📄  Facturación Electrónica", lambda: abrir_facturacion(ventana_menu)),
        ("📋  Historial de Ventas", lambda: abrir_registro(ventana_menu)),
        ("👤  Clientes", lambda: abrir_clientes(ventana_menu)),
        ("📊  Reportes y Analítica", lambda: abrir_reportes(ventana_menu)),
        ("⚙  Configuración DIAN", lambda: abrir_config_dian(ventana_menu)),
    ]

    for texto, comando in modulos:
        btn = crear_boton(body, texto, comando, width=30)
        btn.configure(pady=12, font=("Segoe UI", 11, "bold"))
        btn.pack(pady=4)

    ventana_menu.update_idletasks()
    w = ventana_menu.winfo_reqwidth()
    h = ventana_menu.winfo_reqheight()
    ventana_menu.geometry(f"{w}x{h}")
    centrar_ventana(ventana_menu)

    ventana_menu.mainloop()
