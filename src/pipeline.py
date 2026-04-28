"""Pipeline integrado: OCR -> Extracción -> Clasificación."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from config import MODELS_DIR

from .classifier import DocumentClassifier
from .extractor import DataExtractor
from .ocr import OCRProcessor

logger = logging.getLogger(__name__)



class OCRPipeline:
    """Pipeline completo de OCR, extracción y clasificación."""

    def __init__(
        self,
        tesseract_path: Optional[str] = None,
        classifier_model_path: Optional[str] = None,
    ):
        """
        Inicializa el pipeline.

        Intenta cargar automáticamente el modelo entrenado de models/classifier_model.joblib
        si no se especifica una ruta diferente.

        Args:
            tesseract_path: Ruta a Tesseract (Windows)
            classifier_model_path: Ruta al modelo de clasificación entrenado (opcional)
        """
        self.ocr = OCRProcessor(tesseract_path=tesseract_path)
        self.extractor = DataExtractor()

        # Cargar modelo entrenado si existe
        if classifier_model_path:
            model_path = classifier_model_path
        else:
            # Buscar modelo entrenado automáticamente
            default_model_path = Path(MODELS_DIR) / "classifier_model.joblib"
            model_path = str(default_model_path) if default_model_path.exists() else None

        self.classifier = DocumentClassifier(model_path=model_path)
        self.last_result = None

    def process_image(self, image_path: str, lang: str = "spa") -> Dict[str, Any]:
        """
        Procesa una imagen a través del pipeline completo con error boundaries.

        Args:
            image_path: Ruta a la imagen
            lang: Idioma para OCR

        Returns:
            dict: Resultado del pipeline con field 'errors' si hay fallos
        """
        result = {
            "input_file": image_path,
            "format": "image",
            "steps": {},
            "errors": []
        }

        # Paso 1: OCR (con error boundary)
        try:
            logger.info("Iniciando OCR de imagen: %s", image_path)
            ocr_result = self.ocr.extract_text_from_image(image_path, lang=lang)
            result["steps"]["ocr"] = ocr_result

            if ocr_result.get("status") != "success":
                error_msg = ocr_result.get("error", "OCR failed")
                result["errors"].append(f"OCR: {error_msg}")
                logger.error("OCR falló: %s", error_msg)
                result["status"] = "error"
                return result

            extracted_text = ocr_result["text"]
        except Exception as e:
            error_msg = f"OCR exception: {str(e)}"
            result["errors"].append(error_msg)
            logger.error("Excepción en OCR: %s", e)
            result["status"] = "error"
            return result

        # Paso 2: Extracción de datos (con error boundary)
        try:
            logger.info("Iniciando extracción de datos")
            extraction_result = self.extractor.extract_all(extracted_text)
            result["steps"]["extraction"] = extraction_result
            logger.debug("Extracción completada")
        except Exception as e:
            error_msg = f"Extraction: {str(e)}"
            result["errors"].append(error_msg)
            logger.error("Excepción en extracción: %s", e)
            extraction_result = {}

        # Paso 3: Clasificación (con error boundary)
        try:
            logger.info("Iniciando clasificación")
            classification_result = self.classifier.predict(extracted_text)
            result["steps"]["classification"] = classification_result
            logger.debug("Clasificación completada")
        except Exception as e:
            error_msg = f"Classification: {str(e)}"
            result["errors"].append(error_msg)
            logger.error("Excepción en clasificación: %s", e)
            classification_result = {
                "class": "error",
                "confidence": 0.0,
                "error": str(e)
            }

        # Información adicional
        result["extracted_text"] = extracted_text
        try:
            result["lines"] = self.extractor.extract_lines(extracted_text)
        except Exception as e:
            logger.warning("Error extrayendo líneas: %s", e)
            result["lines"] = []

        # Determinar estado final
        result["status"] = "error" if result["errors"] else "success"

        self.last_result = result
        return result

    def process_pdf(self, pdf_path: str, lang: str = "spa") -> Dict[str, Any]:
        """
        Procesa un PDF a través del pipeline con error boundaries por página.

        Args:
            pdf_path: Ruta al PDF
            lang: Idioma para OCR

        Returns:
            dict: Resultado del pipeline con field 'errors' si hay fallos
        """
        result = {
            "input_file": pdf_path,
            "format": "pdf",
            "pages": [],
            "errors": []
        }

        # Paso 1: OCR en PDF (con error boundary)
        try:
            logger.info("Iniciando OCR de PDF: %s", pdf_path)
            ocr_result = self.ocr.extract_text_from_pdf(pdf_path, lang=lang)
            result["steps"] = {"ocr": ocr_result}

            if ocr_result.get("status") != "success":
                error_msg = ocr_result.get("error", "PDF OCR failed")
                result["errors"].append(f"OCR: {error_msg}")
                logger.error("OCR PDF falló: %s", error_msg)
                result["status"] = "error"
                return result
        except Exception as e:
            error_msg = f"PDF OCR exception: {str(e)}"
            result["errors"].append(error_msg)
            logger.error("Excepción en OCR PDF: %s", e)
            result["status"] = "error"
            return result

        # Procesar cada página (con error boundary por página)
        for page_data in ocr_result["pages"]:
            page_num = page_data["page"]
            page_text = page_data["text"]

            page_result = {
                "page_number": page_num,
                "text": page_text,
                "page_errors": []
            }

            # Extracción (con error boundary)
            try:
                logger.debug("Extrayendo datos de página %d", page_num)
                extraction = self.extractor.extract_all(page_text)
                page_result["extraction"] = extraction
            except Exception as e:
                error_msg = f"Extraction page {page_num}: {str(e)}"
                page_result["page_errors"].append(error_msg)
                result["errors"].append(error_msg)
                logger.error("Excepción en extracción página %d: %s", page_num, e)
                extraction = {}

            # Clasificación (con error boundary)
            try:
                logger.debug("Clasificando página %d", page_num)
                classification = self.classifier.predict(page_text)
                page_result["classification"] = classification
            except Exception as e:
                error_msg = f"Classification page {page_num}: {str(e)}"
                page_result["page_errors"].append(error_msg)
                result["errors"].append(error_msg)
                logger.error("Excepción en clasificación página %d: %s", page_num, e)
                classification = {
                    "class": "error",
                    "confidence": 0.0,
                    "error": str(e)
                }

            result["pages"].append(page_result)

        result["status"] = "error" if result["errors"] else "success"
        self.last_result = result
        return result

    def process_file(self, file_path: str, lang: str = "spa") -> Dict[str, Any]:
        """
        Procesa cualquier archivo (imagen o PDF).

        Args:
            file_path: Ruta al archivo
            lang: Idioma para OCR

        Returns:
            dict: Resultado del pipeline
        """
        file_path_obj = Path(file_path)

        if not file_path_obj.exists():
            return {
                "status": "error",
                "error": f"Archivo no encontrado: {file_path}"
            }

        if file_path_obj.suffix.lower() == '.pdf':
            return self.process_pdf(str(file_path), lang=lang)
        if file_path_obj.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
            return self.process_image(str(file_path), lang=lang)
        return {
            "status": "error",
            "error": f"Formato no soportado: {file_path_obj.suffix}"
        }

    def get_last_result_json(self) -> str:
        """
        Obtiene el último resultado en formato JSON.

        Returns:
            str: JSON con el resultado
        """
        if self.last_result is None:
            return json.dumps({"error": "Sin resultados previos"})

        return json.dumps(self.last_result, indent=2, ensure_ascii=False)

    def train_classifier(self, training_data: list):
        """
        Entrena el clasificador con nuevos datos.

        Args:
            training_data: Lista de tuplas (texto, etiqueta)
        """
        if not training_data:
            return

        texts, labels = zip(*training_data)
        self.classifier.train(list(texts), list(labels))

    def save_classifier(self, path: str):
        """
        Guarda el clasificador entrenado.

        Args:
            path: Ruta para guardar
        """
        self.classifier.save_model(path)
