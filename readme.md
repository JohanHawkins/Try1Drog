# Drogs+ - Sistema de Gestión para Droguería

Aplicación de escritorio en Python (tkinter) para la gestión integral de pequeñas farmacias.

## Módulos

| Módulo | Archivo | Descripción |
|--------|---------|-------------|
| Inicio | `VenIni.py` | Ventana de login con serial de acceso |
| Menú | `VenMenu.py` | Navegación entre módulos |
| Inventario | `Inventario/Inventario.py` | CRUD de productos con alertas de vencimiento y stock |
| Edición | `Inventario/Editar_Producto.py` | Búsqueda y edición inline de productos |
| Punto de Venta | `Ventas/Ventas.py` | POS con búsqueda instantánea y total a pagar |
| Registro | `Registro.py` | Historial de ventas con filtros y paginación |
| Clientes | `Clientes/Clientes.py` | Gestión de clientes (CRUD) |
| Reportes | `Reportes/Reportes.py` | Dashboard con estadísticas y ranking |

## Dependencias

```
pip install pandas openpyxl Pillow tkcalendar fpdf python-dateutil
```

## Ejecución

```bash
python VenIni.py
```

## Estructura del Proyecto

```
Try1Drog/
├── VenIni.py              # Punto de entrada
├── VenMenu.py             # Menú principal
├── theme.py               # Sistema de diseño (paleta, helpers)
├── utils.py               # Utilidades (centrar_ventana)
├── Registro.py            # Historial de ventas
├── Inventario/
│   ├── Inventario.py      # Gestión de inventario
│   └── Editar_Producto.py # Búsqueda/edición de productos
├── Ventas/
│   └── Ventas.py          # Punto de venta
├── Clientes/
│   └── Clientes.py        # Gestión de clientes
├── Reportes/
│   └── Reportes.py        # Dashboard y analítica
├── images/
│   ├── cruz_azul.ico      # Icono de ventana
│   └── cruz_azul.png      # Logo
└── ideas.txt              # Documentación del proyecto
```

## Datos

Los datos se almacenan en archivos Excel:
- `Inventario/inventario_productos.xlsx` - Stock de productos
- `Ventas/registros_compra.xlsx` - Historial de ventas
- `Clientes/clientes.xlsx` - Base de datos de clientes

## Moneda

Pesos Colombianos (COP)
