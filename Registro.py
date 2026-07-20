import tkinter as tk
import pandas as pd
import os
from tkinter import filedialog, messagebox
from fpdf import FPDF

def centrar_ventana(ventana):
    ventana.update_idletasks()
    width = ventana.winfo_width()
    height = ventana.winfo_height()
    x = (ventana.winfo_screenwidth() // 2) - (width // 2)
    y = (ventana.winfo_screenheight() // 2) - (height // 2)
    ventana.geometry(f'{width}x{height}+{x}+{y}')

def volver_al_menu(ventana):
    ventana.destroy()
    import VenMenu
    VenMenu.mostrar_ventana_menu()

def mostrar_tabla_registros(frame, datos, start_row, end_row):
    for widget in frame.winfo_children():
        widget.destroy()

    for col_idx, col_name in enumerate(datos.columns):
        encabezado = tk.Label(frame, text=col_name, font=("Arial", 10, "bold"), borderwidth=1, relief="solid")
        encabezado.grid(row=0, column=col_idx, sticky="nsew")

    for row_idx, row_data in enumerate(datos.values[start_row:end_row]):
        for col_idx, cell_data in enumerate(row_data):
            celda = tk.Label(frame, text=cell_data, font=("Arial", 10), borderwidth=1, relief="solid")
            celda.grid(row=row_idx + 1, column=col_idx, sticky="nsew")

def aplicar_filtro(datos, nombre, fecha, hora):
    if nombre:
        datos = datos[datos['Nombre Producto'].str.contains(nombre, case=False, na=False)]
    if fecha:
        datos = datos[datos['Fecha'].astype(str).str.contains(fecha, na=False)]
    if hora:
        datos = datos[datos['Hora'].astype(str).str.contains(hora, na=False)]
    return datos

def guardar_registros():
    # Selección de formato
    formato = filedialog.asksaveasfilename(defaultextension=".xlsx", 
                                           filetypes=[("Excel files", "*.xlsx"),
                                                      ("Text files", "*.txt"),
                                                      ("PDF files", "*.pdf")])
    
    if not formato:
        return  # Salir si el usuario cancela

    extension = os.path.splitext(formato)[1].lower()
    
    if extension == ".xlsx":
        datos_filtrados.to_excel(formato, index=False)
    elif extension == ".txt":
        datos_filtrados.to_csv(formato, index=False, sep='\t')
    elif extension == ".pdf":
        try:
            # Crear el archivo PDF
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            # Agregar encabezados
            encabezados = list(datos_filtrados.columns)
            pdf.set_font("Arial", style="B", size=12)
            for encabezado in encabezados:
                pdf.cell(40, 10, encabezado, border=1)
            pdf.ln()

            # Agregar filas de datos
            pdf.set_font("Arial", size=10)
            for row in datos_filtrados.values:
                for cell in row:
                    pdf.cell(40, 10, str(cell), border=1)
                pdf.ln()

            # Guardar el archivo PDF
            pdf.output(formato)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo como PDF: {e}")
            return
    else:
        messagebox.showerror("Error", "Formato no soportado.")

    messagebox.showinfo("Éxito", f"Registros guardados en {formato}")

# Definir variables de paginación a nivel de módulo
current_page = 0
rows_per_page = 20

# Definir frame_tabla y datos_filtrados como variables globales
def mostrar_ventana_registro():
    global frame_tabla, datos_filtrados, datos, current_page, datos
    
    ventana_registro = tk.Tk()
    ventana_registro.title("Registro")
    ventana_registro.geometry("600x400")
    ventana_registro.resizable(False, False)

    excel_path = "Ventas/registros_compra.xlsx"
    if os.path.exists(excel_path):
        datos = pd.read_excel(excel_path)

        icon_path = os.path.join("images", "cruz_azul.ico")
        ventana_registro.iconbitmap(icon_path)

        centrar_ventana(ventana_registro)

        contenedor = tk.Frame(ventana_registro)
        contenedor.pack(expand=False, fill=tk.BOTH)

        # Crear frame para los filtros
        frame_filtros = tk.Frame(contenedor, padx=10, pady=5)
        frame_filtros.pack(anchor="center")

        tk.Label(frame_filtros, text="Producto:").grid(row=0, column=0)
        entrada_nombre = tk.Entry(frame_filtros, width=15)
        entrada_nombre.grid(row=0, column=1)

        tk.Label(frame_filtros, text="Fecha (AA-MM-DD):").grid(row=0, column=2)
        entrada_fecha = tk.Entry(frame_filtros, width=12)
        entrada_fecha.grid(row=0, column=3)

        tk.Label(frame_filtros, text="Hora (HH:MM):").grid(row=0, column=4)
        entrada_hora = tk.Entry(frame_filtros, width=10)
        entrada_hora.grid(row=0, column=5)

        # Crear un frame para la tabla y el scrollbar
        frame_tabla_scroll = tk.Frame(contenedor)
        frame_tabla_scroll.pack(pady=10, padx=10, fill=tk.X)

        canvas = tk.Canvas(frame_tabla_scroll)
        frame_tabla = tk.Frame(canvas)
        scrollbar = tk.Scrollbar(frame_tabla_scroll, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def actualizar_tabla(start_row=0, end_row=20):
            mostrar_tabla_registros(frame_tabla, datos_filtrados, start_row, end_row)

        def mostrar_pagina(pagina):
            global current_page
            current_page = pagina
            start_row = current_page * rows_per_page
            end_row = start_row + rows_per_page

            if end_row > len(datos_filtrados):
                end_row = len(datos_filtrados)

            if start_row >= len(datos_filtrados):
                current_page = (len(datos_filtrados) - 1) // rows_per_page

            actualizar_tabla(start_row, end_row)

        def siguiente_pagina():
            mostrar_pagina(current_page + 1)

        def pagina_anterior():
            mostrar_pagina(current_page - 1)

        # Frame para los botones de paginación
        frame_botones_superiores = tk.Frame(contenedor)
        frame_botones_superiores.pack(side=tk.TOP, pady=5)

        boton_anterior = tk.Button(frame_botones_superiores, text="<< Anterior", command=pagina_anterior)
        boton_anterior.pack(side=tk.LEFT, padx=(0, 5))

        boton_siguiente = tk.Button(frame_botones_superiores, text="Siguiente >>", command=siguiente_pagina)
        boton_siguiente.pack(side=tk.LEFT)

        # Mensaje de error de filtro
        mensaje_error = tk.Label(ventana_registro, text="", font=("Arial", 10), fg="red")
        mensaje_error.pack(pady=10)

        def filtrar_datos():
            nombre = entrada_nombre.get()
            fecha = entrada_fecha.get()
            hora = entrada_hora.get()
            global datos_filtrados
            datos_filtrados = aplicar_filtro(datos, nombre, fecha, hora)

            if datos_filtrados.empty:
                if nombre:
                    mensaje_error.config(text=f"No se ha encontrado el filtro 'Producto: {nombre}'")
                elif fecha:
                    mensaje_error.config(text=f"No se ha encontrado el filtro 'Fecha: {fecha}'")
                elif hora:
                    mensaje_error.config(text=f"No se ha encontrado el filtro 'Hora: {hora}'")
                mostrar_tabla_registros(frame_tabla, datos)
            else:
                mensaje_error.config(text="")
                mostrar_pagina(0)

        datos_filtrados = datos
        mostrar_tabla_registros(frame_tabla, datos, 0, 20)

        canvas.create_window((0, 0), window=frame_tabla, anchor="nw")

        # Frame para los botones de filtro y volver
        frame_botones_inferiores = tk.Frame(contenedor)
        frame_botones_inferiores.pack(side=tk.BOTTOM, pady=10)

        boton_guardar = tk.Button(frame_botones_inferiores, text="Guardar", command=guardar_registros)
        boton_guardar.pack(side=tk.RIGHT, padx=(10, 0))

        boton_eliminar = tk.Button(frame_botones_inferiores, text="Eliminar Registro", command=eliminar_registro)
        boton_eliminar.pack(side=tk.RIGHT, padx=(220, 0))

        boton_filtrar = tk.Button(frame_botones_inferiores, text="Aplicar Filtro", command=filtrar_datos)
        boton_filtrar.pack(side=tk.RIGHT, padx=(10, 0))

        boton_volver = tk.Button(frame_botones_inferiores, text="Volver al menú", command=lambda: volver_al_menu(ventana_registro))
        boton_volver.pack(side=tk.LEFT, padx=(0, 0))

    else:
        mensaje_error = tk.Label(ventana_registro, text="Archivo 'registros_compra.xlsx' no encontrado.", font=("Arial", 10), fg="red")
        mensaje_error.pack(pady=10)

    ventana_registro.mainloop()

# Función para eliminar registros
def eliminar_registro():
    global datos_filtrados, datos, current_page

    if not messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas eliminar los registros filtrados?"):
        return

    if datos_filtrados.empty:
        messagebox.showerror("Error", "No hay datos para eliminar.")
        return

    try:
        # Eliminar los registros filtrados del DataFrame original
        indices_a_eliminar = datos_filtrados.index
        datos = datos.drop(indices_a_eliminar).reset_index(drop=True)
        datos_filtrados = datos.copy()
        current_page = 0

        # Guardar los cambios en el archivo original
        excel_path = "Ventas/registros_compra.xlsx"
        datos.to_excel(excel_path, index=False)
        messagebox.showinfo("Éxito", "Los registros han sido eliminados correctamente.")
        mostrar_tabla_registros(frame_tabla, datos_filtrados, 0, rows_per_page)
    except Exception as e:
        messagebox.showerror("Error", f"Error al eliminar los registros: {e}")
