import tkinter as tk
from tkinter import ttk
import os
import Inventario.Inventario as Inventario
import Ventas.Ventas as Ventas
import Registro
import Clientes.Clientes as Clientes
import Reportes.Reportes as Reportes

def crear_ventana_menu():
    ventana_menu = tk.Tk()
    ventana_menu.title("Menú")
    ventana_menu.geometry("300x300")
    ventana_menu.resizable(width=False, height=False)

    x = (ventana_menu.winfo_screenwidth() // 2) - (300 // 2)
    y = (ventana_menu.winfo_screenheight() // 2) - (300 // 2)
    ventana_menu.geometry('+{}+{}'.format(x, y))

    icon_path = os.path.join("images", "cruz_azul.ico")
    ventana_menu.iconbitmap(icon_path)

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

def mostrar_ventana_menu():
    ventana_menu = crear_ventana_menu()

    label_titulo = ttk.Label(ventana_menu, text="Menú Principal", font=("Helvetica", 16))
    label_titulo.pack(pady=5)

    texto_seleccion = tk.Label(ventana_menu, text="Seleccione una opción", font=("Helvetica", 10), fg="#800000")
    texto_seleccion.pack()

    boton_gestion_inventario = tk.Button(ventana_menu, text="Gestion de Inventario", font=("Helvetica", 12), command=lambda: abrir_inventario(ventana_menu))
    boton_gestion_inventario.pack(pady=5, padx=20)

    boton_ventas = tk.Button(ventana_menu, text="Ventas", font=("Helvetica", 12), command=lambda: abrir_ventas(ventana_menu))
    boton_ventas.pack(pady=5, padx=20)

    boton_registros = tk.Button(ventana_menu, text="Registros", font=("Helvetica", 12), command=lambda: abrir_registro(ventana_menu))
    boton_registros.pack(pady=5, padx=20)

    boton_clientes = tk.Button(ventana_menu, text="Clientes", font=("Helvetica", 12), command=lambda: abrir_clientes(ventana_menu))
    boton_clientes.pack(pady=5, padx=20)

    boton_reportes = tk.Button(ventana_menu, text="Reportes", font=("Helvetica", 12), command=lambda: abrir_reportes(ventana_menu))
    boton_reportes.pack(pady=5, padx=20)

    x = (ventana_menu.winfo_screenwidth() // 2) - (300 // 2)
    y = (ventana_menu.winfo_screenheight() // 2) - (300 // 2)
    ventana_menu.geometry('+{}+{}'.format(x, y))

    ventana_menu.mainloop()
