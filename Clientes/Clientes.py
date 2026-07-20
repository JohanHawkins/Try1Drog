import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os
from utils import centrar_ventana

ARCHIVO_CLIENTES = os.path.join("Clientes", "clientes.xlsx")

def cargar_clientes():
    if os.path.exists(ARCHIVO_CLIENTES):
        return pd.read_excel(ARCHIVO_CLIENTES)
    return pd.DataFrame(columns=["Nombre", "Cedula", "Telefono", "Direccion", "Email"])

def guardar_clientes(df):
    os.makedirs("Clientes", exist_ok=True)
    df.to_excel(ARCHIVO_CLIENTES, index=False)

def mostrar_ventana_clientes():
    ventana = tk.Tk()
    ventana.title("Gestión de Clientes")
    ventana.geometry("650x450")
    ventana.resizable(False, False)

    icon_path = os.path.join("images", "cruz_azul.ico")
    if os.path.exists(icon_path):
        ventana.iconbitmap(icon_path)

    centrar_ventana(ventana)

    frame_form = tk.Frame(ventana)
    frame_form.pack(padx=10, pady=10, anchor="w")

    tk.Label(frame_form, text="Nombre:").grid(row=0, column=0, sticky="w", pady=2)
    entry_nombre = tk.Entry(frame_form, width=25)
    entry_nombre.grid(row=0, column=1, padx=5, pady=2)

    tk.Label(frame_form, text="Cédula:").grid(row=0, column=2, sticky="w", pady=2)
    entry_cedula = tk.Entry(frame_form, width=15)
    entry_cedula.grid(row=0, column=3, padx=5, pady=2)

    tk.Label(frame_form, text="Teléfono:").grid(row=1, column=0, sticky="w", pady=2)
    entry_telefono = tk.Entry(frame_form, width=25)
    entry_telefono.grid(row=1, column=1, padx=5, pady=2)

    tk.Label(frame_form, text="Dirección:").grid(row=1, column=2, sticky="w", pady=2)
    entry_direccion = tk.Entry(frame_form, width=15)
    entry_direccion.grid(row=1, column=3, padx=5, pady=2)

    tk.Label(frame_form, text="Email:").grid(row=2, column=0, sticky="w", pady=2)
    entry_email = tk.Entry(frame_form, width=25)
    entry_email.grid(row=2, column=1, padx=5, pady=2)

    columns = ["Nombre", "Cedula", "Telefono", "Direccion", "Email"]
    tree = ttk.Treeview(ventana, columns=columns, show="headings", height=12)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120)
    tree.pack(padx=10, pady=5, fill="x")

    def cargar_tabla():
        for item in tree.get_children():
            tree.delete(item)
        df = cargar_clientes()
        for _, row in df.iterrows():
            tree.insert("", "end", values=[row.get(c, "") for c in columns])

    def limpiar_campos():
        entry_nombre.delete(0, tk.END)
        entry_cedula.delete(0, tk.END)
        entry_telefono.delete(0, tk.END)
        entry_direccion.delete(0, tk.END)
        entry_email.delete(0, tk.END)

    def agregar_cliente():
        nombre = entry_nombre.get().strip()
        cedula = entry_cedula.get().strip()
        if not nombre or not cedula:
            messagebox.showwarning("Advertencia", "Nombre y Cédula son obligatorios.")
            return
        df = cargar_clientes()
        if cedula in df["Cedula"].astype(str).values:
            messagebox.showwarning("Advertencia", f"Ya existe un cliente con cédula {cedula}.")
            return
        nuevo = pd.DataFrame([{
            "Nombre": nombre,
            "Cedula": cedula,
            "Telefono": entry_telefono.get().strip(),
            "Direccion": entry_direccion.get().strip(),
            "Email": entry_email.get().strip()
        }])
        df = pd.concat([df, nuevo], ignore_index=True)
        guardar_clientes(df)
        messagebox.showinfo("Éxito", "Cliente agregado correctamente.")
        limpiar_campos()
        cargar_tabla()

    def eliminar_cliente():
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un cliente para eliminar.")
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar cliente seleccionado?"):
            return
        df = cargar_clientes()
        for item in seleccion:
            valores = tree.item(item, "values")
            cedula = str(valores[1])
            df = df[df["Cedula"].astype(str) != cedula]
        guardar_clientes(df)
        cargar_tabla()
        messagebox.showinfo("Éxito", "Cliente eliminado.")

    def seleccionar_cliente(event):
        seleccion = tree.selection()
        if not seleccion:
            return
        valores = tree.item(seleccion[0], "values")
        limpiar_campos()
        entry_nombre.insert(0, valores[0])
        entry_cedula.insert(0, valores[1])
        entry_telefono.insert(0, valores[2])
        entry_direccion.insert(0, valores[3])
        entry_email.insert(0, valores[4])

    tree.bind("<<TreeviewSelect>>", seleccionar_cliente)

    frame_botones = tk.Frame(ventana)
    frame_botones.pack(pady=5)

    tk.Button(frame_botones, text="Agregar", command=agregar_cliente).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_botones, text="Eliminar", command=eliminar_cliente).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_botones, text="Limpiar", command=limpiar_campos).pack(side=tk.LEFT, padx=5)

    def volver():
        ventana.destroy()
        import VenMenu
        VenMenu.mostrar_ventana_menu()

    tk.Button(frame_botones, text="Volver al menú", command=volver).pack(side=tk.LEFT, padx=5)

    cargar_tabla()
    ventana.mainloop()
