import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd

# Variables globales para verificar si las ventanas están abiertas
ventana_editar_abierta = False
ventana_resultados_abierta = False

def mostrar_ventana_editar():
    global ventana_editar_abierta  # Utiliza la variable global

    if ventana_editar_abierta:
        messagebox.showwarning("Advertencia", "La ventana de edición ya está abierta.")
        return  # Si la ventana ya está abierta, no hacemos nada

    ventana_editar_abierta = True  # Marcar como abierta
    ventana_editar = tk.Toplevel()
    ventana_editar.title("Buscar Producto")
    ventana_editar.geometry("300x200")  # Tamaño de la ventana

    # Campo de entrada de texto para búsqueda
    label_editar = tk.Label(ventana_editar, text="Buscar Producto:")
    label_editar.pack(padx=10, pady=10)

    entry_editar = tk.Entry(ventana_editar)
    entry_editar.pack(padx=10, pady=10)

    # Función para buscar datos en el Excel
    def buscar_datos():
        producto_buscado = entry_editar.get()
        try:
            df = pd.read_excel("Inventario/inventario_productos.xlsx")
            resultados = df[df['Nombre Producto'].str.contains(producto_buscado, case=False, na=False)]

            if not resultados.empty:
                mostrar_resultados(resultados)
            else:
                messagebox.showinfo("Resultados de la búsqueda", "No se encontraron coincidencias.")

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al buscar: {str(e)}")

    def mostrar_resultados(resultados):
        global ventana_resultados_abierta

        if ventana_resultados_abierta:
            messagebox.showwarning("Advertencia", "La ventana de resultados de búsqueda ya está abierta.")
            return

        ventana_resultados_abierta = True
        ventana_resultados = tk.Toplevel()
        ventana_resultados.title("Resultados de la Búsqueda")
        ventana_resultados.geometry("800x400")

        # Configurar cierre de la ventana de resultados
        ventana_resultados.protocol("WM_DELETE_WINDOW", lambda: cerrar_ventana_resultados(ventana_resultados))

        # Verificar si la columna 'Categoria' existe en el DataFrame
        if 'Categoria' not in resultados.columns:
            resultados['Categoria'] = ''  # Agrega la columna si no existe (opcional)

        # Definir las columnas para el Treeview, incluyendo 'Categoria'
        columns = ['Nombre Producto', 'Cantidad Producto', 'Precio Producto (COP)', 'Categoria', 'Fecha Vencimiento']
        tree = ttk.Treeview(ventana_resultados, columns=columns, show='headings')
        tree.pack(expand=True, fill='both')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor='center')

        # Insertar los datos en el Treeview
        for index, row in resultados.iterrows():
            values = [row.get(col, '') for col in columns]  # Extrae los valores de cada columna incluida
            item_id = tree.insert("", "end", values=values)  # Guarda índice del DataFrame en 'item_id'

            # Obtener el color según la categoría (solo para la columna 4)
            categoria_value = row['Categoria'].lower()
            if categoria_value == "rojo":
                tree.item(item_id, tags=("color_categoria_rojo",))
            elif categoria_value == "amarillo":
                tree.item(item_id, tags=("color_categoria_amarillo",))
            elif categoria_value == "verde":
                tree.item(item_id, tags=("color_categoria_verde",))

        # Configuración de los tags para colorear solo la columna 'Categoria'
        tree.tag_configure("color_categoria_rojo", background="#e6452a")  # Rojo
        tree.tag_configure("color_categoria_amarillo", background="#e8ee00")  # Amarillo
        tree.tag_configure("color_categoria_verde", background="#a9e597")  # Verde

        # Función para guardar todos los cambios en el archivo Excel
        def guardar_todos_los_cambios():
            try:
                # Actualiza el DataFrame con los cambios del Treeview
                rows = []
                for item_id in tree.get_children():
                    row_data = tree.item(item_id, "values")  # Extrae todos los valores de las columnas
                    rows.append(row_data)

                # Crear DataFrame a partir de los datos editados
                df_actualizado = pd.DataFrame(rows, columns=columns)
                df_actualizado.to_excel("Inventario/inventario_productos.xlsx", index=False)
                messagebox.showinfo("Guardado", "Todos los cambios han sido guardados en el archivo Excel.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo: {str(e)}")

        # Función para editar la celda con doble clic
        def editar_celda(event):
            seleccion = tree.selection()
            if not seleccion:
                return
            item = seleccion[0]
            col = tree.identify_column(event.x)
            col = int(col[1:]) - 1  # Convierte la columna a índice numérico

            valor_actual = tree.item(item, "values")[col]
            entry_editar = tk.Entry(ventana_resultados)
            entry_editar.insert(0, valor_actual)
            entry_editar.place(x=event.x, y=event.y)  # Ubica el Entry en la posición de la celda

            def guardar_edicion(event):
                nuevo_valor = entry_editar.get()
                # Actualiza solo la columna editada, conservando las demás
                valores_actuales = list(tree.item(item, "values"))
                valores_actuales[col] = nuevo_valor  # Actualiza el valor de la columna editada
                tree.item(item, values=valores_actuales)  # Guarda los valores actualizados
                entry_editar.destroy()  # Eliminar la entrada de texto

            entry_editar.bind("<Return>", guardar_edicion)  # Guardar al presionar Enter

        # Asociar la función de edición al evento de doble clic
        tree.bind("<Double-1>", editar_celda)

        # Botones de control
        boton_cerrar_resultados = tk.Button(ventana_resultados, text="Cerrar", command=lambda: cerrar_ventana_resultados(ventana_resultados))
        boton_cerrar_resultados.pack(side=tk.LEFT, padx=10, pady=10)

        # Botón Guardar Cambios en la esquina inferior derecha
        boton_guardar_cambios = tk.Button(ventana_resultados, text="Guardar Cambios", command=guardar_todos_los_cambios)
        boton_guardar_cambios.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)  # Ubicado en la esquina inferior derecha

    boton_buscar = tk.Button(ventana_editar, text="Buscar", command=buscar_datos)
    boton_buscar.pack(pady=10)

    boton_cerrar = tk.Button(ventana_editar, text="Cerrar", command=lambda: cerrar_ventana(ventana_editar))
    boton_cerrar.pack(pady=10)

    # Configurar la acción de cierre de la ventana de edición
    ventana_editar.protocol("WM_DELETE_WINDOW", lambda: cerrar_ventana(ventana_editar))

def cerrar_ventana(ventana):
    global ventana_editar_abierta
    ventana.destroy()  # Cierra la ventana
    ventana_editar_abierta = False  # Marca la ventana de edición como cerrada

def cerrar_ventana_resultados(ventana):
    global ventana_resultados_abierta
    ventana.destroy()  # Cierra la ventana de resultados
    ventana_resultados_abierta = False  # Marca la ventana de resultados como cerrada

# Ejecutar la ventana solo cuando se desee abrirla
if __name__ == "__main__":
    # Espera hasta que se ejecute la función para abrir la ventana
    pass
