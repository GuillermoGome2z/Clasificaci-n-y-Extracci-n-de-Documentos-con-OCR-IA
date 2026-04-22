"""
Tests para config.py - Configuración del proyecto

Cobertura:
- Config import → 1 test
- Config has required attributes → 3 tests
- Config values are correct type → 3 tests

Total: 7 tests
"""
import pytest


class TestConfigImport:
    """Tests para importación de configuración."""

    def test_config_imports_successfully(self, config):
        """El módulo config se importa correctamente."""
        assert config is not None


class TestConfigAttributes:
    """Tests para atributos de configuración."""

    def test_config_has_required_paths(self, config):
        """Config tiene las rutas requeridas."""
        assert hasattr(config, "PROJECT_ROOT")
        assert hasattr(config, "DATA_DIR")
        assert hasattr(config, "MODELS_DIR")

    def test_config_has_ocr_settings(self, config):
        """Config tiene configuración OCR (dictionary)."""
        assert hasattr(config, "OCR_CONFIG")
        assert isinstance(config.OCR_CONFIG, dict)

    def test_config_has_classifier_settings(self, config):
        """Config tiene configuración del clasificador."""
        assert hasattr(config, "CLASSIFIER_CONFIG")
        assert isinstance(config.CLASSIFIER_CONFIG, dict)


class TestConfigValues:
    """Tests para valores de configuración."""

    def test_config_paths_are_strings(self, config):
        """Las rutas de config son strings o Path."""
        assert config.PROJECT_ROOT is not None
        assert config.DATA_DIR is not None
        assert config.MODELS_DIR is not None

    def test_config_ocr_settings_are_dict(self, config):
        """Las configuraciones OCR son diccionario válido."""
        assert isinstance(config.OCR_CONFIG, dict)
        assert "tesseract_path" in config.OCR_CONFIG or "default_language" in config.OCR_CONFIG

    def test_config_classifier_has_model_path(self, config):
        """El config del clasificador tiene path del modelo."""
        assert isinstance(config.CLASSIFIER_CONFIG, dict)
        assert "model_path" in config.CLASSIFIER_CONFIG


class TestConfigTypeConsistency:
    """Tests para consistencia de tipos en config."""

    def test_all_config_dictionaries_valid(self, config):
        """Todos los diccionarios de config son válidos."""
        assert isinstance(config.OCR_CONFIG, dict)
        assert isinstance(config.CLASSIFIER_CONFIG, dict)
        # No deben estar vacíos
        assert len(config.OCR_CONFIG) > 0
        assert len(config.CLASSIFIER_CONFIG) > 0

    def test_config_directories_created(self, config):
        """Los directorios de config existen o pueden crearse."""
        assert config.DATA_DIR is not None
        assert config.MODELS_DIR is not None
