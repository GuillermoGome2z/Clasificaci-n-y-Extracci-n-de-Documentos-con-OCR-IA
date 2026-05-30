"""Extracción contextual de campos etiquetados según tipo de documento."""

import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ── Utilidades internas ───────────────────────────────────────────────────────

def _first(lst: list, default: Any = None) -> Any:
    """Primer elemento de una lista, o default si vacía."""
    return lst[0] if lst else default


def _clean(s: Optional[str]) -> Optional[str]:
    """Strip y None si vacío."""
    if s is None:
        return None
    s = s.strip()
    return s if s else None


# ── Constantes de patrones ────────────────────────────────────────────────────

# NIT con contexto de rol (FEL / documentos guatemaltecos)
_NIT_EMISOR = re.compile(
    r'NIT\s+(?:Emisor|del\s+Emisor|Vendedor|del\s+Vendedor)\s*:?\s*(\d{5,9}(?:-\d)?)',
    re.IGNORECASE,
)
_NIT_RECEPTOR = re.compile(
    r'NIT\s+(?:Receptor|del\s+Receptor|Comprador|Cliente)\s*:?\s*(\d{5,9}(?:-\d)?)',
    re.IGNORECASE,
)
_NIT_CERTIFICADOR = re.compile(
    r'NIT\s+Certificador\s*:?\s*(\d{5,9}(?:-\d)?)',
    re.IGNORECASE,
)
_NIT_GENERIC = re.compile(
    r'NIT\s*:?\s*(\d{5,9}(?:-\d)?)',
    re.IGNORECASE,
)

# Razón social / proveedor (emisor)
_RAZON_SOCIAL = re.compile(
    r'Raz[oó]n\s+Social\s*:?\s*([^\n\r]{3,80})',
    re.IGNORECASE,
)
_NOMBRE_COMERCIAL = re.compile(
    r'Nombre\s+Comercial\s*:?\s*([^\n\r]{3,80})',
    re.IGNORECASE,
)

# Receptor: busca el primer "Nombre:" que aparece *después* de la línea "RECEPTOR"
_RECEPTOR_NOMBRE = re.compile(
    r'RECEPTOR\s*[\n\r](?:[^\n\r]*[\n\r]){0,5}?Nombre\s*:?\s*([^\n\r]{3,80})',
    re.IGNORECASE,
)

# Certificador: primer "Nombre:" después de "CERTIFICADOR"
_CERTIFICADOR_NOMBRE = re.compile(
    r'CERTIFICADOR\s*[\n\r](?:[^\n\r]*[\n\r]){0,5}?Nombre\s*:?\s*([^\n\r]{3,80})',
    re.IGNORECASE,
)

# Serie y número FEL
_SERIE_FEL = re.compile(
    r'(?:^|\b)SERIE\s*:?\s*([0-9A-Fa-f]{8})(?![-0-9A-Fa-f])',
    re.IGNORECASE | re.MULTILINE,
)
_NUMERO_DTE = re.compile(
    r'N[°º]?\s*(?:DE\s*)?DTE\s*:?\s*(\d{8,12})\b',
    re.IGNORECASE,
)
_FECHA_CERTIFICACION = re.compile(
    r'Fecha\s+de\s+Certificaci[oó]n\s*:?\s*([^\n\r]{5,30})',
    re.IGNORECASE,
)
_MONEDA = re.compile(
    r'MONEDA\s*:?\s*(GTQ|USD|EUR|MXN|HNL|NIO|CRC|Q)\b',
    re.IGNORECASE,
)

# Total de factura / recibo
_TOTAL = re.compile(
    r'^(?:Gran\s+)?Total\s*:?\s*[Q$]?\s*([\d,]+(?:\.\d{2})?)',
    re.IGNORECASE | re.MULTILINE,
)
_MONTO_RECIBO = re.compile(
    r'(?:Monto|Total|Importe|Valor)\s*:?\s*[Q$]?\s*([\d,]+(?:\.\d{2})?)',
    re.IGNORECASE,
)

# Identificaciones
_DPI_NOMBRE = re.compile(
    r'(?:Nombre(?:\s+Completo)?|Apellidos?\s+y\s+Nombres?)\s*:?\s*([^\n\r]{5,80})',
    re.IGNORECASE,
)
_DPI_CUI = re.compile(
    r'(?:CUI|N[°º]?\s*DPI|Código\s+[Úu]nico)\s*:?\s*([\d]{4}[\s-]?[\d]{5}[\s-]?[\d]{4})',
    re.IGNORECASE,
)
_LICENCIA_NUM = re.compile(
    r'(?:N[°º]?\s*)?Licencia(?:\s+de\s+Conducir)?\s*:\s*([A-Z0-9\-]{5,20})',
    re.IGNORECASE,
)
_PASAPORTE_NUM = re.compile(
    r'(?:N[°º]?\s*)?Pasaporte\s*:\s*([A-Z0-9]{6,12})',
    re.IGNORECASE,
)
_FECHA_NACIMIENTO = re.compile(
    r'(?:Fecha\s+de\s+Nacimiento|Nacimiento|DOB)\s*:?\s*([^\n\r]{5,30})',
    re.IGNORECASE,
)
_FECHA_VENCIMIENTO = re.compile(
    r'(?:Fecha\s+de\s+Vencimiento|Vence|Expira(?:ci[oó]n)?|Expiry)\s*:?\s*([^\n\r]{5,30})',
    re.IGNORECASE,
)

# Contratos
_CONTRATO_PARTES = re.compile(
    r'(?:entre|parte[s]?|contratante[s]?|arrendador[a]?|arrendatario[a]?)\s*:?\s*([^\n\r]{5,80})',
    re.IGNORECASE,
)
_CONTRATO_OBJETO = re.compile(
    r'(?:objeto\s+del\s+contrato'
    r'|cl[aá]usula\s+(?:primera|1[aª]?)[:\s]+objeto'
    r'|\bOBJETO\s*:)\s*\n?\s*([^\n\r]{5,200})',
    re.IGNORECASE | re.MULTILINE,
)
_CONTRATO_VIGENCIA = re.compile(
    r'(?:plazo|vigencia|duraci[oó]n|t[eé]rmino)\s*:?\s*([^\n\r]{5,80})',
    re.IGNORECASE,
)

# Constancias
_CONSTANCIA_NOMBRE = re.compile(
    # Captura solo el nombre de la persona, se detiene antes del verbo (labora/trabaja/etc.)
    r'(?:Se\s+hace\s+constar\s+que|constamos?\s+que)\s+'
    r'(?:el\s+se[nñ]or\s+|la\s+se[nñ]ora\s+|don\s+|do[nñ]a\s+|el\s+|la\s+)?'
    r'([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑa-záéíóúñ ]{5,60}?)'
    r'(?=\s+(?:labora|trabaja|presta\s+sus|se\s+desempe|tiene\s+el|fue\s+|es\s+))',
    re.IGNORECASE,
)
_CONSTANCIA_CARGO = re.compile(
    # Requiere dos puntos para no capturar "en el cargo de"
    r'(?:cargo|puesto|posici[oó]n|ocupa)\s*:\s*([^\n\r]{3,60})',
    re.IGNORECASE,
)
_CONSTANCIA_EMPRESA = re.compile(
    # Requiere dos puntos y no cruza líneas para evitar "nuestra empresa\n siguiente línea"
    r'(?:empresa|organizaci[oó]n|instituci[oó]n|entidad|compan[íi]a)\s*:[^\S\r\n]*([^\n\r]{5,80})',
    re.IGNORECASE,
)

# Cartas formales
# Destinatario inline: "Señor: Juan Pérez" al inicio de línea
_CARTA_DESTINATARIO_INLINE = re.compile(
    r'(?:^|\n)[ \t]*(?:Se[ñn]or(?:es)?|Doctor(?:a)?|Licenciado(?:a)?|Ingeniero(?:a)?|Para|Destinatario)\s*:\s*([^\n\r]{5,80})',
    re.IGNORECASE,
)
# Destinatario en línea siguiente: "Señor:\n Juan Pérez" al inicio de línea
_CARTA_DESTINATARIO_NEXTLINE = re.compile(
    r'(?:^|\n)[ \t]*(?:Se[ñn]or(?:es)?|Doctor(?:a)?|Licenciado(?:a)?|Ingeniero(?:a)?|Para|Destinatario)\s*:?\s*\n[ \t]*([^\n\r]{5,80})',
    re.IGNORECASE,
)
# Frases que indican inicio del cuerpo — no son destinatario
_CARTA_BODY_STARTERS = re.compile(
    r'^(?:por\s+medio\s+de|me\s+permito|solicito|en\s+atenci[oó]n|le\s+informo|el\s+motivo|estimado)',
    re.IGNORECASE,
)
_CARTA_REMITENTE = re.compile(
    r'(?:Atentamente|Suscribe|De\s+usted)\s*[:,]?\s*\n'
    r'(?:[^\n\r]*\n){0,3}?([A-ZÁÉÍÓÚÑ][^\n\r]{5,60})',
    re.IGNORECASE,
)
_CARTA_ASUNTO = re.compile(
    r'(?:ASUNTO|MOTIVO)\s*:\s*([^\n\r]{5,120})',
    re.IGNORECASE,
)

# Asunto cuando aparece en línea siguiente: "ASUNTO\n<texto>" (sin dos puntos)
_CARTA_ASUNTO_NEXTLINE = re.compile(
    r'(?:^|\n)[ \t]*(?:ASUNTO|MOTIVO)\s*:?\s*\n[ \t]*([^\n\r]{5,120})',
    re.IGNORECASE,
)

# Fecha de emisión (separado de certificación)
_FECHA_EMISION = re.compile(
    r'Fecha\s+de\s+(?:Emisi[oó]n|Facturaci[oó]n|Expedici[oó]n)\s*:?\s*([^\n\r]{5,35})',
    re.IGNORECASE,
)

# Número de recibo
_NUMERO_RECIBO = re.compile(
    r'(?:Recibo|Comprobante|Voucher)\s+(?:de\s+\w+\s+)?N[°º]?\.?\s*:?\s*([A-Z0-9\-]{2,20})',
    re.IGNORECASE,
)

# Lugar en carta formal (ciudad, dd de mes de aaaa)
_CARTA_LUGAR = re.compile(
    r'^([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){0,3})'
    r'\s*,\s*\d{1,2}\s+de\s+',
    re.MULTILINE,
)

# Entidad emisora de identificación
_ID_ENTIDAD_EMISORA = re.compile(
    r'(?:Registro\s+Nacional\s+de\s+las\s+Personas'
    r'|RENAP'
    r'|Ministerio\s+de\s+(?:Gobernaci[oó]n|Transportes?)'
    r'|Direcci[oó]n\s+General\s+de\s+Tr[aá]nsito|DGTT'
    r'|Migraci[oó]n)',
    re.IGNORECASE,
)

# Detalle tabla FEL (línea de bien/servicio)
_COL = r'\s{2,}([\d,]+(?:\.\d{2})?)'
_FEL_ITEM_LINE = re.compile(
    r'^(.+?)\s{2,}(\d+(?:\.\d+)?)' + _COL + _COL + _COL,
    re.MULTILINE,
)
_FEL_DETALLE_SECTION = re.compile(
    r'(?:DETALLE|Descripci[oó]n\s+Cantidad)',
    re.IGNORECASE,
)
_CONCEPTO = re.compile(
    r'(?:Concepto|Descripci[oó]n|Por\s+concepto\s+de)\s*:?\s*([^\n\r]{5,120})',
    re.IGNORECASE,
)

# ── Patrones FEL extendidos ────────────────────────────────────────────────────

# Dirección del emisor
_DIRECCION_EMISOR = re.compile(
    r'Direcci[oó]n(?:\s+del?\s+Emisor)?\s*:?\s*([^\n\r]{5,120})',
    re.IGNORECASE,
)

# Autorización SAT — mismo renglón o renglón siguiente al encabezado
_AUTORIZACION_SAT_RE = re.compile(
    r'(?:N[úu]mero\s+de\s+)?Autorizaci[oó]n\s*:?\s*\n?\s*([0-9A-Fa-f\-]{8,60})',
    re.IGNORECASE,
)

# Fechas con "y hora" — formato FEL real de SAT Guatemala
_FECHA_HORA_EMISION = re.compile(
    r'Fecha\s+y\s+hora\s+de\s+emisi[oó]n\s*:?\s*([^\n\r]{5,35})',
    re.IGNORECASE,
)
_FECHA_HORA_CERT = re.compile(
    r'Fecha\s+y\s+hora\s+de\s+certificaci[oó]n\s*:?\s*([^\n\r]{5,35})',
    re.IGNORECASE,
)

# Nombre receptor en línea explícita
_NOMBRE_RECEPTOR_INLINE = re.compile(
    r'Nombre\s+(?:del?\s+)?Receptor\s*:?\s*([^\n\r]{3,80})',
    re.IGNORECASE,
)

# NIT certificador en línea con nombre de la institución
_CERTIF_NIT_INLINE = re.compile(
    r'(?:Superintendencia|SAT)[^\n]*NIT\s*:?\s*(\d{5,9}(?:-\d)?)',
    re.IGNORECASE,
)

# Palabras clave de dirección postal guatemalteca (para detección posicional)
_DIR_KEYWORDS_FEL = re.compile(
    r'\b(?:CALLE|AVENIDA|ZONA\s+\d|BARRIO|COLONIA|ALDEA|MUNICIPIO|DEPARTAMENTO|'
    r'JUTIAPA|GUATEMALA|EL\s+PROGRESO|ZACAPA|QUETZALTENANGO|HUEHUETENANGO|'
    r'SACATEP[EÉ]QUEZ|CHIQUIMULA|IZABAL|PETEN|ALTA\s+VERAPAZ|BAJA\s+VERAPAZ)\b',
    re.IGNORECASE,
)

# Serie y DTE juntos en la misma línea
_SERIE_Y_DTE = re.compile(
    r'Serie\s*:?\s*([0-9A-Fa-f]{8})\s+N[uú]mero\s+de\s+DTE\s*:?\s*(\d{8,12})',
    re.IGNORECASE,
)

# Ítem FEL formato simple: "1 Bien 1 Desayuno 40.00 0.00 40.00"
_FEL_ITEM_SIMPLE_LINE = re.compile(
    r'^\d+\s+(?:Bien|Servicio)\s+(\d+(?:\.\d+)?)\s+(.+?)\s+'
    r'([\d,]+\.\d{2})\s+([\d,]+\.\d{2})\s+([\d,]+\.\d{2})\s*$',
    re.MULTILINE | re.IGNORECASE,
)

# Ítem formato "Descripción  1  Q 6,500.00  Q 6,500.00" (con prefijo Q, sin columna descuento)
_FEL_ITEM_Q_LINE = re.compile(
    r'^(.+?)\s+(\d+(?:\.\d+)?)\s+Q\s*([\d,]+(?:\.\d{2})?)\s+Q\s*([\d,]+(?:\.\d{2})?)\s*$',
    re.MULTILINE | re.IGNORECASE,
)

# ── Patrones adicionales para recibo, contrato, constancia, carta, id ─────────

# Recibo: emisor explícito (solo etiquetas claras al inicio de línea)
_RECIBO_EMISOR_EXPLICIT = re.compile(
    r'(?:^|\n)[ \t]*(?:Emisor|Empresa|Instituci[oó]n'
    r'|Nombre\s+del?\s+emisor|Recibido\s+por|Extendido\s+por)\s*:?\s*([^\n\r]{3,80})',
    re.IGNORECASE,
)

# Recibo: receptor / cliente (anclar al inicio de línea para evitar "NIT Cliente:")
_RECIBO_RECEPTOR = re.compile(
    r'(?:^|\n)[ \t]*(?:Cliente|Receptor|Pagador|Beneficiario)\s*:\s*([^\n\r]{3,80})',
    re.IGNORECASE,
)

# Contrato: monto y representante
_CONTRATO_MONTO = re.compile(
    r'(?:monto|valor\s+(?:mensual|total)?|precio|honorarios?|renta|canon|pago\s+mensual)\s*:?\s*[Q$]?\s*([\d,]+(?:\.\d{2})?)',
    re.IGNORECASE,
)
_CONTRATO_REPRESENTANTE = re.compile(
    r'(?:representante\s+legal|representado\s+por|firm[oó]|apoderado\s+(?:legal)?)\s*:?\s*([^\n\r]{5,60})',
    re.IGNORECASE,
)

# Constancia: motivo (cargo de la persona)
_CONSTANCIA_MOTIVO = re.compile(
    r'(?:cargo|puesto|posici[oó]n)\s+de\s+([^\n.;]{5,60})',
    re.IGNORECASE,
)

# Constancia: nombre cuando el texto usa "HACE CONSTAR QUE:" y el nombre va en la línea siguiente
_CONSTANCIA_NOMBRE_HACECONSTAR = re.compile(
    r'HACE\s+CONSTAR\s+QUE\s*:?\s*\n+'
    r'(?:[Ee]l\s+se[nñ]or[a]?\s+|[Ll]a\s+se[nñ]ora\s+|[Dd]on\s+|[Dd]o[nñ]a\s+)?'
    r'([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑa-záéíóúñ ]{5,60}?)'
    r'(?=[,\n]'
    r'|\s+(?:labora|trabaja|presta|ha\s+\w+|se\s+desempe|tiene\s+el|fue\s+|es\s+|identificado))',
    re.IGNORECASE,
)

# Carta formal: cargo del firmante — solo captura explícito o palabras clave de rol
_CARTA_CARGO_EXPLICIT = re.compile(
    r'(?:Cargo|Puesto|Posici[oó]n|Funci[oó]n)\s*:\s*([^\n\r]{3,60})',
    re.IGNORECASE,
)
_CARTA_CARGO_KEYWORDS = re.compile(
    r'\b(Director(?:a)?(?:\s+(?:General|Ejecutivo|a))?'
    r'|Gerente(?:\s+(?:General|Administrativo|Financiero|Comercial))?'
    r'|Jefe(?:\s+(?:de|del)\s+\w+(?:\s+\w+)?)?'
    r'|Coordinador(?:a)?(?:\s+(?:de|del)\s+\w+(?:\s+\w+)?)?'
    r'|Representante\s+Legal'
    r'|Presidente(?:\s+Ejecutivo)?'
    r'|Secretario(?:a)?(?:\s+General)?'
    r'|Administrador(?:a)?'
    r'|Supervisor(?:a)?)\b',
    re.IGNORECASE,
)

# Identificación: nacionalidad
_ID_NACIONALIDAD = re.compile(
    r'(?:Nacionalidad|Nationality|Citizenship)\s*:?\s*([^\n\r]{3,40})',
    re.IGNORECASE,
)

# ── Patrones adicionales (campos extendidos) ──────────────────────────────────

# Tipo fiscal de factura
_TIPO_FISCAL = re.compile(
    r'(?:Tipo\s+de\s+(?:Factura|DTE|Documento)|Tipo\s+Fiscal)\s*:?\s*([^\n\r]{3,60})',
    re.IGNORECASE,
)

# Tipo de contrato / constancia desde encabezado
_TIPO_CONTRATO = re.compile(
    r'CONTRATO\s+DE\s+([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑa-záéíóúñ ]{2,50})',
    re.IGNORECASE | re.MULTILINE,
)
_TIPO_CONSTANCIA = re.compile(
    r'CONSTANCIA\s+DE\s+([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑa-záéíóúñ ]{2,50})',
    re.IGNORECASE | re.MULTILINE,
)

# Teléfono explícito en texto del documento
_TELEFONO_INLINE = re.compile(
    r'(?:Tel[eé]fonos?|Tel\.?|Fax)\s*:?\s*([\d][\d\s\-\+\(\)\.]{5,18})',
    re.IGNORECASE,
)

# Correo electrónico explícito en texto del documento
_EMAIL_INLINE = re.compile(
    r'(?:Correo|E-?mail|correo\s+electr[oó]nico)\s*:?\s*([\w.\-+]+@[\w.\-]+\.[a-z]{2,})',
    re.IGNORECASE,
)

# Dirección del receptor en factura
_DIRECCION_RECEPTOR = re.compile(
    r'(?:Direcci[oó]n\s+(?:del?\s+)?(?:Receptor|Cliente|Comprador))\s*:?\s*([^\n\r]{5,120})',
    re.IGNORECASE,
)

# Forma de pago en texto de factura
_FORMA_PAGO_INLINE = re.compile(
    r'(?:Forma\s+de\s+(?:Pago)?|M[eé]todo\s+de\s+Pago|Pago\s+en)\s*:?\s*([^\n\r]{3,40})',
    re.IGNORECASE,
)

# Impuesto (IVA / ISR)
_IMPUESTO = re.compile(
    r'(?:IVA|ISR|Impuesto\s+al\s+Valor\s+Agregado)\s*:?\s*[Q$]?\s*([\d,]+(?:\.\d{2})?)',
    re.IGNORECASE,
)

# Monto en letras (recibo)
_RECIBO_LETRAS = re.compile(
    r'(?:Son\s*:?\s*(?:exactamente\s+)?'
    r'|Importe\s+en\s+letras?\s*:?\s*'
    r'|en\s+letras?\s*:?\s*)([^\n\r]{5,100})',
    re.IGNORECASE,
)

# Género en identificación
_ID_GENERO = re.compile(
    r'(?:Sexo|G[eé]nero|Sex)\s*:?\s*(Masculino|Femenino|[MF])\b',
    re.IGNORECASE,
)

# Dirección/domicilio en identificación
_ID_DIRECCION = re.compile(
    r'(?:Domicilio|Direcci[oó]n|Residencia)\s*:?\s*([^\n\r]{5,120})',
    re.IGNORECASE,
)

# Número de carné (universitario, colegiado, etc.)
_CARNE_NUM = re.compile(
    r'(?:Carn[eé](?:[^\S\r\n]+(?:de[^\S\r\n]+)?\w+)?|Colegiado|Carnet)\s*:[^\S\r\n]*([A-Z0-9\-]{3,20})',
    re.IGNORECASE,
)

# ── Patrones factura avanzados ─────────────────────────────────────────────────

# Autorización SAT en la línea siguiente al encabezado (fallback)
_AUTH_SAT_NEXTLINE = re.compile(
    r'(?:N[úu]MERO\s+DE\s+AUTORIZACIÓN|AUTORIZACIÓN\s+(?:SAT|DTE))\s*:?\s*\n\s*([0-9A-Fa-f\-]{8,60})',
    re.IGNORECASE,
)

# UUID SAT completo posible (deformado por OCR)
_AUTH_SAT_UUID = re.compile(
    r'\b([0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12})\b',
)

# Receptor multilinea: desde "Nombre Receptor:" hasta separator keyword
_RECEPTOR_MULTILINEA = re.compile(
    r'Nombre\s+(?:del?\s+)?Receptor\s*:?\s*((?:[^\n\r]{3,80}\n?){1,3}?)(?=\s*(?:N[°º]?\s*NIT|NÚMERO|N[°º]\s*DE\s*AUTORIZACIÓN|Serie|Fecha|Moneda|MONEDA))',
    re.IGNORECASE,
)

# ── Patrones recibo avanzados ──────────────────────────────────────────────────

_RECIBI_DE = re.compile(
    r'(?:Recib[ií](?:mos|ó)?\s+de|Recibido\s+de)\s*:?\s*([^\n\r]{3,80})',
    re.IGNORECASE,
)
# Factura formato "Cliente: X" (sin sección RECEPTOR ni "Nombre Receptor:")
_CLIENTE_RECEPTOR = re.compile(
    r'(?:^|\n)[ \t]*Cliente\s*:\s*([^\n\r]{3,80})',
    re.IGNORECASE,
)
_POR_CONCEPTO = re.compile(
    r'(?:Por\s+concepto\s+de|Por\s+concepto)\s*:?\s*([^\n\r]{5,120})',
    re.IGNORECASE,
)
_LA_CANTIDAD_DE = re.compile(
    r'(?:La\s+cantidad\s+de|Cantidad\s+de)\s*:?\s*[Q$]?\s*([\d,]+(?:\.\d{2})?)',
    re.IGNORECASE,
)
_OBSERVACIONES = re.compile(
    r'(?:Observaciones?|Nota[s]?|Aclaraci[oó]n[es]*)\s*:?\s*([^\n\r]{5,200})',
    re.IGNORECASE,
)

# Recibo: fallback posicional para empresa sin etiqueta tras el título RECIBO
_RECIBO_TITLE_LINE = re.compile(r'^RECIBO\b', re.IGNORECASE)
_RECIBO_EMISOR_SKIP = re.compile(
    r'RECIBO|\bNo\.?\s*\d|\bNIT\b|@|\bQ\s*[\d,]'
    r'|\bconcepto\b|\bmonto\b|\bfecha\b|\bdatos\b|\bcliente\b|\bpago\b'
    r'|\bn[úu]m(?:ero)?\.?\b',
    re.IGNORECASE,
)

# ── Patrones contrato avanzados ────────────────────────────────────────────────

_CONTRATANTE = re.compile(
    r'(?:Contratante|Primera\s+Parte|El\s+Empleador|El\s+Arrendador)\s*:?\s*([^\n\r]{5,80})',
    re.IGNORECASE,
)
_CONTRATADO = re.compile(
    r'(?:Contratado(?:a)?|Segunda\s+Parte|El\s+Trabajador|El\s+Empleado|El\s+Arrendatario)\s*:?\s*([^\n\r]{5,80})',
    re.IGNORECASE,
)
_CONTRATO_FIRMANTE = re.compile(
    r'(?:Firma(?:do\s+por)?|f\.\s*|Suscribe(?:n)?)\s*[:,]?\s*\n'
    r'(?:[^\n\r]*\n){0,2}?([A-ZÁÉÍÓÚÑ][^\n\r]{5,60})',
    re.IGNORECASE,
)
_CONTRATO_FECHA_INICIO = re.compile(
    r'(?:a\s+partir\s+del?|inicia\s+el|con\s+vigencia\s+desde|con\s+fecha\s+de\s+inicio)\s*:?\s*([^\n\r,;\.]{5,40})',
    re.IGNORECASE,
)
_CONTRATO_FECHA_FIN = re.compile(
    r'(?:hasta\s+el|finaliza\s+el|concluye\s+el|termina\s+el|fecha\s+de\s+(?:fin|t[eé]rmino|vencimiento))\s*:?\s*([^\n\r,;\.]{5,40})',
    re.IGNORECASE,
)

# ── Patrones constancia avanzados ─────────────────────────────────────────────

_CONSTANCIA_FIRMANTE = re.compile(
    r'(?:Atentamente|f\.\s*|Firmado\s+por|Suscribe)\s*,?\s*\n'
    r'(?:[^\n\r]*\n){0,3}?([A-ZÁÉÍÓÚÑ][^\n\r]{5,60})',
    re.IGNORECASE,
)
_CONSTANCIA_CARGO_FIRMANTE = re.compile(
    r'(?:Atentamente|f\.\s*)\s*,?\s*\n[^\n\r]*\n([A-ZÁÉÍÓÚÑ][^\n\r]{3,60})',
    re.IGNORECASE,
)

# ── Patrones identificación avanzados ─────────────────────────────────────────

_LICENCIA_CLASE = re.compile(
    r'(?:Clase|Categor[ií]a|Tipo)\s*:?\s*([A-CM]\b)',
    re.IGNORECASE,
)
_ID_PAIS = re.compile(
    r'(?:Pa[ií]s\s+(?:de\s+)?(?:origen|expedici[oó]n)?|Country)\s*:?\s*([^\n\r]{3,40})',
    re.IGNORECASE,
)

# ── Mapa de sub-conceptos para detección en texto de facturas ────────────────
_SUBCONCEPTO_MAP: list = [
    # Alimentación
    (re.compile(r'\bdesayuno\b', re.IGNORECASE), "Desayuno"),
    (re.compile(r'\balmuerzo\b', re.IGNORECASE), "Almuerzo"),
    (re.compile(r'\bcena\b', re.IGNORECASE), "Cena"),
    (re.compile(r'\bmerienda\b', re.IGNORECASE), "Merienda"),
    (re.compile(r'\bcaf[eé]\b|\bbebida[s]?\b|\bjugo[s]?\b|\bgaseosa[s]?\b', re.IGNORECASE), "Bebida"),
    (re.compile(r'\bpollo\b', re.IGNORECASE), "Pollo"),
    (re.compile(r'\bhamburguesa[s]?\b', re.IGNORECASE), "Hamburguesa"),
    (re.compile(r'\bpizza[s]?\b', re.IGNORECASE), "Pizza"),
    (re.compile(r'\bcarne[s]?\b', re.IGNORECASE), "Carne"),
    (re.compile(r'\bpescado[s]?\b|\bmariscos?\b', re.IGNORECASE), "Pescado/Mariscos"),
    (re.compile(r'\bcomida[s]?\b|\bmen[uú]\b', re.IGNORECASE), "Comida"),
    # Hospedaje
    (re.compile(r'\bhotel\b|\bmotel\b|\bhostal\b', re.IGNORECASE), "Hotel"),
    (re.compile(r'\bhabitaci[oó]n\b|\bnoche[s]?\b', re.IGNORECASE), "Habitación/Noche"),
    (re.compile(r'\bhospedaje\b|\balojamiento\b', re.IGNORECASE), "Hospedaje"),
    (re.compile(r'\bcheck.?in\b|\bcheck.?out\b', re.IGNORECASE), "Noche de hotel"),
    # Combustible
    (re.compile(r'\bgasolina\b|\bnafta\b', re.IGNORECASE), "Gasolina"),
    (re.compile(r'\bdiesel\b|\bdi[eé]sel\b', re.IGNORECASE), "Diésel"),
    (re.compile(r'\bcombustible\b', re.IGNORECASE), "Combustible"),
    # Transporte
    (re.compile(r'\btaxi\b|\buber\b|\bcabify\b', re.IGNORECASE), "Taxi"),
    (re.compile(r'\bbus\b|\bautobus\b|\bautob[uú]s\b', re.IGNORECASE), "Bus"),
    (re.compile(r'\bpasaje\b|\bboleto\b', re.IGNORECASE), "Pasaje"),
    (re.compile(r'\bflete\b|\btransporte\b', re.IGNORECASE), "Transporte"),
    # Salud
    (re.compile(r'\bfarmacia\b|\bmedicamento[s]?\b|\bmedicina[s]?\b', re.IGNORECASE), "Medicamentos"),
    (re.compile(r'\bconsulta\b', re.IGNORECASE), "Consulta médica"),
    (re.compile(r'\bcl[ií]nica\b|\bhospital\b', re.IGNORECASE), "Atención clínica"),
    (re.compile(r'\blaboratorio\b|\bexamen\b|\ban[aá]lisis\b', re.IGNORECASE), "Laboratorio"),
    # Servicios
    (re.compile(r'\binternet\b|\bwifi\b', re.IGNORECASE), "Internet"),
    (re.compile(r'\belectricidad\b|\benerg[ií]a\s+el[eé]ctrica\b', re.IGNORECASE), "Electricidad"),
    (re.compile(r'\btel[eé]fono\b|\btelefon[ií]a\b', re.IGNORECASE), "Telefonía"),
    (re.compile(r'\blimpieza\b', re.IGNORECASE), "Limpieza"),
    # Mantenimiento
    (re.compile(r'\breparaci[oó]n\b|\breparar\b', re.IGNORECASE), "Reparación"),
    (re.compile(r'\brepuesto[s]?\b|\brefacci[oó]n\b', re.IGNORECASE), "Repuestos"),
    (re.compile(r'\bmantenimiento\b', re.IGNORECASE), "Mantenimiento"),
    # Educación
    (re.compile(r'\bmatr[ií]cula\b', re.IGNORECASE), "Matrícula"),
    (re.compile(r'\bcolegiatura\b', re.IGNORECASE), "Colegiatura"),
    (re.compile(r'\bcurso\b|\btaller\b|\bcapacitaci[oó]n\b', re.IGNORECASE), "Curso"),
    (re.compile(r'\binscripci[oó]n\b', re.IGNORECASE), "Inscripción"),
]


def _detect_sub_concepto(text: str, items: list) -> Optional[str]:
    """Detecta el subtipo de consumo/servicio/producto del texto e ítems FEL."""
    search_str = text + " " + " ".join(it.get("descripcion", "") for it in items)
    for pattern, label in _SUBCONCEPTO_MAP:
        if pattern.search(search_str):
            return label
    return None


def _detect_tipo_contrato(text: str) -> Optional[str]:
    """Detecta el tipo de contrato desde keywords en el encabezado o texto."""
    keywords = [
        (re.compile(r'\bLaboral\b', re.IGNORECASE), "Laboral"),
        (re.compile(r'\bServicios?\b', re.IGNORECASE), "Servicios"),
        (re.compile(r'\bArrendamiento\b', re.IGNORECASE), "Arrendamiento"),
        (re.compile(r'\bCompraventa\b', re.IGNORECASE), "Compraventa"),
        (re.compile(r'\bConfidencialidad\b', re.IGNORECASE), "Confidencialidad"),
        (re.compile(r'\bHonorarios?\b', re.IGNORECASE), "Honorarios profesionales"),
        (re.compile(r'\bConsultor[ií]a\b', re.IGNORECASE), "Consultoría"),
        (re.compile(r'\bComodato\b', re.IGNORECASE), "Comodato"),
    ]
    header = text[:500]  # solo buscar en encabezado
    for pat, label in keywords:
        if pat.search(header):
            return label
    return None


def _detect_tipo_constancia(text: str) -> Optional[str]:
    """Detecta el tipo de constancia desde keywords."""
    keywords = [
        (re.compile(r'\bTrabajo\b', re.IGNORECASE), "Trabajo"),
        (re.compile(r'\bLaboral\b', re.IGNORECASE), "Trabajo"),
        (re.compile(r'\bEstudios?\b', re.IGNORECASE), "Estudios"),
        (re.compile(r'\bIngresos?\b', re.IGNORECASE), "Ingresos"),
        (re.compile(r'\bParticipaci[oó]n\b', re.IGNORECASE), "Participación"),
        (re.compile(r'\bResidencia\b', re.IGNORECASE), "Residencia"),
        (re.compile(r'\bNaci[oó]n(?:alidad)?\b', re.IGNORECASE), "Residencia"),
        (re.compile(r'\bMiembro\b', re.IGNORECASE), "Membresía"),
    ]
    header = text[:500]
    for pat, label in keywords:
        if pat.search(header):
            return label
    return None


def _parse_fel_unlabeled(text: str) -> Dict[str, Optional[str]]:
    """
    Extrae campos FEL que el OCR no etiqueta explícitamente.

    Usa posición relativa de líneas respecto a "Nit Emisor:" para obtener:
    tipo_fiscal, nombre_emisor, nombre_comercial, direccion_emisor,
    receptor (multilinea), certificador.
    """
    result: Dict[str, Optional[str]] = {}
    lines_raw = text.splitlines()
    stripped = [ln.strip() for ln in lines_raw]

    # ── tipo_fiscal: línea standalone con nombre del tipo de factura ─────────────
    _tipo_re = re.compile(
        r'^Factura\s+(?:Peque[ñn]o\s+Contribuyente|Cambiaria(?:\s+con\s+IVA)?'
        r'|Electr[oó]nica|Especial|Combustible|de\s+Peque[ñn]o\s+Contribuyente)',
        re.IGNORECASE,
    )
    for ln in stripped:
        if _tipo_re.match(ln) and len(ln) < 70:
            result["tipo_fiscal"] = ln
            break

    # ── emisor: posición relativa a "Nit Emisor:" ────────────────────────────────
    _nit_emit_re = re.compile(r'^(?:NIT|Nit)\s+Emisor\s*:', re.IGNORECASE)
    nit_idx = next(
        (i for i, ln in enumerate(stripped) if _nit_emit_re.match(ln)), None
    )

    # Palabras que son encabezados de sección FEL estructurado (no datos reales)
    _FEL_HDRS = {
        "EMISOR", "RECEPTOR", "CERTIFICADOR", "DETALLE", "MONEDA",
        "DTE", "SAT", "FEL", "SERIE", "NUMERO", "DATOS",
        "TOTAL", "DESCRIPCION", "CANTIDAD", "FACTURA", "CLIENTE",
    }
    def _is_unlabeled_data(ln: str) -> bool:
        """True si la línea es un dato libre sin etiqueta.

        Descarta: vacías, encabezados de sección (RECEPTOR, EMISOR…),
        y líneas con 'algo: valor' (colon en los primeros 40 chars).
        """
        if not ln or ln.upper() in _FEL_HDRS:
            return False
        colon_pos = ln.find(":")
        return colon_pos < 0 or colon_pos > 40

    if nit_idx is not None:
        # nombre_emisor: última línea no vacía antes del NIT (excluye tipo_fiscal y headers)
        for j in range(nit_idx - 1, max(nit_idx - 8, -1), -1):
            if _is_unlabeled_data(stripped[j]) and not _tipo_re.match(stripped[j]):
                result["nombre_emisor"] = stripped[j]
                break

        # siguientes dos líneas no vacías tras el NIT (solo datos sin etiqueta)
        non_empty_after: list = []
        for j in range(nit_idx + 1, min(nit_idx + 12, len(stripped))):
            if _is_unlabeled_data(stripped[j]):
                non_empty_after.append(stripped[j])
            if len(non_empty_after) >= 2:
                break

        if non_empty_after:
            result["nombre_comercial"] = non_empty_after[0]
        if len(non_empty_after) >= 2 and _DIR_KEYWORDS_FEL.search(non_empty_after[1]):
            result["direccion_emisor"] = non_empty_after[1]

    # ── receptor multilinea: "Nombre Receptor:" + líneas de continuación ─────────
    _recp_hdr_re = re.compile(r'^Nombre\s+(?:del?\s+)?Receptor\s*:', re.IGNORECASE)
    _recp_sep_re = re.compile(
        r'^(?:N[°º]?\s*NIT|NUMERO\s+DE\s+AUTORIZACION|N[ÚU]MERO\s+DE\s+AUTORIZACI[OÓ]N'
        r'|Serie|Fecha|Moneda)',
        re.IGNORECASE,
    )
    recp_idx = next(
        (i for i, ln in enumerate(stripped) if _recp_hdr_re.match(ln)), None
    )
    if recp_idx is not None:
        colon_pos = stripped[recp_idx].find(":")
        first_part = stripped[recp_idx][colon_pos + 1:].strip() if colon_pos >= 0 else ""
        parts = [first_part] if first_part else []
        for j in range(recp_idx + 1, min(recp_idx + 6, len(stripped))):
            if not stripped[j] or _recp_sep_re.match(stripped[j]):
                break
            parts.append(stripped[j])
        if parts:
            result["receptor"] = " ".join(parts)

    # ── certificador: "Superintendencia de ... NIT: XXXXX" en una sola línea ─────
    _cert_nit_re = re.compile(r'^(.+?)\s+NIT\s*:', re.IGNORECASE)
    for ln in stripped:
        if "superintendencia" in ln.lower() and re.search(r'NIT\s*:', ln, re.IGNORECASE):
            m = _cert_nit_re.match(ln)
            if m:
                result["certificador"] = m.group(1).strip()
                break

    return result


class ContextualExtractor:
    """
    Extrae campos etiquetados y listos para mostrar al usuario,
    según el tipo de documento detectado por el clasificador.

    Complementa al DataExtractor (campos genéricos sin rol/contexto) con
    campos como 'proveedor', 'nit_emisor', 'receptor', 'total', etc.
    """

    # Despacha al método privado correspondiente
    _DISPATCHERS: Dict[str, str] = {
        "factura":      "_extract_factura",
        "recibo":       "_extract_recibo",
        "contrato":     "_extract_contrato",
        "constancia":   "_extract_constancia",
        "carta_formal": "_extract_carta_formal",
        "identificacion": "_extract_identificacion",
    }

    def extract(
        self,
        text: str,
        generic_fields: Dict[str, Any],
        document_class: str,
        semantic: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Extrae campos contextuales según el tipo de documento.

        Args:
            text: Texto completo extraído por OCR.
            generic_fields: Salida de DataExtractor.extract_all().
            document_class: Clase predicha por el clasificador.
            semantic: Salida del SemanticAnalyzer (opcional).

        Returns:
            dict con clave 'contextual' que contiene los campos etiquetados
            más 'tipo' (document_class normalizado).
        """
        doc_class = (document_class or "otro").lower().strip()
        method_name = self._DISPATCHERS.get(doc_class, "_extract_otro")

        try:
            method = getattr(self, method_name)
            fields = method(text, generic_fields)
        except Exception as e:  # noqa: BLE001
            logger.error("ContextualExtractor error en '%s': %s", doc_class, e)
            fields = {}

        fields["tipo"] = doc_class

        # Enriquecimiento semántico: agregar categoría y subtipo si disponibles
        if semantic:
            cat = semantic.get("categoria_contenido")
            sub = semantic.get("subtipo_documento")
            if cat:
                fields["categoria_gasto"] = cat
            if sub:
                fields["subtipo"] = sub

        return {"contextual": fields}

    # ── Utilidad regex interna ────────────────────────────────────────────────

    @staticmethod
    def _re1(pattern: re.Pattern, text: str) -> Optional[str]:
        """Primer grupo de captura del primer match, limpiado."""
        m = pattern.search(text)
        return _clean(m.group(1)) if m else None

    @staticmethod
    def _re_all(pattern: re.Pattern, text: str) -> List[str]:
        """Todos los grupos 1 que hacen match, limpios y únicos."""
        cleaned = [v for m in pattern.finditer(text) if (v := _clean(m.group(1))) is not None]
        return list(dict.fromkeys(cleaned))

    # ── Extractores por tipo ──────────────────────────────────────────────────

    def _extract_factura(self, text: str, gf: Dict[str, Any]) -> Dict[str, Any]:
        fields: Dict[str, Any] = {}

        # ── Parseo posicional sin etiqueta (OCR real FEL Guatemala) ─────────────
        _pos = _parse_fel_unlabeled(text)

        # ── Emisor ───────────────────────────────────────────────────────────────
        fields["nombre_emisor"] = (
            self._re1(_RAZON_SOCIAL, text) or _pos.get("nombre_emisor")
        )
        fields["nombre_comercial"] = (
            self._re1(_NOMBRE_COMERCIAL, text) or _pos.get("nombre_comercial")
        )
        # lugar_comercio: marca visible > razón social
        fields["lugar_comercio"] = (
            fields["nombre_comercial"] or fields["nombre_emisor"]
        )
        # proveedor: retrocompatibilidad
        fields["proveedor"] = fields["nombre_emisor"] or fields["nombre_comercial"]
        fields["nit_emisor"] = self._re1(_NIT_EMISOR, text)
        fields["direccion_emisor"] = (
            self._re1(_DIRECCION_EMISOR, text) or _pos.get("direccion_emisor")
        )
        fields["tipo_fiscal"] = (
            self._re1(_TIPO_FISCAL, text) or _pos.get("tipo_fiscal")
        )
        fields["telefono_emisor"] = self._re1(_TELEFONO_INLINE, text)
        fields["email_emisor"] = self._re1(_EMAIL_INLINE, text)

        # ── Receptor ─────────────────────────────────────────────────────────────
        # Siempre intentar la versión posicional (multilinea real) primero;
        # es más completa que _NOMBRE_RECEPTOR_INLINE que solo captura 1 línea.
        _recp_pos = _pos.get("receptor")
        _recp_re = (
            self._re1(_NOMBRE_RECEPTOR_INLINE, text)
            or self._re1(_RECEPTOR_NOMBRE, text)
        )
        if not _recp_re:
            m_ml = _RECEPTOR_MULTILINEA.search(text)
            if m_ml:
                _recp_re = _clean(m_ml.group(1).replace("\n", " "))
        if not _recp_re:
            _recp_re = self._re1(_CLIENTE_RECEPTOR, text)
        # Preferir el resultado más largo (más completo)
        if _recp_pos and _recp_re:
            fields["receptor"] = (
                _recp_pos if len(_recp_pos) >= len(_recp_re) else _recp_re
            )
        else:
            fields["receptor"] = _recp_pos or _recp_re
        fields["nit_receptor"] = self._re1(_NIT_RECEPTOR, text)
        fields["direccion_receptor"] = self._re1(_DIRECCION_RECEPTOR, text)

        # ── Certificador ─────────────────────────────────────────────────────────
        fields["certificador"] = (
            self._re1(_CERTIFICADOR_NOMBRE, text) or _pos.get("certificador")
        )
        fields["nit_certificador"] = (
            self._re1(_NIT_CERTIFICADOR, text)
            or self._re1(_CERTIF_NIT_INLINE, text)
        )

        # ── Autorización SAT ─────────────────────────────────────────────────────
        fields["autorizacion_sat"] = (
            self._re1(_AUTORIZACION_SAT_RE, text)
            or _first(gf.get("autorizacion_sat", []))
        )
        if not fields["autorizacion_sat"]:
            fields["autorizacion_sat"] = (
                self._re1(_AUTH_SAT_NEXTLINE, text)
                or self._re1(_AUTH_SAT_UUID, text)
            )

        # ── FEL metadata: serie y DTE (línea combinada o individuales) ───────────
        _m_sd = _SERIE_Y_DTE.search(text)
        _serie_comb = _clean(_m_sd.group(1)) if _m_sd else None
        _dte_comb   = _clean(_m_sd.group(2)) if _m_sd else None

        fields["serie_fel"] = (
            _first(gf.get("serie_sat", []))
            or _serie_comb
        )
        fields["numero_dte"] = (
            _first(gf.get("numero_dte", []))
            or self._re1(_NUMERO_DTE, text)
            or _dte_comb
        )

        # Fechas — soportar "Fecha y hora de ..." (FEL real) y "Fecha de ..."
        fields["fecha_emision"] = (
            self._re1(_FECHA_HORA_EMISION, text)
            or self._re1(_FECHA_EMISION, text)
        )
        fields["fecha_certificacion"] = (
            self._re1(_FECHA_HORA_CERT, text)
            or self._re1(_FECHA_CERTIFICACION, text)
        )
        fields["moneda"] = _first(gf.get("moneda", []))
        fields["total"] = self._re1(_TOTAL, text)
        fields["impuesto"] = self._re1(_IMPUESTO, text)
        fields["forma_pago"] = (
            self._re1(_FORMA_PAGO_INLINE, text)
            or _first(gf.get("forma_pago", []))
        )

        # ── Líneas de detalle ────────────────────────────────────────────────────
        _items = self._parse_fel_items(text)[:10]
        if not _items:
            _items = self._parse_fel_items_simple(text)[:10]
        if not _items:
            _items = self._parse_fel_items_q_prefix(text)[:10]
        fields["items"] = _items

        fields["consumo_detectado"] = _detect_sub_concepto(text, _items)
        if _items:
            fields["producto_servicio"] = _items[0]["descripcion"]
            fields["cantidad"]          = _items[0].get("cantidad")
            fields["precio_unitario"]   = _items[0].get("precio_unitario")
            fields["descuento"]         = _items[0].get("descuento")
            if not fields["total"]:
                fields["total"] = _items[0].get("total")
        else:
            fields["producto_servicio"] = None

        # ── Fallback NIT emisor desde campos genéricos ───────────────────────────
        if not fields["nit_emisor"] and gf.get("nit"):
            fields["nit_emisor"] = _first(gf["nit"])

        return fields

    def _extract_recibo(self, text: str, gf: Dict[str, Any]) -> Dict[str, Any]:
        gf = gf or {}
        fields: Dict[str, Any] = {}

        fields["emisor"] = (
            self._re1(_RAZON_SOCIAL, text)
            or self._re1(_NOMBRE_COMERCIAL, text)
            or self._re1(_RECIBO_EMISOR_EXPLICIT, text)
        )
        # Fallback: primer renglón sin etiqueta tras el título "RECIBO ..."
        if not fields.get("emisor"):
            _non_empty = [ln.strip() for ln in text.splitlines() if ln.strip()]
            _start = 0
            for _i, _ln in enumerate(_non_empty):
                if _RECIBO_TITLE_LINE.match(_ln):
                    _start = _i + 1
                    break
            for _ln in _non_empty[_start:_start + 4]:
                _cp = _ln.find(":")
                if (
                    (_cp < 0 or _cp > 35)
                    and not _RECIBO_EMISOR_SKIP.search(_ln)
                    and len(_ln) >= 5
                ):
                    fields["emisor"] = _ln
                    break
        fields["nit_emisor"] = (
            self._re1(_NIT_EMISOR, text)
            or _first(gf.get("nit", []))
        )
        fields["receptor"] = (
            self._re1(_RECIBO_RECEPTOR, text)
            or self._re1(_RECIBI_DE, text)
            or self._re1(_NOMBRE_RECEPTOR_INLINE, text)
        )
        fields["monto"] = (
            self._re1(_LA_CANTIDAD_DE, text)
            or self._re1(_MONTO_RECIBO, text)
            or self._re1(_TOTAL, text)
        )
        fields["moneda"] = _first(gf.get("moneda", []))
        fields["forma_pago"] = (
            self._re1(_FORMA_PAGO_INLINE, text)
            or _first(gf.get("forma_pago", []))
        )
        fields["fecha"] = (
            _first(gf.get("fecha_texto", []))
            or _first(gf.get("dates", []))
        )
        fields["referencia"] = (
            _first(gf.get("serie_dte", []))
            or self._re1(_NUMERO_RECIBO, text)
        )
        fields["concepto"] = (
            self._re1(_POR_CONCEPTO, text)
            or self._re1(_CONCEPTO, text)
        )
        fields["letras"] = self._re1(_RECIBO_LETRAS, text)
        fields["observaciones"] = self._re1(_OBSERVACIONES, text)

        return {k: v for k, v in fields.items() if v is not None}

    def _extract_contrato(self, text: str, gf: Dict[str, Any]) -> Dict[str, Any]:
        gf = gf or {}
        fields: Dict[str, Any] = {}

        fields["tipo_contrato"] = (
            self._re1(_TIPO_CONTRATO, text)
            or _detect_tipo_contrato(text)
        )
        fields["lugar"] = self._re1(_CARTA_LUGAR, text)
        fields["fecha"] = (
            _first(gf.get("fecha_texto", []))
            or _first(gf.get("dates", []))
        )
        fields["contratante"] = self._re1(_CONTRATANTE, text)
        fields["contratado"] = self._re1(_CONTRATADO, text)

        partes = self._re_all(_CONTRATO_PARTES, text)
        fields["partes"] = partes[:4] if partes else None

        fields["objeto"] = self._re1(_CONTRATO_OBJETO, text)
        fields["vigencia"] = self._re1(_CONTRATO_VIGENCIA, text)
        fields["fecha_inicio"] = self._re1(_CONTRATO_FECHA_INICIO, text)
        fields["fecha_fin"] = self._re1(_CONTRATO_FECHA_FIN, text)
        fields["monto"] = self._re1(_CONTRATO_MONTO, text)
        fields["forma_pago"] = self._re1(_FORMA_PAGO_INLINE, text)
        fields["representante"] = self._re1(_CONTRATO_REPRESENTANTE, text)
        fields["firmante"] = self._re1(_CONTRATO_FIRMANTE, text)

        nits = self._re_all(_NIT_GENERIC, text)
        fields["nit_relacionado"] = ", ".join(nits[:3]) if nits else None

        return {k: v for k, v in fields.items() if v is not None}

    def _extract_constancia(self, text: str, gf: Dict[str, Any]) -> Dict[str, Any]:
        gf = gf or {}
        fields: Dict[str, Any] = {}

        fields["tipo_constancia"] = (
            self._re1(_TIPO_CONSTANCIA, text)
            or _detect_tipo_constancia(text)
        )
        fields["lugar"] = self._re1(_CARTA_LUGAR, text)
        fields["fecha"] = (
            _first(gf.get("fecha_texto", []))
            or _first(gf.get("dates", []))
        )
        fields["entidad_emisora"] = self._re1(_CONSTANCIA_EMPRESA, text)
        fields["nombre"] = (
            self._re1(_CONSTANCIA_NOMBRE, text)
            or self._re1(_CONSTANCIA_NOMBRE_HACECONSTAR, text)
        )
        fields["cargo"] = self._re1(_CONSTANCIA_CARGO, text)
        fields["motivo"] = self._re1(_CONSTANCIA_MOTIVO, text)
        fields["firmante"] = self._re1(_CONSTANCIA_FIRMANTE, text)
        fields["cargo_firmante"] = self._re1(_CONSTANCIA_CARGO_FIRMANTE, text)

        return {k: v for k, v in fields.items() if v is not None}

    def _extract_carta_formal(self, text: str, gf: Dict[str, Any]) -> Dict[str, Any]:
        gf = gf or {}
        fields: Dict[str, Any] = {}

        fields["lugar"] = self._re1(_CARTA_LUGAR, text)
        fields["fecha"] = (
            _first(gf.get("fecha_texto", []))
            or _first(gf.get("dates", []))
        )
        # Buscar destinatario en las primeras 15 líneas para cubrir bloques DESTINATARIO tardíos
        _header = "\n".join(text.splitlines()[:15])
        _dest = (
            self._re1(_CARTA_DESTINATARIO_INLINE, _header)
            or self._re1(_CARTA_DESTINATARIO_NEXTLINE, _header)
        )
        if _dest and _CARTA_BODY_STARTERS.match(_dest.strip()):
            _dest = None
        fields["destinatario"] = _dest
        fields["asunto"] = (
            self._re1(_CARTA_ASUNTO, text)
            or self._re1(_CARTA_ASUNTO_NEXTLINE, text)
        )
        fields["remitente"] = self._re1(_CARTA_REMITENTE, text)
        fields["cargo"] = (
            self._re1(_CARTA_CARGO_EXPLICIT, text)
            or self._re1(_CARTA_CARGO_KEYWORDS, text)
        )
        fields["email"] = _first(gf.get("emails", []))
        fields["telefono"] = _first(gf.get("phones", []))
        fields["url"] = _first(gf.get("urls", []))

        # Resumen del cuerpo: primer párrafo no vacío tras el saludo
        _lines = text.splitlines()
        _body_lines = []
        _past_header = False
        for ln in _lines:
            ln_s = ln.strip()
            if not _past_header and any(
                kw in ln_s.lower() for kw in ("estimado", "por medio", "me permito", "en atención")
            ):
                _past_header = True
            if _past_header and len(ln_s) > 20:
                _body_lines.append(ln_s)
            if len(_body_lines) >= 2:
                break
        if _body_lines:
            fields["resumen_cuerpo"] = " ".join(_body_lines)[:200]

        return {k: v for k, v in fields.items() if v is not None}

    def _extract_identificacion(self, text: str, gf: Dict[str, Any]) -> Dict[str, Any]:
        fields: Dict[str, Any] = {}

        fields["nombre"] = self._re1(_DPI_NOMBRE, text)
        fields["cui"] = (
            self._re1(_DPI_CUI, text)
            or _first(gf.get("dpi", []))
        )
        fields["numero_licencia"] = self._re1(_LICENCIA_NUM, text)
        fields["numero_pasaporte"] = self._re1(_PASAPORTE_NUM, text)
        fields["numero_carne"] = self._re1(_CARNE_NUM, text)
        fields["clase_licencia"] = self._re1(_LICENCIA_CLASE, text)
        fields["pais"] = self._re1(_ID_PAIS, text)
        fields["fecha_nacimiento"] = self._re1(_FECHA_NACIMIENTO, text)
        fields["fecha_vencimiento"] = self._re1(_FECHA_VENCIMIENTO, text)
        fields["genero"] = self._re1(_ID_GENERO, text)
        fields["direccion"] = self._re1(_ID_DIRECCION, text)

        m_emisor = _ID_ENTIDAD_EMISORA.search(text)
        fields["entidad_emisora"] = m_emisor.group(0) if m_emisor else None

        fields["nacionalidad"] = self._re1(_ID_NACIONALIDAD, text)

        # Subtipo auto-detectado
        if fields.get("cui"):
            fields["subtipo"] = "DPI / CUI"
        elif fields.get("numero_licencia"):
            fields["subtipo"] = "Licencia de conducir"
        elif fields.get("numero_pasaporte"):
            fields["subtipo"] = "Pasaporte"
        elif fields.get("numero_carne"):
            fields["subtipo"] = "Carné"
        else:
            fields["subtipo"] = "No determinado"

        return {k: v for k, v in fields.items() if v is not None}

    def _extract_otro(self, text: str, gf: Dict[str, Any]) -> Dict[str, Any]:
        gf = gf or {}
        fields: Dict[str, Any] = {}

        first_line = next(
            (ln.strip() for ln in text.splitlines() if len(ln.strip()) > 10),
            None,
        )
        if first_line:
            fields["resumen"] = first_line[:120]

        fechas = list(dict.fromkeys(
            (gf.get("fecha_texto") or []) + (gf.get("dates") or [])
        ))
        if fechas:
            fields["fechas"] = ", ".join(fechas[:5])

        valores = gf.get("currency") or []
        if valores:
            fields["valores"] = ", ".join(str(v) for v in valores[:5])

        nits = gf.get("nit") or []
        if nits:
            fields["nits"] = ", ".join(nits[:3])

        codigos = list(dict.fromkeys(
            (gf.get("serie_sat") or []) + (gf.get("serie_dte") or [])
        ))
        if codigos:
            fields["codigos"] = ", ".join(codigos[:3])

        emails = gf.get("emails") or []
        if emails:
            fields["emails"] = ", ".join(str(e) for e in emails[:3])

        telefonos = gf.get("phones") or []
        if telefonos:
            fields["telefonos"] = ", ".join(str(t) for t in telefonos[:3])

        urls = gf.get("urls") or []
        if urls:
            fields["urls"] = ", ".join(str(u) for u in urls[:3])

        dpis = gf.get("dpi") or []
        if dpis:
            fields["dpis"] = ", ".join(dpis[:3])

        return fields

    # ── Tabla FEL ─────────────────────────────────────────────────────────────

    def _parse_fel_items(self, text: str) -> List[Dict[str, str]]:
        """
        Extrae líneas de detalle de la tabla FEL (Bien/Servicio).

        Busca la sección DETALLE y luego parsea líneas con columnas
        separadas por 2+ espacios: descripción, cantidad, precio_unit,
        descuento, total.
        """
        # Intentar encontrar sección de detalle
        m = _FEL_DETALLE_SECTION.search(text)
        if m:
            section = text[m.start():]
        else:
            section = text

        items = []
        for m in _FEL_ITEM_LINE.finditer(section):
            desc, qty, price, discount, total = (
                _clean(m.group(1)),
                _clean(m.group(2)),
                _clean(m.group(3)),
                _clean(m.group(4)),
                _clean(m.group(5)),
            )
            if desc and qty and total:
                items.append({
                    "descripcion": desc,
                    "cantidad": qty,
                    "precio_unitario": price,
                    "descuento": discount,
                    "total": total,
                })
        return items

    def _parse_fel_items_simple(self, text: str) -> List[Dict[str, str]]:
        """
        Extrae ítems FEL en formato: '1 Bien 1 Desayuno 40.00 0.00 40.00'
        Grupos capturados: cantidad, descripcion, precio_unitario, descuento, total
        """
        items = []
        for m in _FEL_ITEM_SIMPLE_LINE.finditer(text):
            qty   = _clean(m.group(1))
            desc  = _clean(m.group(2))
            price = _clean(m.group(3))
            disc  = _clean(m.group(4))
            total = _clean(m.group(5))
            if desc and total:
                items.append({
                    "descripcion":     desc,
                    "cantidad":        qty,
                    "precio_unitario": price,
                    "descuento":       disc,
                    "total":           total,
                })
        return items

    def _parse_fel_items_q_prefix(self, text: str) -> List[Dict[str, str]]:
        """
        Extrae ítems formato: 'Descripción  1  Q 6,500.00  Q 6,500.00'
        Usado cuando las columnas de precio llevan prefijo Q (sin columna de descuento).
        """
        m_sec = _FEL_DETALLE_SECTION.search(text)
        section = text[m_sec.start():] if m_sec else text

        _HEADER_SKIP = re.compile(
            r'^(?:Descripci[oó]n|Cantidad|Precio|Subtotal|Cant\.|P\.\s*Unitario)',
            re.IGNORECASE,
        )
        items = []
        for m in _FEL_ITEM_Q_LINE.finditer(section):
            desc = _clean(m.group(1))
            if not desc or _HEADER_SKIP.match(desc):
                continue
            qty   = _clean(m.group(2))
            price = _clean(m.group(3))
            total = _clean(m.group(4))
            if desc and total:
                items.append({
                    "descripcion":     desc,
                    "cantidad":        qty,
                    "precio_unitario": price,
                    "descuento":       None,
                    "total":           total,
                })
        return items
