"""
generar_dataset.py — Generador de dataset sintético de alta calidad.

Genera documentos de entrenamiento para clasificación en 4 categorías:
  - Facturas (FACTURA ELECTRONICA, tributario, SAT, IVA, NIT)
  - Recibos (RECIBO, recibi de, efectivo, firma, sello)
  - Contratos (CONTRATO, clausula, vigencia, el contratante, convenimos)
  - Otros (Comunicado, estimado, informamos, cordialmente, aviso)

Genera 35 archivos por categoría (140 total) con vocabulario diferenciador claro.

Ejecutar:
    python generar_dataset.py
"""
import random
from pathlib import Path
from datetime import datetime, timedelta

# Palabras clave únicas por categoría para máxima diferenciación
KEYWORDS = {
    "factura": [
        "FACTURA ELECTRONICA", "documento tributario", "SAT Guatemala",
        "IVA 12%", "subtotal", "contribuyente", "serie correlativo",
        "monto total", "RFC", "NIT", "autorizado", "GTQ", "Q",
        "serie", "acreditar", "vencimiento", "SAT autorizado"
    ],
    "recibo": [
        "RECIBO", "recibi de", "cantidad de", "por concepto de",
        "forma de pago", "efectivo", "transferencia", "cheque",
        "sello", "firma", "departamento cobros", "pago puntual",
        "recibidor", "comprobante", "vale"
    ],
    "contrato": [
        "CONTRATO", "clausula", "partes", "vigencia", "obligaciones",
        "el contratante", "el contratado", "convenimos", "a partir de",
        "acuerdo", "incumplimiento", "Guatemala", "suspend", "rescisión",
        "firmamos", "acta", "términos y condiciones"
    ],
    "otro": [
        "COMUNICADO", "estimado", "por medio de la presente",
        "informamos", "agradecemos", "atentamente", "cordialmente",
        "horario", "aviso", "departamento administrativo",
        "favor de", "le comunicamos", "en consideración",
        "La administración", "informacion general"
    ]
}


def gen_factura(i):
    """Genera una factura sintética con vocabulario diferenciador claro."""
    keywords = KEYWORDS["factura"]
    keyword1 = random.choice(keywords)
    keyword2 = random.choice(keywords)
    
    serie = f"FAC-2026-{str(i).zfill(4)}"
    nit = f"{random.randint(1000000, 9999999)}-{random.randint(1, 9)}"
    subtotal = random.randint(500, 50000)
    iva = int(subtotal * 0.12)
    total = subtotal + iva
    
    nombres = ["Distribuidora Guatemalteca", "Empresa Comercial SA", "Grupo Industrial", "Servicios Globales"]
    cliente = f"Cliente: {random.choice(nombres)}"
    
    texto = f"""
FACTURA ELECTRONICA
Numero: {serie}
Fecha: {(datetime.now() - timedelta(days=random.randint(0, 60))).strftime('%d/%m/%Y')}

Empresa Emisora
NIT: {nit}
{cliente}
Direccion: Ciudad de Guatemala

Concepto de Venta
Descripcion de servicio/producto: Articulo {i}
Cantidad: {random.randint(1, 100)} unidades
Precio unitario: Q{random.randint(5, 500)}.00

Detalle Tributario
Subtotal: Q{subtotal}.00
IVA 12%: Q{iva}.00
Monto Total: Q{total}.00

{keyword1}
SAT Guatemala autorizado
Documento tributario electronico
{keyword2}

Forma de pago: Transferencia Bancaria
Banco: Banco del Pais
Cuenta: 1234567890
Referencia: INV-2026-{i}

Serie: {serie}
Correlativo: {i}
RFC Guatemala
Contribuyente activo
Acreditar IVA
Moneda GTQ quetzal Q
Vencimiento: {(datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y')}
"""
    return texto.strip()


def gen_recibo(i):
    """Genera un recibo sintético con vocabulario diferenciador claro."""
    keywords = KEYWORDS["recibo"]
    keyword1 = random.choice(keywords)
    keyword2 = random.choice(keywords)
    
    numero = f"REC-{str(i).zfill(5)}"
    monto = random.randint(50, 5000)
    
    conceptos = ["Pago de servicio", "Pago de renta", "Deposito en cuenta", "Pago de cuota", "Pago mensual"]
    concepto = random.choice(conceptos)
    
    formas = ["efectivo", "cheque", "transferencia", "deposito"]
    forma = random.choice(formas)
    
    texto = f"""
RECIBO OFICIAL DE PAGO
Numero: {numero}
Fecha: {datetime.now().strftime('%d/%m/%Y')}

Recibi de:
Nombre: Empresa Receptora {i}
Direccion: Ciudad de Guatemala
Telefono: {random.randint(2000, 9999)}-{random.randint(1000, 9999)}

Cantidad de Dinero:
Monto recibido: Q{monto}.00
Cantidad en letras: {monto} quetzales

Por concepto de:
{concepto}
Descripcion: Pago correspondiente al mes/servicio

Forma de pago: {forma.upper()}
{keyword1}

Detalles del Recibo:
Departamento de cobros
Sello: [OFICINA]
Firma: ____________________
Autorizado por: Recibidor

{keyword2}
Muchas gracias por su pago puntual
Comprobante fiscal
Vale de caja
Referencia: {numero}
"""
    return texto.strip()


def gen_contrato(i):
    """Genera un contrato sintético con vocabulario diferenciador claro."""
    keywords = KEYWORDS["contrato"]
    keyword1 = random.choice(keywords)
    keyword2 = random.choice(keywords)
    
    fecha_inicio = datetime.now()
    fecha_fin = fecha_inicio + timedelta(days=random.randint(30, 730))
    
    texto = f"""
CONTRATO DE PRESTACION DE SERVICIOS
Numero: CTR-2026-{str(i).zfill(4)}
Fecha: {fecha_inicio.strftime('%d/%m/%Y')}

PARTES CONTRATANTES

El contratante:
Empresa Prestadora de Servicios
NIT: 1234567-8
Domicilio: Ciudad de Guatemala

El contratado:
Beneficiario del Servicio {i}
Domicilio: Ciudad de Guatemala

CLAUSULAS DEL CONTRATO

PRIMERA: Objeto y Alcance
Las partes convenimos en que el contratante prestará servicios al contratado.

SEGUNDA: Vigencia
Este contrato tendrá vigencia a partir del {fecha_inicio.strftime('%d/%m/%Y')}
hasta el {fecha_fin.strftime('%d/%m/%Y')}, plazo de {random.randint(6, 24)} meses.

TERCERA: Contraprestacion Economica
El contratado se obliga a pagar Q{random.randint(1000, 10000)}.00 mensuales.

CUARTA: Obligaciones del Contratante
{keyword1}
Prestar servicios de calidad y profesionalismo.
Cumplir horarios establecidos.
Mantener confidencialidad.

QUINTA: Obligaciones del Contratado
Efectuar pagos puntuales.
Proveer herramientas necesarias.

{keyword2}

SEXTA: Resolucion y Rescisión
En caso de incumplimiento grave, cualquiera de las partes podrá rescindir.
Aviso con 30 días de anticipación.

SÉPTIMA: Acuerdo General
Ambas partes se comprometen a cumplir íntegramente.
Lo anterior según las leyes de Guatemala.

Firmamos en la ciudad de Guatemala:

______________________________     ______________________________
El Contratante                    El Contratado
Firma y sello                      Firma
"""
    return texto.strip()


def gen_otro(i):
    """Genera un comunicado/otro documento con vocabulario diferenciador claro."""
    keywords = KEYWORDS["otro"]
    keyword1 = random.choice(keywords)
    keyword2 = random.choice(keywords)
    
    texto = f"""
COMUNICADO OFICIAL
Fecha: {datetime.now().strftime('%d/%m/%Y')}
Numero: COM-2026-{str(i).zfill(4)}

Estimado Cliente/Usuario:

Por medio de la presente le informamos sobre información importante
que debe tomar en consideración.

Aviso General:
{keyword1} sobre cambios en nuestros servicios y horarios.

Horario de Atencion:
Lunes a Viernes: 08:00 - 17:00
Sabado: 08:00 - 12:00
Domingo: Cerrado

Informacion Importante:
Agradecemos su comprensión y paciencia.
{keyword2}

Datos de Contacto:
Departamento Administrativo
Telefono: 2234-5678
Correo: info@empresa.gt
Pagina web: www.empresa.gt

Le comunicamos que cualquier duda puede dirigirse a nuestras oficinas.
En consideración del tiempo que toma procesar solicitudes,
favor de presentarse con anticipación.

La administración se compromete a brindar el mejor servicio.
Cordialmente,

______________________________
La Administracion
Departamento de Comunicacion
"""
    return texto.strip()


def main():
    """Genera el dataset completo con 35 documentos por categoría."""
    print("=" * 70)
    print(" GENERADOR DE DATASET — OCR IA PROYECTO")
    print("=" * 70)
    
    base_dir = Path("data/training")
    base_dir.mkdir(parents=True, exist_ok=True)
    
    categorias = ["factura", "recibo", "contrato", "otro"]
    generadores = {
        "factura": gen_factura,
        "recibo": gen_recibo,
        "contrato": gen_contrato,
        "otro": gen_otro
    }
    
    stats = {}
    
    for categoria in categorias:
        carpeta = base_dir / categoria
        carpeta.mkdir(exist_ok=True)
        
        # Limpiar archivos antiguos
        for archivo in carpeta.glob("*.txt"):
            archivo.unlink()
        
        generador = generadores[categoria]
        total_generados = 0
        
        # Generar 30 documentos base
        print(f"\nGenerando {categoria}...")
        for i in range(1, 31):
            try:
                contenido = generador(i)
                archivo = carpeta / f"{categoria}_{str(i).zfill(3)}.txt"
                archivo.write_text(contenido, encoding="utf-8")
                total_generados += 1
            except Exception as e:
                print(f"  ❌ Error generando {categoria}_{i}: {e}")
        
        # Generar 5 documentos cortos adicionales (índices 31-35)
        for i in range(31, 36):
            try:
                if categoria == "factura":
                    contenido = f"FACTURA ELECTRONICA No.{i} SAT Guatemala Documento tributario Total Q{random.randint(100, 5000)} NIT Contribuyente IVA 12% Monto Q{random.randint(50, 3000)}"
                elif categoria == "recibo":
                    contenido = f"RECIBO Numero REC-{i} Recibi de cliente cantidad Q{random.randint(50, 1000)} por concepto de pago forma efectivo transferencia sello firma departamento cobros"
                elif categoria == "contrato":
                    contenido = f"CONTRATO Clausula el contratante el contratado Obligaciones vigencia {random.randint(6, 24)} meses convenimos a partir de acuerdo incumplimiento Guatemala"
                else:
                    contenido = f"COMUNICADO Estimado por medio de la presente le informamos aviso horario agradecemos atentamente cordialmente la administracion informacion contactenos"
                
                archivo = carpeta / f"{categoria}_corto_{str(i-30).zfill(2)}.txt"
                archivo.write_text(contenido, encoding="utf-8")
                total_generados += 1
            except Exception as e:
                print(f"  ❌ Error generando {categoria} corto_{i-30}: {e}")
        
        stats[categoria] = total_generados
        print(f"  ✅ {total_generados} archivos generados")
    
    print(f"\n{'=' * 70}")
    print(" RESUMEN")
    print("=" * 70)
    total = sum(stats.values())
    for cat, count in stats.items():
        print(f"  {cat:12s}: {count:2d} archivos")
    print(f"  {'TOTAL':12s}: {total:3d} archivos")
    print(f"{'=' * 70}")
    print(f"\n✅ Dataset generado exitosamente en data/training/")
    print(f"Próximo paso: python train_classifier.py")
    print()


if __name__ == "__main__":
    main()
