import tkinter as tk
import os
import pandas as pd
from tkinter import messagebox
from datetime import datetime
from utils import centrar_ventana
from theme import (get_paleta, aplicar_estilos, crear_header, crear_boton,
                    crear_entry, crear_label, crear_card, crear_alerta)
from Clientes.Clientes import cargar_puntos_cliente, sumar_puntos
from Facturacion.facturacion import mostrar_ventana_facturacion

ventana_confirmacion = None
indices_sugerencias = []
metodo_pago_seleccionado = "Efectivo"

def volver_al_menu(ventana):
    ventana.destroy()
    import VenMenu
    VenMenu.mostrar_ventana_menu()

def solo_numeros(event):
    if not event.char.isdigit() and event.keysym not in ["BackSpace", "Delete"]:
        return "break"

def cargar_productos():
    try:
        df = pd.read_excel("Inventario/inventario_productos.xlsx")
        columnas = ["Nombre Producto", "Cantidad Producto", "Precio Producto (COP)", "Categoria", "Fecha Vencimiento"]
        if "Unidad" in df.columns:
            columnas.append("Unidad")
        return df[columnas].dropna(subset=["Nombre Producto", "Cantidad Producto", "Precio Producto (COP)"])
    except Exception:
        return pd.DataFrame(columns=["Nombre Producto", "Cantidad Producto", "Precio Producto (COP)", "Categoria", "Fecha Vencimiento", "Unidad"])

def actualizar_sugerencias(event):
    global indices_sugerencias
    texto = entry_nombre.get().lower()
    sugerencias = lista_productos[lista_productos["Nombre Producto"].str.lower().str.contains(texto, na=False)]
    listbox_sugerencias.delete(0, tk.END)
    indices_sugerencias = []
    for idx, producto in sugerencias.iterrows():
        listbox_sugerencias.insert(tk.END, producto["Nombre Producto"])
        indices_sugerencias.append(idx)
    if not sugerencias.empty:
        listbox_sugerencias.place(x=entry_nombre.winfo_x(), y=entry_nombre.winfo_y() + entry_nombre.winfo_height())
        listbox_sugerencias.lift()
    else:
        listbox_sugerencias.place_forget()

def ocultar_sugerencias(event=None):
    listbox_sugerencias.place_forget()

def seleccionar_sugerencia(event):
    seleccion_index = listbox_sugerencias.curselection()
    if seleccion_index:
        idx_producto = indices_sugerencias[seleccion_index[0]]
        nombre_producto = lista_productos.loc[idx_producto, "Nombre Producto"]
        entry_nombre.delete(0, tk.END)
        entry_nombre.insert(0, nombre_producto)
        actualizar_stock_y_precio(nombre_producto)
    listbox_sugerencias.place_forget()

def actualizar_stock_y_precio(nombre_producto):
    paleta = get_paleta()
    cantidad = lista_productos.loc[lista_productos["Nombre Producto"] == nombre_producto, "Cantidad Producto"]
    precio = lista_productos.loc[lista_productos["Nombre Producto"] == nombre_producto, "Precio Producto (COP)"]
    unidad = lista_productos.loc[lista_productos["Nombre Producto"] == nombre_producto, "Unidad"] if "Unidad" in lista_productos.columns else None
    categoria = lista_productos.loc[lista_productos["Nombre Producto"] == nombre_producto, "Categoria"] if "Categoria" in lista_productos.columns else None

    if not cantidad.empty:
        stock_val = int(cantidad.iloc[0])
        label_stock_val.config(text=str(stock_val))
        if stock_val <= 0:
            label_stock_val.config(fg=paleta["alerta_rojo"])
        else:
            label_stock_val.config(fg=paleta["alerta_verde"])

    if unidad is not None and not unidad.empty:
        label_unidad_val.config(text=str(unidad.iloc[0]))
    else:
        label_unidad_val.config(text="Unidad")

    if categoria is not None and not categoria.empty:
        cat = str(categoria.iloc[0]).lower()
        colores = {"rojo": paleta["alerta_rojo"], "amarillo": paleta["alerta_amarillo"], "verde": paleta["alerta_verde"]}
        label_categoria_val.config(text=categoria.iloc[0], fg=colores.get(cat, paleta["texto_principal"]))
    else:
        label_categoria_val.config(text="-")

    if not precio.empty:
        try:
            precio_value = precio.iloc[0]
            if isinstance(precio_value, str):
                precio_numerico = float(precio_value.replace(',', '').replace('$', '').replace('COP', '').strip())
            else:
                precio_numerico = float(precio_value)
            label_precio_val.config(text=f"${precio_numerico:,.2f} COP")
        except ValueError:
            pass

def calcular_total(event=None):
    paleta = get_paleta()
    try:
        cantidad = int(entry_cantidad.get())
        precio_texto = label_precio_val.cget("text").replace('$', '').replace('COP', '').replace(',', '').strip()
        precio = float(precio_texto) if precio_texto else 0.0
        total = cantidad * precio
        label_total.config(text=f"${total:,.2f} COP", fg=paleta["alerta_verde"])
    except ValueError:
        label_total.config(text="$0.00 COP", fg=paleta["texto_secundario"])

def seleccionar_metodo_pago(metodo):
    global metodo_pago_seleccionado
    paleta = get_paleta()
    metodo_pago_seleccionado = metodo
    
    if hasattr(seleccionar_metodo_pago, 'btn_efectivo'):
        seleccionar_metodo_pago.btn_efectivo.config(bg=paleta["bg_boton_secundario"])
        seleccionar_metodo_pago.btn_banco.config(bg=paleta["bg_boton_secundario"])
        seleccionar_metodo_pago.btn_puntos.config(bg=paleta["bg_boton_secundario"])
    
    if metodo == "Efectivo":
        seleccionar_metodo_pago.btn_efectivo.config(bg=paleta["bg_boton_exito"])
    elif metodo == "Banco":
        seleccionar_metodo_pago.btn_banco.config(bg=paleta["alerta_amarillo"])
        messagebox.showinfo("No disponible", "El pago por banco no está disponible aún.")
    elif metodo == "Puntos":
        seleccionar_metodo_pago.btn_puntos.config(bg=paleta["alerta_azul"])
    
    if hasattr(seleccionar_metodo_pago, 'label_metodo'):
        seleccionar_metodo_pago.label_metodo.config(text=f"Método: {metodo}")

def confirmar_compra():
    global ventana_confirmacion

    if ventana_confirmacion is not None and ventana_confirmacion.winfo_exists():
        return

    if not entry_nombre.get() or not entry_cantidad.get() or label_precio_val.cget("text") == "$0.00 COP":
        messagebox.showwarning("Campos incompletos", "Complete todos los campos antes de confirmar.")
        return

    paleta = get_paleta()
    ventana_confirmacion = tk.Toplevel()
    ventana_confirmacion.title("Confirmar Venta")
    ventana_confirmacion.resizable(True, True)
    ventana_confirmacion.minsize(320, 320)
    ventana_confirmacion.configure(bg=paleta["bg_frame"])
    ventana_confirmacion.grab_set()

    centrar_ventana(ventana_confirmacion)

    body = tk.Frame(ventana_confirmacion, bg=paleta["bg_frame"])
    body.pack(fill="both", expand=True, padx=20, pady=15)

    crear_label(body, "Confirmar Venta", "subtitle").pack(anchor="w", pady=(0, 10))

    info_frame = tk.Frame(body, bg=paleta["bg_card"], bd=1, relief="solid",
                           highlightbackground=paleta["borde"], highlightthickness=1)
    info_frame.pack(fill="x", pady=(0, 15))

    crear_label(info_frame, f"Producto: {entry_nombre.get()}", "normal").pack(anchor="w", padx=10, pady=3)
    crear_label(info_frame, f"Cantidad: {entry_cantidad.get()}", "normal").pack(anchor="w", padx=10, pady=3)
    crear_label(info_frame, f"Total: {label_total.cget('text')}", "bold").pack(anchor="w", padx=10, pady=3)

    metodo_frame = tk.Frame(body, bg=paleta["bg_card"], bd=1, relief="solid",
                             highlightbackground=paleta["borde"], highlightthickness=1)
    metodo_frame.pack(fill="x", pady=(0, 15))
    
    tk.Label(metodo_frame, text="Método de Pago", font=("Segoe UI", 10, "bold"),
             fg=paleta["texto_principal"], bg=paleta["bg_card"]).pack(anchor="w", padx=10, pady=(8, 5))
    
    btn_metodos = tk.Frame(metodo_frame, bg=paleta["bg_card"])
    btn_metodos.pack(fill="x", padx=10, pady=(0, 10))
    
    seleccionar_metodo_pago.btn_efectivo = crear_boton(btn_metodos, "💵 Efectivo", 
        lambda: seleccionar_metodo_pago("Efectivo"), "Exito", "pequeño")
    seleccionar_metodo_pago.btn_efectivo.pack(side="left", padx=(0, 5))
    
    seleccionar_metodo_pago.btn_banco = crear_boton(btn_metodos, "🏦 Banco", 
        lambda: seleccionar_metodo_pago("Banco"), "Advertencia", "pequeño")
    seleccionar_metodo_pago.btn_banco.pack(side="left", padx=(0, 5))
    
    seleccionar_metodo_pago.btn_puntos = crear_boton(btn_metodos, "🎯 Puntos", 
        lambda: seleccionar_metodo_pago("Puntos"), "Primario", "pequeño")
    seleccionar_metodo_pago.btn_puntos.pack(side="left")
    
    seleccionar_metodo_pago.label_metodo = crear_label(metodo_frame, "Método: Efectivo", "info")
    seleccionar_metodo_pago.label_metodo.pack(anchor="w", padx=10, pady=(0, 8))
    
    seleccionar_metodo_pago("Efectivo")

    btn_frame = tk.Frame(body, bg=paleta["bg_frame"])
    btn_frame.pack(fill="x")

    crear_boton(btn_frame, "Cancelar", cerrar_ventana_confirmacion, "Secundario").pack(side="left")
    crear_boton(btn_frame, "✓ Confirmar", lambda: realizar_compra(ventana_confirmacion), "Exito").pack(side="right")

    centrar_ventana(ventana_confirmacion)

def cerrar_ventana_confirmacion():
    global ventana_confirmacion
    if ventana_confirmacion:
        ventana_confirmacion.destroy()
        ventana_confirmacion = None

def realizar_compra(ventana_confirmacion):
    global lista_productos, metodo_pago_seleccionado
    paleta = get_paleta()

    nombre_producto = entry_nombre.get()
    cantidad_comprada = int(entry_cantidad.get())

    if metodo_pago_seleccionado == "Banco":
        messagebox.showinfo("No disponible", "El pago por banco no está disponible aún.")
        return

    if metodo_pago_seleccionado == "Puntos":
        cedula = entrada_cedula.get().strip()
        if not cedula:
            messagebox.showwarning("Campos incompletos", "Ingrese la cédula del cliente para canjear puntos.")
            return
        
        puntos_disponibles = cargar_puntos_cliente(cedula)
        if puntos_disponibles is None:
            messagebox.showerror("Error", "Cliente no encontrado.")
            return
        
        try:
            total_texto = label_total.cget("text").replace('$', '').replace('COP', '').replace(',', '').strip()
            total_compra = float(total_texto)
        except ValueError:
            messagebox.showerror("Error", "No se pudo calcular el total.")
            return
        
        puntos_necesarios = int(total_compra / 100)
        
        if puntos_disponibles < puntos_necesarios:
            messagebox.showwarning("Puntos insuficientes", 
                f"Puntos disponibles: {puntos_disponibles}\nPuntos necesarios: {puntos_necesarios}")
            return
        
        if not messagebox.askyesno("Confirmar Canjeo", 
            f"Canjear {puntos_necesarios} puntos por ${total_compra:,.2f} COP?\nPuntos restantes: {puntos_disponibles - puntos_necesarios}"):
            return
        
        sumar_puntos(cedula, -puntos_necesarios)

    producto = lista_productos.loc[lista_productos["Nombre Producto"] == nombre_producto]
    if not producto.empty:
        stock_actual = int(producto["Cantidad Producto"].values[0])
        nuevo_stock = stock_actual - cantidad_comprada
        if nuevo_stock < 0:
            messagebox.showwarning("Stock insuficiente", "No hay suficiente stock para completar la compra.")
            cerrar_ventana_confirmacion()
            return

        lista_productos.loc[lista_productos["Nombre Producto"] == nombre_producto, "Cantidad Producto"] = nuevo_stock
        try:
            lista_productos.to_excel("Inventario/inventario_productos.xlsx", index=False)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el inventario: {e}")

        registro_compra = pd.DataFrame({
            "Nombre Producto": [nombre_producto],
            "Cantidad Comprada": [cantidad_comprada],
            "Precio Total": [label_total.cget("text")],
            "Método Pago": [metodo_pago_seleccionado],
            "Fecha": [datetime.now().strftime("%Y-%m-%d")],
            "Hora": [datetime.now().strftime("%H:%M:%S")]
        })

        try:
            archivo = "Ventas/registros_compra.xlsx"
            if os.path.exists(archivo):
                df_registros = pd.read_excel(archivo)
                df_registros = pd.concat([df_registros, registro_compra], ignore_index=True)
            else:
                df_registros = registro_compra
            df_registros.to_excel(archivo, index=False)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el registro: {e}")

        if metodo_pago_seleccionado == "Efectivo":
            try:
                total_texto = label_total.cget("text").replace('$', '').replace('COP', '').replace(',', '').strip()
                total_compra = float(total_texto)
                puntos_ganados = int(total_compra / 1000)
                if puntos_ganados > 0:
                    cedula_cliente = entrada_cedula.get().strip()
                    if cedula_cliente:
                        sumar_puntos(cedula_cliente, puntos_ganados)
                        messagebox.showinfo("Puntos", f"¡El cliente ganó {puntos_ganados} puntos!")
            except:
                pass

        cerrar_ventana_confirmacion()
        entry_nombre.delete(0, tk.END)
        entry_cantidad.delete(0, tk.END)
        label_precio_val.config(text="$0.00 COP")
        label_stock_val.config(text="-", fg=paleta["texto_secundario"])
        label_unidad_val.config(text="-")
        label_categoria_val.config(text="-", fg=paleta["texto_principal"])
        label_total.config(text="$0.00 COP", fg=paleta["texto_secundario"])
        messagebox.showinfo("Venta exitosa", "La venta se completó correctamente.")
    else:
        messagebox.showerror("Error", "El producto no se encuentra en el inventario.")
        cerrar_ventana_confirmacion()

def mostrar_ventana_ventas():
    global entry_nombre, entry_cantidad, label_total, listbox_sugerencias, lista_productos
    global label_stock_val, label_precio_val, label_unidad_val, label_categoria_val
    global entrada_cedula

    paleta = get_paleta()
    lista_productos = cargar_productos()

    ventana_ventas = tk.Tk()
    ventana_ventas.title("Drogs+ - Punto de Venta")
    ventana_ventas.resizable(True, True)
    ventana_ventas.minsize(400, 480)
    ventana_ventas.configure(bg=paleta["bg_principal"])

    icon_path = os.path.join("images", "cruz_azul.ico")
    if os.path.exists(icon_path):
        ventana_ventas.iconbitmap(icon_path)

    aplicar_estilos(ventana_ventas)
    centrar_ventana(ventana_ventas)

    crear_header(ventana_ventas, "Punto de Venta")

    main_frame = tk.Frame(ventana_ventas, bg=paleta["bg_principal"])
    main_frame.pack(fill="both", expand=True, padx=25, pady=12)

    search_card = crear_card(main_frame, "Producto")
    search_card.pack(fill="x", pady=(0, 14))
    search_inner = tk.Frame(search_card, bg=paleta["bg_card"])
    search_inner.pack(fill="x", padx=15, pady=(0, 16))

    entry_nombre = crear_entry(search_inner, width=40, font=("Segoe UI", 12))
    entry_nombre.pack(fill="x")
    entry_nombre.bind("<KeyRelease>", actualizar_sugerencias)
    entry_nombre.bind("<FocusOut>", ocultar_sugerencias)
    entry_nombre.focus_set()

    listbox_sugerencias = tk.Listbox(search_inner, height=4, font=("Segoe UI", 10),
                                      bg=paleta["bg_input"], fg=paleta["texto_principal"],
                                      selectbackground=paleta["bg_seleccion"],
                                      highlightbackground=paleta["borde"], highlightthickness=1)
    listbox_sugerencias.bind("<<ListboxSelect>>", seleccionar_sugerencia)

    detalle_card = crear_card(main_frame, "Detalles del Producto")
    detalle_card.pack(fill="x", pady=(0, 14))
    detalle_inner = tk.Frame(detalle_card, bg=paleta["bg_card"])
    detalle_inner.pack(fill="x", padx=15, pady=(0, 16))

    crear_label(detalle_inner, "Stock:", "bold").grid(row=0, column=0, sticky="e", padx=(0, 6), pady=6)
    label_stock_val = crear_label(detalle_inner, "-", "normal")
    label_stock_val.grid(row=0, column=1, sticky="w", padx=(0, 20), pady=6)

    crear_label(detalle_inner, "Precio:", "bold").grid(row=0, column=2, sticky="e", padx=(0, 6), pady=6)
    label_precio_val = crear_label(detalle_inner, "$0.00 COP", "normal")
    label_precio_val.grid(row=0, column=3, sticky="w", pady=6)

    crear_label(detalle_inner, "Unidad:", "bold").grid(row=1, column=0, sticky="e", padx=(0, 6), pady=6)
    label_unidad_val = crear_label(detalle_inner, "-", "normal")
    label_unidad_val.grid(row=1, column=1, sticky="w", padx=(0, 20), pady=6)

    crear_label(detalle_inner, "Categoría:", "bold").grid(row=1, column=2, sticky="e", padx=(0, 6), pady=6)
    label_categoria_val = crear_label(detalle_inner, "-", "normal")
    label_categoria_val.grid(row=1, column=3, sticky="w", pady=6)

    cant_card = crear_card(main_frame, "Cantidad")
    cant_card.pack(fill="x", pady=(0, 14))
    cant_inner = tk.Frame(cant_card, bg=paleta["bg_card"])
    cant_inner.pack(fill="x", padx=15, pady=(0, 16))

    entry_cantidad = crear_entry(cant_inner, font=("Segoe UI", 16))
    entry_cantidad.pack(fill="x")
    entry_cantidad.bind("<KeyRelease>", calcular_total)
    entry_cantidad.bind("<KeyPress>", solo_numeros)

    cliente_card = crear_card(main_frame, "Cliente (Opcional - Para Puntos)")
    cliente_card.pack(fill="x", pady=(0, 14))
    cliente_inner = tk.Frame(cliente_card, bg=paleta["bg_card"])
    cliente_inner.pack(fill="x", padx=15, pady=(0, 16))
    
    crear_label(cliente_inner, "Cédula:", "bold").pack(anchor="w")
    entrada_cedula = crear_entry(cliente_inner, font=("Segoe UI", 12))
    entrada_cedula.pack(fill="x")

    total_card = tk.Frame(main_frame, bg=paleta["bg_boton_primario"], bd=0)
    total_card.pack(fill="x", pady=(0, 14))
    total_inner = tk.Frame(total_card, bg=paleta["bg_boton_primario"])
    total_inner.pack(fill="x", padx=20, pady=18)
    tk.Label(total_inner, text="TOTAL A PAGAR", font=("Segoe UI", 10, "bold"),
             fg=paleta["texto_blanco"], bg=paleta["bg_boton_primario"]).pack(anchor="w")
    label_total = tk.Label(total_inner, text="$0.00 COP", font=("Segoe UI", 24, "bold"),
                            fg=paleta["texto_blanco"], bg=paleta["bg_boton_primario"])
    label_total.pack(anchor="w")

    btn_frame = tk.Frame(main_frame, bg=paleta["bg_principal"])
    btn_frame.pack(fill="x", pady=(8, 0))

    crear_boton(btn_frame, "← Volver", lambda: volver_al_menu(ventana_ventas), "Secundario", "pequeño").pack(side="left")
    crear_boton(btn_frame, "📄 Factura", lambda: [ventana_ventas.destroy(), mostrar_ventana_facturacion()], "Primario", "pequeño").pack(side="left", padx=(10, 0))
    crear_boton(btn_frame, "✓ Vender (Enter)", confirmar_compra, "Exito", "pequeño").pack(side="right")

    entry_nombre.bind("<Return>", lambda e: entry_cantidad.focus_set())
    entry_cantidad.bind("<Return>", lambda e: confirmar_compra())

    centrar_ventana(ventana_ventas)

    ventana_ventas.mainloop()
