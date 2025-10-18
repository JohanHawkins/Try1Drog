import tkinter as tk
from tkcalendar import DateEntry
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import os
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from tkinter import ttk, messagebox
from Inventario.Editar_Producto import mostrar_ventana_editar  # Importa la función
import random
import string

ventana_editar_abierta = False
# Simulamos una lista de productos almacenados (puedes reemplazar esto con la base de datos real o almacenamiento)
productos_guardados = []

def centrar_ventana(ventana):
    ventana.update_idletasks()
    width = ventana.winfo_width()
    height = ventana.winfo_height()
    x = (ventana.winfo_screenwidth() // 2) - (width // 2)
    y = (ventana.winfo_screenheight() // 2) - (height // 2)
    ventana.geometry('{}x{}+{}+{}'.format(width, height, x, y))

def volver_al_menu(ventana):
    ventana.destroy()
    import VenMenu
    VenMenu.mostrar_ventana_menu()

def solo_enteros(char):
    return char.isdigit()

def solo_reales(char, texto):
    if char.isdigit() or (char == '.' and '.' not in texto):
        return True
    return False

def calcular_diferencia_meses(fecha_entrega, fecha_vencimiento):
    """Calcula la diferencia en meses entre dos fechas."""
    return relativedelta(fecha_vencimiento, fecha_entrega).months + relativedelta(fecha_vencimiento, fecha_entrega).years * 12

def actualizar_color_categoria(event=None):
    """Actualiza el color del rectángulo según la diferencia de meses."""
    fecha_entrega = date_entry_entrega.get_date()
    fecha_vencimiento = date_entry_vencimiento.get_date()

    diferencia_meses = calcular_diferencia_meses(fecha_entrega, fecha_vencimiento)
    
    if diferencia_meses > 12:
        canvas_categoria.config(bg="green")
    elif 6 <= diferencia_meses <= 12:
        canvas_categoria.config(bg="yellow")
    else:
        canvas_categoria.config(bg="red")

def formato_pesos(valor):
    """Formatea el valor en formato de Pesos Colombianos (COP)."""
    return f"${float(valor):,.2f} COP"

def ajustar_ancho_columnas(ws):
    """Ajusta el ancho de las columnas según el contenido más largo."""
    for column_cells in ws.columns:
        max_length = 0
        column = column_cells[0].column_letter  # Obtener la letra de la columna
        for cell in column_cells:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = max_length + 2  # Un poco más de espacio
        ws.column_dimensions[column].width = adjusted_width

def aplicar_color_condicional(archivo_excel):
    """Aplica color condicional en la columna 'Categoría' según el valor."""
    wb = load_workbook(archivo_excel)
    ws = wb.active
    
    # Recorrer la columna de "Categoría" (suponemos que está en la columna 'D')
    for row in ws.iter_rows(min_row=2, min_col=4, max_col=4):  # Columna D (4ta columna)
        for cell in row:
            if cell.value == "Red":
                cell.fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
            elif cell.value == "Yellow":
                cell.fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
            elif cell.value == "Green":
                cell.fill = PatternFill(start_color="00FF00", end_color="00FF00", fill_type="solid")

    # Ajustar el ancho de las columnas
    ajustar_ancho_columnas(ws)

    wb.save(archivo_excel)

def generar_codigo_unico():
    """Genera un código alfanumérico de 6 caracteres (a-z, 0-9)."""
    while True:
        codigo = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        if not any(producto['codigo'] == codigo for producto in productos_guardados):
            return codigo

def mostrar_codigo_producto():
    """Muestra el código alfanumérico cuando se ingresa el nombre del producto."""
    if entry_nombre.get():
        codigo = generar_codigo_unico()
        entry_identificador.config(state="normal")  # Permite modificar el campo temporalmente
        entry_identificador.delete(0, tk.END)  # Borra cualquier valor anterior
        entry_identificador.insert(0, codigo)  # Muestra el nuevo código
        entry_identificador.config(state="readonly")  # Vuelve a hacer el campo de solo lectura

def guardar_datos():
    nombre_producto = entry_nombre.get().strip()
    cantidad_producto = entry_cantidad.get()
    precio_producto = float(entry_precio.get())  # Guardar el precio como un número flotante
    
    # Obtener el color de la categoría
    categoria_color = canvas_categoria.cget("bg")
    if categoria_color == "green":
        categoria = "Verde"
    elif categoria_color == "yellow":
        categoria = "Amarillo"
    elif categoria_color == "red":
        categoria = "Rojo"
    else:
        categoria = "Sin definir"  # Por si acaso el color es diferente

    # Obtener la fecha de vencimiento
    fecha_vencimiento = date_entry_vencimiento.get_date()

    codigo = entry_identificador.get()

    # Crear un diccionario con los datos
    datos = {
        "Nombre Producto": [nombre_producto + ": " + codigo],
        "Cantidad Producto": [cantidad_producto],
        "Precio Producto (COP)": [precio_producto],
        "Categoria": [categoria],  # Guardar la categoría con el color adecuado
        "Fecha Vencimiento": [fecha_vencimiento.strftime("%d/%m/%Y")]  # Formato de fecha como string
    }

    # Ruta para guardar el archivo en la carpeta 'Inventario'
    carpeta_inventario = "Inventario"
    
    # Crear la carpeta si no existe
    if not os.path.exists(carpeta_inventario):
        os.makedirs(carpeta_inventario)

    archivo_excel = os.path.join(carpeta_inventario, "inventario_productos.xlsx")
    
    # Verificar si el archivo ya existe y si el nombre del producto ya está en el inventario
    if os.path.exists(archivo_excel):
        df_existente = pd.read_excel(archivo_excel)
        # Verificar si el nombre del producto ya existe (sin importar mayúsculas)
        if str(nombre_producto).lower() in df_existente['Nombre Producto'].str.lower().values:
            confirmacion = tk.messagebox.askyesno("Confirmación", f"El producto '{nombre_producto}' ya existe. ¿Deseas agregarlo de todos modos?")
            if not confirmacion:
                print("Datos no guardados.")
                return  # No guardar los datos si el usuario cancela
            
        # Agregar una nueva fila
        df_nuevo = pd.DataFrame(datos)
        df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
        df_final.to_excel(archivo_excel, index=False)
    else:
        # Si el archivo no existe, se crea uno nuevo
        df = pd.DataFrame(datos)
        df.to_excel(archivo_excel, index=False)

    # Aplicar color condicional a la columna de categoría y ajustar ancho de columnas
    aplicar_color_condicional(archivo_excel)

    print("Datos guardados correctamente")
    tk.messagebox.showinfo("Éxito", "Los datos se han guardado correctamente.")

def mostrar_ventana_inventario():
    global ventana_editar_abierta
    if ventana_editar_abierta:
        messagebox.showwarning("Advertencia", "La ventana de edición ya está abierta.")
        return

    ventana_inventario = tk.Tk()
    ventana_inventario.title("Inventario")
    ventana_inventario.geometry("350x300")
    ventana_inventario.resizable(False, False)

    ventana_inventario.grab_set()  # Previene la interacción con ventanas anteriores

    # Establecer el icono de la ventana
    icon_path = os.path.join("images", "cruz_azul.ico")
    ventana_inventario.iconbitmap(icon_path)

    # Centramos la ventana
    centrar_ventana(ventana_inventario)

    frame_formulario = tk.Frame(ventana_inventario)
    frame_formulario.pack(padx=10, pady=10)

    # Campo para Nombre Producto
    label_nombre = tk.Label(frame_formulario, text="Nombre Producto:")
    label_nombre.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
    global entry_nombre
    entry_nombre = tk.Entry(frame_formulario)
    entry_nombre.grid(row=0, column=1, padx=5, pady=5)
    entry_nombre.bind("<KeyRelease>", lambda event: mostrar_codigo_producto())  # Actualiza el código cuando se ingresa un nombre

    # Campo para Identificador (solo lectura)
    label_identificador = tk.Label(frame_formulario, text="Identificador:")
    label_identificador.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
    global entry_identificador
    entry_identificador = tk.Entry(frame_formulario, state="readonly")
    entry_identificador.grid(row=1, column=1, padx=5, pady=5)

    # Campo para Cantidad Producto
    label_cantidad = tk.Label(frame_formulario, text="Cantidad Producto:")
    label_cantidad.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
    vcmd_entero = (ventana_inventario.register(solo_enteros), '%S')
    global entry_cantidad
    entry_cantidad = tk.Entry(frame_formulario, validate="key", validatecommand=vcmd_entero)
    entry_cantidad.grid(row=2, column=1, padx=5, pady=5)

    # Campo para Precio Producto
    label_precio = tk.Label(frame_formulario, text="Precio Producto (COP):")
    label_precio.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
    vcmd_real = (ventana_inventario.register(solo_reales), '%S', '%P')
    global entry_precio
    entry_precio = tk.Entry(frame_formulario, validate="key", validatecommand=vcmd_real)
    entry_precio.grid(row=3, column=1, padx=5, pady=5)

    # Campo para seleccionar Fecha de Entrega
    global date_entry_entrega
    label_fecha_entrega = tk.Label(frame_formulario, text="Fecha de Entrega:")
    label_fecha_entrega.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
    date_entry_entrega = DateEntry(frame_formulario, date_pattern='dd/mm/yyyy', width=16, background='darkblue',
                                   foreground='white', borderwidth=2, state='readonly')  # Solo lectura
    date_entry_entrega.grid(row=4, column=1, padx=5, pady=5)
    date_entry_entrega.bind("<<DateEntrySelected>>", actualizar_color_categoria)

    # Campo para seleccionar Fecha de Vencimiento
    global date_entry_vencimiento
    label_fecha_vencimiento = tk.Label(frame_formulario, text="Fecha de Vencimiento:")
    label_fecha_vencimiento.grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
    date_entry_vencimiento = DateEntry(frame_formulario, date_pattern='dd/mm/yyyy', width=16, background='darkblue',
                                       foreground='white', borderwidth=2, state='readonly')  # Solo lectura
    date_entry_vencimiento.grid(row=5, column=1, padx=5, pady=5)
    date_entry_vencimiento.bind("<<DateEntrySelected>>", actualizar_color_categoria)

    # Rectángulo para la categoría
    label_categoria = tk.Label(frame_formulario, text="Categoria:")
    label_categoria.grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
    global canvas_categoria
    canvas_categoria = tk.Canvas(frame_formulario, width=120, height=15, bg="white")
    canvas_categoria.grid(row=6, column=1, padx=5, pady=5)

    # Inicializar el color del rectángulo al cargar la ventana
    actualizar_color_categoria()

    # Botón para volver
    boton_volver = tk.Button(ventana_inventario, text="Volver al menú", command=lambda: volver_al_menu(ventana_inventario))
    boton_volver.pack(side=tk.LEFT, padx=10, pady=10)

    # Botón para guardar datos
    boton_guardar = tk.Button(ventana_inventario, text="Guardar", command=guardar_datos)
    boton_guardar.pack(side=tk.RIGHT, padx=10, pady=10)

    # Botón para editar datos (sin funcionalidad aún)
    boton_buscar = tk.Button(ventana_inventario, text="Buscar", command=mostrar_ventana_editar)  # Llama a la función mostrar_ventana_editar
    boton_buscar.pack(side=tk.RIGHT, padx=10, pady=10)

    ventana_inventario.mainloop()