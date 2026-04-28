"""Configuración del proyecto OCR IA."""

import os
import shutil
import logging as _logging
from pathlib import Path

# Rutas principales
PROJECT_ROOT = Path(__file__).parent
SRC_DIR = PROJECT_ROOT / "src"
APP_DIR = PROJECT_ROOT / "app"
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"

# Crear directorios si no existen
for directory in [DATA_DIR, MODELS_DIR]:
    directory.mkdir(exist_ok=True)


def find_tesseract_path() -> str | None:
    """
    Busca Tesseract en 3 lugares por orden de prioridad:
    1. Variable de entorno TESSERACT_PATH
    2. PATH del sistema operativo (shutil.which)
    3. Ruta por defecto de Windows

    Returns:
        str con la ruta si se encuentra, None si no.
    """
    # Prioridad 1: variable de entorno
    env_path = os.getenv("TESSERACT_PATH")
    if env_path and Path(env_path).exists():
        return env_path

    # Prioridad 2: PATH del sistema
    system_path = shutil.which("tesseract")
    if system_path:
        return system_path

    # Prioridad 3: ruta por defecto Windows
    windows_default = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if Path(windows_default).exists():
        return windows_default

    return None


# Configuración de Tesseract (auto-detección)
TESSERACT_PATH = find_tesseract_path()

# Configuración de logging
_logging.basicConfig(
    level=_logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)

# Configuración de OCR
OCR_CONFIG = {
    "default_language": "spa",
    "languages": ["spa", "eng", "fra", "deu"],
    "tesseract_path": TESSERACT_PATH,
}

# Configuración de clasificación
CLASSIFIER_CONFIG = {
    "model_path": str(MODELS_DIR / "classifier_model.joblib"),
    "max_features": 5000,
    "ngram_range": (1, 2),
    "categories": ["factura", "recibo", "contrato",
                   "constancia", "carta_formal", "identificacion", "otro"]
}

# Configuración de datos
DATA_CONFIG = {
    "raw_data_path": str(DATA_DIR / "raw"),
    "processed_data_path": str(DATA_DIR / "processed"),
}

# Configuración de Streamlit
STREAMLIT_CONFIG = {
    "theme": {
        "primaryColor": "#2E86AB",
        "backgroundColor": "#F5F5F5",
        "secondaryBackgroundColor": "#D0D0D0",
        "textColor": "#262730",
        "font": "sans serif",
    }
}
