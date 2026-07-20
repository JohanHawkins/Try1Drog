import tkinter as tk
from tkinter import messagebox
import pandas as pd
import os
from utils import centrar_ventana
from theme import (get_paleta, aplicar_estilos, crear_header, crear_boton,
                    crear_label, crear_card, crear_treeview)

def cargar_ventas():
    archivo = os.path.join("Ventas", "registros_compra.xlsx")
    if os.path.exists(archivo):
        return pd.read_excel(archivo)
    return pd.DataFrame()

def cargar_inventario():
    archivo = os.path.join("Inventario", "inventario_productos.xlsx")
    if os.path.exists(archivo):
        return pd.read_excel(archivo)
    return pd.DataFrame()

def volver_al_menu(ventana):
    ventana.destroy()
    import VenMenu
    VenMenu.mostrar_ventana_menu()

def mostrar_ventana_reportes():
    paleta = get_paleta()
    df_ventas = cargar_ventas()
    df_inv = cargar_inventario()

    ventana = tk.Tk()
    ventana.title("Drogs+ - Reportes y Analítica")
    ventana.geometry("700x520")
    ventana.resizable(False, False)
    ventana.configure(bg=paleta["bg_principal"])

    icon_path = os.path.join("images", "cruz_azul.ico")
    if os.path.exists(icon_path):
        ventana.iconbitmap(icon_path)
    aplicar_estilos(ventana)
    centrar_ventana(ventana)

    crear_header(ventana, "Reportes y Analítica")

    main_frame = tk.Frame(ventana, bg=paleta["bg_principal"])
    main_frame.pack(fill="both", expand=True, padx=15, pady=10)

    resumen_card = crear_card(main_frame, "Resumen General")
    resumen_card.pack(fill="x", pady=(0, 10))

    resumen_inner = tk.Frame(resumen_card, bg=paleta["bg_card"])
    resumen_inner.pack(fill="x", padx=15, pady=10)

    total_ventas = len(df_ventas)
    total_productos = len(df_inv) if not df_inv.empty else 0

    ingresos = 0
    if not df_ventas.empty and "Precio Total" in df_ventas.columns:
        for val in df_ventas["Precio Total"]:
            try:
                num = str(val).replace("$", "").replace("COP", "").replace(",", "").strip()
                ingresos += float(num)
            except (ValueError, TypeError):
                continue

    stats = [
        ("Ventas registradas", str(total_ventas), paleta["alerta_azul"]),
        ("Productos en inventario", str(total_productos), paleta["alerta_amarillo"]),
        ("Ingresos totales", f"${ingresos:,.2f} COP", paleta["alerta_verde"]),
    ]

    for i, (titulo, valor, color) in enumerate(stats):
        stat_frame = tk.Frame(resumen_inner, bg=paleta["bg_card"])
        stat_frame.grid(row=0, column=i, padx=20, pady=5, sticky="nsew")
        resumen_inner.columnconfigure(i, weight=1)

        crear_label(stat_frame, titulo, "normal").pack(anchor="w")
        tk.Label(stat_frame, text=valor, font=("Segoe UI", 18, "bold"),
                 fg=color, bg=paleta["bg_card"]).pack(anchor="w", pady=(2, 0))

    if not df_ventas.empty and "Nombre Producto" in df_ventas.columns:
        crear_label(main_frame, "Top Productos Más Vendidos", "subtitle").pack(anchor="w", pady=(5, 5))

        resumen = df_ventas.groupby("Nombre Producto").agg(
            Unidades=("Cantidad Comprada", "sum"),
            Ingresos=("Precio Total", "count")
        ).reset_index()

        ingresos_por_producto = {}
        for _, row in df_ventas.iterrows():
            nombre = row["Nombre Producto"]
            try:
                num = str(row["Precio Total"]).replace("$", "").replace("COP", "").replace(",", "").strip()
                ingresos_por_producto[nombre] = ingresos_por_producto.get(nombre, 0) + float(num)
            except (ValueError, TypeError):
                continue

        lista = []
        for _, row in resumen.iterrows():
            nombre = row["Nombre Producto"]
            ing = ingresos_por_producto.get(nombre, 0)
            lista.append((nombre, int(row["Unidades"]), ing))
        lista.sort(key=lambda x: x[1], reverse=True)

        tree_frame = tk.Frame(main_frame, bg=paleta["bg_principal"])
        tree_frame.pack(fill="both", expand=True, pady=(0, 10))

        columns = ["Producto", "Unidades Vendidas", "Ingresos"]
        tree = crear_treeview(tree_frame, columns)
        tree.pack(fill="both", expand=True)

        for i, (nombre, unidades, ing) in enumerate(lista[:15]):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            tree.insert("", "end", values=[nombre, unidades, f"${ing:,.2f}"], tags=(tag,))
    else:
        crear_label(main_frame, "No hay datos de ventas registrados.", "normal",
                    fg=paleta["texto_secundario"]).pack(pady=40)

    btn_frame = tk.Frame(main_frame, bg=paleta["bg_principal"])
    btn_frame.pack(fill="x")

    crear_boton(btn_frame, "← Volver", lambda: volver_al_menu(ventana), "Secundario").pack(side="left")

    ventana.mainloop()
