import tkinter as tk
from tkinter import messagebox, filedialog
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import xml.etree.ElementTree as ET
from xml.dom import minidom
import hashlib
from utils import centrar_ventana
from theme import (get_paleta, aplicar_estilos, crear_header, crear_boton,
                    crear_entry, crear_label, crear_card, crear_treeview)
from Facturacion.config_empresa import cargar_config, obtener_siguiente_consecutivo

CARPETA_FACTURAS = os.path.join("Facturacion", "facturas")
CARPETA_XML = os.path.join("Facturacion", "facturas_xml")

def volver_al_menu(ventana):
    ventana.destroy()
    import VenMenu
    VenMenu.mostrar_ventana_menu()

def cargar_clientes():
    archivo = os.path.join("Clientes", "clientes.xlsx")
    if os.path.exists(archivo):
        return pd.read_excel(archivo)
    return pd.DataFrame(columns=["Nombre", "Cedula", "Telefono", "Direccion", "Email"])

def calcular_digito_verificador(nit):
    pesos = [71, 67, 59, 53, 47, 43, 41, 37, 29, 23, 17, 13, 7, 3, 2]
    nit_limpio = nit.replace("-", "").replace(".", "").strip()
    suma = 0
    for i, digito in enumerate(reversed(nit_limpio)):
        suma += int(digito) * pesos[i % len(pesos)]
    resto = suma % 11
    digito = 11 - resto
    if digito == 11:
        return "0"
    elif digito == 10:
        return "K"
    return str(digito)

def generar_cufe(datos):
    cadena = (
        f"{datos['num_factura']}"
        f"{datos['fecha']}"
        f"{datos['hora']}"
        f"{datos['valor_sin_iva']}"
        f"{datos['iva']}"
        f"{datos['total']}"
        f"{datos['nit_emisor']}"
        f"{datos['tipo_doc_cliente']}"
        f"{datos['doc_cliente']}"
        f"{datos['pin_software']}"
        f"{datos['ambiente']}"
    )
    return hashlib.sha384(cadena.encode()).hexdigest()

def generar_xml_UBL(datos, items):
    nsmap = {
        None: "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "sts": "dian:gov:co:facturaelectronica:Structures-2-1",
    }

    invoice = ET.Element("Invoice", nsmap=nsmap)

    ext = ET.SubElement(invoice, "ext:UBLExtensions")
    ext1 = ET.SubElement(ext, "ext:UBLExtension")
    ext_content = ET.SubElement(ext1, "ext:ExtensionContent")
    dian_ext = ET.SubElement(ext_content, "sts:DianExtensions")

    inv_control = ET.SubElement(dian_ext, "sts:InvoiceControl")
    auth_provider = ET.SubElement(inv_control, "sts:AuthorizationProvider")
    ET.SubElement(auth_provider, "sts:AuthorizationID").text = "0000000000000"

    auth_range = ET.SubElement(inv_control, "sts:AuthorizedRange")
    ET.SubElement(auth_range, "sts:From").text = datos.get("rango_desde", "1")
    ET.SubElement(auth_range, "sts:To").text = datos.get("rango_hasta", "5000")

    inv_source = ET.SubElement(dian_ext, "sts:InvoiceSource")
    ET.SubElement(inv_source, "sts:IdentificationCode").text = datos.get("cod_municipio", "11001")

    sw_provider = ET.SubElement(dian_ext, "sts:SoftwareProvider")
    ET.SubElement(sw_provider, "sts:ProviderID").text = datos["nit_emisor"]
    ET.SubElement(sw_provider, "sts:SoftwareID").text = datos.get("cod_software", "")

    sw_security = ET.SubElement(dian_ext, "sts:SoftwareSecurityCode")
    ET.SubElement(sw_security, "sts:PinCode").text = datos.get("pin_software", "")

    ET.SubElement(invoice, "cbc:UBLVersionID").text = "2.1"
    ET.SubElement(invoice, "cbc:CustomizationID").text = "101"
    ET.SubElement(invoice, "cbc:ProfileExecutionID").text = "2"
    ET.SubElement(invoice, "cbc:ID").text = datos["num_factura"]
    ET.SubElement(invoice, "cbc:IssueDate").text = datos["fecha"]
    ET.SubElement(invoice, "cbc:IssueTime").text = datos["hora"] + "-05:00"
    ET.SubElement(invoice, "cbc:InvoiceTypeCode").text = "380"
    ET.SubElement(invoice, "cbc:DocumentCurrencyCode").text = "COP"

    supplier = ET.SubElement(invoice, "cac:AccountingSupplierParty")
    sup_party = ET.SubElement(supplier, "cac:Party")
    ET.SubElement(sup_party, "cbc:EndpointID", schemeID="31").text = datos["nit_emisor"]
    sup_id = ET.SubElement(sup_party, "cac:PartyIdentification")
    ET.SubElement(sup_id, "cbc:ID", schemeID="31").text = datos["nit_emisor"]
    sup_name = ET.SubElement(sup_party, "cac:PartyName")
    ET.SubElement(sup_name, "cbc:Name").text = datos["razon_social"]
    sup_addr = ET.SubElement(sup_party, "cac:PostalAddress")
    ET.SubElement(sup_addr, "cbc:ID").text = datos.get("cod_municipio", "11001")
    ET.SubElement(sup_addr, "cbc:StreetName").text = datos.get("direccion", "")
    ET.SubElement(sup_addr, "cbc:CityName").text = datos.get("municipio", "")
    sup_country = ET.SubElement(sup_addr, "cac:Country")
    ET.SubElement(sup_country, "cbc:IdentificationCode").text = "CO"
    sup_tax = ET.SubElement(sup_party, "cac:PartyTaxScheme")
    ET.SubElement(sup_tax, "cbc:CompanyID").text = datos["nit_emisor"]
    sup_tax_level = ET.SubElement(sup_tax, "cac:TaxLevelCode")
    sup_tax_level.text = datos.get("resp_fiscal", "O-47")
    sup_tax_scheme = ET.SubElement(sup_tax, "cac:TaxScheme")
    ET.SubElement(sup_tax_scheme, "cbc:ID").text = "01"
    sup_legal = ET.SubElement(sup_party, "cac:PartyLegalEntity")
    ET.SubElement(sup_legal, "cbc:RegistrationName").text = datos["razon_social"]
    ET.SubElement(sup_legal, "cbc:CompanyID").text = datos["nit_emisor"]

    customer = ET.SubElement(invoice, "cac:AccountingCustomerParty")
    cust_party = ET.SubElement(customer, "cac:Party")
    tipo_doc = datos.get("tipo_doc_cliente", "13")
    ET.SubElement(cust_party, "cbc:EndpointID", schemeID=tipo_doc).text = datos["doc_cliente"]
    cust_id = ET.SubElement(cust_party, "cac:PartyIdentification")
    ET.SubElement(cust_id, "cbc:ID", schemeID=tipo_doc).text = datos["doc_cliente"]
    cust_legal = ET.SubElement(cust_party, "cac:PartyLegalEntity")
    ET.SubElement(cust_legal, "cbc:RegistrationName").text = datos.get("nombre_cliente", "Consumidor Final")

    tax_total = ET.SubElement(invoice, "cac:TaxTotal")
    ET.SubElement(tax_total, "cbc:TaxAmount", currencyID="COP").text = f"{datos['iva']:.2f}"
    tax_sub = ET.SubElement(tax_total, "cac:TaxSubtotal")
    ET.SubElement(tax_sub, "cbc:TaxableAmount", currencyID="COP").text = f"{datos['valor_sin_iva']:.2f}"
    ET.SubElement(tax_sub, "cbc:TaxAmount", currencyID="COP").text = f"{datos['iva']:.2f}"
    tax_cat = ET.SubElement(tax_sub, "cac:TaxCategory")
    ET.SubElement(tax_cat, "cbc:ID").text = "S"
    ET.SubElement(tax_cat, "cbc:Percent").text = "19"
    tax_scheme = ET.SubElement(tax_cat, "cac:TaxScheme")
    ET.SubElement(tax_scheme, "cbc:ID").text = "01"

    legal_total = ET.SubElement(invoice, "cac:LegalMonetaryTotal")
    ET.SubElement(legal_total, "cbc:LineExtensionAmount", currencyID="COP").text = f"{datos['valor_sin_iva']:.2f}"
    ET.SubElement(legal_total, "cbc:TaxExclusiveAmount", currencyID="COP").text = f"{datos['valor_sin_iva']:.2f}"
    ET.SubElement(legal_total, "cbc:TaxInclusiveAmount", currencyID="COP").text = f"{datos['total']:.2f}"
    ET.SubElement(legal_total, "cbc:PayableAmount", currencyID="COP").text = f"{datos['total']:.2f}"

    for i, item in enumerate(items, 1):
        inv_line = ET.SubElement(invoice, "cac:InvoiceLine")
        ET.SubElement(inv_line, "cbc:ID").text = str(i)
        ET.SubElement(inv_line, "cbc:InvoicedQuantity", unitCode="C62").text = str(item["cantidad"])
        ET.SubElement(inv_line, "cbc:LineExtensionAmount", currencyID="COP").text = f"{item['subtotal']:.2f}"
        line_tax = ET.SubElement(inv_line, "cac:TaxTotal")
        ET.SubElement(line_tax, "cbc:TaxAmount", currencyID="COP").text = f"{item['iva']:.2f}"
        line_tax_sub = ET.SubElement(line_tax, "cac:TaxSubtotal")
        ET.SubElement(line_tax_sub, "cbc:TaxableAmount", currencyID="COP").text = f"{item['subtotal']:.2f}"
        ET.SubElement(line_tax_sub, "cbc:TaxAmount", currencyID="COP").text = f"{item['iva']:.2f}"
        line_tax_cat = ET.SubElement(line_tax_sub, "cac:TaxCategory")
        ET.SubElement(line_tax_cat, "cbc:ID").text = "S"
        ET.SubElement(line_tax_cat, "cbc:Percent").text = "19"
        line_tax_scheme = ET.SubElement(line_tax_cat, "cac:TaxScheme")
        ET.SubElement(line_tax_scheme, "cbc:ID").text = "01"
        item_elem = ET.SubElement(inv_line, "cac:Item")
        ET.SubElement(item_elem, "cbc:Description").text = item["nombre"]
        ET.SubElement(item_elem, "cbc:Name").text = item["nombre"]
        sellers_id = ET.SubElement(item_elem, "cac:SellersItemIdentification")
        ET.SubElement(sellers_id, "cbc:ID").text = item.get("codigo", "")
        price = ET.SubElement(inv_line, "cac:Price")
        ET.SubElement(price, "cbc:PriceAmount", currencyID="COP").text = f"{item['precio_unitario']:.2f}"

    payment = ET.SubElement(invoice, "cac:PaymentMeans")
    ET.SubElement(payment, "cbc:PaymentMeansCode").text = datos.get("cod_pago", "10")
    ET.SubElement(payment, "cbc:PaymentDueDate").text = datos["fecha"]

    return invoice

def guardar_xml(invoice_elem, num_factura):
    os.makedirs(CARPETA_XML, exist_ok=True)
    xml_str = ET.tostring(invoice_elem, encoding="unicode", xml_declaration=False)
    xml_pretty = minidom.parseString(xml_str).toprettyxml(indent="  ", encoding=None)
    lines = xml_pretty.split("\n")
    lines[0] = '<?xml version="1.0" encoding="UTF-8"?>'
    xml_final = "\n".join(lines)

    filepath = os.path.join(CARPETA_XML, f"{num_factura}.xml")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(xml_final)
    return filepath

class PDFFactura(FPDF):
    def __init__(self, config_empresa):
        super().__init__()
        self.config = config_empresa

    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "FACTURA DE VENTA", 0, 1, "C")
        self.set_font("Arial", "", 10)
        self.cell(0, 5, f"NIT: {self.config.get('NIT', '')}", 0, 1, "C")
        self.cell(0, 5, self.config.get("Razon Social", ""), 0, 1, "C")
        self.cell(0, 5, self.config.get("Direccion", ""), 0, 1, "C")
        self.cell(0, 5, f"Tel: {self.config.get('Telefono', '')} - Email: {self.config.get('Email', '')}", 0, 1, "C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()}/{{nb}}", 0, 0, "C")

def generar_pdf(datos, items, filepath):
    config = cargar_config()
    pdf = PDFFactura(config)
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.set_font("Arial", "B", 12)
    pdf.cell(95, 8, f"Factura N°: {datos['num_factura']}", 0, 0, "L")
    pdf.cell(95, 8, f"Fecha: {datos['fecha']}", 0, 1, "R")
    pdf.cell(95, 8, f"Hora: {datos['hora']}", 0, 1, "L")

    pdf.ln(3)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "DATOS DEL CLIENTE", 0, 1, "L")
    pdf.set_font("Arial", "", 10)
    tipo_doc = "NIT" if datos.get("tipo_doc_cliente") == "31" else "C.C."
    pdf.cell(0, 6, f"{tipo_doc}: {datos['doc_cliente']}", 0, 1)
    pdf.cell(0, 6, f"Nombre: {datos.get('nombre_cliente', 'Consumidor Final')}", 0, 1)
    pdf.cell(0, 6, f"Dirección: {datos.get('direccion_cliente', '')}", 0, 1)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 10)
    col_w = [12, 80, 25, 35, 35]
    headers = ["#", "Descripción", "Cant.", "P. Unitario", "Subtotal"]
    for i, h in enumerate(headers):
        pdf.cell(col_w[i], 8, h, 1, 0, "C")
    pdf.ln()

    pdf.set_font("Arial", "", 9)
    for i, item in enumerate(items, 1):
        pdf.cell(col_w[0], 7, str(i), 1, 0, "C")
        pdf.cell(col_w[1], 7, item["nombre"][:40], 1, 0, "L")
        pdf.cell(col_w[2], 7, str(item["cantidad"]), 1, 0, "C")
        pdf.cell(col_w[3], 7, f"${item['precio_unitario']:,.0f}", 1, 0, "R")
        pdf.cell(col_w[4], 7, f"${item['subtotal']:,.0f}", 1, 0, "R")
        pdf.ln()

    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(120, 8, "Subtotal:", 0, 0, "R")
    pdf.cell(50, 8, f"${datos['valor_sin_iva']:,.2f}", 0, 1, "R")
    pdf.cell(120, 8, "IVA (19%):", 0, 0, "R")
    pdf.cell(50, 8, f"${datos['iva']:,.2f}", 0, 1, "R")
    pdf.set_font("Arial", "B", 13)
    pdf.cell(120, 10, "TOTAL:", 0, 0, "R")
    pdf.cell(50, 10, f"${datos['total']:,.2f} COP", 0, 1, "R")

    pdf.ln(5)
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 6, f"Método de Pago: {datos.get('metodo_pago', 'Efectivo')}", 0, 1)

    pdf.ln(3)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 6, f"CUFE: {datos.get('cufe', 'Pendiente validación DIAN')}", 0, 1)
    pdf.set_font("Arial", "", 8)
    pdf.cell(0, 5, "Documento generado para validación ante la DIAN", 0, 1, "C")

    pdf.output(filepath)

def mostrar_ventana_facturacion(ultima_venta=None):
    paleta = get_paleta()
    config = cargar_config()

    if not config.get("NIT") or not config.get("Razon Social"):
        messagebox.showwarning("Configuración requerida",
            "Primero debe configurar los datos de la empresa.\n\nVaya a: Facturación > Configuración Empresa")
        from Facturacion.config_empresa import mostrar_ventana_config
        mostrar_ventana_config()
        return

    clientes_df = cargar_clientes()

    ventana = tk.Tk()
    ventana.title("Drogs+ - Generar Factura")
    ventana.resizable(True, True)
    ventana.minsize(500, 450)
    ventana.configure(bg=paleta["bg_principal"])

    icon_path = os.path.join("images", "cruz_azul.ico")
    if os.path.exists(icon_path):
        ventana.iconbitmap(icon_path)
    aplicar_estilos(ventana)
    centrar_ventana(ventana)

    crear_header(ventana, "Generar Factura Electrónica")

    main_frame = tk.Frame(ventana, bg=paleta["bg_principal"])
    main_frame.pack(fill="both", expand=True, padx=15, pady=10)

    config_card = crear_card(main_frame, "Datos Empresa")
    config_card.pack(fill="x", pady=(0, 10))
    config_inner = tk.Frame(config_card, bg=paleta["bg_card"])
    config_inner.pack(fill="x", padx=15, pady=(0, 10))

    crear_label(config_inner, f"NIT: {config.get('NIT', '')}", "normal").pack(anchor="w")
    crear_label(config_inner, f"Razón Social: {config.get('Razon Social', '')}", "normal").pack(anchor="w")

    btn_config = crear_boton(config_inner, "⚙ Configurar Empresa",
        lambda: [ventana.destroy(), mostrar_ventana_config()], "Secundario", "pequeño")
    btn_config.pack(anchor="w", pady=(5, 0))

    cliente_card = crear_card(main_frame, "Datos del Cliente")
    cliente_card.pack(fill="x", pady=(0, 10))
    cliente_inner = tk.Frame(cliente_card, bg=paleta["bg_card"])
    cliente_inner.pack(fill="x", padx=15, pady=(0, 10))

    clientes_combo_frame = tk.Frame(cliente_inner, bg=paleta["bg_card"])
    clientes_combo_frame.pack(fill="x")

    crear_label(clientes_combo_frame, "Cliente:", "bold").pack(side="left")
    var_cliente = tk.StringVar(value="Seleccionar cliente")
    nombres_clientes = ["Seleccionar cliente", "Consumidor Final"] + \
        [f"{r.get('Nombre', '')} - {r.get('Cedula', '')}" for _, r in clientes_df.iterrows()] if not clientes_df.empty else \
        ["Seleccionar cliente", "Consumidor Final"]
    combo_clientes = tk.OptionMenu(clientes_combo_frame, var_cliente, *nombres_clientes)
    combo_clientes.config(width=40)
    combo_clientes.pack(side="left", padx=(10, 0))

    cliente_datos_frame = tk.Frame(cliente_inner, bg=paleta["bg_card"])
    cliente_datos_frame.pack(fill="x", pady=(10, 0))

    campos_cliente = [
        ("Tipo Doc:", 0, 0), ("N° Documento:", 0, 2),
        ("Nombre:", 1, 0), ("Dirección:", 1, 2),
    ]
    entries_cliente = {}
    for texto, fila, col in campos_cliente:
        crear_label(cliente_datos_frame, texto, "bold").grid(row=fila, column=col, sticky="e", padx=(0, 6), pady=4)
        e = crear_entry(cliente_datos_frame, width=22)
        e.grid(row=fila, column=col + 1, sticky="w", padx=(0, 10), pady=4)
        entries_cliente[texto.replace(":", "").strip()] = e

    entries_cliente["Tipo Doc"].insert(0, "13")
    entries_cliente["N° Documento"].config(state="normal")
    entries_cliente["Nombre"].config(state="normal")
    entries_cliente["Dirección"].config(state="normal")

    def on_cliente_select(*args):
        seleccion = var_cliente.get()
        if seleccion in ["Seleccionar cliente", "Consumidor Final"]:
            for e in entries_cliente.values():
                e.config(state="normal")
                e.delete(0, tk.END)
            if seleccion == "Consumidor Final":
                entries_cliente["Tipo Doc"].insert(0, "13")
                entries_cliente["N° Documento"].insert(0, "222222222222")
                entries_cliente["Nombre"].insert(0, "Consumidor Final")
            return

        nombre_completo = seleccion
        nombre_partes = nombre_completo.rsplit(" - ", 1)
        if len(nombre_partes) == 2:
            nombre = nombre_partes[0]
            cedula = nombre_partes[1]
            cliente_row = clientes_df[clientes_df["Cedula"].astype(str) == str(cedula)]
            if not cliente_row.empty:
                for e in entries_cliente.values():
                    e.config(state="normal")
                    e.delete(0, tk.END)
                entries_cliente["Tipo Doc"].insert(0, "13")
                entries_cliente["N° Documento"].insert(0, cedula)
                entries_cliente["Nombre"].insert(0, nombre)
                entries_cliente["Dirección"].insert(0, str(cliente_row.iloc[0].get("Direccion", "")))

    var_cliente.trace("w", on_cliente_select)

    items_card = crear_card(main_frame, "Productos de la Venta")
    items_card.pack(fill="x", pady=(0, 10))
    items_inner = tk.Frame(items_card, bg=paleta["bg_card"])
    items_inner.pack(fill="x", padx=15, pady=(0, 10))

    columnas_item = ["Producto", "Cantidad", "Precio Unit.", "Subtotal"]
    tree_items = crear_treeview(items_inner, columnas_item)
    tree_items.pack(fill="x", pady=(0, 10))

    items_venta = []

    def agregar_item():
        nombre = entry_producto.get().strip()
        try:
            cantidad = int(entry_cantidad.get())
            precio = float(entry_precio.get().replace(",", "").replace("$", ""))
        except ValueError:
            messagebox.showwarning("Error", "Ingrese cantidad y precio válidos.")
            return

        subtotal = cantidad * precio
        iva = subtotal * 0.19
        items_venta.append({
            "nombre": nombre,
            "cantidad": cantidad,
            "precio_unitario": precio,
            "subtotal": subtotal,
            "iva": iva,
        })

        tag = "evenrow" if len(items_venta) % 2 == 0 else "oddrow"
        tree_items.insert("", "end", values=[nombre, cantidad, f"${precio:,.0f}", f"${subtotal:,.0f}"], tags=(tag,))

        entry_producto.delete(0, tk.END)
        entry_cantidad.delete(0, tk.END)
        entry_precio.delete(0, tk.END)

        total_general = sum(it["subtotal"] for it in items_venta)
        label_total.config(text=f"Total: ${total_general:,.0f} COP")

    item_form = tk.Frame(items_inner, bg=paleta["bg_card"])
    item_form.pack(fill="x")

    crear_label(item_form, "Producto:", "bold").pack(side="left")
    entry_producto = crear_entry(item_form, width=20)
    entry_producto.pack(side="left", padx=(5, 10))

    crear_label(item_form, "Cant:", "bold").pack(side="left")
    entry_cantidad = crear_entry(item_form, width=6)
    entry_cantidad.pack(side="left", padx=(5, 10))

    crear_label(item_form, "Precio:", "bold").pack(side="left")
    entry_precio = crear_entry(item_form, width=12)
    entry_precio.pack(side="left", padx=(5, 10))

    crear_boton(item_form, "+ Agregar", agregar_item, "Exito", "pequeño").pack(side="left")

    label_total = crear_label(items_inner, "Total: $0 COP", "bold")
    label_total.pack(anchor="e", pady=(5, 0))

    def generar_factura():
        if not items_venta:
            messagebox.showwarning("Sin productos", "Agregue al menos un producto.")
            return

        doc_cliente = entries_cliente["N° Documento"].get().strip()
        nombre_cliente = entries_cliente["Nombre"].get().strip()
        tipo_doc = entries_cliente["Tipo Doc"].get().strip()

        if not doc_cliente or not nombre_cliente:
            messagebox.showwarning("Cliente requerido", "Seleccione o ingrese los datos del cliente.")
            return

        consecutivo = obtener_siguiente_consecutivo()
        if not consecutivo:
            messagebox.showerror("Rango agotado", "Se agotó el rango autorizado de facturación.")
            return

        now = datetime.now()
        valor_sin_iva = sum(it["subtotal"] for it in items_venta)
        iva_total = sum(it["iva"] for it in items_venta)
        total = valor_sin_iva + iva_total

        num_doc_limpio = doc_cliente.replace("-", "").replace(".", "")
        datos_factura = {
            "num_factura": consecutivo,
            "fecha": now.strftime("%Y-%m-%d"),
            "hora": now.strftime("%H:%M:%S"),
            "nit_emisor": config["NIT"].replace("-", "").replace(".", ""),
            "razon_social": config["Razon Social"],
            "direccion": config.get("Direccion", ""),
            "cod_municipio": config.get("Codigo Municipio DANE", "11001"),
            "municipio": "Bogota D.C.",
            "resp_fiscal": config.get("Responsabilidad Fiscal", "O-47"),
            "rango_desde": config.get("Rango Desde", "1"),
            "rango_hasta": config.get("Rango Hasta", "5000"),
            "cod_software": config.get("Codigo Software DIAN", ""),
            "pin_software": config.get("Pin Software DIAN", ""),
            "tipo_doc_cliente": tipo_doc,
            "doc_cliente": num_doc_limpio,
            "nombre_cliente": nombre_cliente,
            "direccion_cliente": entries_cliente["Dirección"].get().strip(),
            "valor_sin_iva": valor_sin_iva,
            "iva": iva_total,
            "total": total,
            "metodo_pago": "Efectivo",
            "ambiente": "2",
        }

        datos_factura["cufe"] = generar_cufe(datos_factura)

        os.makedirs(CARPETA_FACTURAS, exist_ok=True)
        pdf_path = os.path.join(CARPETA_FACTURAS, f"{consecutivo}.pdf")
        generar_pdf(datos_factura, items_venta, pdf_path)

        invoice_xml = generar_xml_UBL(datos_factura, items_venta)
        xml_path = guardar_xml(invoice_xml, consecutivo)

        messagebox.showinfo("Factura Generada",
            f"Factura: {consecutivo}\n\nPDF: {pdf_path}\nXML: {xml_path}")

        factura_reg = pd.DataFrame({
            "N° Factura": [consecutivo],
            "Cliente": [nombre_cliente],
            "Documento": [doc_cliente],
            "Subtotal": [f"${valor_sin_iva:,.2f}"],
            "IVA": [f"${iva_total:,.2f}"],
            "Total": [f"${total:,.2f} COP"],
            "Fecha": [now.strftime("%Y-%m-%d")],
            "Hora": [now.strftime("%H:%M:%S")],
        })

        try:
            archivo_reg = "Ventas/registros_compra.xlsx"
            if os.path.exists(archivo_reg):
                df_reg = pd.read_excel(archivo_reg)
                if "N° Factura" not in df_reg.columns:
                    df_reg["N° Factura"] = ""
                ultima_idx = df_reg.index[-1] if not df_reg.empty else None
                if ultima_idx is not None:
                    df_reg.loc[ultima_idx, "N° Factura"] = consecutivo
                else:
                    df_reg = pd.concat([df_reg, factura_reg], ignore_index=True)
                df_reg.to_excel(archivo_reg, index=False)
        except Exception as e:
            print(f"Error guardando registro de factura: {e}")

        items_venta.clear()
        for item in tree_items.get_children():
            tree_items.delete(item)
        label_total.config(text="Total: $0 COP")

    btn_frame = tk.Frame(main_frame, bg=paleta["bg_principal"])
    btn_frame.pack(fill="x", pady=(8, 0))

    crear_boton(btn_frame, "← Volver", lambda: volver_al_menu(ventana), "Secundario", "pequeño").pack(side="left")
    crear_boton(btn_frame, "📄 Generar Factura", generar_factura, "Exito", "pequeño").pack(side="right")

    ventana.update_idletasks()
    w = ventana.winfo_reqwidth()
    h = ventana.winfo_reqheight()
    ventana.geometry(f"{w}x{h}")
    centrar_ventana(ventana)
    ventana.mainloop()
