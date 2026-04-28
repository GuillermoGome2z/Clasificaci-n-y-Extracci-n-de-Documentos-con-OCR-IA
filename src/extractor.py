"""Módulo de extracción de datos con regex y patrones."""

import logging
import re
from typing import List, Dict, Any

logger = logging.getLogger(__name__)



class DataExtractor:
    """Extrae información estructurada del texto OCR."""

    def __init__(self):
        """Inicializa los patrones de regex."""
        self.patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b(?:\+?1[-.\.\s])?\(?([0-9]{3})\)?[-.\.\s]?([0-9]{3})[-.\.\s]?([0-9]{4})\b',
            "date": r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',
            "url": (
                r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}'
                r'\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)'
            ),
            "currency": r'\$\s?[\d,]+\.?\d{0,2}|\b(?:USD|EUR|MXN)\s?[\d,]+\.?\d{0,2}',
            "dni": r'\b[0-9]{1,2}\.?[0-9]{3}\.?[0-9]{3}(?:-[A-Z])?\b',
            "rfc": r'\b[A-ZÑ&]{3,4}\d{6}(?:[A-Z0-9]{3})?\b',
        }

    def extract_emails(self, text: str) -> List[str]:
        """Extrae emails del texto."""
        return list(set(re.findall(self.patterns["email"], text)))

    def extract_phones(self, text: str) -> List[str]:
        """Extrae números telefónicos del texto."""
        matches = re.findall(self.patterns["phone"], text)
        return [f"({m[0]}) {m[1]}-{m[2]}" for m in matches]

    def extract_dates(self, text: str) -> List[str]:
        """Extrae fechas del texto."""
        return list(set(re.findall(self.patterns["date"], text)))

    def extract_urls(self, text: str) -> List[str]:
        """Extrae URLs del texto."""
        return list(set(re.findall(self.patterns["url"], text)))

    def extract_currency(self, text: str) -> List[str]:
        """Extrae valores en moneda del texto."""
        return list(set(re.findall(self.patterns["currency"], text)))

    def extract_dni(self, text: str) -> List[str]:
        """Extrae DNI/NIE del texto."""
        return list(set(re.findall(self.patterns["dni"], text)))

    def extract_rfc(self, text: str) -> List[str]:
        """Extrae RFC (México) del texto."""
        return list(set(re.findall(self.patterns["rfc"], text)))

    def extract_custom_pattern(self, text: str, pattern: str) -> List[str]:
        """
        Extrae datos usando un patrón regex personalizado.

        Args:
            text: Texto a procesar
            pattern: Patrón regex

        Returns:
            Lista de coincidencias
        """
        try:
            return list(set(re.findall(pattern, text)))
        except re.error as e:
            return [f"Error en patrón: {str(e)}"]

    def extract_all(self, text: str) -> Dict[str, Any]:
        """
        Extrae todos los tipos de datos del texto.

        Args:
            text: Texto a procesar

        Returns:
            Diccionario con todas las extracciones
        """
        try:
            logger.debug("Iniciando extracción de todos los datos (texto: %d caracteres)", len(text))
            result = {
                "emails": self.extract_emails(text),
                "phones": self.extract_phones(text),
                "dates": self.extract_dates(text),
                "urls": self.extract_urls(text),
                "currency": self.extract_currency(text),
                "dni": self.extract_dni(text),
                "rfc": self.extract_rfc(text),
            }
            total_items = sum(len(v) if isinstance(v, list) else 1 for v in result.values())
            logger.info("Extracción completada: %d items extraídos", total_items)
            return result
        except Exception as e:
            logger.error("Error en extracción: %s", e)
            return {
                "emails": [],
                "phones": [],
                "dates": [],
                "urls": [],
                "currency": [],
                "dni": [],
                "rfc": [],
                "error": str(e)
            }

    def extract_lines(self, text: str) -> List[str]:
        """
        Limpia y extrae líneas significativas del texto.

        Args:
            text: Texto a procesar

        Returns:
            Lista de líneas sin espacios en blanco
        """
        try:
            logger.debug("Extrayendo líneas del texto")
            lines = text.split('\n')
            cleaned_lines = [line.strip() for line in lines if line.strip()]
            logger.debug("Líneas extraídas: %d", len(cleaned_lines))
            return cleaned_lines
        except Exception as e:
            logger.error("Error extrayendo líneas: %s", e)
            return []

    def extract_tables(self, text: str) -> List[List[str]]:
        """
        Intenta extraer tablas del texto.

        Args:
            text: Texto con formato de tabla

        Returns:
            Lista de filas (cada fila es una lista de celdas)
        """
        try:
            logger.debug("Extrayendo tablas del texto")
            lines = self.extract_lines(text)
            table = []

            for line in lines:
                # Dividir por espacios múltiples (posibles separadores de columna)
                cells = [cell.strip() for cell in re.split(r'\s{2,}', line)]
                if len(cells) > 1:
                    table.append(cells)

            logger.debug("Tablas extraídas: %d filas", len(table))
            return table
        except Exception as e:
            logger.error("Error extrayendo tablas: %s", e)
            return []
