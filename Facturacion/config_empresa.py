import tkinter as tk
from tkinter import messagebox
import pandas as pd
import os
from utils import centrar_ventana
from theme import (get_paleta, aplicar_estilos, crear_header, crear_boton,
                    crear_entry, crear_label, crear_card)

ARCHIVO_CONFIG = os.path.join("Facturacion", "config_empresa.xlsx")

CAMPOS_DEFAULT = {
    "NIT": "",
    "Razon Social": "",
    "Direccion": "",
    "Codigo Municipio DANE": "11001",
    "Telefono": "",
    "Email": "",
    "Responsabilidad Fiscal": "O-47",
    "Rango Desde": "1",
    "Rango Hasta": "5000",
    "Consecutivo Actual": "1",
    "Prefijo Consecutivo": "SETP",
    "Codigo Software DIAN": "",
    "Pin Software DIAN": "",
}

RESPONSABILIDADES_FISCALES = [
    "O-13", "O-15", "O-23", "O-47", "R-99-PN"
]

def cargar_config():
    if os.path.exists(ARCHIVO_CONFIG):
        df = pd.read_excel(ARCHIVO_CONFIG)
        config = {}
        for _, row in df.iterrows():
            config[row["Campo"]] = str(row["Valor"])
        return config
    return CAMPOS_DEFAULT.copy()

def guardar_config(config):
    os.makedirs("Facturacion", exist_ok=True)
    df = pd.DataFrame([{"Campo": k, "Valor": v} for k, v in config.items()])
    df.to_excel(ARCHIVO_CONFIG, index=False)

def obtener_siguiente_consecutivo():
    config = cargar_config()
    prefijo = config.get("Prefijo Consecutivo", "SETP")
    actual = int(config.get("Consecutivo Actual", "1"))
    rango_hasta = int(config.get("Rango Hasta", "5000"))

    if actual > rango_hasta:
        return None

    consecutivo = f"{prefijo}{actual:010d}"

    config["Consecutivo Actual"] = str(actual + 1)
    guardar_config(config)

    return consecutivo

def mostrar_ventana_config():
    paleta = get_paleta()
    config = cargar_config()

    ventana = tk.Tk()
    ventana.title("Drogs+ - Configuración Empresa (DIAN)")
    ventana.resizable(True, True)
    ventana.minsize(520, 480)
    ventana.configure(bg=paleta["bg_principal"])

    icon_path = os.path.join("images", "cruz_azul.ico")
    if os.path.exists(icon_path):
        ventana.iconbitmap(icon_path)
    aplicar_estilos(ventana)
    centrar_ventana(ventana)

    crear_header(ventana, "Configuración Empresa (DIAN)")

    main_frame = tk.Frame(ventana, bg=paleta["bg_principal"])
    main_frame.pack(fill="both", expand=True, padx=15, pady=10)

    canvas = tk.Canvas(main_frame, bg=paleta["bg_principal"], highlightthickness=0)
    scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg=paleta["bg_principal"])

    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    empresa_card = crear_card(scroll_frame, "Datos de la Empresa")
    empresa_card.pack(fill="x", pady=(0, 10))
    empresa_inner = tk.Frame(empresa_card, bg=paleta["bg_card"])
    empresa_inner.pack(fill="x", padx=15, pady=(0, 10))

    campos_empresa = [
        ("NIT:", "NIT", 0),
        ("Razón Social:", "Razon Social", 1),
        ("Dirección:", "Direccion", 2),
        ("Cód. Municipio DANE:", "Codigo Municipio DANE", 3),
        ("Teléfono:", "Telefono", 4),
        ("Email:", "Email", 5),
    ]

    entries_empresa = {}
    for texto, key, fila in campos_empresa:
        crear_label(empresa_inner, texto, "bold").grid(row=fila, column=0, sticky="e", padx=(0, 8), pady=5)
        e = crear_entry(empresa_inner, width=30)
        e.grid(row=fila, column=1, sticky="w", pady=5)
        e.insert(0, config.get(key, CAMPOS_DEFAULT[key]))
        entries_empresa[key] = e

    fiscal_card = crear_card(scroll_frame, "Responsabilidad Fiscal")
    fiscal_card.pack(fill="x", pady=(0, 10))
    fiscal_inner = tk.Frame(fiscal_card, bg=paleta["bg_card"])
    fiscal_inner.pack(fill="x", padx=15, pady=(0, 10))

    crear_label(fiscal_inner, "Código:", "bold").grid(row=0, column=0, sticky="e", padx=(0, 8), pady=5)
    var_responsabilidad = tk.StringVar(value=config.get("Responsabilidad Fiscal", "O-47"))
    entry_responsabilidad = tk.OptionMenu(fiscal_inner, var_responsabilidad, *RESPONSABILIDADES_FISCALES)
    entry_responsabilidad.grid(row=0, column=1, sticky="w", pady=5)

    dian_card = crear_card(scroll_frame, "Configuración DIAN")
    dian_card.pack(fill="x", pady=(0, 10))
    dian_inner = tk.Frame(dian_card, bg=paleta["bg_card"])
    dian_inner.pack(fill="x", padx=15, pady=(0, 10))

    campos_dian = [
        ("Rango Desde:", "Rango Desde", 0),
        ("Rango Hasta:", "Rango Hasta", 1),
        ("Consecutivo Actual:", "Consecutivo Actual", 2),
        ("Prefijo Consecutivo:", "Prefijo Consecutivo", 3),
        ("Cód. Software DIAN:", "Codigo Software DIAN", 4),
        ("Pin Software DIAN:", "Pin Software DIAN", 5),
    ]

    entries_dian = {}
    for texto, key, fila in campos_dian:
        crear_label(dian_inner, texto, "bold").grid(row=fila, column=0, sticky="e", padx=(0, 8), pady=5)
        e = crear_entry(dian_inner, width=30)
        e.grid(row=fila, column=1, sticky="w", pady=5)
        e.insert(0, config.get(key, CAMPOS_DEFAULT[key]))
        entries_dian[key] = e

    def guardar():
        nuevo_config = {}
        for key, entry in entries_empresa.items():
            nuevo_config[key] = entry.get().strip()
        for key, entry in entries_dian.items():
            nuevo_config[key] = entry.get().strip()
        nuevo_config["Responsabilidad Fiscal"] = var_responsabilidad.get()

        if not nuevo_config["NIT"] or not nuevo_config["Razon Social"]:
            messagebox.showwarning("Campos requeridos", "NIT y Razón Social son obligatorios.")
            return

        guardar_config(nuevo_config)
        messagebox.showinfo("Éxito", "Configuración guardada correctamente.")
        ventana.destroy()

    btn_frame = tk.Frame(scroll_frame, bg=paleta["bg_principal"])
    btn_frame.pack(fill="x", pady=(10, 0))

    crear_boton(btn_frame, "← Cerrar", ventana.destroy, "Secundario").pack(side="left")
    crear_boton(btn_frame, "💾 Guardar", guardar, "Exito").pack(side="right")

    ventana.update_idletasks()
    w = ventana.winfo_reqwidth()
    h = ventana.winfo_reqheight()
    ventana.geometry(f"{w}x{h}")
    centrar_ventana(ventana)
    ventana.mainloop()
