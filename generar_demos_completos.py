"""
generar_demos_completos.py — Generador de 7 PDFs demo para todas las categorías.

Genera documentos PDF realistas para cada categoría:
  1. Factura Electrónica (tributaria)
  2. Recibo (de pago)
  3. Contrato (servicios)
  4. Constancia (laboral)
  5. Carta Formal (oficial)
  6. Identificación (DPI)
  7. Comunicado (administrativo)

Ejecutar:
    python generar_demos_completos.py
"""
from fpdf import FPDF
from pathlib import Path
from datetime import datetime, timedelta
import random

class PDFGenerator(FPDF):
    """Generador de PDFs con encabezado y pie de página."""
    
    def header(self):
        """Encabezado de todas las páginas."""
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 10, "PROYECTO 04 - OCR IA", align="C", ln=True)
        self.ln(5)
    
    def footer(self):
        """Pie de página con número de página."""
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")


def gen_factura_pdf():
    """Genera PDF de factura electrónica."""
    pdf = PDFGenerator()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "FACTURA ELECTRONICA", align="C", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.ln(5)
    
    # Datos
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(50, 8, "Numero:", ln=False)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, "FAC-2026-0001", ln=True)
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(50, 8, "Fecha:", ln=False)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, datetime.now().strftime("%d/%m/%Y"), ln=True)
    pdf.ln(5)
    
    # Empresa
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 8, "EMPRESA EMISORA", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, "NIT: 7654321-8", ln=True)
    pdf.cell(0, 6, "Cliente: Distribuidora Guatemalteca", ln=True)
    pdf.cell(0, 6, "Direccion: Ciudad de Guatemala", ln=True)
    pdf.ln(3)
    
    # Detalles
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 8, "CONCEPTO DE VENTA", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, "Descripcion: Articulo 001", ln=True)
    pdf.cell(0, 6, "Cantidad: 25 unidades", ln=True)
    pdf.cell(0, 6, "Precio unitario: Q150.00", ln=True)
    pdf.ln(3)
    
    # Resumen
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 8, "RESUMEN TRIBUTARIO", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, "Subtotal: Q3,750.00", ln=True)
    pdf.cell(0, 6, "IVA 12%: Q450.00", ln=True)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 8, "TOTAL: Q4,200.00 GTQ", ln=True)
    pdf.ln(3)
    
    # Información SAT
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(0, 6, "FACTURA ELECTRONICA SAT Guatemala", ln=True)
    pdf.cell(0, 6, "Documento tributario electronico", ln=True)
    pdf.cell(0, 6, "Autorizado por SAT", ln=True)
    pdf.cell(0, 6, "RFC Guatemala - Contribuyente activo", ln=True)
    pdf.cell(0, 6, f"Vigencia: {(datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y')}", ln=True)
    
    # Guardar
    path = Path("demos/demo_factura_completo.pdf")
    path.parent.mkdir(exist_ok=True)
    pdf.output(str(path))
    return path


def gen_recibo_pdf():
    """Genera PDF de recibo de pago."""
    pdf = PDFGenerator()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "RECIBO OFICIAL DE PAGO", align="C", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.ln(5)
    
    # Datos
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(50, 8, "Numero:", ln=False)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, "REC-00001", ln=True)
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(50, 8, "Fecha:", ln=False)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, datetime.now().strftime("%d/%m/%Y"), ln=True)
    pdf.ln(5)
    
    # Recibi de
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 8, "RECIBI DE", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, "Nombre: Empresa Receptora 001", ln=True)
    pdf.cell(0, 6, "Direccion: Ciudad de Guatemala", ln=True)
    pdf.cell(0, 6, "Telefono: 2234-5678", ln=True)
    pdf.ln(3)
    
    # Monto
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 8, "CANTIDAD DE DINERO", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, "Monto recibido: Q2,500.00", ln=True)
    pdf.cell(0, 6, "Cantidad en letras: Dos mil quinientos quetzales", ln=True)
    pdf.ln(3)
    
    # Concepto
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 8, "POR CONCEPTO DE", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, "Pago de servicio mensual", ln=True)
    pdf.cell(0, 6, "Descripcion: Pago correspondiente al mes", ln=True)
    pdf.ln(3)
    
    # Datos finales
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, "Forma de pago: EFECTIVO", ln=True)
    pdf.cell(0, 6, "Departamento de cobros", ln=True)
    pdf.cell(0, 6, "Sello: [OFICINA]", ln=True)
    pdf.cell(0, 6, "Firma: ____________________", ln=True)
    pdf.cell(0, 6, "Muchas gracias por su pago puntual", ln=True)
    
    # Guardar
    path = Path("demos/demo_recibo_completo.pdf")
    path.parent.mkdir(exist_ok=True)
    pdf.output(str(path))
    return path


def gen_contrato_pdf():
    """Genera PDF de contrato de servicios."""
    pdf = PDFGenerator()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "CONTRATO DE PRESTACION DE SERVICIOS", align="C", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.ln(5)
    
    # Número y fecha
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(50, 7, "Numero:", ln=False)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 7, "CTR-2026-0001", ln=True)
    
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(50, 7, "Fecha:", ln=False)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 7, datetime.now().strftime("%d/%m/%Y"), ln=True)
    pdf.ln(3)
    
    # Partes
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 8, "PARTES CONTRATANTES", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, "El contratante: Empresa Prestadora de Servicios", ln=True)
    pdf.cell(0, 6, "NIT: 1234567-8", ln=True)
    pdf.cell(0, 6, "El contratado: Beneficiario del Servicio", ln=True)
    pdf.ln(3)
    
    # Cláusulas
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 8, "CLAUSULAS DEL CONTRATO", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, "PRIMERA: Objeto y Alcance", ln=True)
    pdf.cell(0, 6, "Las partes convenimos en que el contratante prestara servicios", ln=True)
    pdf.cell(0, 6, "al contratado.", ln=True)
    pdf.ln(2)
    
    pdf.cell(0, 6, "SEGUNDA: Vigencia", ln=True)
    fecha_fin = datetime.now() + timedelta(days=365)
    pdf.cell(0, 6, f"Desde: {datetime.now().strftime('%d/%m/%Y')} hasta: {fecha_fin.strftime('%d/%m/%Y')}", ln=True)
    pdf.cell(0, 6, "Plazo: 12 meses", ln=True)
    pdf.ln(2)
    
    pdf.cell(0, 6, "TERCERA: Contraprestacion Economica", ln=True)
    pdf.cell(0, 6, "Pago mensual: Q5,000.00", ln=True)
    pdf.ln(3)
    
    # Firmas
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, "Ambas partes se comprometen a cumplir integramente.", ln=True)
    pdf.cell(0, 6, "Segun las leyes de Guatemala.", ln=True)
    pdf.ln(10)
    pdf.cell(80, 6, "____________________", ln=False)
    pdf.cell(0, 6, "____________________", ln=True)
    pdf.cell(80, 6, "El Contratante", ln=False)
    pdf.cell(0, 6, "El Contratado", ln=True)
    
    # Guardar
    path = Path("demos/demo_contrato_completo.pdf")
    path.parent.mkdir(exist_ok=True)
    pdf.output(str(path))
    return path


def gen_constancia_pdf():
    """Genera PDF de constancia de trabajo."""
    pdf = PDFGenerator()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "CONSTANCIA DE TRABAJO", align="C", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.ln(5)
    
    # Número y empresa
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 7, "Numero: CONST-2026-0001", ln=True)
    pdf.cell(0, 7, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
    pdf.cell(0, 7, "Empresa: Distribuidora Central SA", ln=True)
    pdf.ln(3)
    
    # Encabezado
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, "La Gerencia de Recursos Humanos de Distribuidora Central SA", ln=True)
    pdf.ln(2)
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 8, "HACE CONSTAR QUE:", ln=True)
    pdf.ln(2)
    
    # Datos del trabajador
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, "El senor(a) Juan Carlos Ramirez", ln=True)
    pdf.cell(0, 6, "Identificado(a) con DPI numero: 1234-56789-0123", ln=True)
    pdf.cell(0, 6, "Ha prestado servicios en nuestra institucion desempenando el cargo de", ln=True)
    pdf.cell(0, 6, "Auxiliar Contable", ln=True)
    pdf.cell(0, 6, "Desde: 15/03/2018 hasta la fecha", ln=True)
    pdf.cell(0, 6, "Con una antiguedad de 6 anos de servicio continuo", ln=True)
    pdf.ln(2)
    
    # Evaluación
    pdf.cell(0, 6, "Durante este tiempo ha demostrado responsabilidad, puntualidad", ln=True)
    pdf.cell(0, 6, "y compromiso con sus funciones laborales.", ln=True)
    pdf.ln(3)
    
    # Propósito
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, "La presente constancia se extiende a solicitud del interesado", ln=True)
    pdf.cell(0, 6, "para los fines que estime convenientes, en la ciudad de Guatemala", ln=True)
    pdf.cell(0, 6, f"a los {random.randint(1, 28)} dias del mes de abril de 2026.", ln=True)
    pdf.ln(10)
    
    pdf.cell(0, 6, "____________________", ln=True)
    pdf.cell(0, 6, "Recursos Humanos", ln=True)
    pdf.cell(0, 6, "Distribuidora Central SA", ln=True)
    pdf.cell(0, 6, "Sello: [OFICIAL]", ln=True)
    
    # Guardar
    path = Path("demos/demo_constancia_completo.pdf")
    path.parent.mkdir(exist_ok=True)
    pdf.output(str(path))
    return path


def gen_carta_formal_pdf():
    """Genera PDF de carta formal."""
    pdf = PDFGenerator()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "CARTA FORMAL", align="C", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.ln(5)
    
    # Encabezado
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, f"Numero de referencia: CF-2026-0001", ln=True)
    pdf.cell(0, 6, f"Guatemala, {datetime.now().strftime('%d de %B de %Y')}", ln=True)
    pdf.ln(2)
    
    pdf.cell(0, 6, "Senor(a):", ln=True)
    pdf.cell(0, 6, "Gerente General", ln=True)
    pdf.cell(0, 6, "Empresa Receptora SA", ln=True)
    pdf.cell(0, 6, "Presente.", ln=True)
    pdf.ln(3)
    
    # Cuerpo
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, "Estimado senor(a):", ln=True)
    pdf.ln(2)
    
    pdf.multi_cell(0, 5, 
        "Por este medio me dirijo a usted con el respeto que se merece, "
        "para exponerle lo siguiente en relacion al asunto: Solicitud de informacion.\n\n"
        "La presente tiene por objeto hacer de su conocimiento que solicitamos "
        "informacion respecto a los servicios ofrecidos por su organizacion, "
        "por lo que respetuosamente solicito su atencion al presente.\n\n"
        "En atencion a lo anterior, adjunto encontrara la documentacion correspondiente "
        "para su revision y consideracion.\n\n"
        "Quedo a su disposicion para cualquier consulta adicional que estime pertinente.")
    pdf.ln(5)
    
    # Cierre
    pdf.cell(0, 6, "Sin otro particular por el momento, me suscribo de usted", ln=True)
    pdf.cell(0, 6, "atentamente y le saluda,", ln=True)
    pdf.ln(10)
    
    pdf.cell(0, 6, "____________________", ln=True)
    pdf.cell(0, 6, "Lic. Roberto Sandoval", ln=True)
    pdf.cell(0, 6, "Telefono: 2345-6789", ln=True)
    pdf.cell(0, 6, "Correo: contacto@empresa.gt", ln=True)
    
    # Guardar
    path = Path("demos/demo_carta_formal_completo.pdf")
    path.parent.mkdir(exist_ok=True)
    pdf.output(str(path))
    return path


def gen_identificacion_pdf():
    """Genera PDF de identificación (DPI)."""
    pdf = PDFGenerator()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "DOCUMENTO PERSONAL DE IDENTIFICACION", align="C", ln=True)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 10, "DPI - RENAP GUATEMALA", align="C", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.ln(5)
    
    # Numero
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(50, 8, "Numero de documento:", ln=False)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, "00000001", ln=True)
    pdf.ln(3)
    
    # Datos
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 7, "DATOS DEL TITULAR", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(50, 6, "Nombre completo:", ln=False)
    pdf.cell(0, 6, "Juan Carlos Ramirez", ln=True)
    pdf.cell(50, 6, "Numero DPI:", ln=False)
    pdf.cell(0, 6, "1234 56789 0123", ln=True)
    pdf.cell(50, 6, "Fecha nacimiento:", ln=False)
    pdf.cell(0, 6, "15/03/1980", ln=True)
    pdf.ln(2)
    
    # Ubicación
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 7, "INFORMACION DE UBICACION", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(50, 6, "Lugar nacimiento:", ln=False)
    pdf.cell(0, 6, "Guatemala, Guatemala", ln=True)
    pdf.cell(50, 6, "Municipio:", ln=False)
    pdf.cell(0, 6, "Guatemala", ln=True)
    pdf.cell(50, 6, "Departamento:", ln=False)
    pdf.cell(0, 6, "Guatemala", ln=True)
    pdf.cell(50, 6, "Vecino de:", ln=False)
    pdf.cell(0, 6, "Guatemala", ln=True)
    pdf.ln(2)
    
    # Información general
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 7, "INFORMACION GENERAL", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, "Nacionalidad: Guatemalteco", ln=True)
    pdf.cell(0, 6, "Registro Nacional de las Personas - RENAP", ln=True)
    pdf.cell(0, 6, "Guatemala, Centro America", ln=True)
    pdf.cell(0, 6, "Este documento es valido en todo el territorio nacional", ln=True)
    pdf.ln(2)
    
    # Validez
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, f"Emitido: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
    pdf.cell(0, 6, f"Vigente hasta: 2032/12/31", ln=True)
    
    # Guardar
    path = Path("demos/demo_identificacion_completo.pdf")
    path.parent.mkdir(exist_ok=True)
    pdf.output(str(path))
    return path


def gen_comunicado_pdf():
    """Genera PDF de comunicado administrativo."""
    pdf = PDFGenerator()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "COMUNICADO OFICIAL", align="C", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.ln(5)
    
    # Encabezado
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(50, 7, "Numero:", ln=False)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 7, "COM-2026-0001", ln=True)
    
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(50, 7, "Fecha:", ln=False)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 7, datetime.now().strftime("%d/%m/%Y"), ln=True)
    pdf.ln(3)
    
    # Destinatario
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, "Estimado Cliente/Usuario:", ln=True)
    pdf.ln(2)
    
    # Contenido
    pdf.multi_cell(0, 5,
        "Por medio de la presente le informamos sobre informacion importante "
        "que debe tomar en consideracion.\n\n"
        "AVISO GENERAL:\n"
        "Le comunicamos cambios importantes en nuestros servicios y horarios. "
        "Agradecemos su comprension y paciencia durante este proceso.\n\n"
        "HORARIO DE ATENCION:\n"
        "Lunes a Viernes: 08:00 - 17:00\n"
        "Sabado: 08:00 - 12:00\n"
        "Domingo: Cerrado\n\n"
        "INFORMACION IMPORTANTE:\n"
        "Cualquier duda puede dirigirse a nuestras oficinas. "
        "En consideracion del tiempo que toma procesar solicitudes, "
        "favor de presentarse con anticipacion.")
    pdf.ln(5)
    
    # Contacto
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 7, "DATOS DE CONTACTO", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, "Departamento Administrativo", ln=True)
    pdf.cell(0, 6, "Telefono: 2234-5678", ln=True)
    pdf.cell(0, 6, "Correo: info@empresa.gt", ln=True)
    pdf.cell(0, 6, "Pagina web: www.empresa.gt", ln=True)
    pdf.ln(3)
    
    # Cierre
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, "La administracion se compromete a brindar el mejor servicio.", ln=True)
    pdf.cell(0, 6, "Cordialmente,", ln=True)
    pdf.ln(8)
    pdf.cell(0, 6, "____________________", ln=True)
    pdf.cell(0, 6, "La Administracion", ln=True)
    pdf.cell(0, 6, "Departamento de Comunicacion", ln=True)
    
    # Guardar
    path = Path("demos/demo_comunicado_completo.pdf")
    path.parent.mkdir(exist_ok=True)
    pdf.output(str(path))
    return path


def main():
    """Genera todos los 7 PDFs demo."""
    print("=" * 70)
    print(" GENERADOR DE PDFs DEMO — 7 CATEGORÍAS")
    print("=" * 70)
    print()
    
    generadores = {
        "Factura": gen_factura_pdf,
        "Recibo": gen_recibo_pdf,
        "Contrato": gen_contrato_pdf,
        "Constancia": gen_constancia_pdf,
        "Carta Formal": gen_carta_formal_pdf,
        "Identificación": gen_identificacion_pdf,
        "Comunicado": gen_comunicado_pdf,
    }
    
    generados = []
    for nombre, func in generadores.items():
        try:
            ruta = func()
            print(f"✅ {nombre:20s}: {ruta.name}")
            generados.append(ruta)
        except Exception as e:
            print(f"❌ {nombre:20s}: ERROR - {e}")
    
    print()
    print("=" * 70)
    print(" RESUMEN")
    print("=" * 70)
    print(f"  PDFs generados: {len(generados)}/7")
    print(f"  Ubicacion: demos/")
    print()
    print("Archivos creados:")
    for ruta in generados:
        print(f"  - {ruta.name}")
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
