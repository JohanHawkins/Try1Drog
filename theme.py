import tkinter as tk
from tkinter import ttk
import json
import os

MODO_OSCURO = False
ARCHIVO_CONFIG = os.path.join(".opencode", "theme_config.json")

PALETA_CLARA = {
    "bg_principal": "#F5F7FA",
    "bg_frame": "#FFFFFF",
    "bg_header": "#1B3A5C",
    "bg_sidebar": "#2C5F8A",
    "bg_input": "#FFFFFF",
    "bg_boton_primario": "#1B3A5C",
    "bg_boton_secundario": "#2C5F8A",
    "bg_boton_peligro": "#C0392B",
    "bg_boton_exito": "#27AE60",
    "bg_boton_advertencia": "#F39C12",
    "bg_card": "#FFFFFF",
    "bg_seleccion": "#D6E4F0",
    "bg_tabla_encabezado": "#1B3A5C",
    "bg_tabla_fila_par": "#FFFFFF",
    "bg_tabla_fila_impar": "#F0F4F8",
    "bg_tabla_hover": "#E8F0FE",
    "texto_principal": "#1A1A2E",
    "texto_secundario": "#5A6A7A",
    "texto_blanco": "#FFFFFF",
    "texto_boton": "#FFFFFF",
    "texto链接": "#2980B9",
    "borde": "#D1D9E6",
    "borde_foco": "#2980B9",
    "alerta_rojo": "#E74C3C",
    "alerta_amarillo": "#F1C40F",
    "alerta_verde": "#27AE60",
    "alerta_rojo_bg": "#FDEDEC",
    "alerta_amarillo_bg": "#FEF9E7",
    "alerta_verde_bg": "#EAFAF1",
    "sombra": "#00000010",
}

PALETA_OSCURA = {
    "bg_principal": "#0D1117",
    "bg_frame": "#161B22",
    "bg_header": "#0D1117",
    "bg_sidebar": "#161B22",
    "bg_input": "#0D1117",
    "bg_boton_primario": "#238636",
    "bg_boton_secundario": "#1F6FEB",
    "bg_boton_peligro": "#DA3633",
    "bg_boton_exito": "#238636",
    "bg_boton_advertencia": "#9E6A03",
    "bg_card": "#161B22",
    "bg_seleccion": "#1F6FEB22",
    "bg_tabla_encabezado": "#21262D",
    "bg_tabla_fila_par": "#0D1117",
    "bg_tabla_fila_impar": "#161B22",
    "bg_tabla_hover": "#1F6FEB22",
    "texto_principal": "#C9D1D9",
    "texto_secundario": "#8B949E",
    "texto_blanco": "#FFFFFF",
    "texto_boton": "#FFFFFF",
    "texto链接": "#58A6FF",
    "borde": "#30363D",
    "borde_foco": "#1F6FEB",
    "alerta_rojo": "#F85149",
    "alerta_amarillo": "#D29922",
    "alerta_verde": "#3FB950",
    "alerta_rojo_bg": "#F8514915",
    "alerta_amarillo_bg": "#D2992215",
    "alerta_verde_bg": "#3FB95015",
    "sombra": "#00000040",
}

def get_paleta():
    return PALETA_OSCURA if MODO_OSCURO else PALETA_CLARA

def toggle_modo_oscuro():
    global MODO_OSCURO
    MODO_OSCURO = not MODO_OSCURO
    guardar_config()
    return MODO_OSCURO

def guardar_config():
    os.makedirs(".opencode", exist_ok=True)
    with open(ARCHIVO_CONFIG, "w") as f:
        json.dump({"modo_oscuro": MODO_OSCURO}, f)

def cargar_config():
    global MODO_OSCURO
    if os.path.exists(ARCHIVO_CONFIG):
        with open(ARCHIVO_CONFIG, "r") as f:
            config = json.load(f)
            MODO_OSCURO = config.get("modo_oscuro", False)

def aplicar_estilos(ventana):
    paleta = get_paleta()
    style = ttk.Style()
    style.theme_use("clam")

    style.configure(".", background=paleta["bg_frame"], foreground=paleta["texto_principal"],
                     font=("Segoe UI", 10))

    style.configure("TFrame", background=paleta["bg_frame"])
    style.configure("TLabel", background=paleta["bg_frame"], foreground=paleta["texto_principal"],
                     font=("Segoe UI", 10))
    style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"),
                     foreground=paleta["texto_blanco"], background=paleta["bg_header"])
    style.configure("SubHeader.TLabel", font=("Segoe UI", 12, "bold"),
                     foreground=paleta["texto_principal"], background=paleta["bg_frame"])
    style.configure("Info.TLabel", font=("Segoe UI", 9),
                     foreground=paleta["texto_secundario"], background=paleta["bg_frame"])

    style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=(15, 8),
                     background=paleta["bg_boton_primario"], foreground=paleta["texto_boton"],
                     borderwidth=0, relief="flat")
    style.map("TButton",
              background=[("active", paleta["bg_boton_secundario"]), ("pressed", paleta["bg_header"])],
              foreground=[("active", paleta["texto_blanco"])])

    style.configure("Primario.TButton", background=paleta["bg_boton_primario"])
    style.configure("Secundario.TButton", background=paleta["bg_boton_secundario"])
    style.configure("Peligro.TButton", background=paleta["bg_boton_peligro"])
    style.configure("Exito.TButton", background=paleta["bg_boton_exito"])
    style.configure("Advertencia.TButton", background=paleta["bg_boton_advertencia"])

    style.configure("TEntry", fieldbackground=paleta["bg_input"], foreground=paleta["texto_principal"],
                     borderwidth=1, relief="solid", padding=6)
    style.map("TEntry",
              bordercolor=[("focus", paleta["borde_foco"])],
              fieldbackground=[("focus", paleta["bg_input"])])

    style.configure("Treeview", background=paleta["bg_frame"], foreground=paleta["texto_principal"],
                     fieldbackground=paleta["bg_frame"], borderwidth=0, rowheight=28,
                     font=("Segoe UI", 10))
    style.configure("Treeview.Heading", background=paleta["bg_tabla_encabezado"],
                     foreground=paleta["texto_blanco"], font=("Segoe UI", 10, "bold"),
                     borderwidth=0, relief="flat")
    style.map("Treeview",
              background=[("selected", paleta["bg_seleccion"])],
              foreground=[("selected", paleta["texto_principal"])])
    style.map("Treeview.Heading",
              background=[("active", paleta["bg_boton_secundario"])])

    style.configure("TScrollbar", background=paleta["borde"], borderwidth=0, arrowsize=12)
    style.map("TScrollbar",
              background=[("active", paleta["bg_boton_secundario"])])

    style.configure("TNotebook", background=paleta["bg_principal"], borderwidth=0)
    style.configure("TNotebook.Tab", background=paleta["bg_frame"], foreground=paleta["texto_principal"],
                     padding=(15, 8), font=("Segoe UI", 10))
    style.map("TNotebook.Tab",
              background=[("selected", paleta["bg_boton_primario"])],
              foreground=[("selected", paleta["texto_blanco"])])

    style.configure("Horizontal.TScale", background=paleta["bg_frame"],
                     troughcolor=paleta["borde"])

    return style

def crear_header(parent, texto, paleta=None):
    if paleta is None:
        paleta = get_paleta()
    header = tk.Frame(parent, bg=paleta["bg_header"], height=60)
    header.pack(fill="x")
    header.pack_propagate(False)
    tk.Label(header, text=texto, font=("Segoe UI", 18, "bold"),
             fg=paleta["texto_blanco"], bg=paleta["bg_header"]).pack(side="left", padx=20, pady=15)

    btn_modo = tk.Button(header, text="🌙" if not MODO_OSCURO else "☀️",
                         font=("Segoe UI", 14), bg=paleta["bg_header"],
                         fg=paleta["texto_blanco"], bd=0, cursor="hand2",
                         command=lambda: toggle_modo_oscuro())
    btn_modo.pack(side="right", padx=20)
    return header

def crear_card(parent, titulo, paleta=None):
    if paleta is None:
        paleta = get_paleta()
    card = tk.Frame(parent, bg=paleta["bg_card"], bd=1, relief="solid",
                     highlightbackground=paleta["borde"], highlightthickness=1)
    if titulo:
        tk.Label(card, text=titulo, font=("Segoe UI", 11, "bold"),
                 fg=paleta["texto_principal"], bg=paleta["bg_card"]).pack(anchor="w", padx=15, pady=(10, 5))
    return card

def crear_boton(parent, texto, comando, estilo="Primario", **kwargs):
    paleta = get_paleta()
    btn = tk.Button(parent, text=texto, command=comando,
                     font=("Segoe UI", 10, "bold"), fg=paleta["texto_boton"],
                     bg=paleta.get(f"bg_boton_{estilo.lower()}", paleta["bg_boton_primario"]),
                     activebackground=paleta["bg_boton_secundario"],
                     activeforeground=paleta["texto_blanco"],
                     bd=0, padx=15, pady=8, cursor="hand2", **kwargs)
    return btn

def crear_entry(parent, **kwargs):
    paleta = get_paleta()
    defaults = {
        "font": ("Segoe UI", 10),
        "bg": paleta["bg_input"],
        "fg": paleta["texto_principal"],
        "insertbackground": paleta["texto_principal"],
        "bd": 1, "relief": "solid", "highlightthickness": 1,
        "highlightbackground": paleta["borde"],
        "highlightcolor": paleta["borde_foco"],
    }
    defaults.update(kwargs)
    return tk.Entry(parent, **defaults)

def crear_label(parent, texto, estilo="normal", **kwargs):
    paleta = get_paleta()
    configs = {
        "normal": {"font": ("Segoe UI", 10), "fg": paleta["texto_principal"]},
        "bold": {"font": ("Segoe UI", 10, "bold"), "fg": paleta["texto_principal"]},
        "subtitle": {"font": ("Segoe UI", 12, "bold"), "fg": paleta["texto_principal"]},
        "info": {"font": ("Segoe UI", 9), "fg": paleta["texto_secundario"]},
        "error": {"font": ("Segoe UI", 10), "fg": paleta["alerta_rojo"]},
        "success": {"font": ("Segoe UI", 10), "fg": paleta["alerta_verde"]},
        "warning": {"font": ("Segoe UI", 10), "fg": paleta["alerta_amarillo"]},
    }
    config = configs.get(estilo, configs["normal"])
    config.update(kwargs)
    return tk.Label(parent, text=texto, bg=paleta["bg_frame"], **config)

def crear_alerta(parent, tipo, texto, paleta=None):
    if paleta is None:
        paleta = get_paleta()
    colores = {
        "rojo": (paleta["alerta_rojo"], paleta["alerta_rojo_bg"]),
        "amarillo": (paleta["alerta_amarillo"], paleta["alerta_amarillo_bg"]),
        "verde": (paleta["alerta_verde"], paleta["alerta_verde_bg"]),
    }
    color_texto, color_fondo = colores.get(tipo, colores["rojo"])
    frame = tk.Frame(parent, bg=color_fondo, bd=1, relief="solid",
                      highlightbackground=color_texto, highlightthickness=1)
    tk.Label(frame, text=f"  {texto}", font=("Segoe UI", 10, "bold"),
             fg=color_texto, bg=color_fondo, anchor="w").pack(fill="x", padx=10, pady=8)
    return frame

def crear_treeview(parent, columns, paleta=None):
    if paleta is None:
        paleta = get_paleta()
    tree = ttk.Treeview(parent, columns=columns, show="headings", style="Treeview")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120)
    tree.tag_configure("evenrow", background=paleta["bg_tabla_fila_par"])
    tree.tag_configure("oddrow", background=paleta["bg_tabla_fila_impar"])
    return tree

cargar_config()
