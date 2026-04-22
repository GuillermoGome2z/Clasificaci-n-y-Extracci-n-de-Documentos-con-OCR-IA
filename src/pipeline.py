"""Pipeline integrado: OCR -> Extracción -> Clasificación."""

import json
from pathlib import Path
from typing import Dict, Any
from .ocr import OCRProcessor
from .extractor import DataExtractor
from .classifier import DocumentClassifier


class OCRPipeline:
    """Pipeline completo de OCR, extracción y clasificación."""

    def __init__(self, tesseract_path: str = None, classifier_model_path: str = None):
        """
        Inicializa el pipeline.
        
        Args:
            tesseract_path: Ruta a Tesseract (Windows)
            classifier_model_path: Ruta al modelo de clasificación entrenado
        """
        self.ocr = OCRProcessor(tesseract_path=tesseract_path)
        self.extractor = DataExtractor()
        self.classifier = DocumentClassifier(model_path=classifier_model_path)
        self.last_result = None

    def process_image(self, image_path: str, lang: str = "spa") -> Dict[str, Any]:
        """
        Procesa una imagen a través del pipeline completo.
        
        Args:
            image_path: Ruta a la imagen
            lang: Idioma para OCR
            
        Returns:
            dict: Resultado del pipeline
        """
        result = {
            "input_file": image_path,
            "format": "image",
            "steps": {}
        }

        # Paso 1: OCR
        ocr_result = self.ocr.extract_text_from_image(image_path, lang=lang)
        result["steps"]["ocr"] = ocr_result

        if ocr_result["status"] != "success":
            result["status"] = "error"
            return result

        extracted_text = ocr_result["text"]

        # Paso 2: Extracción de datos
        extraction_result = self.extractor.extract_all(extracted_text)
        result["steps"]["extraction"] = extraction_result

        # Paso 3: Clasificación
        classification_result = self.classifier.predict(extracted_text)
        result["steps"]["classification"] = classification_result

        # Información adicional
        result["extracted_text"] = extracted_text
        result["lines"] = self.extractor.extract_lines(extracted_text)
        result["status"] = "success"

        self.last_result = result
        return result

    def process_pdf(self, pdf_path: str, lang: str = "spa") -> Dict[str, Any]:
        """
        Procesa un PDF a través del pipeline.
        
        Args:
            pdf_path: Ruta al PDF
            lang: Idioma para OCR
            
        Returns:
            dict: Resultado del pipeline
        """
        result = {
            "input_file": pdf_path,
            "format": "pdf",
            "pages": []
        }

        # Paso 1: OCR en PDF
        ocr_result = self.ocr.extract_text_from_pdf(pdf_path, lang=lang)
        result["steps"] = {"ocr": ocr_result}

        if ocr_result["status"] != "success":
            result["status"] = "error"
            return result

        # Procesar cada página
        for page_data in ocr_result["pages"]:
            page_text = page_data["text"]
            
            # Extracción
            extraction = self.extractor.extract_all(page_text)
            
            # Clasificación
            classification = self.classifier.predict(page_text)
            
            result["pages"].append({
                "page_number": page_data["page"],
                "text": page_text,
                "extraction": extraction,
                "classification": classification
            })

        result["status"] = "success"
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
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {
                "status": "error",
                "error": f"Archivo no encontrado: {file_path}"
            }

        if file_path.suffix.lower() == '.pdf':
            return self.process_pdf(str(file_path), lang=lang)
        elif file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
            return self.process_image(str(file_path), lang=lang)
        else:
            return {
                "status": "error",
                "error": f"Formato no soportado: {file_path.suffix}"
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
