import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os
from utils import centrar_ventana

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

def mostrar_ventana_reportes():
    ventana = tk.Tk()
    ventana.title("Reportes y Analítica")
    ventana.geometry("700x500")
    ventana.resizable(False, False)

    icon_path = os.path.join("images", "cruz_azul.ico")
    if os.path.exists(icon_path):
        ventana.iconbitmap(icon_path)

    centrar_ventana(ventana)

    tk.Label(ventana, text="Dashboard de Analítica", font=("Helvetica", 16, "bold")).pack(pady=10)

    frame_resumen = tk.Frame(ventana)
    frame_resumen.pack(padx=10, fill="x")

    df_ventas = cargar_ventas()
    df_inv = cargar_inventario()

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

    tk.Label(frame_resumen, text=f"Total de ventas registradas: {total_ventas}", font=("Helvetica", 11)).pack(anchor="w", pady=2)
    tk.Label(frame_resumen, text=f"Total de productos en inventario: {total_productos}", font=("Helvetica", 11)).pack(anchor="w", pady=2)
    tk.Label(frame_resumen, text=f"Ingresos totales: ${ingresos:,.2f} COP", font=("Helvetica", 11, "bold")).pack(anchor="w", pady=2)

    tk.Label(ventana, text="Productos más vendidos:", font=("Helvetica", 12, "bold")).pack(padx=10, anchor="w", pady=(15, 5))

    columns = ["Producto", "Unidades Vendidas", "Ingresos"]
    tree = ttk.Treeview(ventana, columns=columns, show="headings", height=10)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=200)
    tree.pack(padx=10, fill="x")

    if not df_ventas.empty and "Nombre Producto" in df_ventas.columns:
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

        for nombre, unidades, ing in lista[:15]:
            tree.insert("", "end", values=[nombre, unidades, f"${ing:,.2f}"])

    def volver():
        ventana.destroy()
        import VenMenu
        VenMenu.mostrar_ventana_menu()

    tk.Button(ventana, text="Volver al menú", command=volver).pack(pady=10)

    ventana.mainloop()
