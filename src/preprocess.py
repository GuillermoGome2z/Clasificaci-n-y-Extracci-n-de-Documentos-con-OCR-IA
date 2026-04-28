"""
preprocess.py — Funciones de preprocesamiento de texto e imágenes.

Parte del pipeline OCR + IA (Proyecto 04).
"""
import re
import logging
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


def preprocesar_imagen(image_path: str) -> np.ndarray:
    """
    Preprocesa una imagen para mejorar la calidad del OCR.

    Pasos:
    1. Escala de grises
    2. Binarización adaptativa (Otsu)
    3. Reducción de ruido

    Args:
        image_path: Ruta a la imagen

    Returns:
        Imagen preprocesada como ndarray
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"No se puede leer la imagen: {image_path}")

    # Escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Binarización adaptativa (Otsu)
    _, binarized = cv2.threshold(
        gray, 0, 255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # Reducción de ruido leve
    denoised = cv2.fastNlMeansDenoising(binarized, h=10)

    logger.debug("Imagen preprocesada: %s", image_path)
    return denoised


def limpiar_texto_ocr(text: str) -> str:
    """
    Limpia el texto extraído por OCR para mejorar la clasificación.

    Pasos:
    1. Convertir a minúsculas
    2. Eliminar caracteres especiales
    3. Normalizar espacios

    Args:
        text: Texto crudo del OCR

    Returns:
        Texto limpio
    """
    if not text:
        return ""

    # Minúsculas
    text = text.lower()

    # Eliminar caracteres especiales (mantener letras, números y espacios)
    text = re.sub(r'[^a-záéíóúñüa-z0-9\s]', ' ', text, flags=re.IGNORECASE)

    # Normalizar espacios múltiples
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def cargar_imagen_pil(image_path: str) -> Image.Image:
    """
    Carga una imagen como objeto PIL.

    Args:
        image_path: Ruta a la imagen

    Returns:
        Imagen PIL
    """
    return Image.open(image_path).convert('RGB')
