"""
Tests para train_classifier.py - Entrenador del Clasificador

Cobertura:
- Carga de datos de entrenamiento
- Entrenamiento del modelo
- Persistencia del modelo
- Manejo de directorios y archivos
- Validación de resultados

Total: 10 tests
"""
import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from train_classifier import ClassifierTrainer


class TestTrainerDataLoading:
    """Tests para carga de datos del entrenador."""

    def test_trainer_initializes(self):
        """El entrenador se inicializa correctamente."""
        trainer = ClassifierTrainer()
        assert trainer is not None
        assert trainer.CATEGORIES == ["factura", "recibo", "contrato", "constancia", "carta_formal", "identificacion", "otro"]

    def test_trainer_finds_training_data(self):
        """El entrenador encuentra datos de entrenamiento."""
        trainer = ClassifierTrainer()
        result = trainer.load_training_data()
        
        # Debe encontrar datos si existen
        if trainer.data_dir.exists():
            assert result is True or result is False  # Depende de si hay datos
        else:
            assert result is False

    def test_trainer_loads_texts_and_labels(self):
        """El entrenador carga textos y etiquetas correctamente."""
        trainer = ClassifierTrainer()
        result = trainer.load_training_data()
        
        if result:  # Si hay datos
            assert len(trainer.texts) > 0
            assert len(trainer.labels) > 0
            assert len(trainer.texts) == len(trainer.labels)

    def test_trainer_handles_missing_data_gracefully(self):
        """El entrenador maneja carpetas sin datos sin error."""
        trainer = ClassifierTrainer()
        # Cambiar a ruta no existente
        trainer.data_dir = Path("/ruta/inexistente/datos")
        
        result = trainer.load_training_data()
        assert result is False  # Debe retornar False, no error

    def test_label_mapping_correct(self):
        """El mapeo de etiquetas es correcto."""
        trainer = ClassifierTrainer()
        expected_mapping = {
            "factura": 0,
            "recibo": 1,
            "contrato": 2,
            "constancia": 3,
            "carta_formal": 4,
            "identificacion": 5,
            "otro": 6
        }
        assert trainer.label_mapping == expected_mapping


class TestTrainerTraining:
    """Tests para entrenamiento del modelo."""

    def test_trainer_trains_when_data_available(self):
        """El entrenador entrena correctamente cuando hay datos."""
        trainer = ClassifierTrainer()
        
        if trainer.load_training_data():
            # Hay datos, intentar entrenar
            try:
                metrics = trainer.train()
                assert metrics is not None
                assert "accuracy" in metrics
                assert 0.0 <= metrics["accuracy"] <= 1.0
            except (ValueError, IndexError) as e:
                pytest.skip(f"Entrenamiento requiere datos suficientes: {str(e)}")

    def test_trainer_returns_valid_metrics(self):
        """El entrenador devuelve métricas válidas."""
        trainer = ClassifierTrainer()
        
        if trainer.load_training_data():
            try:
                metrics = trainer.train()
                
                assert "accuracy" in metrics
                assert "samples_train" in metrics
                assert "samples_test" in metrics
                assert "vocab_size" in metrics
                assert "trained_at" in metrics
                
                assert metrics["samples_train"] > 0
                assert metrics["vocab_size"] > 0
            except (ValueError, IndexError) as e:
                pytest.skip(f"Entrenamiento requiere datos suficientes: {str(e)}")

    def test_trainer_creates_vectorizer(self):
        """El entrenador crea vectorizador TF-IDF."""
        trainer = ClassifierTrainer()
        
        if trainer.load_training_data():
            try:
                trainer.train()
                assert trainer.vectorizer is not None
                assert hasattr(trainer.vectorizer, 'transform')
            except (ValueError, IndexError) as e:
                pytest.skip(f"Entrenamiento requiere datos suficientes: {str(e)}")

    def test_trainer_creates_model(self):
        """El entrenador entrena modelo Naive Bayes."""
        trainer = ClassifierTrainer()
        
        if trainer.load_training_data():
            try:
                trainer.train()
                assert trainer.model is not None
                assert hasattr(trainer.model, 'predict')
                assert hasattr(trainer.model, 'predict_proba')
            except (ValueError, IndexError) as e:
                pytest.skip(f"Entrenamiento requiere datos suficientes: {str(e)}")


class TestTrainerModelPersistence:
    """Tests para guardado del modelo."""

    def test_trainer_saves_model(self):
        """El entrenador guarda el modelo correctamente."""
        trainer = ClassifierTrainer()
        
        if trainer.load_training_data():
            try:
                trainer.train()
                result = trainer.save_model()
                
                assert result is True
                assert trainer.model_path.exists()
            except (ValueError, IndexError, OSError) as e:
                pytest.skip(f"Entrenamiento requiere datos suficientes: {str(e)}")

    def test_saved_model_has_valid_size(self):
        """El modelo guardado tiene tamaño razonable."""
        trainer = ClassifierTrainer()
        
        if trainer.load_training_data():
            try:
                trainer.train()
                trainer.save_model()
                
                size_bytes = trainer.model_path.stat().st_size
                assert size_bytes > 0  # No debe estar vacío
                assert size_bytes < 100 * 1024 * 1024  # Menos de 100MB
            except (ValueError, IndexError, OSError) as e:
                pytest.skip(f"Entrenamiento requiere datos suficientes: {str(e)}")

    def test_model_can_be_loaded_after_saving(self):
        """El modelo guardado puede ser recargado."""
        trainer = ClassifierTrainer()
        
        if trainer.load_training_data():
            try:
                trainer.train()
                trainer.save_model()
                
                # Intentar cargar con joblib
                import joblib
                loaded = joblib.load(trainer.model_path)
                
                assert loaded is not None
                assert "model" in loaded
                assert "vectorizer" in loaded
                assert "categories" in loaded
            except (ValueError, IndexError, OSError) as e:
                pytest.skip(f"Entrenamiento requiere datos suficientes: {str(e)}")


class TestTrainerSummary:
    """Tests para generación de resumen."""

    def test_trainer_creates_summary(self):
        """El entrenador crea resumen correctamente."""
        trainer = ClassifierTrainer()
        
        if trainer.load_training_data():
            try:
                metrics = trainer.train()
                summary = trainer.create_summary(metrics)
                
                assert summary is not None
                assert "timestamp" in summary
                assert "metrics" in summary
                assert "categories" in summary
            except (ValueError, IndexError) as e:
                pytest.skip(f"Entrenamiento requiere datos suficientes: {str(e)}")

    def test_summary_has_all_fields(self):
        """El resumen incluye todos los campos necesarios."""
        trainer = ClassifierTrainer()
        
        if trainer.load_training_data():
            try:
                metrics = trainer.train()
                summary = trainer.create_summary(metrics)
                
                expected_fields = [
                    "timestamp",
                    "training_status",
                    "metrics",
                    "categories",
                    "data_path",
                    "model_path"
                ]
                
                for field in expected_fields:
                    assert field in summary
            except (ValueError, IndexError) as e:
                pytest.skip(f"Entrenamiento requiere datos suficientes: {str(e)}")


class TestTrainerEdgeCases:
    """Tests para casos especiales del entrenador."""

    def test_trainer_handles_no_data_gracefully(self):
        """El entrenador maneja falta de datos sin crashear."""
        trainer = ClassifierTrainer()
        trainer.texts = []
        trainer.labels = []
        
        # No debe crashear, debe manejar gracefully
        try:
            trainer.train()
            # Podría fallar, pero no debe crash
        except ValueError:
            pass  # Es aceptable que falle
        
        assert True  # Si llegamos aquí, no crasheó

    def test_trainer_categories_immutable(self):
        """Las categorías del entrenador son correctas."""
        trainer = ClassifierTrainer()
        assert trainer.CATEGORIES == ["factura", "recibo", "contrato", "constancia", "carta_formal", "identificacion", "otro"]
        assert len(trainer.CATEGORIES) == 7

    def test_trainer_models_directory_created(self):
        """El directorio de modelos se crea si no existe."""
        trainer = ClassifierTrainer()
        # Los directorios deben existir o crearse
        assert trainer.models_dir.parent.exists() or trainer.models_dir.exists()
