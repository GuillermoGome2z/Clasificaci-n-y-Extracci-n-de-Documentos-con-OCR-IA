"""Módulo OCR con Pytesseract."""

import logging
from pathlib import Path

import cv2
import numpy as np
import pytesseract
from PIL import Image

from config import TESSERACT_PATH

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


class OCRProcessor:
    """Clase para procesar OCR en imágenes y PDFs."""

    def __init__(self, tesseract_path: str | None = None):
        """
        Inicializa el procesador OCR.

        Args:
            tesseract_path: Ruta al ejecutable de Tesseract (opcional - usa config.TESSERACT_PATH por defecto)
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
            logger.debug("Procesando imagen: %s (idioma: %s)", image_path, lang)
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, lang=lang)

            # Obtener datos detallados incluyendo confianza
            data = pytesseract.image_to_data(
                image,
                lang=lang,
                output_type=pytesseract.Output.DICT
            )

            # Calcular confianza promedio
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = np.mean(confidences) if confidences else 0

            logger.info("OCR imagen completado: confianza %.2f", avg_confidence)
            return {
                "status": "success",
                "text": text.strip(),
                "confidence": round(avg_confidence, 2),
                "language": lang
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
            import pdfplumber

            logger.debug("Procesando PDF: %s", pdf_path)
            texts = []
            with pdfplumber.open(pdf_path) as pdf:
                logger.info("PDF abierto: %d páginas", len(pdf.pages))
                for i, page in enumerate(pdf.pages):
                    logger.debug("Procesando página %d", i + 1)
                    # Convertir página a imagen
                    img = page.to_image()
                    text = pytesseract.image_to_string(img.original, lang=lang)
                    texts.append({
                        "page": i + 1,
                        "text": text.strip()
                    })

            logger.info("OCR PDF completado: %d páginas procesadas", len(texts))
            return {
                "status": "success",
                "pages": texts,
                "total_pages": len(texts),
                "language": lang
            }
        except (FileNotFoundError, ValueError, TypeError, OSError) as e:
            logger.error("Error en OCR de PDF: %s", e)
            return {
                "status": "error",
                "pages": [],
                "error": str(e)
            }
