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
    r'|cl[aá]usula\s+(?:primera|1[aª]?)[:\s]+objeto)\s*:?\s*([^\n\r]{5,200})',
    re.IGNORECASE,
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
_CARTA_DESTINATARIO = re.compile(
    r'(?:Se[ñn]or(?:es)?|Doctor(?:a)?|Licenciado(?:a)?|Ingeniero(?:a)?|Para)'
    r'\s*:?\s*\n\s*([^\n\r]{5,80})',
    re.IGNORECASE,
)
_CARTA_REMITENTE = re.compile(
    r'(?:Atentamente|Firma|Suscribe|De\s+usted)\s*[:,]?\s*\n'
    r'(?:[^\n\r]*\n){0,3}?([A-ZÁÉÍÓÚÑ][^\n\r]{5,60})',
    re.IGNORECASE,
)
_CARTA_ASUNTO = re.compile(
    r'(?:ASUNTO|REF(?:ERENCIA)?|MOTIVO)\s*:?\s*([^\n\r]{5,120})',
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

# ── Patrones adicionales para recibo, contrato, constancia, carta, id ─────────

# Recibo: receptor / cliente
_RECIBO_RECEPTOR = re.compile(
    r'(?:Cliente|Receptor|Pagador|Beneficiario)\s*:?\s*([^\n\r]{3,80})',
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
    r'(?:Carn[eé](?:\s+(?:de\s+)?\w+)?|Colegiado|Carnet)\s*:?\s*([A-Z0-9\-]{3,20})',
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

        # ── Emisor ───────────────────────────────────────────────────────────────
        fields["nombre_emisor"] = self._re1(_RAZON_SOCIAL, text)
        fields["nombre_comercial"] = self._re1(_NOMBRE_COMERCIAL, text)
        # lugar_comercio: marca visible > razón social
        fields["lugar_comercio"] = (
            fields["nombre_comercial"] or fields["nombre_emisor"]
        )
        # proveedor: retrocompatibilidad
        fields["proveedor"] = fields["nombre_emisor"] or fields["nombre_comercial"]
        fields["nit_emisor"] = self._re1(_NIT_EMISOR, text)
        fields["direccion_emisor"] = self._re1(_DIRECCION_EMISOR, text)
        fields["tipo_fiscal"] = self._re1(_TIPO_FISCAL, text)
        fields["telefono_emisor"] = self._re1(_TELEFONO_INLINE, text)
        fields["email_emisor"] = self._re1(_EMAIL_INLINE, text)

        # ── Receptor ─────────────────────────────────────────────────────────────
        fields["receptor"] = (
            self._re1(_NOMBRE_RECEPTOR_INLINE, text)
            or self._re1(_RECEPTOR_NOMBRE, text)
        )
        fields["nit_receptor"] = self._re1(_NIT_RECEPTOR, text)
        fields["direccion_receptor"] = self._re1(_DIRECCION_RECEPTOR, text)

        # ── Certificador ─────────────────────────────────────────────────────────
        fields["certificador"] = self._re1(_CERTIFICADOR_NOMBRE, text)
        fields["nit_certificador"] = (
            self._re1(_NIT_CERTIFICADOR, text)
            or self._re1(_CERTIF_NIT_INLINE, text)
        )

        # ── Autorización SAT ─────────────────────────────────────────────────────
        fields["autorizacion_sat"] = (
            self._re1(_AUTORIZACION_SAT_RE, text)
            or _first(gf.get("autorizacion_sat", []))
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
            or next(
                (ln.strip() for ln in text.splitlines() if len(ln.strip()) > 5),
                None,
            )
        )
        fields["nit_emisor"] = (
            self._re1(_NIT_EMISOR, text)
            or _first(gf.get("nit", []))
        )
        fields["receptor"] = (
            self._re1(_RECIBO_RECEPTOR, text)
            or self._re1(_NOMBRE_RECEPTOR_INLINE, text)
        )
        fields["monto"] = (
            self._re1(_MONTO_RECIBO, text)
            or self._re1(_TOTAL, text)
        )
        fields["forma_pago"] = _first(gf.get("forma_pago", []))
        fields["fecha"] = (
            _first(gf.get("fecha_texto", []))
            or _first(gf.get("dates", []))
        )
        fields["referencia"] = (
            _first(gf.get("serie_dte", []))
            or self._re1(_NUMERO_RECIBO, text)
        )
        fields["concepto"] = self._re1(_CONCEPTO, text)
        fields["letras"] = self._re1(_RECIBO_LETRAS, text)

        return {k: v for k, v in fields.items() if v is not None}

    def _extract_contrato(self, text: str, gf: Dict[str, Any]) -> Dict[str, Any]:
        gf = gf or {}
        fields: Dict[str, Any] = {}

        fields["tipo_contrato"] = self._re1(_TIPO_CONTRATO, text)
        fields["lugar"] = self._re1(_CARTA_LUGAR, text)

        partes = self._re_all(_CONTRATO_PARTES, text)
        fields["partes"] = partes[:4] if partes else None

        fields["objeto"] = self._re1(_CONTRATO_OBJETO, text)
        fields["vigencia"] = self._re1(_CONTRATO_VIGENCIA, text)
        fields["monto"] = self._re1(_CONTRATO_MONTO, text)
        fields["representante"] = self._re1(_CONTRATO_REPRESENTANTE, text)

        nits = self._re_all(_NIT_GENERIC, text)
        fields["nit_relacionado"] = ", ".join(nits[:3]) if nits else None

        fields["fecha"] = (
            _first(gf.get("fecha_texto", []))
            or _first(gf.get("dates", []))
        )

        return {k: v for k, v in fields.items() if v is not None}

    def _extract_constancia(self, text: str, gf: Dict[str, Any]) -> Dict[str, Any]:
        gf = gf or {}
        fields: Dict[str, Any] = {}

        fields["tipo_constancia"] = self._re1(_TIPO_CONSTANCIA, text)
        fields["lugar"] = self._re1(_CARTA_LUGAR, text)
        fields["nombre"] = self._re1(_CONSTANCIA_NOMBRE, text)
        fields["cargo"] = self._re1(_CONSTANCIA_CARGO, text)
        fields["entidad_emisora"] = self._re1(_CONSTANCIA_EMPRESA, text)
        fields["motivo"] = self._re1(_CONSTANCIA_MOTIVO, text)
        fields["fecha"] = (
            _first(gf.get("fecha_texto", []))
            or _first(gf.get("dates", []))
        )

        return {k: v for k, v in fields.items() if v is not None}

    def _extract_carta_formal(self, text: str, gf: Dict[str, Any]) -> Dict[str, Any]:
        gf = gf or {}
        fields: Dict[str, Any] = {}

        fields["lugar"] = self._re1(_CARTA_LUGAR, text)
        fields["fecha"] = (
            _first(gf.get("fecha_texto", []))
            or _first(gf.get("dates", []))
        )
        fields["destinatario"] = self._re1(_CARTA_DESTINATARIO, text)
        fields["asunto"] = self._re1(_CARTA_ASUNTO, text)
        fields["remitente"] = self._re1(_CARTA_REMITENTE, text)
        fields["cargo"] = (
            self._re1(_CARTA_CARGO_EXPLICIT, text)
            or self._re1(_CARTA_CARGO_KEYWORDS, text)
        )
        fields["email"] = _first(gf.get("emails", []))
        fields["telefono"] = _first(gf.get("phones", []))
        fields["url"] = _first(gf.get("urls", []))

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
