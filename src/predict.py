"""
predict.py — Función de predicción/inferencia del pipeline completo.

Parte del pipeline OCR + IA (Proyecto 04).
"""
import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def predecir_documento(
    file_path: str,
    lang: str = "spa",
    model_path: Optional[str] = None
) -> dict:
    """
    Predice el tipo de documento y extrae sus campos clave.

    Pipeline completo:
    imagen/PDF → OCR → TF-IDF + LinearSVC → Regex → JSON

    Args:
        file_path: Ruta al archivo (imagen o PDF)
        lang: Idioma para OCR ('spa' o 'eng')
        model_path: Ruta al modelo entrenado (opcional)

    Returns:
        dict con tipo, campos extraídos y metadata
    """
    from src.pipeline import OCRPipeline
    from config import MODELS_DIR

    if model_path is None:
        model_path = str(Path(MODELS_DIR) / "classifier_model.joblib")

    try:
        pipeline = OCRPipeline(classifier_model_path=model_path)
        result = pipeline.process_file(file_path, lang=lang)

        logger.info(
            "Predicción completada: %s → %s",
            file_path,
            result.get("steps", {}).get("classification", {}).get("predicted_class", "?")
        )
        return result

    except Exception as e:
        logger.error("Error en predicción: %s", e)
        return {
            "status": "error",
            "error": str(e),
            "input_file": file_path
        }


def predecir_batch(file_paths: list, lang: str = "spa") -> list:
    """
    Procesa múltiples archivos en secuencia.

    Args:
        file_paths: Lista de rutas a archivos
        lang: Idioma para OCR

    Returns:
        Lista de resultados por archivo
    """
    results = []
    for path in file_paths:
        result = predecir_documento(path, lang=lang)
        results.append(result)
    return results
