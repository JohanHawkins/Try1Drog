import tkinter as tk
from tkinter import ttk
import os

def crear_ventana_menu():
    ventana_menu = tk.Tk()
    ventana_menu.title("Menú")
    ventana_menu.geometry("300x500")  # Reducir el tamaño de la ventana
    ventana_menu.resizable(width=False, height=False)  # Bloquear el redimensionamiento

    # Centrar la ventana en la pantalla
    x = (ventana_menu.winfo_screenwidth() // 2) - (300 // 2)
    y = (ventana_menu.winfo_screenheight() // 2) - (500 // 2)
    ventana_menu.geometry('+{}+{}'.format(x, y))

    icon_path = os.path.join("images", "cruz_azul.ico")
    ventana_menu.iconbitmap(icon_path)

    return ventana_menu

def abrir_inventario(ventana):
    ventana.destroy()
    import Inventario.Inventario as Inventario  # Cambia aquí la importación
    Inventario.mostrar_ventana_inventario()

def abrir_ventas(ventana):
    ventana.destroy()
    import Ventas.Ventas as Ventas
    Ventas.mostrar_ventana_ventas()

def abrir_registro(ventana):
    ventana.destroy()
    import Registro
    Registro.mostrar_ventana_registro()

def mostrar_ventana_menu():
    ventana_menu = crear_ventana_menu()
    ventana_menu.geometry("300x200")  # Reducir el tamaño de la ventana a 300x200

    label_titulo = ttk.Label(ventana_menu, text="Menú Principal", font=("Helvetica", 16))
    label_titulo.pack(pady=5)

    # Texto "Seleccione una opción" en color rojo y tamaño de letra más pequeño
    texto_seleccion = tk.Label(ventana_menu, text="Seleccione una opción", font=("Helvetica", 10), fg="#800000")
    texto_seleccion.pack()

    # Calcula el ancho de los botones como el 70% del ancho de la ventana menos un pequeño margen
    button_width = int(ventana_menu.winfo_width() * 0.7) - 40  # Reducimos 40 píxeles

    # Boton Gestion de Inventario
    boton_gestion_inventario = tk.Button(ventana_menu, text="Gestion de Inventario", width=button_width, font=("Helvetica", 12), command=lambda: abrir_inventario(ventana_menu))
    boton_gestion_inventario.pack(pady=5, padx=20)  # Añade 20 píxeles de espacio a cada lado

    # Boton Ventas
    boton_ventas = tk.Button(ventana_menu, text="Ventas", width=button_width, font=("Helvetica", 12), command=lambda: abrir_ventas(ventana_menu))
    boton_ventas.pack(pady=5, padx=20)  # Añade 20 píxeles de espacio a cada lado

    # Boton Registros
    boton_registros = tk.Button(ventana_menu, text="Registros", width=button_width, font=("Helvetica", 12), command=lambda: abrir_registro(ventana_menu))
    boton_registros.pack(pady=5, padx=20)  # Añade 20 píxeles de espacio a cada lado

    # Centra la ventana en la pantalla
    x = (ventana_menu.winfo_screenwidth() // 2) - (300 // 2)
    y = (ventana_menu.winfo_screenheight() // 2) - (200 // 2)
    ventana_menu.geometry('+{}+{}'.format(x, y))

    ventana_menu.mainloop()
