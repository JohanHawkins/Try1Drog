import tkinter as tk
from tkcalendar import DateEntry
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import os
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from tkinter import ttk, messagebox
from Inventario.Editar_Producto import mostrar_ventana_editar
import random
import string
from utils import centrar_ventana
from theme import (get_paleta, aplicar_estilos, crear_header, crear_boton,
                    crear_entry, crear_label, crear_card, crear_alerta)

def verificar_vencimientos():
    archivo_excel = os.path.join("Inventario", "inventario_productos.xlsx")
    if not os.path.exists(archivo_excel):
        return []
    try:
        df = pd.read_excel(archivo_excel)
        if 'Fecha Vencimiento' not in df.columns:
            return []
        hoy = datetime.now()
        alertas = []
        for _, row in df.iterrows():
            try:
                fecha_str = str(row['Fecha Vencimiento'])
                fecha_ven = datetime.strptime(fecha_str, "%d/%m/%Y")
                dias = (fecha_ven - hoy).days
                if dias < 0:
                    alertas.append(("rojo", f"VENCIDO: {row['Nombre Producto']}"))
                elif dias <= 30:
                    alertas.append(("rojo", f"Vence en {dias} días: {row['Nombre Producto']}"))
                elif dias <= 60:
                    alertas.append(("amarillo", f"Vence en {dias} días: {row['Nombre Producto']}"))
                elif dias <= 90:
                    alertas.append(("verde", f"Vence en {dias} días: {row['Nombre Producto']}"))
            except (ValueError, TypeError):
                continue
        return alertas
    except Exception:
        return []

def verificar_stock_minimo():
    archivo_excel = os.path.join("Inventario", "inventario_productos.xlsx")
    if not os.path.exists(archivo_excel):
        return []
    try:
        df = pd.read_excel(archivo_excel)
        if 'Cantidad Producto' not in df.columns or 'Stock Minimo' not in df.columns:
            return []
        bajos = []
        for _, row in df.iterrows():
            try:
                cantidad = int(row['Cantidad Producto'])
                minimo = int(row['Stock Minimo'])
                if cantidad <= minimo:
                    bajos.append(("amarillo", f"Stock bajo: {row['Nombre Producto']} ({cantidad}/{minimo})"))
            except (ValueError, TypeError):
                continue
        return bajos
    except Exception:
        return []

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
    return relativedelta(fecha_vencimiento, fecha_entrega).months + relativedelta(fecha_vencimiento, fecha_entrega).years * 12

def actualizar_color_categoria(event=None):
    paleta = get_paleta()
    fecha_entrega = date_entry_entrega.get_date()
    fecha_vencimiento = date_entry_vencimiento.get_date()
    diferencia_meses = calcular_diferencia_meses(fecha_entrega, fecha_vencimiento)
    if diferencia_meses > 12:
        canvas_categoria.config(bg=paleta["alerta_verde"])
    elif 6 <= diferencia_meses <= 12:
        canvas_categoria.config(bg=paleta["alerta_amarillo"])
    else:
        canvas_categoria.config(bg=paleta["alerta_rojo"])

def ajustar_ancho_columnas(ws):
    for column_cells in ws.columns:
        max_length = 0
        column = column_cells[0].column_letter
        for cell in column_cells:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = max_length + 2
        ws.column_dimensions[column].width = adjusted_width

def aplicar_color_condicional(archivo_excel):
    wb = load_workbook(archivo_excel)
    ws = wb.active
    for row in ws.iter_rows(min_row=2, min_col=4, max_col=4):
        for cell in row:
            if cell.value == "Red":
                cell.fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
            elif cell.value == "Yellow":
                cell.fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
            elif cell.value == "Green":
                cell.fill = PatternFill(start_color="00FF00", end_color="00FF00", fill_type="solid")
    ajustar_ancho_columnas(ws)
    wb.save(archivo_excel)

def generar_codigo_unico():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

def mostrar_codigo_producto():
    if entry_nombre.get():
        codigo = generar_codigo_unico()
        entry_identificador.config(state="normal")
        entry_identificador.delete(0, tk.END)
        entry_identificador.insert(0, codigo)
        entry_identificador.config(state="readonly")

def guardar_datos():
    nombre_producto = entry_nombre.get().strip()
    cantidad_producto = entry_cantidad.get()
    precio_producto = entry_precio.get().strip()

    if not nombre_producto:
        tk.messagebox.showwarning("Advertencia", "Debe ingresar el nombre del producto.")
        return
    if not cantidad_producto:
        tk.messagebox.showwarning("Advertencia", "Debe ingresar la cantidad del producto.")
        return
    if not precio_producto:
        tk.messagebox.showwarning("Advertencia", "Debe ingresar el precio del producto.")
        return

    try:
        precio_producto = float(precio_producto)
    except ValueError:
        tk.messagebox.showerror("Error", "El precio ingresado no es un número válido.")
        return

    cantidad_producto = int(cantidad_producto)
    stock_minimo = entry_stock_minimo.get().strip()
    stock_minimo = int(stock_minimo) if stock_minimo else 0

    paleta = get_paleta()
    categoria_color = canvas_categoria.cget("bg")
    if categoria_color == paleta["alerta_verde"]:
        categoria = "Verde"
    elif categoria_color == paleta["alerta_amarillo"]:
        categoria = "Amarillo"
    elif categoria_color == paleta["alerta_rojo"]:
        categoria = "Rojo"
    else:
        categoria = "Sin definir"

    fecha_vencimiento = date_entry_vencimiento.get_date()
    codigo = entry_identificador.get()
    unidad = entry_unidad.get().strip() or "Unidad"

    datos = {
        "Nombre Producto": [nombre_producto + ": " + codigo],
        "Cantidad Producto": [cantidad_producto],
        "Precio Producto (COP)": [precio_producto],
        "Categoria": [categoria],
        "Fecha Vencimiento": [fecha_vencimiento.strftime("%d/%m/%Y")],
        "Stock Minimo": [stock_minimo],
        "Unidad": [unidad]
    }

    carpeta_inventario = "Inventario"
    if not os.path.exists(carpeta_inventario):
        os.makedirs(carpeta_inventario)

    archivo_excel = os.path.join(carpeta_inventario, "inventario_productos.xlsx")

    if os.path.exists(archivo_excel):
        df_existente = pd.read_excel(archivo_excel)
        if str(nombre_producto).lower() in df_existente['Nombre Producto'].str.lower().values:
            confirmacion = tk.messagebox.askyesno("Confirmación", f"El producto '{nombre_producto}' ya existe. ¿Deseas agregarlo de todos modos?")
            if not confirmacion:
                return
        df_nuevo = pd.DataFrame(datos)
        df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
        df_final.to_excel(archivo_excel, index=False)
    else:
        df = pd.DataFrame(datos)
        df.to_excel(archivo_excel, index=False)

    aplicar_color_condicional(archivo_excel)
    tk.messagebox.showinfo("Éxito", "Los datos se han guardado correctamente.")

def mostrar_ventana_inventario():
    alertas_vencimiento = verificar_vencimientos()
    alertas_stock = verificar_stock_minimo()

    paleta = get_paleta()
    ventana_inventario = tk.Tk()
    ventana_inventario.title("Drogs+ - Inventario")
    ventana_inventario.geometry("520x650")
    ventana_inventario.resizable(False, True)
    ventana_inventario.configure(bg=paleta["bg_principal"])

    icon_path = os.path.join("images", "cruz_azul.ico")
    if os.path.exists(icon_path):
        ventana_inventario.iconbitmap(icon_path)

    aplicar_estilos(ventana_inventario)
    centrar_ventana(ventana_inventario)

    crear_header(ventana_inventario, "Gestión de Inventario")

    canvas = tk.Canvas(ventana_inventario, bg=paleta["bg_principal"], highlightthickness=0)
    scrollbar = tk.Scrollbar(ventana_inventario, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg=paleta["bg_principal"])

    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _bind_wheel(event):
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def _unbind_wheel(event):
        canvas.unbind_all("<MouseWheel>")

    canvas.bind("<Enter>", _bind_wheel)
    canvas.bind("<Leave>", _unbind_wheel)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    main_frame = tk.Frame(scroll_frame, bg=paleta["bg_principal"])
    main_frame.pack(fill="both", expand=True, padx=15, pady=10)

    if alertas_vencimiento or alertas_stock:
        alertas_frame = crear_card(main_frame, "Alertas")
        alertas_frame.pack(fill="x", pady=(0, 10))
        for tipo, texto in (alertas_vencimiento + alertas_stock)[:5]:
            crear_alerta(alertas_frame, tipo, texto).pack(fill="x", padx=10, pady=2)

    form_card = crear_card(main_frame, "Nuevo Producto")
    form_card.pack(fill="x", pady=(0, 10))

    form = tk.Frame(form_card, bg=paleta["bg_card"])
    form.pack(padx=15, pady=10)

    labels_config = [
        ("Nombre:", 0), ("Identificador:", 1), ("Cantidad:", 2),
        ("Stock Mínimo:", 3), ("Precio (COP):", 4), ("Fecha Entrega:", 5),
        ("Fecha Vencimiento:", 6), ("Categoría:", 7), ("Unidad:", 8)
    ]

    for texto, row in labels_config:
        crear_label(form, texto, "bold").grid(row=row, column=0, sticky="w", pady=4, padx=(0, 10))

    global entry_nombre
    entry_nombre = crear_entry(form, width=25)
    entry_nombre.grid(row=0, column=1, pady=4, sticky="w")
    entry_nombre.bind("<KeyRelease>", lambda e: mostrar_codigo_producto())

    global entry_identificador
    entry_identificador = crear_entry(form, width=25, state="readonly")
    entry_identificador.grid(row=1, column=1, pady=4, sticky="w")

    vcmd_entero = (ventana_inventario.register(solo_enteros), '%S')
    global entry_cantidad
    entry_cantidad = crear_entry(form, width=25, validate="key", validatecommand=vcmd_entero)
    entry_cantidad.grid(row=2, column=1, pady=4, sticky="w")

    global entry_stock_minimo
    entry_stock_minimo = crear_entry(form, width=25, validate="key", validatecommand=vcmd_entero)
    entry_stock_minimo.grid(row=3, column=1, pady=4, sticky="w")

    vcmd_real = (ventana_inventario.register(solo_reales), '%S', '%P')
    global entry_precio
    entry_precio = crear_entry(form, width=25, validate="key", validatecommand=vcmd_real)
    entry_precio.grid(row=4, column=1, pady=4, sticky="w")

    global date_entry_entrega
    date_entry_entrega = DateEntry(form, date_pattern='dd/mm/yyyy', width=22, background='darkblue',
                                   foreground='white', borderwidth=2, state='readonly')
    date_entry_entrega.grid(row=5, column=1, pady=4, sticky="w")
    date_entry_entrega.bind("<<DateEntrySelected>>", actualizar_color_categoria)

    global date_entry_vencimiento
    date_entry_vencimiento = DateEntry(form, date_pattern='dd/mm/yyyy', width=22, background='darkblue',
                                       foreground='white', borderwidth=2, state='readonly')
    date_entry_vencimiento.grid(row=6, column=1, pady=4, sticky="w")
    date_entry_vencimiento.bind("<<DateEntrySelected>>", actualizar_color_categoria)

    global canvas_categoria
    canvas_categoria = tk.Canvas(form, width=120, height=20, bg=paleta["alerta_verde"], highlightthickness=1,
                                  highlightbackground=paleta["borde"])
    canvas_categoria.grid(row=7, column=1, pady=4, sticky="w")
    actualizar_color_categoria()

    global entry_unidad
    entry_unidad = crear_entry(form, width=25)
    entry_unidad.grid(row=8, column=1, pady=4, sticky="w")
    entry_unidad.insert(0, "Unidad")

    btn_frame = tk.Frame(main_frame, bg=paleta["bg_principal"])
    btn_frame.pack(fill="x", pady=5)

    crear_boton(btn_frame, "← Volver", lambda: volver_al_menu(ventana_inventario), "Secundario").pack(side="left")
    crear_boton(btn_frame, "🔍 Buscar", mostrar_ventana_editar, "Secundario").pack(side="left", padx=10)
    crear_boton(btn_frame, "💾 Guardar", guardar_datos, "Exito").pack(side="right")

    entry_nombre.focus_set()
    ventana_inventario.mainloop()
