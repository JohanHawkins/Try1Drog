import tkinter as tk
import pandas as pd
import os
from tkinter import filedialog, messagebox
from fpdf import FPDF
from utils import centrar_ventana
from theme import (get_paleta, aplicar_estilos, crear_header, crear_boton,
                    crear_entry, crear_label, crear_card, crear_treeview)

current_page = 0
rows_per_page = 20
frame_tabla = None
datos_filtrados = None
datos = None

def volver_al_menu(ventana):
    ventana.destroy()
    import VenMenu
    VenMenu.mostrar_ventana_menu()

def aplicar_filtro(datos, nombre, fecha, hora, metodo_pago):
    if nombre:
        datos = datos[datos['Nombre Producto'].str.contains(nombre, case=False, na=False)]
    if fecha:
        datos = datos[datos['Fecha'].astype(str).str.contains(fecha, na=False)]
    if hora:
        datos = datos[datos['Hora'].astype(str).str.contains(hora, na=False)]
    if metodo_pago:
        datos = datos[datos['Método Pago'].astype(str).str.contains(metodo_pago, case=False, na=False)]
    return datos

def guardar_registros():
    formato = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                           filetypes=[("Excel files", "*.xlsx"),
                                                      ("Text files", "*.txt"),
                                                      ("PDF files", "*.pdf")])
    if not formato:
        return
    extension = os.path.splitext(formato)[1].lower()
    if extension == ".xlsx":
        datos_filtrados.to_excel(formato, index=False)
    elif extension == ".txt":
        datos_filtrados.to_csv(formato, index=False, sep='\t')
    elif extension == ".pdf":
        try:
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Arial", style="B", size=12)
            encabezados = list(datos_filtrados.columns)
            for encabezado in encabezados:
                pdf.cell(40, 10, encabezado, border=1)
            pdf.ln()
            pdf.set_font("Arial", size=10)
            for row in datos_filtrados.values:
                for cell in row:
                    pdf.cell(40, 10, str(cell), border=1)
                pdf.ln()
            pdf.output(formato)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar como PDF: {e}")
            return
    else:
        messagebox.showerror("Error", "Formato no soportado.")
    messagebox.showinfo("Éxito", f"Registros guardados en {formato}")

def eliminar_registro():
    global datos_filtrados, datos, current_page
    if not messagebox.askyesno("Confirmar", "¿Eliminar los registros filtrados?"):
        return
    if datos_filtrados.empty:
        messagebox.showerror("Error", "No hay datos para eliminar.")
        return
    try:
        indices_a_eliminar = datos_filtrados.index
        datos = datos.drop(indices_a_eliminar).reset_index(drop=True)
        datos_filtrados = datos.copy()
        current_page = 0
        datos.to_excel("Ventas/registros_compra.xlsx", index=False)
        messagebox.showinfo("Éxito", "Registros eliminados correctamente.")
        cargar_pagina()
    except Exception as e:
        messagebox.showerror("Error", f"Error al eliminar: {e}")

def cargar_pagina():
    global current_page
    start = current_page * rows_per_page
    end = start + rows_per_page
    sub = datos_filtrados.iloc[start:end]

    for item in tree.get_children():
        tree.delete(item)

    for i, (_, row) in enumerate(sub.iterrows()):
        valores = [str(v) for v in row.values]
        tag = "evenrow" if i % 2 == 0 else "oddrow"
        tree.insert("", "end", values=valores, tags=(tag,))

    total = len(datos_filtrados)
    total_paginas = max(1, (total + rows_per_page - 1) // rows_per_page)
    lbl_pagina.config(text=f"Página {current_page + 1} de {total_paginas}  ({total} registros)")

def siguiente_pagina():
    global current_page
    total_paginas = max(1, (len(datos_filtrados) + rows_per_page - 1) // rows_per_page)
    if current_page + 1 < total_paginas:
        current_page += 1
        cargar_pagina()

def pagina_anterior():
    global current_page
    if current_page > 0:
        current_page -= 1
        cargar_pagina()

def filtrar_datos():
    global datos_filtrados, current_page
    current_page = 0
    nombre = entrada_nombre.get()
    fecha = entrada_fecha.get()
    hora = entrada_hora.get()
    metodo_pago = entrada_metodo.get() if entrada_metodo else ""
    datos_filtrados = aplicar_filtro(datos, nombre, fecha, hora, metodo_pago)
    if datos_filtrados.empty:
        mensaje_error.config(text="Sin resultados para el filtro aplicado.")
    else:
        mensaje_error.config(text="")
    cargar_pagina()

def mostrar_ventana_registro():
    global frame_tabla, datos_filtrados, datos, current_page
    global tree, entrada_nombre, entrada_fecha, entrada_hora, entrada_metodo, mensaje_error, lbl_pagina

    paleta = get_paleta()
    excel_path = "Ventas/registros_compra.xlsx"

    ventana_registro = tk.Tk()
    ventana_registro.title("Drogs+ - Registro de Ventas")
    ventana_registro.resizable(True, True)
    ventana_registro.minsize(550, 400)
    ventana_registro.configure(bg=paleta["bg_principal"])

    icon_path = os.path.join("images", "cruz_azul.ico")
    if os.path.exists(icon_path):
        ventana_registro.iconbitmap(icon_path)
    aplicar_estilos(ventana_registro)
    centrar_ventana(ventana_registro)

    crear_header(ventana_registro, "Registro de Ventas")

    if not os.path.exists(excel_path):
        msg_frame = tk.Frame(ventana_registro, bg=paleta["bg_principal"])
        msg_frame.pack(fill="both", expand=True)
        crear_label(msg_frame, "Archivo 'registros_compra.xlsx' no encontrado.", "normal", fg=paleta["alerta_rojo"]).pack(pady=50)
        crear_boton(msg_frame, "← Volver", lambda: volver_al_menu(ventana_registro), "Secundario").pack()
        ventana_registro.mainloop()
        return

    datos = pd.read_excel(excel_path)
    
    if "Método Pago" not in datos.columns:
        datos["Método Pago"] = "Efectivo"
        datos.to_excel(excel_path, index=False)
    
    datos_filtrados = datos.copy()

    main_frame = tk.Frame(ventana_registro, bg=paleta["bg_principal"])
    main_frame.pack(fill="both", expand=True, padx=25, pady=12)

    filtros_card = crear_card(main_frame, "Filtros de Búsqueda")
    filtros_card.pack(fill="x", pady=0)
    filtros_inner = tk.Frame(filtros_card, bg=paleta["bg_card"])
    filtros_inner.pack(fill="x", padx=15, pady=(0, 14))

    crear_label(filtros_inner, "Producto:", "bold").grid(row=0, column=0, sticky="e", padx=(0, 6), pady=6)
    entrada_nombre = crear_entry(filtros_inner, width=15)
    entrada_nombre.grid(row=0, column=1, padx=(0, 10), pady=6)

    crear_label(filtros_inner, "Fecha:", "bold").grid(row=0, column=2, sticky="e", padx=(0, 6), pady=6)
    entrada_fecha = crear_entry(filtros_inner, width=10)
    entrada_fecha.grid(row=0, column=3, padx=(0, 10), pady=6)

    crear_label(filtros_inner, "Hora:", "bold").grid(row=0, column=4, sticky="e", padx=(0, 6), pady=6)
    entrada_hora = crear_entry(filtros_inner, width=8)
    entrada_hora.grid(row=0, column=5, padx=(0, 10), pady=6)

    crear_label(filtros_inner, "Método:", "bold").grid(row=0, column=6, sticky="e", padx=(0, 6), pady=6)
    entrada_metodo = crear_entry(filtros_inner, width=10)
    entrada_metodo.grid(row=0, column=7, padx=(0, 10), pady=6)

    crear_boton(filtros_inner, "🔍 Buscar", filtrar_datos, "Primario", "pequeño").grid(row=0, column=8, pady=6)

    mensaje_error = crear_label(main_frame, "", "normal", fg=paleta["alerta_rojo"])
    mensaje_error.pack(anchor="w")

    tabla_card = crear_card(main_frame, "Historial de Ventas")
    tabla_card.pack(fill="both", expand=True)

    columnas = list(datos.columns)
    tree = crear_treeview(tabla_card, columnas)
    tree.pack(fill="both", expand=True, padx=10, pady=2)

    pag_card = tk.Frame(main_frame, bg=paleta["bg_principal"])
    pag_card.pack(fill="x", pady=(6, 0))

    pag_der = tk.Frame(pag_card, bg=paleta["bg_principal"])
    pag_der.pack(side="right")
    crear_boton(pag_der, "←", pagina_anterior, "Secundario", "pequeño").pack(side="left")
    lbl_pagina = crear_label(pag_der, "", "normal")
    lbl_pagina.pack(side="left", padx=10)
    crear_boton(pag_der, "→", siguiente_pagina, "Secundario", "pequeño").pack(side="left")

    btn_frame = tk.Frame(main_frame, bg=paleta["bg_principal"])
    btn_frame.pack(fill="x", pady=(8, 0))

    crear_boton(btn_frame, "← Volver", lambda: volver_al_menu(ventana_registro), "Secundario", "pequeño").pack(side="left")
    crear_boton(btn_frame, "🗑 Eliminar", eliminar_registro, "Peligro", "pequeño").pack(side="right", padx=(10, 0))
    crear_boton(btn_frame, "📥 Exportar", guardar_registros, "Exito", "pequeño").pack(side="right")

    cargar_pagina()
    ventana_registro.update_idletasks()
    w = ventana_registro.winfo_reqwidth()
    h = ventana_registro.winfo_reqheight()
    ventana_registro.geometry(f"{w}x{h}")
    centrar_ventana(ventana_registro)
    ventana_registro.mainloop()
