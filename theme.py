import tkinter as tk
from tkinter import ttk

PALETA = {
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
    "borde": "#D1D9E6",
    "borde_foco": "#2980B9",
    "alerta_rojo": "#E74C3C",
    "alerta_amarillo": "#F1C40F",
    "alerta_verde": "#27AE60",
    "alerta_azul": "#2980B9",
    "alerta_rojo_bg": "#FDEDEC",
    "alerta_amarillo_bg": "#FEF9E7",
    "alerta_verde_bg": "#EAFAF1",
    "sombra": "#00000010",
}

def get_paleta():
    return PALETA

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
    return header

def crear_card(parent, titulo, paleta=None):
    if paleta is None:
        paleta = get_paleta()
    card = tk.Frame(parent, bg=paleta["bg_card"], bd=1, relief="solid",
                     highlightbackground=paleta["borde"], highlightthickness=1)
    if titulo:
        tk.Label(card, text=titulo, font=("Segoe UI", 11, "bold"),
                 fg=paleta["texto_principal"], bg=paleta["bg_card"]).pack(anchor="w", padx=15, pady=(6, 2))
    return card

def crear_boton(parent, texto, comando, estilo="Primario", tamaño="normal", **kwargs):
    paleta = get_paleta()
    if tamaño == "pequeño":
        font = ("Segoe UI", 9)
        px, py = 10, 5
    else:
        font = ("Segoe UI", 10, "bold")
        px, py = 15, 8
    btn = tk.Button(parent, text=texto, command=comando,
                     font=font, fg=paleta["texto_boton"],
                     bg=paleta.get(f"bg_boton_{estilo.lower()}", paleta["bg_boton_primario"]),
                     activebackground=paleta["bg_boton_secundario"],
                     activeforeground=paleta["texto_blanco"],
                     bd=0, padx=px, pady=py, cursor="hand2", **kwargs)
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
