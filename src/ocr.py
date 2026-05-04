"""Módulo OCR con Pytesseract."""

import logging

import cv2
import numpy as np
import pdfplumber
import pytesseract
from PIL import Image

from config import TESSERACT_PATH, TESSDATA_PREFIX

logger = logging.getLogger(__name__)

# Configurar ruta de Tesseract si se encontró
if TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    logger.info("Tesseract encontrado en: %s", TESSERACT_PATH)
else:
    logger.warning(
        "Tesseract no encontrado. OCR no funcionará. "
        "Instala Tesseract o define la variable de entorno TESSERACT_PATH."
    )

if TESSDATA_PREFIX:
    logger.info("TESSDATA_PREFIX configurado en: %s", TESSDATA_PREFIX)


def _get_available_languages() -> set[str]:
    """Obtiene el conjunto de idiomas disponibles en la instalación de Tesseract."""
    try:
        return set(pytesseract.get_languages())
    except pytesseract.TesseractNotFoundError:
        logger.error("Tesseract no encontrado al consultar idiomas.")
        return set()
    except (OSError, RuntimeError, ValueError) as e:
        logger.warning("No se pudo obtener lista de idiomas: %s", e)
        return set()


def _resolve_lang(requested: str) -> str:
    """
    Resuelve el idioma efectivo a usar, priorizando español.

    - Si 'spa' está disponible y 'eng' también → usa 'spa+eng' para mejor cobertura.
    - Si solo 'spa' está disponible → usa 'spa'.
    - Si 'spa' no está disponible pero 'eng' sí → avisa y usa 'eng'.
    - Si el idioma solicitado no es 'spa' → lo valida; si no existe cae a 'eng'.
    """
    available = _get_available_languages()

    if not available:
        logger.warning("No se pudo verificar idiomas disponibles; usando '%s' tal cual.", requested)
        return requested

    # Caso principal: español
    if requested in ("spa", "spa+eng"):
        if "spa" in available and "eng" in available:
            return "spa+eng"
        if "spa" in available:
            return "spa"
        logger.warning(
            "Idioma 'spa' no está en la instalación de Tesseract (%s). "
            "Usando 'eng'. Instala spa.traineddata en %s.",
            available,
            TESSDATA_PREFIX or "tessdata/",
        )
        return "eng"

    # Idioma arbitrario solicitado
    if requested in available:
        return requested
    logger.warning("Idioma '%s' no disponible, usando 'eng'.", requested)
    return "eng"


# Pre-calcular idioma efectivo al cargar el módulo para detectar problemas temprano
_EFFECTIVE_LANG = _resolve_lang("spa")
logger.info("Idioma OCR activo: %s", _EFFECTIVE_LANG)


class OCRProcessor:
    """Clase para procesar OCR en imágenes y PDFs."""

    def __init__(self, tesseract_path: str | None = None):
        """
        Inicializa el procesador OCR.

        Args:
            tesseract_path: Ruta al ejecutable de Tesseract (opcional).
        """
        if tesseract_path:
            # Permitir override por parámetro
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
            logger.debug("Tesseract path sobrescrito: %s", tesseract_path)

    def extract_text_from_image(self, image_path: str, lang: str = "spa") -> dict:
        """
        Extrae texto de una imagen usando OCR.

        Args:
            image_path: Ruta a la imagen
            lang: Idioma para OCR (spa para español, eng para inglés)

        Returns:
            dict: Diccionario con texto extraído y confianza
        """
        try:
            effective_lang = _resolve_lang(lang)
            logger.debug("Procesando imagen: %s (idioma efectivo: %s)", image_path, effective_lang)
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, lang=effective_lang)

            # Obtener datos detallados incluyendo confianza
            data = pytesseract.image_to_data(
                image,
                lang=effective_lang,
                output_type=pytesseract.Output.DICT
            )

            # Calcular confianza promedio (distingue "sin texto" de "confianza baja")
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            has_text = bool(text.strip())
            if confidences:
                avg_confidence = float(np.mean(confidences))
            elif has_text:
                avg_confidence = 0.0  # texto detectado pero sin datos de confianza
            else:
                avg_confidence = -1.0  # indica que no se detectó texto

            logger.info("OCR imagen completado: idioma=%s confianza=%.2f", effective_lang, avg_confidence)
            return {
                "status": "success",
                "text": text.strip(),
                "confidence": round(avg_confidence, 2),
                "has_text": has_text,
                "language": effective_lang
            }
        except (FileNotFoundError, ValueError, TypeError, OSError) as e:
            logger.error("Error en OCR de imagen: %s", e)
            return {
                "status": "error",
                "text": "",
                "confidence": 0,
                "error": str(e)
            }

    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocesa una imagen para mejorar OCR.

        Args:
            image_path: Ruta a la imagen

        Returns:
            np.ndarray: Imagen procesada
        """
        image = cv2.imread(image_path)

        if image is None:
            raise ValueError(f"No se puede leer la imagen: {image_path}")

        # Convertir a escala de grises
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Aplicar threshold
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh, h=10)

        return denoised

    def extract_text_from_pdf(self, pdf_path: str, lang: str = "spa") -> dict:
        """
        Extrae texto de un PDF usando OCR.

        Args:
            pdf_path: Ruta al archivo PDF
            lang: Idioma para OCR

        Returns:
            dict: Diccionario con texto extraído por página
        """
        try:
            effective_lang = _resolve_lang(lang)
            logger.debug("Procesando PDF: %s (idioma efectivo: %s)", pdf_path, effective_lang)
            texts = []
            with pdfplumber.open(pdf_path) as pdf:
                logger.info("PDF abierto: %d páginas", len(pdf.pages))
                for i, page in enumerate(pdf.pages):
                    logger.debug("Procesando página %d", i + 1)
                    img = page.to_image()
                    text = pytesseract.image_to_string(img.original, lang=effective_lang)
                    texts.append({
                        "page": i + 1,
                        "text": text.strip()
                    })

            logger.info("OCR PDF completado: %d páginas procesadas", len(texts))
            return {
                "status": "success",
                "pages": texts,
                "total_pages": len(texts),
                "language": effective_lang
            }
        except (FileNotFoundError, ValueError, TypeError, OSError) as e:
            logger.error("Error en OCR de PDF: %s", e)
            return {
                "status": "error",
                "pages": [],
                "error": str(e)
            }
