import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os
from theme import (get_paleta, aplicar_estilos, crear_header, crear_boton,
                    crear_entry, crear_label, crear_card)
from utils import centrar_ventana

ventana_editar_abierta = False
ventana_resultados_abierta = False

def mostrar_ventana_editar():
    global ventana_editar_abierta

    if ventana_editar_abierta:
        messagebox.showwarning("Advertencia", "La ventana de edición ya está abierta.")
        return

    paleta = get_paleta()
    ventana_editar_abierta = True

    ventana_editar = tk.Toplevel()
    ventana_editar.title("Drogs+ - Buscar Producto")
    ventana_editar.resizable(True, True)
    ventana_editar.minsize(420, 200)
    ventana_editar.configure(bg=paleta["bg_principal"])

    icon_path = os.path.join("images", "cruz_azul.ico")
    if os.path.exists(icon_path):
        ventana_editar.iconbitmap(icon_path)

    aplicar_estilos(ventana_editar)

    body = tk.Frame(ventana_editar, bg=paleta["bg_frame"])
    body.pack(fill="both", expand=True, padx=20, pady=15)

    crear_label(body, "Buscar Producto", "subtitle").pack(anchor="w", pady=(0, 10))

    search_frame = tk.Frame(body, bg=paleta["bg_frame"])
    search_frame.pack(fill="x")

    entry_editar = crear_entry(search_frame, width=30, font=("Segoe UI", 11))
    entry_editar.pack(side="left", padx=(0, 10))
    entry_editar.focus_set()

    def buscar_datos():
        producto_buscado = entry_editar.get()
        try:
            df = pd.read_excel("Inventario/inventario_productos.xlsx")
            resultados = df[df['Nombre Producto'].str.contains(producto_buscado, case=False, na=False)]
            if not resultados.empty:
                mostrar_resultados(resultados)
            else:
                messagebox.showinfo("Resultados", "No se encontraron coincidencias.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar: {str(e)}")

    entry_editar.bind("<Return>", lambda e: buscar_datos())

    crear_boton(search_frame, "🔍 Buscar", buscar_datos).pack(side="left")

    btn_frame = tk.Frame(body, bg=paleta["bg_frame"])
    btn_frame.pack(fill="x", pady=(10, 0))
    crear_boton(btn_frame, "Cerrar", lambda: cerrar_ventana(ventana_editar), "Secundario").pack(side="right")

    ventana_editar.protocol("WM_DELETE_WINDOW", lambda: cerrar_ventana(ventana_editar))

def mostrar_resultados(resultados):
    global ventana_resultados_abierta

    if ventana_resultados_abierta:
        messagebox.showwarning("Advertencia", "La ventana de resultados ya está abierta.")
        return

    paleta = get_paleta()
    ventana_resultados_abierta = True

    ventana_resultados = tk.Toplevel()
    ventana_resultados.title("Drogs+ - Resultados de Búsqueda")
    ventana_resultados.resizable(True, True)
    ventana_resultados.minsize(650, 380)
    ventana_resultados.configure(bg=paleta["bg_principal"])

    icon_path = os.path.join("images", "cruz_azul.ico")
    if os.path.exists(icon_path):
        ventana_resultados.iconbitmap(icon_path)

    aplicar_estilos(ventana_resultados)
    ventana_resultados.protocol("WM_DELETE_WINDOW", lambda: cerrar_ventana_resultados(ventana_resultados))

    crear_header(ventana_resultados, "Resultados de Búsqueda")

    if 'Categoria' not in resultados.columns:
        resultados['Categoria'] = ''

    columns = ['Nombre Producto', 'Cantidad Producto', 'Precio Producto (COP)', 'Categoria', 'Fecha Vencimiento']

    tree_frame = tk.Frame(ventana_resultados, bg=paleta["bg_frame"])
    tree_frame.pack(fill="both", expand=True, padx=15, pady=10)

    tree = ttk.Treeview(tree_frame, columns=columns, show='headings', selectmode="extended")
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor='center', width=150)

    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    colores_categoria = {
        "rojo": paleta["alerta_rojo"],
        "amarillo": paleta["alerta_amarillo"],
        "verde": paleta["alerta_verde"],
    }

    for index, row in resultados.iterrows():
        values = [row.get(col, '') for col in columns]
        item_id = tree.insert("", "end", values=values)
        cat = str(row['Categoria']).lower()
        if cat in colores_categoria:
            tree.item(item_id, tags=(f"cat_{cat}",))

    for cat, color in colores_categoria.items():
        tree.tag_configure(f"cat_{cat}", background=color, foreground="white" if cat == "rojo" else "black")

    def guardar_todos_los_cambios():
        try:
            rows = []
            for item_id in tree.get_children():
                rows.append(tree.item(item_id, "values"))
            df_actualizado = pd.DataFrame(rows, columns=columns)
            df_actualizado.to_excel("Inventario/inventario_productos.xlsx", index=False)
            messagebox.showinfo("Guardado", "Todos los cambios han sido guardados.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {str(e)}")

    def editar_celda(event):
        seleccion = tree.selection()
        if not seleccion:
            return
        item = seleccion[0]
        col = tree.identify_column(event.x)
        col = int(col[1:]) - 1
        valor_actual = tree.item(item, "values")[col]

        entry_editar = tk.Entry(ventana_resultados, font=("Segoe UI", 10),
                                 bg=paleta["bg_input"], fg=paleta["texto_principal"],
                                 insertbackground=paleta["texto_principal"])
        entry_editar.insert(0, valor_actual)
        entry_editar.place(x=event.x, y=event.y)

        def guardar_edicion(event):
            nuevo_valor = entry_editar.get()
            valores_actuales = list(tree.item(item, "values"))
            valores_actuales[col] = nuevo_valor
            tree.item(item, values=valores_actuales)
            entry_editar.destroy()

        entry_editar.bind("<Return>", guardar_edicion)
        entry_editar.focus_set()

    tree.bind("<Double-1>", editar_celda)

    btn_frame = tk.Frame(ventana_resultados, bg=paleta["bg_frame"])
    btn_frame.pack(fill="x", padx=15, pady=10)

    def eliminar_producto():
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un producto para eliminar.")
            return
        if not messagebox.askyesno("Confirmar", f"¿Eliminar {len(seleccion)} producto(s)?"):
            return
        for item in seleccion:
            tree.delete(item)

    crear_boton(btn_frame, "← Cerrar", lambda: cerrar_ventana_resultados(ventana_resultados), "Secundario").pack(side="left")
    crear_boton(btn_frame, "🗑️ Eliminar", eliminar_producto, "Peligro").pack(side="left", padx=10)
    crear_boton(btn_frame, "💾 Guardar Cambios", guardar_todos_los_cambios, "Exito").pack(side="right")

def cerrar_ventana(ventana):
    global ventana_editar_abierta
    ventana.destroy()
    ventana_editar_abierta = False

def cerrar_ventana_resultados(ventana):
    global ventana_resultados_abierta
    ventana.destroy()
    ventana_resultados_abierta = False
