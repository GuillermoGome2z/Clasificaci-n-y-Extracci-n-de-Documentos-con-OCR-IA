"""Configuración del proyecto OCR IA."""

import os
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

# Configuración de Tesseract (Windows)
# Cambiar esta ruta según tu instalación
TESSERACT_PATH = os.getenv(
    "TESSERACT_PATH",
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# Configuración de OCR
OCR_CONFIG = {
    "default_language": "spa",
    "languages": ["spa", "eng", "fra", "deu"],
    "tesseract_path": TESSERACT_PATH,
}

# Configuración de clasificación
CLASSIFIER_CONFIG = {
    "model_path": str(MODELS_DIR / "classifier.pkl"),
    "classes": ["factura", "recibo", "contrato", "otro"],
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
