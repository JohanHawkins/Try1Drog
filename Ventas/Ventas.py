import tkinter as tk
import os
import pandas as pd
from tkinter import messagebox
from datetime import datetime

indices_sugerencias = []
ventana_confirmacion = None  # Variable global para la ventana de confirmación

def centrar_ventana(ventana):
    ventana.update_idletasks()
    width = ventana.winfo_width()
    height = ventana.winfo_height()
    x = (ventana.winfo_screenwidth() // 2) - (width // 2)
    y = (ventana.winfo_screenheight() // 2) - (height // 2)
    ventana.geometry(f'{width}x{height}+{x}+{y}')

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
        return df[["Nombre Producto", "Cantidad Producto", "Precio Producto (COP)", "Categoria", "Fecha Vencimiento"]].dropna()
    except Exception as e:
        print(f"Error al cargar el archivo: {e}")
        return pd.DataFrame(columns=["Nombre Producto", "Cantidad Producto", "Precio Producto (COP)", "Categoria", "Fecha Vencimiento"])

def actualizar_sugerencias(event):
    global indices_sugerencias
    texto = entry_nombre.get().lower()
    
    # Filtramos productos que coincidan con el texto ingresado
    sugerencias = lista_productos[lista_productos["Nombre Producto"].str.lower().str.contains(texto, na=False)]
    
    # Limpiar las sugerencias previas y la lista de índices
    listbox_sugerencias.delete(0, tk.END)
    indices_sugerencias = []

    # Agregar nuevas sugerencias al Listbox y guardar sus índices
    for idx, producto in sugerencias.iterrows():
        listbox_sugerencias.insert(tk.END, producto["Nombre Producto"])
        indices_sugerencias.append(idx)  # Guardamos el índice original de lista_productos

    # Mostrar el Listbox si hay sugerencias, ocultarlo si no
    if not sugerencias.empty:
        listbox_sugerencias.place(x=entry_nombre.winfo_x(), y=entry_nombre.winfo_y() + entry_nombre.winfo_height())
        listbox_sugerencias.lift()  # Asegurar que está en primer plano
    else:
        listbox_sugerencias.place_forget()

def ocultar_sugerencias(event=None):
    # Ocultar el Listbox de sugerencias
    listbox_sugerencias.place_forget()

def seleccionar_sugerencia(event):
    seleccion_index = listbox_sugerencias.curselection()
    if seleccion_index:
        # Obtener el índice del producto en lista_productos usando indices_sugerencias
        idx_producto = indices_sugerencias[seleccion_index[0]]
        nombre_producto = lista_productos.loc[idx_producto, "Nombre Producto"]
        
        # Actualizar el campo de entrada con el nombre del producto seleccionado
        entry_nombre.delete(0, tk.END)
        entry_nombre.insert(0, nombre_producto)
        
        # Actualizar el stock y el precio
        actualizar_stock_y_precio(nombre_producto)
    listbox_sugerencias.place_forget()

def actualizar_stock_y_precio(nombre_producto):
    cantidad = lista_productos.loc[lista_productos["Nombre Producto"] == nombre_producto, "Cantidad Producto"]
    precio = lista_productos.loc[lista_productos["Nombre Producto"] == nombre_producto, "Precio Producto (COP)"]
    
    if not cantidad.empty:
        entry_stock.config(state="normal")
        entry_stock.delete(0, tk.END)
        entry_stock.insert(0, int(cantidad.iloc[0]))
        entry_stock.config(state="readonly")
    
    if not precio.empty:
        try:
            # Verificar si el precio es una cadena, de ser así se hace la limpieza
            precio_value = precio.iloc[0]
            if isinstance(precio_value, str):
                precio_numerico = float(precio_value.replace(',', '').replace('$', '').replace('COP', '').strip())
            else:
                # Si el precio ya es numérico, lo asignamos directamente
                precio_numerico = float(precio_value)

            entry_precio.config(state="normal")
            entry_precio.delete(0, tk.END)
            entry_precio.insert(0, f"${precio_numerico:,.2f} COP")
            entry_precio.config(state="readonly")
        except ValueError:
            print("Error: El precio no está en un formato numérico válido.")

def calcular_total(event=None):
    try:
        cantidad = int(entry_cantidad.get())
        precio_texto = entry_precio.get().replace('$', '').replace('COP', '').replace(',', '').strip()
        precio = float(precio_texto) if precio_texto else 0.0
        total = cantidad * precio
        label_total.config(text=f"Total a pagar: ${total:,.2f} COP")
    except ValueError:
        label_total.config(text="Total a pagar: $0.00 COP")

def confirmar_compra():
    global ventana_confirmacion

    if ventana_confirmacion is not None and ventana_confirmacion.winfo_exists():
        return

    if not entry_nombre.get() or not entry_cantidad.get() or not entry_precio.get():
        messagebox.showwarning("Campos incompletos", "Por favor, complete todos los campos antes de confirmar.")
        return

    ventana_confirmacion = tk.Toplevel()
    ventana_confirmacion.title("Confirmación de Compra")
    ventana_confirmacion.resizable(False, False)
    ventana_confirmacion.geometry("250x150")

    nombre_producto = entry_nombre.get()
    cantidad_producto = entry_cantidad.get()
    precio_total = label_total.cget("text")

    label_info = tk.Label(
        ventana_confirmacion,
        text=f"Nombre del Producto: {nombre_producto}\n"
             f"Cantidad Producto: {cantidad_producto}\n"
             f"{precio_total}",
        padx=20, pady=10
    )
    label_info.pack()

    centrar_ventana(ventana_confirmacion)

    frame_botones = tk.Frame(ventana_confirmacion)
    frame_botones.pack(pady=10)

    boton_comprar = tk.Button(frame_botones, text="Comprar", command=lambda: realizar_compra(ventana_confirmacion))
    boton_comprar.grid(row=0, column=0, padx=5)

    boton_cancelar = tk.Button(frame_botones, text="Cancelar", command=cerrar_ventana_confirmacion)
    boton_cancelar.grid(row=0, column=1, padx=5)

def cerrar_ventana_confirmacion():
    global ventana_confirmacion
    if ventana_confirmacion:
        ventana_confirmacion.destroy()
        ventana_confirmacion = None

def realizar_compra(ventana_confirmacion):
    global lista_productos
    
    nombre_producto = entry_nombre.get()
    cantidad_comprada = int(entry_cantidad.get())
    
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
            messagebox.showinfo("Compra confirmada", "La compra se realizó exitosamente y el stock ha sido actualizado.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el archivo de inventario: {e}")
        
        registro_compra = pd.DataFrame({
            "Nombre Producto": [nombre_producto],
            "Cantidad Comprada": [cantidad_comprada],
            "Precio Total": [label_total.cget("text")],
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
            messagebox.showerror("Error", f"No se pudo guardar el registro de compra: {e}")
        
        cerrar_ventana_confirmacion()
        
        entry_nombre.delete(0, tk.END)
        entry_cantidad.delete(0, tk.END)
        entry_precio.config(state="normal")
        entry_precio.delete(0, tk.END)
        entry_precio.config(state="readonly")
        label_total.config(text="Total a pagar: $0.00 COP")
    else:
        messagebox.showerror("Error", "El producto no se encuentra en el inventario.")
        cerrar_ventana_confirmacion()

def mostrar_ventana_ventas():
    global entry_nombre, entry_stock, entry_precio, entry_cantidad, label_total, listbox_sugerencias, lista_productos

    lista_productos = cargar_productos()

    ventana_ventas = tk.Tk()
    ventana_ventas.title("Ventas")
    ventana_ventas.geometry("290x270")
    ventana_ventas.resizable(False, False)
    ventana_ventas.attributes('-fullscreen', False)

    icon_path = os.path.join("images", "cruz_azul.ico")
    ventana_ventas.iconbitmap(icon_path)

    centrar_ventana(ventana_ventas)

    frame = tk.Frame(ventana_ventas)
    frame.pack(pady=15, padx=10, anchor="w")

    label_nombre = tk.Label(frame, text="Nombre del producto:")
    label_nombre.grid(row=0, column=0, sticky="e", pady=(0, 8))
    entry_nombre = tk.Entry(frame, width=20)
    entry_nombre.grid(row=0, column=1, padx=(10, 0), pady=(0, 8), sticky="w")
    entry_nombre.bind("<KeyRelease>", actualizar_sugerencias)
    entry_nombre.bind("<FocusOut>", ocultar_sugerencias)

    scrollbar = tk.Scrollbar(frame)
    listbox_sugerencias = tk.Listbox(frame, width=20, height=4, yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox_sugerencias.yview)
    listbox_sugerencias.bind("<<ListboxSelect>>", seleccionar_sugerencia)

    label_stock = tk.Label(frame, text="Stock disponible:")
    label_stock.grid(row=1, column=0, sticky="e", pady=(0, 8))
    entry_stock = tk.Entry(frame, state="readonly", width=20)
    entry_stock.grid(row=1, column=1, padx=(10, 0), pady=(0, 8), sticky="w")

    label_precio = tk.Label(frame, text="Precio unitario (COP):")
    label_precio.grid(row=2, column=0, sticky="e", pady=(0, 8))
    entry_precio = tk.Entry(frame, state="readonly", width=20)
    entry_precio.grid(row=2, column=1, padx=(10, 0), pady=(0, 8), sticky="w")

    label_cantidad = tk.Label(frame, text="Cantidad a comprar:")
    label_cantidad.grid(row=3, column=0, sticky="e", pady=(0, 8))
    entry_cantidad = tk.Entry(frame, width=20)
    entry_cantidad.grid(row=3, column=1, padx=(10, 0), pady=(0, 8), sticky="w")
    entry_cantidad.bind("<KeyRelease>", calcular_total)
    entry_cantidad.bind("<KeyPress>", solo_numeros)

    label_total = tk.Label(ventana_ventas, text="Total a pagar: $0.00 COP", font=("Arial", 12))
    label_total.pack(pady=10)

    boton_confirmar = tk.Button(ventana_ventas, text="Confirmar compra", command=confirmar_compra)
    boton_confirmar.pack(pady=(0, 5))

    boton_volver = tk.Button(ventana_ventas, text="Volver al menú", command=lambda: volver_al_menu(ventana_ventas))
    boton_volver.pack()

    ventana_ventas.mainloop()