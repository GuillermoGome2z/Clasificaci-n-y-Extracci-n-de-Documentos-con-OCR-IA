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

Genera 70 archivos por categoría (490 total) con múltiples variantes de formato
y vocabulario diferenciador claro por categoría.
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
    
    # Formato 1: Estándar detallado
    formato1 = f"""
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
    
    # Formato 2: Compacto SAT
    formato2 = f"""
FACTURA ELECTRONICA SAT
Serie: {serie}
Fecha Emision: {datetime.now().strftime('%d/%m/%Y')}
NIT Emisor: {nit}
{cliente}

CONCEPTO: Articulo {i}
CANTIDAD: {random.randint(1, 100)} unidades
PRECIO: Q{random.randint(5, 500)}.00

---
SUBTOTAL: Q{subtotal}.00
IVA 12%: Q{iva}.00
TOTAL: Q{total}.00
---

{keyword1}
Documento tributario electronico SAT Guatemala
Autorizado por SAT
{keyword2}
RFC {random.randint(100, 999)}-{random.randint(100, 999)}
"""
    
    # Formato 3: Alternativo con detalle de conceptos
    formato3 = f"""
---FACTURA ELECTRONICA---
Numero de Factura: {serie}
Correlativo: {i}
Fecha: {(datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%d/%m/%Y')}

Datos del Emisor
NIT: {nit}
{cliente}
Guatemala

Detalles de la Transaccion
Renglon 1: {keyword1} - Q{subtotal}.00
Cantidad: {random.randint(1, 50)} unidades

Resumen Tributario
Monto Gravable: Q{subtotal}.00
{keyword2}
Impuesto Valor Agregado 12%: Q{iva}.00

Total a Pagar: Q{total}.00 GTQ

Forma de Pago: {random.choice(['Efectivo', 'Transferencia', 'Cheque'])}
Vencimiento Pago: {(datetime.now() + timedelta(days=random.randint(15, 45))).strftime('%d/%m/%Y')}
"""
    
    return random.choice([formato1, formato2, formato3]).strip()


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
    
    # Formato 1: Recibo estándar detallado
    formato1 = f"""
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
    
    # Formato 2: Recibo compacto
    formato2 = f"""
---RECIBO DE PAGO---
No.: {numero}
Fecha: {datetime.now().strftime('%d/%m/%Y')}

Recibi de: Empresa {i}
Monto: Q{monto}.00
Concepto: {concepto}
Forma: {forma.upper()}

{keyword1}
Sello de cobros
Firma: _________________

{keyword2}
"""
    
    # Formato 3: Recibo con detalles expandidos
    formato3 = f"""
=== RECIBO OFICIAL ===
Numero de Recibo: {numero}
Fecha de Emision: {datetime.now().strftime('%d/%m/%Y')}
Hora: {datetime.now().strftime('%H:%M:%S')}

De: Empresa Receptora {i}
Telefono de contacto: {random.randint(2200, 7700)}-{random.randint(1000, 9999)}

MONTO PAGADO: Q{monto}.00
{keyword1}

Por: {concepto}
Periodo: {datetime.now().strftime('%B %Y')}

Forma de Pago: {forma.upper()}
{keyword2}

Departamento de Cobros y Recaudacion
Sello: [EMPRESA]
Firma Autorizada: _______________
Pago Puntual

Comprobante: {numero}
Vale
"""
    
    return random.choice([formato1, formato2, formato3]).strip()


def gen_contrato(i):
    """Genera un contrato sintético con vocabulario diferenciador claro."""
    keywords = KEYWORDS["contrato"]
    keyword1 = random.choice(keywords)
    keyword2 = random.choice(keywords)
    
    fecha_inicio = datetime.now()
    fecha_fin = fecha_inicio + timedelta(days=random.randint(30, 730))
    
    # Formato 1: Contrato estándar formal
    formato1 = f"""
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
    
    # Formato 2: Contrato simplificado
    formato2 = f"""
===== CONTRATO =====
Numero: CTR-2026-{str(i).zfill(4)}
Fecha: {fecha_inicio.strftime('%d/%m/%Y')}

CONTRATANTE: Empresa Prestadora
NIT: 1234567-8
CONTRATADO: Beneficiario {i}

{keyword1}
Vigencia desde: {fecha_inicio.strftime('%d/%m/%Y')}
Hasta: {fecha_fin.strftime('%d/%m/%Y')}
Duracion: {random.randint(6, 24)} meses

Pago Mensual: Q{random.randint(1000, 10000)}.00

Clausulas Principales:
- Prestar servicios profesionales
- Cumplimiento de horarios
- Confidencialidad de informacion

{keyword2}
- Resolucion con 30 dias aviso previo
- Acuerdo segun leyes de Guatemala

Firmamos:
_________________  ___________________
Contratante        Contratado
"""
    
    # Formato 3: Contrato con tabla de términos
    formato3 = f"""
CONTRATO DE SERVICIOS PROFESIONALES
Numero de Contrato: CTR-2026-{str(i).zfill(4)}
Lugar: Guatemala
Fecha: {fecha_inicio.strftime('%d/%m/%Y')}

PARTES:
Empresa: Empresa Prestadora de Servicios
Persona: Beneficiario Contrato {i}

{keyword1}

TERMINOS Y CONDICIONES:
Fecha de Inicio: {fecha_inicio.strftime('%d/%m/%Y')}
Fecha de Terminacion: {fecha_fin.strftime('%d/%m/%Y')}
Vigencia Total: {random.randint(6, 24)} meses

Compensacion Economica:
Monto Mensual: Q{random.randint(1000, 10000)}.00
Moneda: Quetzal Guatemalteco

Obligaciones del Contratante:
- {keyword2}
- Cumplimiento diligente
- Profesionalismo

Clausula de Terminacion:
Previo aviso de 30 dias, cualquiera de las partes puede rescindir.
Causales de rescisión: incumplimiento grave de obligaciones.

ACUERDO FINAL:
Ambas partes aceptan los terminos y condiciones establecidas.
Ley aplicable: Leyes de la Republica de Guatemala

FIRMANTES:
________________           ________________
Empresa                    Persona Contratada
"""
    
    return random.choice([formato1, formato2, formato3]).strip()


def gen_otro(i):
    """Genera un comunicado/otro documento con vocabulario diferenciador claro."""
    keywords = KEYWORDS["otro"]
    keyword1 = random.choice(keywords)
    keyword2 = random.choice(keywords)
    
    # Formato 1: Comunicado formal
    formato1 = f"""
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
    
    # Formato 2: Comunicado simplificado
    formato2 = f"""COMUNICADO
Numero: COM-2026-{str(i).zfill(4)}
Fecha: {datetime.now().strftime('%d/%m/%Y')}

{keyword1}

{keyword2}

Horario: L-V 08:00-17:00, S 08:00-12:00

Contacto:
Telefono: 2234-5678
Email: info@empresa.gt

Cordialmente,
La Administracion
"""
    
    # Formato 3: Comunicado expandido
    formato3 = f"""
===== COMUNICADO INSTITUCIONAL =====
Numero: COM-2026-{str(i).zfill(4)}
Fecha de Emision: {datetime.now().strftime('%d/%m/%Y')}
Prioridad: NORMAL

DE: Departamento Administrativo
A: Clientes y Usuarios

ASUNTO: Comunicacion importante

CONTENIDO:

{keyword1}

Por este medio informamos sobre cambios importantes en nuestros servicios
y horarios de atención que es necesario que usted conozca.

DETALLES:

{keyword2}

Agradecemos su comprension y paciencia durante este proceso.

HORARIOS DE ATENCION:
Lunes a Viernes: 08:00 - 17:00 horas
Sabado: 08:00 - 12:00 horas
Domingo: Cerrado

CANALES DE COMUNICACION:
Telefono Principal: 2234-5678
Correo Electronico: info@empresa.gt
Pagina Web: www.empresa.gt
Departamento: Administracion

NOTA IMPORTANTE:
La administracion se compromete a brindar el mejor servicio posible.

Cordialmente,
La Administracion
Firma: _________________
"""
    
    return random.choice([formato1, formato2, formato3]).strip()


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

    # Formato 1: Constancia formal estándar
    formato1 = f"""CONSTANCIA DE TRABAJO
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
    
    # Formato 2: Constancia compacta
    formato2 = f"""CONSTANCIA LABORAL
Numero: CONST-2026-{str(i).zfill(4)}
{empresa}
Guatemala, {datetime.now().strftime('%d/%m/%Y')}

Se hace constar que:
{nombre}
DPI: {random.randint(1000,9999)}-{random.randint(10000,99999)}-{random.randint(1000,9999)}

{keyword1}

Laboró en: {cargo}
Desde: {fecha_ingreso}
Antiguedad: {anios} años

{keyword2}

Para los fines que estime convenientes.

Sello: [OFICIAL]
Firma: __________________
"""
    
    # Formato 3: Constancia con detalles expandidos
    formato3 = f"""
===== CONSTANCIA DE PRESTACION DE SERVICIOS =====
Numero de Constancia: CONST-2026-{str(i).zfill(4)}
Fecha: {datetime.now().strftime('%d/%m/%Y')}

Institucion Empleadora:
{empresa}
Departamento: Recursos Humanos

Datos del Trabajador:
Nombre: {nombre}
Documento Personal de Identificacion: {random.randint(1000,9999)}-{random.randint(10000,99999)}-{random.randint(1000,9999)}
Cargo: {cargo}

Información del Empleo:
{keyword1}
Fecha de Inicio de Labores: {fecha_ingreso}
Tiempo de Antigüedad: {anios} años de servicio continuo
Periodo de Evaluacion: Desde inicio hasta presente

Conducta y Desempeño:
El trabajador ha demostrado:
- {keyword2}
- Responsabilidad y puntualidad
- Compromiso con sus funciones
- Profesionalismo en sus actividades

Propósito de la Constancia:
Se extiende a solicitud del interesado para los fines administrativos
y legales que estime convenientes.

Lugar: Guatemala
Autorizado por Recursos Humanos
Sello Institucional: [EMPRESA]
Firma: _______________________
"""
    
    return random.choice([formato1, formato2, formato3]).strip()


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

    # Formato 1: Carta formal completa
    formato1 = f"""CARTA FORMAL
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
    
    # Formato 2: Carta formal simplificada
    formato2 = f"""CARTA FORMAL
Ref: CF-2026-{str(i).zfill(4)}
Guatemala, {datetime.now().strftime('%d/%m/%Y')}

{random.choice(destinatarios)}
Presente

{keyword1}

{keyword2}

{asunto}

Respetuosamente,
{random.choice(remitentes)}
Telefono: {random.randint(2000, 7999)}-{random.randint(1000, 9999)}
"""
    
    # Formato 3: Carta formal con detalles expandidos
    formato3 = f"""
===== CARTA FORMAL =====
Numero: CF-2026-{str(i).zfill(4)}
Fecha: {datetime.now().strftime('%d de %B de %Y')}
Lugar: Guatemala

REMITENTE:
{random.choice(remitentes)}
Direccion: Guatemala

DESTINATARIO:
{random.choice(destinatarios)}
{random.choice(['Empresa Receptora SA', 'Corporacion Guatemala', 'Servicios Administrativos'])}
Presente

ASUNTO: {asunto}

CUERPO DE LA CARTA:

Estimado señor(a):

{keyword1} por este medio me dirijo respetuosamente a su persona
para exponer lo siguiente:

{keyword2}

Con relacion al asunto mencionado, solicito su atención especial.
Adjunto encontrará documentación complementaria para su revision.

Quedo atentamente a su disposición para resolver inquietudes adicionales.

Sin otro particular por ahora,

FIRMA Y CONTACTO:
_____________________________
{random.choice(remitentes)}
Telefono: {random.randint(2200, 7800)}-{random.randint(1000, 9999)}
Email: contacto@empresa.gt
Firma: _____________________
"""
    
    return random.choice([formato1, formato2, formato3]).strip()


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

    # Formato 1: DPI estándar detallado
    formato1 = f"""DOCUMENTO PERSONAL DE IDENTIFICACION
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
    
    # Formato 2: DPI simplificado
    formato2 = f"""DPI RENAP
Numero: {str(i).zfill(8)}

{nombre}
DPI: {dpi}
Fecha Nac: {fecha_nac}
Municipio: {municipio}
Departamento: {depto}

{keyword1}
Nacionalidad: Guatemalteco
Vigencia: {random.randint(2028, 2035)}
"""
    
    # Formato 3: DPI con información expandida
    formato3 = f"""
===== DOCUMENTO PERSONAL DE IDENTIFICACION =====
Registro Nacional de las Personas - RENAP
Numero de Identificacion: {str(i).zfill(8)}
Tipo: DPI Guatemalteco

INFORMACION DEL TITULAR:
Nombre Completo: {nombre}
Numero de DPI: {dpi}
{keyword1}

DATOS DE NACIMIENTO:
Fecha de Nacimiento: {fecha_nac}
Lugar de Nacimiento: {municipio}, {depto}
Municipio: {municipio}
Departamento: {depto}

INFORMACION ADICIONAL:
Nacionalidad: Guatemalteco
Domicilio: {municipio}, {depto}
Vecino de: {municipio}

VALIDEZ DEL DOCUMENTO:
Emision: {datetime.now().strftime('%d/%m/%Y')}
Vencimiento: {random.randint(2028, 2035)}/12/31
Estado: Vigente en todo territorio nacional

DATOS DE EMISION:
Entidad Emisora: RENAP Guatemala
Centro America
Firmas y Sellos: [OFICIAL]
"""
    
    return random.choice([formato1, formato2, formato3]).strip()


def main():
    """Genera el dataset completo con 70 documentos por categoría (7 categorías = 490 total)."""
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

        # 65 documentos completos (ampliar de 30 a 65)
        for i in range(1, 66):
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

        # 5 documentos cortos (índices 66-70)
        for i in range(66, 71):
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
                archivo = carpeta / f"{categoria}_corto_{str(i-65).zfill(2)}.txt"
                archivo.write_text(contenido, encoding="utf-8")
                total_generados += 1
                ground_truth_rows.append({
                    "archivo": str(archivo),
                    "categoria": categoria,
                    "num_palabras": len(contenido.split()),
                    "tipo": "corto"
                })
            except Exception as e:
                print(f"  ❌ Error corto {categoria}_{i-65}: {e}")

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
