"""Genera todos los PDFs demo con fpdf2 para máxima compatibilidad OCR.

Ejecutar: python demos/_gen_demos.py
"""
from fpdf import FPDF
from pathlib import Path

OUT = Path(__file__).parent


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def new_pdf() -> FPDF:
    pdf = FPDF()
    pdf.set_margins(20, 18, 20)
    pdf.set_auto_page_break(auto=True, margin=18)
    return pdf


def header(pdf: FPDF, title: str, subtitle: str = "") -> None:
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 9, title, new_x="LMARGIN", new_y="NEXT", align="C")
    if subtitle:
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 7, subtitle, new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(3)


def section(pdf: FPDF, title: str) -> None:
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)


def row(pdf: FPDF, label: str, value: str) -> None:
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(55, 6, label, new_x="RIGHT", new_y="TOP")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, value, new_x="LMARGIN", new_y="NEXT")


def line_txt(pdf: FPDF, txt: str, size: int = 10) -> None:
    pdf.set_font("Helvetica", "", size)
    pdf.cell(0, 6, txt, new_x="LMARGIN", new_y="NEXT")


def hrule(pdf: FPDF) -> None:
    pdf.ln(1)
    pdf.set_draw_color(180, 180, 180)
    pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 170, pdf.get_y())
    pdf.ln(2)


# ─────────────────────────────────────────────────────────────────────────────
# A — demo_multipagina.pdf  (3 paginas, todo FACTURA)
# ─────────────────────────────────────────────────────────────────────────────

def gen_multipagina():
    pdf = new_pdf()

    # ---------- Pagina 1: encabezado + datos ----------
    pdf.add_page()
    header(pdf, "FACTURA ELECTRONICA", "Documento Tributario Electronico - SAT Guatemala")
    hrule(pdf)

    section(pdf, "DATOS DEL EMISOR")
    row(pdf, "Empresa:", "Tecnologia Empresarial GT S.A.")
    row(pdf, "NIT:", "4521890-3")
    row(pdf, "Direccion:", "12 Calle 5-30 Zona 10, Guatemala")
    row(pdf, "Telefono:", "2400-5678")
    row(pdf, "Correo:", "facturacion@tecnogt.com.gt")
    row(pdf, "Serie DTE:", "FAC-2026-0512")

    section(pdf, "DATOS DEL CLIENTE")
    row(pdf, "Cliente:", "Luis Fernando Morales")
    row(pdf, "NIT Cliente:", "7234501-8")
    row(pdf, "DPI:", "2312 45678 0101")
    row(pdf, "Correo:", "l.morales@cliente.gt")
    row(pdf, "Telefono:", "5512-3456")
    row(pdf, "Fecha emision:", "22/04/2026")
    row(pdf, "Vencimiento:", "22/05/2026")

    # ---------- Pagina 2: detalle de servicios ----------
    pdf.add_page()
    header(pdf, "FACTURA FAC-2026-0512", "Detalle de Servicios - Pagina 2 de 3")
    hrule(pdf)

    section(pdf, "DESCRIPCION DE SERVICIOS")
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(80, 6, "Descripcion", border="B")
    pdf.cell(20, 6, "Cant.", border="B", align="C")
    pdf.cell(35, 6, "P. Unitario", border="B", align="R")
    pdf.cell(35, 6, "Subtotal", border="B", align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)

    items = [
        ("Consultoria en software ERP",    "1", "Q 8,500.00", "Q 8,500.00"),
        ("Licencia anual plataforma CRM",  "2", "Q 3,200.00", "Q 6,400.00"),
        ("Mantenimiento preventivo",       "1", "Q 1,800.00", "Q 1,800.00"),
        ("Soporte tecnico mensual",        "1", "Q 2,500.00", "Q 2,500.00"),
        ("Capacitacion usuarios (8 hrs)",  "1", "Q 1,200.00", "Q 1,200.00"),
    ]
    for desc, cant, pu, sub in items:
        pdf.cell(80, 6, desc)
        pdf.cell(20, 6, cant, align="C")
        pdf.cell(35, 6, pu, align="R")
        pdf.cell(35, 6, sub, align="R", new_x="LMARGIN", new_y="NEXT")

    hrule(pdf)
    pdf.set_font("Helvetica", "", 10)
    line_txt(pdf, "Forma de Pago: TRANSFERENCIA BANCARIA")
    line_txt(pdf, "Banco receptor: Banco Industrial de Guatemala")
    line_txt(pdf, "Cuenta No.: 987-654321-0")

    # ---------- Pagina 3: totales + firma ----------
    pdf.add_page()
    header(pdf, "FACTURA FAC-2026-0512", "Resumen y Autorizacion - Pagina 3 de 3")
    hrule(pdf)

    section(pdf, "RESUMEN TRIBUTARIO")
    row(pdf, "Subtotal:", "Q 20,400.00")
    row(pdf, "Descuento:", "Q 0.00")
    row(pdf, "IVA (12%):", "Q 2,191.07")
    row(pdf, "TOTAL:", "Q 22,591.07")
    row(pdf, "Moneda:", "GTQ")

    section(pdf, "AUTORIZACION SAT")
    row(pdf, "Num. Autorizacion:", "A1B2C3D4-E5F6-7890-ABCD-EF1234567890")
    row(pdf, "Serie SAT:", "A1B2C3D4")
    row(pdf, "Num. DTE:", "1234567890")
    row(pdf, "Fecha certif.:", "22 de abril de 2026")
    row(pdf, "Certificador:", "INFILE S.A.")
    row(pdf, "NIT Certificador:", "16693949")
    row(pdf, "URL verificacion:", "https://fel.sat.gob.gt/verify/FAC-2026-0512")

    hrule(pdf)
    line_txt(pdf, "Este documento es una Factura Electronica autorizada por la SAT de Guatemala.")
    line_txt(pdf, "Conserve este documento como comprobante de pago valido.")

    pdf.output(str(OUT / "demo_multipagina.pdf"))
    print("  OK demo_multipagina.pdf (3 paginas factura)")


# ─────────────────────────────────────────────────────────────────────────────
# B.1 — demo_factura_completo.pdf
# ─────────────────────────────────────────────────────────────────────────────

def gen_factura_completo():
    pdf = new_pdf()
    pdf.add_page()
    header(pdf, "FACTURA ELECTRONICA", "Distribuidora Central S.A. - SAT Guatemala")
    hrule(pdf)

    section(pdf, "EMISOR")
    row(pdf, "NIT Emisor:", "7823401-5")
    row(pdf, "Empresa:", "Distribuidora Central S.A.")
    row(pdf, "Direccion:", "6a Av. 4-12 Zona 1, Guatemala")
    row(pdf, "Telefono:", "2345-6789")
    row(pdf, "Correo:", "ventas@distribuidoracentral.com.gt")
    row(pdf, "Serie DTE:", "FAC-2026-0001")
    row(pdf, "Fecha emision:", "22/04/2026")
    row(pdf, "Vencimiento:", "22/05/2026")

    section(pdf, "CLIENTE")
    row(pdf, "Cliente:", "Carlos Mendoza Lopez")
    row(pdf, "NIT Cliente:", "3456789-1")
    row(pdf, "Correo:", "carlos.mendoza@correo.gt")
    row(pdf, "Telefono:", "5543-2109")
    row(pdf, "Fecha:", "22 de abril de 2026")

    section(pdf, "DETALLE")
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(85, 6, "Descripcion", border="B")
    pdf.cell(20, 6, "Cant.", border="B", align="C")
    pdf.cell(32, 6, "P. Unitario", border="B", align="R")
    pdf.cell(33, 6, "Subtotal", border="B", align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)

    for desc, c, pu, sub in [
        ("Servicio de Consultoria TI",  "1", "Q 6,500.00", "Q 6,500.00"),
        ("Licencia de Software Anual",  "2", "Q 1,200.00", "Q 2,400.00"),
        ("Mantenimiento de Equipos",    "1", "Q 850.00",   "Q 850.00"),
    ]:
        pdf.cell(85, 6, desc)
        pdf.cell(20, 6, c, align="C")
        pdf.cell(32, 6, pu, align="R")
        pdf.cell(33, 6, sub, align="R", new_x="LMARGIN", new_y="NEXT")

    hrule(pdf)
    row(pdf, "Subtotal:", "Q 9,750.00")
    row(pdf, "IVA (12%):", "Q 1,170.00")
    row(pdf, "TOTAL:", "Q 10,920.00")
    row(pdf, "Moneda:", "GTQ")

    section(pdf, "PAGO")
    row(pdf, "Forma de Pago:", "TRANSFERENCIA BANCARIA")
    row(pdf, "Banco:", "Banco Industrial")
    row(pdf, "Cuenta No.:", "123-456789-0")
    row(pdf, "URL verificacion:", "https://fel.sat.gob.gt/verify/FAC-2026-0001")
    line_txt(pdf, "Documento Tributario Electronico autorizado por la SAT de Guatemala.")

    pdf.output(str(OUT / "demo_factura_completo.pdf"))
    print("  OK demo_factura_completo.pdf")


# ─────────────────────────────────────────────────────────────────────────────
# B.2 — demo_recibo_completo.pdf
# ─────────────────────────────────────────────────────────────────────────────

def gen_recibo_completo():
    pdf = new_pdf()
    pdf.add_page()
    header(pdf, "RECIBO OFICIAL DE PAGO", "Servicios Administrativos Guatemala")
    hrule(pdf)

    section(pdf, "DATOS DEL RECIBO")
    row(pdf, "Numero:", "REC-2026-00892")
    row(pdf, "Fecha:", "22/04/2026")
    row(pdf, "Lugar:", "Ciudad de Guatemala")

    section(pdf, "DATOS DEL PAGO")
    row(pdf, "Recibi de:", "Ana Sofia Castillo Reyes")
    row(pdf, "NIT Pagador:", "5512340-7")
    row(pdf, "Correo:", "ana.castillo@empresa.com")
    row(pdf, "Telefono:", "2334-5678")
    row(pdf, "Monto recibido:", "Q 2,500.00")
    row(pdf, "En letras:", "DOS MIL QUINIENTOS QUETZALES EXACTOS")
    row(pdf, "Fecha texto:", "22 de abril de 2026")

    section(pdf, "CONCEPTO")
    line_txt(pdf, "Pago mensual de arrendamiento de oficina - Abril 2026")
    line_txt(pdf, "Piso 3, Edificio Torre Empresarial, 5a Avenida 10-15 Zona 10")

    section(pdf, "FORMA DE PAGO")
    row(pdf, "Forma de Pago:", "CHEQUE")
    row(pdf, "No. Cheque:", "00234")
    row(pdf, "Banco:", "G&T Continental")
    row(pdf, "Estado:", "PAGADO - CANCELADO")

    section(pdf, "COBRADOR")
    row(pdf, "Departamento:", "Cobros y Facturacion")
    row(pdf, "Telefono oficina:", "2456-7890")
    row(pdf, "Correo cobros:", "cobros@serviciosadmin.gt")
    row(pdf, "Subtotal:", "Q 2,500.00")
    row(pdf, "TOTAL:", "Q 2,500.00")
    hrule(pdf)
    line_txt(pdf, "Este recibo es valido unicamente con sello oficial y firma autorizada.")
    line_txt(pdf, "Conservelo como comprobante de pago realizado.")

    pdf.output(str(OUT / "demo_recibo_completo.pdf"))
    print("  OK demo_recibo_completo.pdf")


# ─────────────────────────────────────────────────────────────────────────────
# B.3 — demo_contrato_completo.pdf
# ─────────────────────────────────────────────────────────────────────────────

def gen_contrato_completo():
    pdf = new_pdf()
    pdf.add_page()
    header(pdf, "CONTRATO DE PRESTACION DE SERVICIOS PROFESIONALES")
    hrule(pdf)

    line_txt(pdf, "En la ciudad de Guatemala, a los veintidos dias del mes de abril del ano 2026.")
    pdf.ln(2)

    section(pdf, "PARTES CONTRATANTES")
    row(pdf, "El Contratante:", "TechSoluciones Guatemala S.A.")
    row(pdf, "NIT:", "4521890-3")
    row(pdf, "Representante:", "Luis Fernando Rodriguez")
    row(pdf, "Direccion:", "12 Calle 5-30 Zona 10, Guatemala")
    row(pdf, "Correo:", "contratos@techsoluciones.gt")
    row(pdf, "Telefono:", "2300-4500")
    pdf.ln(2)
    row(pdf, "El Contratado:", "Maria Elena Lopez Perez")
    row(pdf, "DPI:", "2312 45678 0101")
    row(pdf, "Correo:", "m.lopez@profesional.gt")
    row(pdf, "Telefono:", "5678-9012")

    section(pdf, "CLAUSULAS DEL CONTRATO")
    pdf.set_font("Helvetica", "", 10)
    clauses = [
        ("PRIMERA - OBJETO:", "Consultoria en desarrollo de software empresarial."),
        ("SEGUNDA - VIGENCIA:", "Doce meses a partir del 01/05/2026, prorrogable por acuerdo mutuo."),
        ("TERCERA - HONORARIOS:", "Q 8,000.00 mensuales dentro de los primeros cinco dias habiles."),
        ("CUARTA - OBLIGACIONES:", "Prestar servicios con diligencia y confidencialidad absoluta."),
        ("QUINTA - TERMINACION:", "Treinta dias de anticipacion con notificacion escrita."),
    ]
    for bold_part, rest in clauses:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(60, 6, bold_part, new_x="RIGHT", new_y="TOP")
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 6, rest, new_x="LMARGIN", new_y="NEXT")

    section(pdf, "RESUMEN ECONOMICO")
    row(pdf, "Honorario mensual:", "Q 8,000.00")
    row(pdf, "Duracion:", "12 meses")
    row(pdf, "Valor total contrato:", "Q 96,000.00")
    row(pdf, "Fecha inicio:", "01/05/2026")
    row(pdf, "Fecha fin:", "30/04/2027")
    row(pdf, "Forma de Pago:", "DEPOSITO BANCARIO")

    hrule(pdf)
    line_txt(pdf, "Las partes firman el presente contrato de conformidad.")
    line_txt(pdf, "Sujeto a las leyes de la Republica de Guatemala.")

    pdf.output(str(OUT / "demo_contrato_completo.pdf"))
    print("  OK demo_contrato_completo.pdf")


# ─────────────────────────────────────────────────────────────────────────────
# B.4 — demo_constancia_completo.pdf
# ─────────────────────────────────────────────────────────────────────────────

def gen_constancia_completo():
    pdf = new_pdf()
    pdf.add_page()
    header(pdf, "CONSTANCIA DE TRABAJO", "Distribuidora Central S.A.")
    hrule(pdf)

    section(pdf, "DATOS DE LA EMPRESA")
    row(pdf, "Empresa:", "Distribuidora Central S.A.")
    row(pdf, "NIT:", "7823401-5")
    row(pdf, "Departamento:", "Recursos Humanos")
    row(pdf, "Direccion:", "6a Avenida 4-12 Zona 1, Guatemala")
    row(pdf, "Telefono:", "2345-6789")
    row(pdf, "Correo:", "rrhh@distribuidoracentral.com.gt")

    section(pdf, "HACE CONSTAR QUE:")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6,
        "El senor Jose Carlos Ramirez Gutierrez, identificado con DPI 1234 56789 0125, "
        "ha prestado sus servicios en nuestra institucion desempenando el cargo de "
        "Analista de Sistemas Senior.", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    section(pdf, "PERIODO DE SERVICIO")
    row(pdf, "Fecha ingreso:", "01/03/2019")
    row(pdf, "Fecha emision:", "22/04/2026")
    row(pdf, "Antiguedad:", "7 anos de servicio continuo")
    row(pdf, "Estado:", "ACTIVO")
    row(pdf, "Salario mensual:", "Q 12,500.00")
    row(pdf, "Fecha texto:", "22 de abril de 2026")

    section(pdf, "OBSERVACIONES")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6,
        "El trabajador ha demostrado responsabilidad, puntualidad y compromiso "
        "con sus funciones laborales. La presente constancia se extiende a "
        "solicitud del interesado para los usos y fines que estime convenientes.",
        new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    hrule(pdf)
    line_txt(pdf, "Guatemala, 22 de abril de 2026")
    pdf.ln(6)
    line_txt(pdf, "____________________________")
    line_txt(pdf, "Gerencia de Recursos Humanos")
    line_txt(pdf, "Distribuidora Central S.A.")
    line_txt(pdf, "Sello: OFICIAL")

    pdf.output(str(OUT / "demo_constancia_completo.pdf"))
    print("  OK demo_constancia_completo.pdf")


# ─────────────────────────────────────────────────────────────────────────────
# B.5 — demo_carta_formal_completo.pdf
# ─────────────────────────────────────────────────────────────────────────────

def gen_carta_formal_completo():
    pdf = new_pdf()
    pdf.add_page()
    header(pdf, "CARTA FORMAL", "Comunicacion Oficial")
    hrule(pdf)

    section(pdf, "REFERENCIA Y FECHA")
    row(pdf, "Num. referencia:", "CF-2026-0001")
    row(pdf, "Fecha:", "22/04/2026")
    row(pdf, "Fecha texto:", "22 de abril de 2026")
    row(pdf, "Lugar:", "Guatemala, Guatemala")

    section(pdf, "DESTINATARIO")
    pdf.set_font("Helvetica", "", 10)
    line_txt(pdf, "Senor")
    line_txt(pdf, "Director General")
    line_txt(pdf, "Empresa Receptora S.A.")
    line_txt(pdf, "Ciudad de Guatemala")
    pdf.ln(2)

    section(pdf, "ASUNTO")
    line_txt(pdf, "Solicitud formal de servicios de consultoria empresarial")
    pdf.ln(2)

    section(pdf, "CUERPO DE LA CARTA")
    pdf.set_font("Helvetica", "", 10)
    paragraphs = [
        "Estimado senor Director:",
        ("Por medio de la presente, nos dirigimos a usted respetuosamente para "
         "hacer de su conocimiento que nuestra organizacion requiere los servicios "
         "especializados que su empresa ofrece en el area de consultoria estrategica."),
        ("Hemos revisado detenidamente su propuesta de servicios con fecha "
         "01/04/2026 y consideramos que se ajusta a nuestras necesidades "
         "institucionales. El monto estimado del proyecto es de Q 25,000.00, "
         "sujeto a negociacion entre las partes."),
        ("Solicitamos respetuosamente concretar una reunion el dia 05/05/2026 "
         "para discutir los terminos del contrato y formalizarlos mediante "
         "documento oficial. Quedamos a sus ordenes para cualquier consulta."),
    ]
    for p in paragraphs:
        pdf.multi_cell(0, 6, p, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

    section(pdf, "FIRMA")
    pdf.ln(4)
    line_txt(pdf, "Atentamente,")
    pdf.ln(4)
    line_txt(pdf, "____________________________")
    line_txt(pdf, "Lic. Roberto Sandoval Fuentes")
    line_txt(pdf, "Gerente General")
    pdf.ln(2)
    row(pdf, "Telefono:", "2305-6789")
    row(pdf, "Correo:", "contacto@empresa.gt")
    row(pdf, "Sitio web:", "https://www.empresa.gt")

    pdf.output(str(OUT / "demo_carta_formal_completo.pdf"))
    print("  OK demo_carta_formal_completo.pdf")


# ─────────────────────────────────────────────────────────────────────────────
# B.6 — demo_comunicado_completo.pdf
# ─────────────────────────────────────────────────────────────────────────────

def gen_comunicado_completo():
    pdf = new_pdf()
    pdf.add_page()
    header(pdf, "COMUNICADO OFICIAL", "Corporacion Innovacion Guatemala")
    hrule(pdf)

    section(pdf, "DATOS DEL COMUNICADO")
    row(pdf, "Numero:", "COM-2026-0042")
    row(pdf, "Fecha:", "22/04/2026")
    row(pdf, "Fecha texto:", "22 de abril de 2026")
    row(pdf, "Para:", "Todos nuestros clientes y colaboradores")
    row(pdf, "De:", "Gerencia General")

    section(pdf, "ESTIMADOS SENORES:")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6,
        "Por medio del presente comunicado, la Gerencia General de Corporacion "
        "Innovacion Guatemala les informa sobre importantes actualizaciones en "
        "nuestros servicios y politicas internas, con vigencia a partir del "
        "01 de mayo de 2026.", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    section(pdf, "1. NUEVOS HORARIOS DE ATENCION")
    pdf.set_font("Helvetica", "", 10)
    line_txt(pdf, "Lunes a Viernes: 8:00 AM a 6:00 PM")
    line_txt(pdf, "Sabados: 9:00 AM a 1:00 PM (servicio limitado)")
    line_txt(pdf, "Domingos y festivos: CERRADO")

    section(pdf, "2. NUEVA PLATAFORMA DIGITAL")
    pdf.set_font("Helvetica", "", 10)
    line_txt(pdf, "Nueva plataforma web para gestion de solicitudes:")
    row(pdf, "URL:", "https://clientes.corporacion.gt")
    line_txt(pdf, "Soporte tecnico disponible en linea 24/7.")

    section(pdf, "3. LINEA DIRECTA DE ATENCION")
    row(pdf, "Linea directa:", "2400-1234")
    row(pdf, "Correo:", "atencion@corporacion.gt")
    row(pdf, "Correo alterno:", "soporte@corporacion.gt")

    hrule(pdf)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6,
        "Agradecemos sinceramente la confianza que han depositado en nosotros "
        "durante estos anos de trayectoria empresarial.",
        new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    line_txt(pdf, "Atentamente,")
    pdf.ln(2)
    line_txt(pdf, "Lic. Roberto Sanchez Mendez - Gerente General")
    row(pdf, "Telefono:", "2400-5678")
    row(pdf, "Sitio web:", "https://www.corporacion.gt")

    pdf.output(str(OUT / "demo_comunicado_completo.pdf"))
    print("  OK demo_comunicado_completo.pdf")


# ─────────────────────────────────────────────────────────────────────────────
# B.7 — demo_identificacion_completo.pdf
# ─────────────────────────────────────────────────────────────────────────────

def gen_identificacion_completo():
    pdf = new_pdf()
    pdf.add_page()
    header(pdf, "DOCUMENTO PERSONAL DE IDENTIFICACION", "DPI - RENAP GUATEMALA")
    hrule(pdf)

    section(pdf, "DATOS DEL TITULAR")
    row(pdf, "Nombre completo:", "Juan Carlos Ramirez Lopez")
    row(pdf, "Numero DPI:", "2468 13579 2468")
    row(pdf, "CUI:", "2468 13579 2468")
    row(pdf, "Fecha nacimiento:", "15/03/1985")
    row(pdf, "Fecha emision:", "10/01/2020")
    row(pdf, "Fecha vencimiento:", "10/01/2030")

    section(pdf, "INFORMACION DE UBICACION")
    row(pdf, "Municipio:", "Guatemala")
    row(pdf, "Departamento:", "Guatemala")
    row(pdf, "Lugar nacimiento:", "Guatemala, Guatemala")

    section(pdf, "INFORMACION GENERAL")
    row(pdf, "Nacionalidad:", "Guatemalteco")
    row(pdf, "Estado civil:", "Soltero")
    row(pdf, "Sexo:", "Masculino")
    row(pdf, "Profesion:", "Ingeniero en Sistemas")

    section(pdf, "DATOS ADICIONALES DEL TITULAR")
    row(pdf, "Nombre padre:", "Carlos Alberto Ramirez Gomez")
    row(pdf, "DPI padre:", "1357 24680 1357")
    row(pdf, "Nombre madre:", "Maria Elena Lopez de Ramirez")
    row(pdf, "DPI madre:", "9753 13579 9753")

    section(pdf, "AUTORIDAD EMISORA")
    row(pdf, "Entidad:", "Registro Nacional de las Personas - RENAP")
    row(pdf, "Oficina:", "Guatemala, Ciudad Capital")
    row(pdf, "Fecha texto:", "10 de enero de 2020")
    row(pdf, "Vigencia:", "10 anos a partir de la fecha de emision")

    hrule(pdf)
    line_txt(pdf, "Documento oficial emitido por el RENAP - Guatemala, Centro America.")
    line_txt(pdf, "Este documento es de uso personal e intransferible.")

    pdf.output(str(OUT / "demo_identificacion_completo.pdf"))
    print("  OK demo_identificacion_completo.pdf")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Generando PDFs demo...")
    gen_multipagina()
    gen_factura_completo()
    gen_recibo_completo()
    gen_contrato_completo()
    gen_constancia_completo()
    gen_carta_formal_completo()
    gen_comunicado_completo()
    gen_identificacion_completo()
    print("Listo. Todos los PDFs generados en demos/")
