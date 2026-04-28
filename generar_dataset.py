"""
generar_dataset.py — Generador de dataset sintético de alta calidad.

Genera documentos de entrenamiento para clasificación en 7 categorías:
  - Facturas (FACTURA ELECTRONICA, tributario, SAT, IVA, NIT)
  - Recibos (RECIBO, recibi de, efectivo, firma, sello)
  - Contratos (CONTRATO, clausula, vigencia, el contratante, convenimos)
  - Constancias (CONSTANCIA, se hace constar, presto servicios, cargo, fecha_ingreso)
  - Cartas Formales (CARTA FORMAL, estimado, por este medio, respetuosamente)
  - Identificaciones (DOCUMENTO PERSONAL, DPI, RENAP, fecha nacimiento)
  - Otros (Comunicado, estimado, informamos, cordialmente, aviso)

Genera 35 archivos por categoría (245 total) con vocabulario diferenciador claro.
También genera data/ground_truth.csv con metadata del dataset.

Ejecutar:
    python generar_dataset.py
"""
import random
import csv
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
    "constancia": [
        "CONSTANCIA", "se hace constar", "hace constar que",
        "prestó servicios", "laboró en", "tiempo de servicio",
        "cargo de", "fecha de ingreso", "extendida a solicitud",
        "para los fines que estime convenientes", "firmo y sello"
    ],
    "carta_formal": [
        "CARTA FORMAL", "estimado señor", "estimada señora",
        "por este medio", "me dirijo a usted",
        "respetuosamente", "en atención a", "adjunto encontrará",
        "quedo a su disposición", "sin otro particular",
        "atentamente le saluda"
    ],
    "identificacion": [
        "DOCUMENTO PERSONAL DE IDENTIFICACION", "DPI",
        "Registro Nacional de las Personas", "RENAP",
        "número de identificación", "municipio de",
        "lugar de nacimiento", "fecha de nacimiento",
        "vecino de", "guatemalteco"
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


def gen_constancia(i):
    """Genera una constancia de trabajo sintética."""
    keywords = KEYWORDS["constancia"]
    keyword1 = random.choice(keywords)
    keyword2 = random.choice(keywords)

    nombres = ["Juan Carlos Ramirez", "Maria Lopez", "Pedro Gonzalez",
               "Ana Castillo", "Luis Mendoza", "Sofia Herrera"]
    cargos = ["Auxiliar Contable", "Asistente Administrativo",
              "Tecnico en Sistemas", "Secretaria Ejecutiva",
              "Coordinador de Proyectos", "Analista de Datos"]
    empresas = ["Distribuidora Central SA", "Servicios Guatemala",
                "Corporacion Innovacion", "Grupo Empresarial GT"]

    nombre = random.choice(nombres)
    cargo = random.choice(cargos)
    empresa = random.choice(empresas)
    anios = random.randint(1, 10)
    fecha_ingreso = f"{random.randint(1, 28)}/0{random.randint(1, 9)}/201{random.randint(0, 9)}"

    texto = f"""CONSTANCIA DE TRABAJO
Numero: CONST-2026-{str(i).zfill(4)}

{empresa}
Guatemala, {datetime.now().strftime('%d/%m/%Y')}

La Gerencia de Recursos Humanos de {empresa}

HACE CONSTAR QUE:

{keyword1}

El señor(a) {nombre} identificado(a) con DPI numero {random.randint(1000,9999)}-{random.randint(10000,99999)}-{random.randint(1000,9999)}
ha prestado servicios en nuestra institución desempeñando el cargo de
{cargo} desde el {fecha_ingreso} hasta la fecha, con una
antigüedad de {anios} años de servicio continuo.

Durante este tiempo ha demostrado responsabilidad, puntualidad
y compromiso con sus funciones.

{keyword2}

La presente constancia se extiende a solicitud del interesado
para los fines que estime convenientes, en la ciudad de Guatemala
a los {random.randint(1, 28)} días del mes de abril de 2026.

______________________________
Recursos Humanos
{empresa}
Sello: [OFICIAL]
Firma autorizada
"""
    return texto.strip()


def gen_carta_formal(i):
    """Genera una carta formal sintética."""
    keywords = KEYWORDS["carta_formal"]
    keyword1 = random.choice(keywords)
    keyword2 = random.choice(keywords)

    asuntos = [
        "Solicitud de información",
        "Notificación de cambio de domicilio",
        "Solicitud de prórroga de plazo",
        "Presentación de propuesta comercial",
        "Confirmación de reunión"
    ]
    asunto = random.choice(asuntos)
    remitentes = ["Lic. Roberto Sandoval", "Ing. Maria Fuentes",
                  "Dr. Carlos Morales", "Dra. Ana Recinos"]
    destinatarios = ["Gerente General", "Director Administrativo",
                     "Jefe de Departamento", "Coordinador de Area"]

    texto = f"""CARTA FORMAL
Numero de referencia: CF-2026-{str(i).zfill(4)}
Guatemala, {datetime.now().strftime('%d de %B de %Y')}

Señor(a):
{random.choice(destinatarios)}
{random.choice(['Empresa Receptora SA', 'Corporacion Guatemala', 'Servicios Administrativos'])}
Presente.

Estimado señor(a):

{keyword1} con el respeto que se merece, para exponerle
lo siguiente en relación al asunto: {asunto}.

Por este medio me dirijo a usted para hacer de su conocimiento
que {keyword2}, por lo que respetuosamente solicito
su atención al presente.

En atención a lo anterior, adjunto encontrará la documentación
correspondiente para su revisión y consideración.

Quedo a su disposición para cualquier consulta adicional
que estime pertinente.

Sin otro particular por el momento, me suscribo de usted
atentamente y le saluda,

______________________________
{random.choice(remitentes)}
Telefono: {random.randint(2000, 7999)}-{random.randint(1000, 9999)}
Correo: contacto@empresa.gt
"""
    return texto.strip()


def gen_identificacion(i):
    """Genera un documento de identificación sintético (DPI simulado)."""
    keywords = KEYWORDS["identificacion"]
    keyword1 = random.choice(keywords)

    nombres = ["Juan", "Maria", "Carlos", "Ana", "Pedro", "Sofia"]
    apellidos = ["Ramirez", "Lopez", "Gonzalez", "Castillo", "Mendoza"]
    municipios = ["Guatemala", "Mixco", "Villa Nueva", "San Jose Pinula",
                  "Amatitlan", "Chinautla"]
    departamentos = ["Guatemala", "Sacatepequez", "Chimaltenango",
                     "Escuintla", "Quetzaltenango"]

    nombre = f"{random.choice(nombres)} {random.choice(apellidos)}"
    dpi = f"{random.randint(1000,9999)} {random.randint(10000,99999)} {random.randint(1000,9999)}"
    fecha_nac = f"{random.randint(1, 28)}/0{random.randint(1, 9)}/19{random.randint(70, 99)}"
    municipio = random.choice(municipios)
    depto = random.choice(departamentos)

    texto = f"""DOCUMENTO PERSONAL DE IDENTIFICACION
DPI - RENAP Guatemala
Numero de documento: {str(i).zfill(8)}

{keyword1}

DATOS DEL TITULAR:
Nombre completo: {nombre}
Numero DPI: {dpi}
Fecha de nacimiento: {fecha_nac}
Lugar de nacimiento: {municipio}, {depto}
Vecino de: {municipio}
Municipio: {municipio}
Departamento: {depto}
Nacionalidad: Guatemalteco

Registro Nacional de las Personas RENAP
Guatemala, Centro America
Este documento es valido en todo el territorio nacional.

Emitido: {datetime.now().strftime('%d/%m/%Y')}
Vigente hasta: {random.randint(2028, 2035)}/01/01
"""
    return texto.strip()


def main():
    """Genera el dataset completo con 35 documentos por categoría (7 categorías)."""
    print("=" * 70)
    print(" GENERADOR DE DATASET — OCR IA PROYECTO 04 (7 CATEGORÍAS)")
    print("=" * 70)

    base_dir = Path("data/training")
    base_dir.mkdir(parents=True, exist_ok=True)

    # 7 categorías según enunciado
    categorias = ["factura", "recibo", "contrato",
                  "constancia", "carta_formal", "identificacion", "otro"]

    generadores = {
        "factura": gen_factura,
        "recibo": gen_recibo,
        "contrato": gen_contrato,
        "constancia": gen_constancia,
        "carta_formal": gen_carta_formal,
        "identificacion": gen_identificacion,
        "otro": gen_otro
    }

    # Crear ground truth CSV
    ground_truth_rows = []

    stats = {}
    for categoria in categorias:
        carpeta = base_dir / categoria
        carpeta.mkdir(exist_ok=True)

        # Limpiar archivos anteriores
        for archivo in carpeta.glob("*.txt"):
            archivo.unlink()

        generador = generadores[categoria]
        total_generados = 0

        print(f"\nGenerando {categoria}...")

        # 30 documentos completos
        for i in range(1, 31):
            try:
                contenido = generador(i)
                archivo = carpeta / f"{categoria}_{str(i).zfill(3)}.txt"
                archivo.write_text(contenido, encoding="utf-8")
                total_generados += 1

                # Agregar al ground truth
                ground_truth_rows.append({
                    "archivo": str(archivo),
                    "categoria": categoria,
                    "num_palabras": len(contenido.split()),
                    "tipo": "completo"
                })
            except Exception as e:
                print(f"  ❌ Error en {categoria}_{i}: {e}")

        # 5 documentos cortos
        for i in range(31, 36):
            shorts = {
                "factura": f"FACTURA ELECTRONICA No.{i} SAT Guatemala NIT IVA 12% Total Q{random.randint(100,5000)} contribuyente documento tributario",
                "recibo": f"RECIBO No.{i} Recibi de cliente Q{random.randint(50,1000)} efectivo pago concepto sello firma cobros",
                "contrato": f"CONTRATO clausula el contratante el contratado vigencia {random.randint(6,24)} meses convenimos obligaciones Guatemala",
                "constancia": f"CONSTANCIA se hace constar que laboró en cargo de servicio tiempo antigüedad firmo sello recursos humanos",
                "carta_formal": f"CARTA FORMAL estimado señor por este medio me dirijo a usted respetuosamente atentamente sin otro particular",
                "identificacion": f"DPI RENAP documento personal identificacion guatemalteco municipio departamento fecha nacimiento numero identificacion",
                "otro": f"COMUNICADO estimado informamos cordialmente atentamente la administracion aviso horario contactenos",
            }
            try:
                contenido = shorts[categoria]
                archivo = carpeta / f"{categoria}_corto_{str(i-30).zfill(2)}.txt"
                archivo.write_text(contenido, encoding="utf-8")
                total_generados += 1
                ground_truth_rows.append({
                    "archivo": str(archivo),
                    "categoria": categoria,
                    "num_palabras": len(contenido.split()),
                    "tipo": "corto"
                })
            except Exception as e:
                print(f"  ❌ Error corto {categoria}_{i-30}: {e}")

        stats[categoria] = total_generados
        print(f"  ✅ {total_generados} archivos generados")

    # Guardar ground truth CSV
    gt_path = Path("data/ground_truth.csv")
    with open(gt_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["archivo", "categoria", "num_palabras", "tipo"])
        writer.writeheader()
        writer.writerows(ground_truth_rows)

    print(f"\n{'=' * 70}")
    print(" RESUMEN")
    print("=" * 70)
    total = sum(stats.values())
    for cat, count in stats.items():
        print(f"  {cat:20s}: {count:2d} archivos")
    print(f"  {'TOTAL':20s}: {total:3d} archivos")
    print(f"\nGround truth guardado en: {gt_path}")
    print(f"Siguiente paso: python train_classifier.py")
    print()


if __name__ == "__main__":
    main()
