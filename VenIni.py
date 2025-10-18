import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

def centrar_ventana(ventana):
    ventana.update_idletasks()
    width = ventana.winfo_width()
    height = ventana.winfo_height()
    x = (ventana.winfo_screenwidth() // 2) - (width // 2)
    y = (ventana.winfo_screenheight() // 2) - (height // 2)
    ventana.geometry('{}x{}+{}+{}'.format(width, height, x, y))

def crear_ventana():
    ventana = tk.Tk()
    ventana.title("Drogs+")
    ventana.geometry("400x260")
    ventana.resizable(width=False, height=False)  # Bloquea el redimensionamiento

    icon_path = os.path.join("images", "cruz_azul.ico")
    ventana.iconbitmap(icon_path)

    return ventana

def cargar_imagen():
    image_path = os.path.join("images", "cruz_azul.png")
    image = Image.open(image_path)
    image = image.resize((100, 100), Image.LANCZOS)
    photo = ImageTk.PhotoImage(image)
    return photo

def acceder(serial, ventana):
    # Aquí puedes hacer algo con el serial, como verificarlo o procesarlo
    print("Serial ingresado:", serial)

    # Cerrar la ventana actual
    ventana.destroy()

    # Importar y mostrar la nueva ventana
    import VenMenu
    VenMenu.mostrar_ventana_menu()

def mostrar_ventana():
    ventana = crear_ventana()
    centrar_ventana(ventana)
    photo = cargar_imagen()

    label_imagen = tk.Label(ventana, image=photo)
    label_imagen.pack(pady=10)

    texto_bienvenida = tk.Label(ventana, text="Bienvenido a Drogs+", font=("Helvetica", 16))
    texto_bienvenida.pack(pady=5)

    texto_serial = tk.Label(ventana, text="Introduzca su serial", font=("Helvetica", 12), fg="red")
    texto_serial.pack()

    marco = ttk.Frame(ventana)
    marco.pack(pady=10)

    campo_serial = ttk.Entry(marco, width=20)
    campo_serial.grid(row=0, column=0, padx=5)

    boton_acceder = ttk.Button(marco, text="Acceder", command=lambda: acceder(campo_serial.get(), ventana))
    boton_acceder.grid(row=0, column=1, padx=5)

    ventana.mainloop()

mostrar_ventana()