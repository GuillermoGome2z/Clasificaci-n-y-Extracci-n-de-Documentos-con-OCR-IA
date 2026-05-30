"""
Tests para src/classifier.py - DocumentClassifier

Cobertura:
- Inicialización del clasificador (sin y con modelo)
- Predicción con modelo entrenado
- Predicción sin modelo (fallback)
- Carga automática de modelo
- Manejo de errores

Total: 12 tests
"""
import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import MODELS_DIR
from src.classifier import DocumentClassifier


class TestClassifierInitialization:
    """Tests para inicialización del clasificador."""

    def test_classifier_initializes_without_model(self):
        """El clasificador se inicializa correctamente sin modelo entrenado."""
        classifier = DocumentClassifier()
        assert classifier is not None
        assert classifier.classes == ['factura', 'recibo', 'contrato', 'constancia', 'carta_formal', 'identificacion', 'otro']
        assert classifier.is_trained is False

    def test_classifier_initializes_with_default_pipeline(self):
        """El clasificador crea pipeline por defecto si no hay modelo."""
        classifier = DocumentClassifier()
        assert classifier.pipeline is not None
        assert hasattr(classifier.pipeline, 'predict')

    def test_classifier_attempts_to_load_model_if_exists(self):
        """El clasificador intenta cargar modelo si existe en ruta."""
        model_path = Path(MODELS_DIR) / "classifier_model.joblib"
        classifier = DocumentClassifier(model_path=str(model_path))

        # Si existe modelo, debe estar marcado como entrenado
        if model_path.exists():
            assert classifier.is_trained is True
            assert classifier.model_data is not None
        else:
            assert classifier.is_trained is False


class TestClassifierPrediction:
    """Tests para predicción del clasificador."""

    def test_predict_returns_dict(self):
        """Predict devuelve diccionario con estructura correcta."""
        classifier = DocumentClassifier()
        result = classifier.predict("Texto de prueba")

        assert isinstance(result, dict)
        assert "class" in result
        assert "confidence" in result
        assert "probabilities" in result

    def test_predict_with_empty_text(self):
        """Predict maneja texto vacío sin error."""
        classifier = DocumentClassifier()
        result = classifier.predict("")

        assert result["class"] is not None
        assert result["confidence"] >= 0.0

    def test_predict_with_long_text(self):
        """Predict maneja textos muy largos."""
        classifier = DocumentClassifier()
        long_text = "palabra " * 10000  # 10000 palabras
        result = classifier.predict(long_text)

        assert result is not None
        assert "class" in result

    def test_predict_batch(self):
        """Predict_batch procesa múltiples textos."""
        classifier = DocumentClassifier()
        texts = ["texto 1", "texto 2", "texto 3"]
        results = classifier.predict_batch(texts)

        assert len(results) == len(texts)
        assert all(isinstance(r, dict) for r in results)
        assert all("class" in r for r in results)

    def test_predict_with_trained_model(self):
        """Predict usa modelo entrenado si está disponible."""
        model_path = Path(MODELS_DIR) / "classifier_model.joblib"

        if model_path.exists():
            classifier = DocumentClassifier(model_path=str(model_path))
            result = classifier.predict("FACTURA de venta con detalles")

            assert classifier.is_trained is True
            assert result["model_type"] == "trained"
            assert result["class"] in classifier.classes
        else:
            pytest.skip("Modelo entrenado no disponible")

    def test_predict_returns_category_names_not_indices(self):
        """Predict devuelve nombres de categoría, no índices."""
        model_path = Path(MODELS_DIR) / "classifier_model.joblib"

        if model_path.exists():
            classifier = DocumentClassifier(model_path=str(model_path))
            result = classifier.predict("Cualquier texto")

            # Debe ser string con nombre, no número
            assert isinstance(result["class"], str)
            assert result["class"] in ['factura', 'recibo', 'contrato', 'constancia', 'carta_formal', 'identificacion', 'otro']
        else:
            pytest.skip("Modelo entrenado no disponible")


class TestClassifierFallback:
    """Tests para comportamiento fallback del clasificador."""

    def test_predict_without_model_doesnt_error(self):
        """Predict sin modelo no lanza error."""
        classifier = DocumentClassifier()
        classifier.is_trained = False
        classifier.model_data = None

        # No debe lanzar excepción
        result = classifier.predict("texto")
        assert result is not None

    def test_predict_returns_model_type_info(self):
        """Predict incluye información del tipo de modelo usado."""
        classifier = DocumentClassifier()
        result = classifier.predict("texto de prueba")

        assert "model_type" in result
        assert result["model_type"] in ["trained", "default (not trained)", "untrained"]

    def test_probabilities_sum_to_one_or_near_zero(self):
        """Las probabilidades devueltas son válidas."""
        classifier = DocumentClassifier()
        result = classifier.predict("texto prueba")

        probs = result.get("probabilities", {})
        if probs:
            total = sum(probs.values())
            # Si hay probabilidades, deben sumar ~1 o ser ~0
            assert total == 0.0 or 0.99 < total < 1.01


class TestClassifierModelLoading:
    """Tests para carga de modelos."""

    def test_load_model_from_path(self):
        """Puede cargar un modelo desde una ruta específica."""
        model_path = Path(MODELS_DIR) / "classifier_model.joblib"

        if model_path.exists():
            classifier = DocumentClassifier()
            classifier.load_model(str(model_path))

            assert classifier.is_trained is True
            assert classifier.model_data is not None
        else:
            pytest.skip("Modelo entrenado no disponible")

    def test_load_nonexistent_model_doesnt_crash(self):
        """Cargar modelo inexistente no crashea."""
        classifier = DocumentClassifier()
        classifier.load_model("/ruta/inexistente/modelo.joblib")

        # No debe crashear, debe mantener estado o usar fallback
        assert classifier is not None


class TestClassifierEdgeCases:
    """Tests para casos edge del clasificador."""

    def test_predict_with_special_characters(self):
        """Predict maneja caracteres especiales."""
        classifier = DocumentClassifier()
        text = "FACTURA #123-XYZ/2024 @ €50.00 & descuento!"
        result = classifier.predict(text)

        assert result["class"] is not None

    def test_predict_with_unicode(self):
        """Predict maneja unicode correctamente."""
        classifier = DocumentClassifier()
        text = "Factura с русским текстом 中文 العربية"
        result = classifier.predict(text)

        assert result is not None

    def test_multiple_instances_independent(self):
        """Múltiples instancias del clasificador son independientes."""
        c1 = DocumentClassifier()
        c2 = DocumentClassifier()

        assert c1 is not c2
        assert c1.pipeline is not c2.pipeline


class TestClassifierIntegration:
    """Tests de integración con pipeline."""

    def test_classifier_in_pipeline_context(self):
        """El clasificador funciona correctamente en contexto del pipeline."""
        try:
            from src.pipeline import OCRPipeline
            pipeline = OCRPipeline()

            # El clasificador debe estar disponible
            assert hasattr(pipeline, 'classifier')
            assert pipeline.classifier is not None

        except (ImportError, AttributeError):
            pytest.skip("Pipeline requires cv2")

    def test_classifier_loads_model_automatically_in_pipeline(self):
        """Pipeline carga modelo automáticamente si existe."""
        try:
            from src.pipeline import OCRPipeline

            model_path = Path(MODELS_DIR) / "classifier_model.joblib"

            if model_path.exists():
                pipeline = OCRPipeline()
                assert pipeline.classifier.is_trained is True

        except (ImportError, AttributeError):
            pytest.skip("Pipeline requires cv2")
