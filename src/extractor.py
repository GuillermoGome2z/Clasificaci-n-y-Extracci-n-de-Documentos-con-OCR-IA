"""Módulo de extracción de datos con regex para documentos guatemaltecos."""

import logging
import re
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# Meses en español para fechas textuales
_MESES = (
    r'enero|febrero|marzo|abril|mayo|junio|julio|agosto'
    r'|septiembre|octubre|noviembre|diciembre'
)
_MESES_CORTO = r'ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic'


class DataExtractor:
    """Extrae información estructurada del texto OCR para documentos guatemaltecos."""

    def __init__(self) -> None:
        """Inicializa los patrones de regex."""
        self.patterns: Dict[str, str] = {
            # ── Email ────────────────────────────────────────────────────
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',

            # ── Teléfono Guatemala ────────────────────────────────────────
            # 8 dígitos con prefijo 2-5 (landlines 2xxx, móviles 3-5xxx)
            # Formato XXXX-XXXX. Lookbehind/ahead evita capturar NITs y DPIs.
            # Soporta +502 opcional (código de país).
            "phone": r'(?:\+502\s*)?(?<!\d)[2-5]\d{3}-\d{4}(?![-\d])',

            # ── Fechas numéricas ──────────────────────────────────────────
            "date": r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',

            # ── URL ───────────────────────────────────────────────────────
            "url": (
                r'https?://(?:www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}'
                r'\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_+.~#?&/=]*)'
            ),

            # ── Moneda guatemalteca y otras ───────────────────────────────
            "currency": (
                r'Q\s?[\d,]+(?:\.\d{2})?'
                r'|GTQ\s?[\d,]+(?:\.\d{2})?'
                r'|\$\s?[\d,]+(?:\.\d{2})?'
                r'|€\s?[\d,]+(?:\.\d{2})?'
                r'|£\s?[\d,]+(?:\.\d{2})?'
                r'|\b(?:USD|EUR|MXN)\s?[\d,]+(?:\.\d{2})?'
            ),

            # ── NIT guatemalteco (interno: con y sin contexto) ────────────
            # Formato: 1-8 dígitos + guión + 1 dígito verificador
            # Ejemplos: 5356261-9   1234567-8   98765432-1
            "_nit_ctx": r'(?:NIT|N\.I\.T\.?)\s*:?\s*(\d{1,8}-\d)\b',
            "_nit_raw": r'\b(\d{6,8}-\d)\b',

            # ── DPI/CUI guatemalteco ──────────────────────────────────────
            # 13 dígitos: XXXX XXXXX XXXX  o  XXXX-XXXXX-XXXX
            # Lookbehind/ahead evitan falsos positivos con números adyacentes.
            "dpi": r'(?<!\d)\d{4}[\s-]\d{5}[\s-]\d{4}(?!\d)',

            # ── Serie DTE (Documento Tributario Electrónico SAT) ──────────
            # FAC-2026-0001  REC-00015  CTR-2026-0015  CONST-2026-0001
            "serie_dte": (
                r'\b(?:FAC|REC|NCR|CTR|DTE|CONST|CF|COM|NDC|NCC)'
                r'-(?:\d{4}-\d{4,6}|\d{4,6})\b'
            ),

            # ── Fechas en español ─────────────────────────────────────────
            # Largo:      "30 de abril de 2026"
            # Abreviado:  "28-abr-2026"
            "fecha_texto": (
                r'\b\d{1,2}\s+de\s+(?:' + _MESES + r')\s+de\s+\d{4}\b'
                r'|\b\d{1,2}[-/](?:' + _MESES_CORTO + r')[-/.]?\d{2,4}\b'
            ),

            # ── Forma de pago ─────────────────────────────────────────────
            "forma_pago": (
                r'\b(?:EFECTIVO'
                r'|CHEQUE'
                r'|TRANSFERENCIA(?:\s+BANCARIA)?'
                r'|TARJETA(?:\s+DE\s+(?:CR[EÉ]DITO|D[EÉ]BITO))?'
                r'|DEP[OÓ]SITO(?:\s+BANCARIO)?)\b'
            ),

            # ── Montos rotulados sin símbolo (TOTAL, IVA, Subtotal…) ──────
            # Captura el número que sigue a la etiqueta tributaria.
            "_monto_kw": (
                r'(?:TOTAL|IVA|Subtotal|Descuento|Monto)\s*:?\s*'
                r'([\d,]+(?:\.\d{2})?)'
            ),
        }

    # ─────────────────────────────────────────────────────────────────────
    # Métodos de extracción individuales
    # ─────────────────────────────────────────────────────────────────────

    def extract_emails(self, text: str) -> List[str]:
        """Extrae correos electrónicos del texto."""
        return list(set(re.findall(self.patterns["email"], text)))

    def extract_phones(self, text: str) -> List[str]:
        """Extrae teléfonos guatemaltecos (XXXX-XXXX, prefijo 2-5)."""
        matches = re.findall(self.patterns["phone"], text)
        return list({m.strip() for m in matches if m.strip()})

    def extract_dates(self, text: str) -> List[str]:
        """Extrae fechas en formato numérico (DD/MM/YYYY, MM-DD-YYYY, etc.)."""
        return list(set(re.findall(self.patterns["date"], text)))

    def extract_urls(self, text: str) -> List[str]:
        """Extrae URLs del texto."""
        return list(set(re.findall(self.patterns["url"], text)))

    def extract_currency(self, text: str) -> List[str]:
        """Extrae valores monetarios (Q, GTQ, $, €, £, códigos ISO)."""
        # Montos con símbolo
        with_symbol = re.findall(self.patterns["currency"], text)
        # Montos sin símbolo cerca de palabras clave tributarias
        labelled = re.findall(self.patterns["_monto_kw"], text, re.IGNORECASE)
        return list(set(with_symbol + labelled))

    def extract_nit(self, text: str) -> List[str]:
        """Extrae NIT guatemalteco (1-8 dígitos + guión + 1 verificador)."""
        # Con contexto "NIT:" — alta precisión
        with_ctx = re.findall(self.patterns["_nit_ctx"], text, re.IGNORECASE)
        # Standalone 6-8 dígitos + guión + 1 — cobertura adicional
        standalone = re.findall(self.patterns["_nit_raw"], text)
        return list(set(with_ctx + standalone))

    def extract_dpi(self, text: str) -> List[str]:
        """Extrae DPI/CUI guatemalteco (13 dígitos: XXXX XXXXX XXXX)."""
        return list(set(re.findall(self.patterns["dpi"], text)))

    def extract_serie_dte(self, text: str) -> List[str]:
        """Extrae series DTE/SAT guatemaltecas (FAC-XXXX-XXXX, REC-XXXXX…)."""
        return list(set(re.findall(self.patterns["serie_dte"], text, re.IGNORECASE)))

    def extract_fecha_texto(self, text: str) -> List[str]:
        """Extrae fechas escritas en español (largo y abreviado)."""
        return list(set(re.findall(self.patterns["fecha_texto"], text, re.IGNORECASE)))

    def extract_forma_pago(self, text: str) -> List[str]:
        """Extrae formas de pago (EFECTIVO, CHEQUE, TRANSFERENCIA…)."""
        matches = re.findall(self.patterns["forma_pago"], text, re.IGNORECASE)
        return list({m.upper() for m in matches})

    def extract_custom_pattern(self, text: str, pattern: str) -> List[str]:
        """Extrae datos usando un patrón regex personalizado."""
        try:
            return list(set(re.findall(pattern, text)))
        except re.error as e:
            return [f"Error en patrón: {str(e)}"]

    # ─────────────────────────────────────────────────────────────────────
    # Orquestador principal
    # ─────────────────────────────────────────────────────────────────────

    def extract_all(self, text: str) -> Dict[str, Any]:
        """
        Extrae todos los tipos de datos del texto.

        Returns:
            Diccionario con claves: emails, phones, dates, urls, currency,
            nit, dpi, serie_dte, fecha_texto, forma_pago.
        """
        try:
            logger.debug(
                "Iniciando extracción GT (texto: %d caracteres)", len(text)
            )
            result: Dict[str, Any] = {
                "emails":      self.extract_emails(text),
                "phones":      self.extract_phones(text),
                "dates":       self.extract_dates(text),
                "urls":        self.extract_urls(text),
                "currency":    self.extract_currency(text),
                "nit":         self.extract_nit(text),
                "dpi":         self.extract_dpi(text),
                "serie_dte":   self.extract_serie_dte(text),
                "fecha_texto": self.extract_fecha_texto(text),
                "forma_pago":  self.extract_forma_pago(text),
            }
            total = sum(len(v) for v in result.values())
            logger.info("Extracción completada: %d items extraídos", total)
            return result
        except (ValueError, TypeError, AttributeError, re.error) as e:
            logger.error("Error en extracción: %s", e)
            return {
                "emails": [], "phones": [], "dates": [], "urls": [],
                "currency": [], "nit": [], "dpi": [], "serie_dte": [],
                "fecha_texto": [], "forma_pago": [], "error": str(e),
            }

    # ─────────────────────────────────────────────────────────────────────
    # Utilidades de texto
    # ─────────────────────────────────────────────────────────────────────

    def extract_lines(self, text: str) -> List[str]:
        """Extrae y limpia líneas no vacías del texto."""
        try:
            return [line.strip() for line in text.split('\n') if line.strip()]
        except (ValueError, AttributeError) as e:
            logger.error("Error extrayendo líneas: %s", e)
            return []

    def extract_tables(self, text: str) -> List[List[str]]:
        """Intenta extraer tablas detectando separadores de columna."""
        try:
            table = []
            for line in self.extract_lines(text):
                cells = [c.strip() for c in re.split(r'\s{2,}', line)]
                if len(cells) > 1:
                    table.append(cells)
            return table
        except (ValueError, AttributeError) as e:
            logger.error("Error extrayendo tablas: %s", e)
            return []
