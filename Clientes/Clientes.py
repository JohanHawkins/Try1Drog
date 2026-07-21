import tkinter as tk
from tkinter import messagebox
import pandas as pd
import os
from utils import centrar_ventana
from theme import (get_paleta, aplicar_estilos, crear_header, crear_boton,
                    crear_entry, crear_label, crear_card, crear_treeview)

ARCHIVO_CLIENTES = os.path.join("Clientes", "clientes.xlsx")

def cargar_clientes():
    if os.path.exists(ARCHIVO_CLIENTES):
        df = pd.read_excel(ARCHIVO_CLIENTES)
        if "Puntos" not in df.columns:
            df["Puntos"] = 0
            df.to_excel(ARCHIVO_CLIENTES, index=False)
        return df
    return pd.DataFrame(columns=["Nombre", "Cedula", "Telefono", "Direccion", "Email", "Puntos"])

def cargar_puntos_cliente(cedula):
    df = cargar_clientes()
    cliente = df[df["Cedula"].astype(str) == str(cedula)]
    if not cliente.empty:
        return int(cliente.iloc[0]["Puntos"])
    return None

def actualizar_puntos_cliente(cedula, nuevos_puntos):
    df = cargar_clientes()
    idx = df[df["Cedula"].astype(str) == str(cedula)].index
    if not idx.empty:
        df.loc[idx[0], "Puntos"] = max(0, int(nuevos_puntos))
        guardar_clientes(df)
        return True
    return False

def sumar_puntos(cedula, puntos_a_sumar):
    puntos_actuales = cargar_puntos_cliente(cedula)
    if puntos_actuales is not None:
        return actualizar_puntos_cliente(cedula, puntos_actuales + puntos_a_sumar)
    return False

def guardar_clientes(df):
    os.makedirs("Clientes", exist_ok=True)
    df.to_excel(ARCHIVO_CLIENTES, index=False)

def volver_al_menu(ventana):
    ventana.destroy()
    import VenMenu
    VenMenu.mostrar_ventana_menu()

def mostrar_ventana_clientes():
    paleta = get_paleta()

    ventana = tk.Tk()
    ventana.title("Drogs+ - Gestión de Clientes")
    ventana.resizable(True, True)
    ventana.minsize(500, 350)
    ventana.configure(bg=paleta["bg_principal"])

    icon_path = os.path.join("images", "cruz_azul.ico")
    if os.path.exists(icon_path):
        ventana.iconbitmap(icon_path)
    aplicar_estilos(ventana)
    centrar_ventana(ventana)

    crear_header(ventana, "Gestión de Clientes")

    main_frame = tk.Frame(ventana, bg=paleta["bg_principal"])
    main_frame.pack(fill="both", expand=True, padx=15, pady=10)

    form_card = crear_card(main_frame, "Datos del Cliente")
    form_card.pack(fill="x", pady=(0, 10))

    form_frame = tk.Frame(form_card, bg=paleta["bg_card"])
    form_frame.pack(fill="x", padx=15, pady=10)

    labels = ["Nombre:", "Cédula:", "Teléfono:", "Dirección:", "Email:"]
    entries = {}
    for i, texto in enumerate(labels):
        crear_label(form_frame, texto, "normal").grid(row=i, column=0, sticky="w", padx=(0, 10), pady=4)
        key = texto.lower().replace(":", "").strip()
        e = crear_entry(form_frame, width=30)
        e.grid(row=i, column=1, sticky="w", pady=4)
        entries[key] = e

    crear_label(form_frame, "Puntos:", "bold").grid(row=5, column=0, sticky="w", padx=(0, 10), pady=4)
    label_puntos_val = crear_label(form_frame, "0", "success")
    label_puntos_val.grid(row=5, column=1, sticky="w", pady=4)

    tree_frame = tk.Frame(main_frame, bg=paleta["bg_principal"])
    tree_frame.pack(fill="both", expand=True, pady=(0, 10))

    columns = ["Nombre", "Cedula", "Telefono", "Direccion", "Email", "Puntos"]
    tree = crear_treeview(tree_frame, columns)
    tree.pack(fill="both", expand=True)

    def cargar_tabla():
        for item in tree.get_children():
            tree.delete(item)
        df = cargar_clientes()
        for i, (_, row) in enumerate(df.iterrows()):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            puntos = int(row.get("Puntos", 0)) if "Puntos" in row else 0
            tree.insert("", "end", values=[row.get(c, "") for c in columns[:5]] + [puntos], tags=(tag,))

    def limpiar_campos():
        for e in entries.values():
            e.delete(0, tk.END)
        label_puntos_val.config(text="0")

    def agregar_cliente():
        nombre = entries["nombre"].get().strip()
        cedula = entries["cédula"].get().strip()
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
            "Telefono": entries["teléfono"].get().strip(),
            "Direccion": entries["dirección"].get().strip(),
            "Email": entries["email"].get().strip(),
            "Puntos": 0
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
        entries["nombre"].insert(0, valores[0])
        entries["cédula"].insert(0, valores[1])
        entries["teléfono"].insert(0, valores[2])
        entries["dirección"].insert(0, valores[3])
        entries["email"].insert(0, valores[4])
        label_puntos_val.config(text=str(valores[5]) if len(valores) > 5 else "0")

    tree.bind("<<TreeviewSelect>>", seleccionar_cliente)

    btn_frame = tk.Frame(main_frame, bg=paleta["bg_principal"])
    btn_frame.pack(fill="x")

    crear_boton(btn_frame, "← Volver", lambda: volver_al_menu(ventana), "Secundario").pack(side="left")
    crear_boton(btn_frame, "🗑 Eliminar", eliminar_cliente, "Peligro").pack(side="right", padx=(10, 0))
    crear_boton(btn_frame, "✓ Agregar", agregar_cliente, "Exito").pack(side="right")
    crear_boton(btn_frame, "Limpiar", limpiar_campos, "Secundario").pack(side="right", padx=(0, 10))

    cargar_tabla()
    ventana.update_idletasks()
    w = ventana.winfo_reqwidth()
    h = ventana.winfo_reqheight()
    ventana.geometry(f"{w}x{h}")
    centrar_ventana(ventana)
    ventana.mainloop()
