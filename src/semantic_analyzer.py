"""Módulo de análisis semántico del contenido de documentos OCR."""

import logging
import re
import unicodedata
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ── Utilidad de normalización ─────────────────────────────────────────────────

def _normalize(text: str) -> str:
    """Convierte a minúsculas y elimina diacríticos para comparación robusta."""
    nfkd = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


# ── Keywords por categoría de gasto (facturas / recibos) ─────────────────────
# Cada entrada: (keyword_normalizada, peso)
# peso 2 → indicador específico o dominante
# peso 1 → indicador genérico o ambiguo (necesita acompañantes)

_FACTURA_RULES: Dict[str, List[tuple]] = {
    "Alimentación": [
        ("restaurante", 2), ("comida", 2), ("desayuno", 2), ("almuerzo", 2),
        ("cena", 2), ("menu", 2), ("pizza", 2), ("hamburguesa", 2),
        ("mariscos", 2), ("buffet", 2), ("cafeteria", 2), ("platillo", 2),
        ("pupusa", 2), ("churrasco", 2), ("antojitos", 2), ("tacos", 2),
        ("alimentos", 1), ("bebida", 1), ("refresco", 1), ("tortilla", 1),
        ("food", 1), ("snack", 2),
    ],
    "Hospedaje": [
        ("hotel", 2), ("hospedaje", 2), ("habitacion", 2), ("suite", 2),
        ("alojamiento", 2), ("check-in", 2), ("check-out", 2), ("motel", 2),
        ("posada", 2), ("hostal", 2), ("resort", 2), ("huesped", 2),
        ("huespedes", 2), ("room", 2), ("noche de estadia", 2),
        ("pension", 1), ("cuarto", 1), ("noche", 1),
    ],
    "Transporte": [
        ("taxi", 2), ("uber", 2), ("transporte", 2), ("pasaje", 2),
        ("flete", 2), ("mototaxi", 2), ("autobus", 2), ("traslado", 2),
        ("servicio de transporte", 2), ("vuelo", 2), ("pasajes aereos", 2),
        ("aerolinea", 2), ("delivery", 1), ("envio", 1),
        ("bus", 1), ("ruta", 1), ("boleto", 1), ("viaje", 1),
    ],
    "Combustible": [
        ("gasolina", 2), ("diesel", 2), ("combustible", 2), ("litros", 2),
        ("galon", 2), ("gasolinera", 2), ("bunker", 2),
        ("estacion de servicio", 2), ("petroleo", 2), ("lubricante", 2),
        ("aceite de motor", 2), ("nafta", 2),
    ],
    "Salud": [
        ("medico", 2), ("medicina", 2), ("farmacia", 2), ("clinica", 2),
        ("hospital", 2), ("laboratorio", 2), ("medicamento", 2),
        ("tratamiento", 2), ("doctor", 2), ("odontologia", 2), ("dentista", 2),
        ("dental", 2), ("rayos x", 2), ("analisis clinico", 2), ("cirugia", 2),
        ("optica", 2), ("atencion medica", 2), ("consulta medica", 2),
        ("examen medico", 2), ("receta", 2),
        ("salud", 1), ("consulta", 1), ("examen", 1),
    ],
    "Educación": [
        ("matricula", 2), ("colegiatura", 2), ("universidad", 2), ("colegio", 2),
        ("escuela", 2), ("academia", 2), ("inscripcion", 2), ("tutoria", 2),
        ("capacitacion", 2), ("seminario", 2), ("diplomado", 2), ("posgrado", 2),
        ("pension escolar", 2),
        ("educacion", 1), ("curso", 1), ("taller", 1),
        ("certificacion", 1), ("alumno", 1), ("estudiante", 1),
    ],
    "Servicios": [
        ("electricidad", 2), ("agua potable", 2), ("internet", 2),
        ("energia electrica", 2), ("servicio basico", 2), ("vigilancia", 2),
        ("contabilidad", 2), ("asesoria", 2), ("consultoria", 2),
        ("servicio profesional", 2), ("honorarios", 2), ("enel", 2),
        ("hosting", 2), ("dominio", 2),
        ("limpieza", 1), ("seguridad", 1), ("telefono", 1),
        ("cable", 1), ("luz", 1), ("claro", 1), ("tigo", 1),
    ],
    "Compras": [
        ("mercaderia", 2), ("inventario", 2), ("mercancia", 2),
        ("ferreteria", 2), ("electrodomestico", 2), ("ropa", 2), ("calzado", 2),
        ("mueble", 2), ("papeleria", 2), ("computadora", 2), ("celular", 2),
        ("producto", 1), ("articulo", 1), ("bien", 1), ("unidad", 1),
        ("cantidad", 1), ("accesorio", 1), ("equipo", 1), ("libreria", 1),
        ("tecnologia", 1),
    ],
    "Mantenimiento": [
        ("reparacion", 2), ("mantenimiento", 2), ("repuesto", 2),
        ("servicio tecnico", 2), ("plomeria", 2), ("electricista", 2),
        ("albanileria", 2), ("carpinteria", 2), ("mecanico", 2),
        ("taller mecanico", 2), ("refaccion", 2), ("fumigacion", 2),
        ("impermeabilizacion", 2), ("soldadura", 2),
        ("instalacion", 1), ("pintura", 1), ("arreglo", 1),
    ],
}

# ── Keywords por subtipo de identificación ────────────────────────────────────

_IDENTIFICACION_RULES: Dict[str, List[tuple]] = {
    "DPI": [
        ("documento personal de identificacion", 2),
        ("dpi", 2), ("cui", 2),
        ("registro nacional de las personas", 2), ("renap", 2),
        ("codigo unico de identificacion", 2), ("cedula de vecindad", 2),
    ],
    "Licencia de conducir": [
        ("licencia de conducir", 2), ("licencia para conducir", 2),
        ("motorista", 2), ("departamento de transito", 2),
        ("licencia de manejo", 2), ("categoria de licencia", 2),
        ("clase de licencia", 2),
        ("conductor", 1), ("conducir", 1),
    ],
    "Pasaporte": [
        ("pasaporte", 2), ("passport", 2), ("documento de viaje", 2),
        ("ministerio de relaciones exteriores", 2), ("visado", 2),
        ("nationality", 2),
        ("nacionalidad", 1), ("visa", 1), ("lugar de nacimiento", 1),
    ],
    "Carné": [
        ("carne de identificacion", 2), ("carnet", 2),
        ("carne estudiantil", 2), ("carne universitario", 2),
        ("carne de trabajo", 2), ("numero de empleado", 2),
        ("codigo de empleado", 2), ("credencial", 2), ("carne", 2),
        ("empleado", 1), ("asociado", 1), ("miembro", 1),
    ],
}

# Clases de documento que activan el análisis semántico
_FACTURA_CLASES = frozenset({"factura", "recibo"})
_IDENTIFICACION_CLASES = frozenset({"identificacion"})
_APPLIES_TO = _FACTURA_CLASES | _IDENTIFICACION_CLASES


class SemanticAnalyzer:
    """
    Analiza el contenido semántico de documentos OCR ya clasificados.

    Lee el texto extraído y los campos del DataExtractor y devuelve
    una interpretación del CONTENIDO del documento (qué es la factura,
    qué tipo de identificación es), sin modificar el clasificador ML.
    """

    # ── helpers privados ──────────────────────────────────────────────────────

    @staticmethod
    def _score(norm_text: str, rules: Dict[str, List[tuple]]) -> Dict[str, int]:
        """Suma el peso de cada keyword presente en el texto normalizado."""
        return {
            cat: sum(
                weight
                for kw, weight in kws
                if re.search(re.escape(kw), norm_text)
            )
            for cat, kws in rules.items()
        }

    @staticmethod
    def _indicators(
        norm_text: str,
        rules: Dict[str, List[tuple]],
        category: str,
    ) -> List[str]:
        """Devuelve las keywords que coincidieron para la categoría dada."""
        return [
            kw
            for kw, _ in rules.get(category, [])
            if re.search(re.escape(kw), norm_text)
        ]

    @staticmethod
    def _confidence(score: int) -> str:
        """Convierte una puntuación numérica en nivel de confianza textual."""
        if score >= 4:
            return "alta"
        if score >= 2:
            return "media"
        if score > 0:
            return "baja"
        return "no_determinado"

    # ── método principal ──────────────────────────────────────────────────────

    def analyze(
        self,
        text: str,
        extracted_fields: Optional[Dict[str, Any]] = None,
        document_class: str = "otro",
    ) -> Dict[str, Any]:
        """
        Analiza el contenido semántico de un documento ya clasificado.

        Args:
            text: Texto completo extraído por OCR.
            extracted_fields: Campos del DataExtractor (NIT, DPI, etc.). Opcional.
            document_class: Categoría predicha por el DocumentClassifier.

        Returns:
            dict con claves:
              categoria_contenido  — categoría de gasto (facturas) o None
              descripcion_detectada — lista de hasta 5 indicadores clave
              subtipo_documento    — subtipo de identificación o None
              confianza_semantica  — "alta" | "media" | "baja" | "no_determinado"
              indicadores          — lista completa de keywords encontradas
        """
        base: Dict[str, Any] = {
            "categoria_contenido": None,
            "descripcion_detectada": [],
            "subtipo_documento": None,
            "confianza_semantica": "no_determinado",
            "indicadores": [],
        }

        doc_class = (document_class or "otro").lower().strip()

        if doc_class not in _APPLIES_TO:
            logger.debug("SemanticAnalyzer: clase '%s' fuera de scope.", doc_class)
            return base

        # Texto vacío o solo espacios
        if not text or not text.strip():
            logger.debug("SemanticAnalyzer: texto vacío.")
            if doc_class in _FACTURA_CLASES:
                return {**base, "categoria_contenido": "No determinado"}
            return {**base, "subtipo_documento": "No determinado"}

        norm = _normalize(text)
        ef = extracted_fields or {}

        # ── Identificaciones ──────────────────────────────────────────────────
        if doc_class in _IDENTIFICACION_CLASES:
            # Refuerzo contextual: si el extractor ya encontró número DPI,
            # suma señales directas al texto de análisis.
            bonus = ""
            if ef.get("dpi"):
                bonus = " dpi cui registro nacional renap"

            combined = norm + bonus
            scores = self._score(combined, _IDENTIFICACION_RULES)
            best = max(scores, key=lambda k: scores[k])
            best_score = scores[best]

            if best_score == 0:
                return {**base, "subtipo_documento": "No determinado"}

            return {
                "categoria_contenido": None,
                "descripcion_detectada": [],
                "subtipo_documento": best,
                "confianza_semantica": self._confidence(best_score),
                "indicadores": self._indicators(combined, _IDENTIFICACION_RULES, best),
            }

        # ── Facturas y recibos ────────────────────────────────────────────────
        scores = self._score(norm, _FACTURA_RULES)
        best = max(scores, key=lambda k: scores[k])
        best_score = scores[best]

        if best_score == 0:
            return {**base, "categoria_contenido": "No determinado"}

        indicators = self._indicators(norm, _FACTURA_RULES, best)
        return {
            "categoria_contenido": best,
            "descripcion_detectada": indicators[:5],
            "subtipo_documento": None,
            "confianza_semantica": self._confidence(best_score),
            "indicadores": indicators,
        }
