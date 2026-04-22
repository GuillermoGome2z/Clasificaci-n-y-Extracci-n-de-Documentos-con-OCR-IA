"""
Configuración central de pytest con fixtures compartidas.
"""
import sys
from pathlib import Path

import pytest

# Agregar el directorio raíz al path para imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def extractor():
    """
    Instancia reutilizable de DataExtractor.
    Se crea una nueva instancia para cada test.
    """
    from src.extractor import DataExtractor
    return DataExtractor()


@pytest.fixture
def config():
    """
    Módulo de configuración del proyecto.
    """
    return sys.modules.get('config') or __import__('config')


@pytest.fixture
def pipeline():
    """
    Instancia reutilizable de OCRPipeline.
    NOTA: Importación lazy para evitar dependencias de cv2 en setup.
    """
    try:
        from src.pipeline import OCRPipeline
        return OCRPipeline()
    except (ImportError, AttributeError) as e:
        # Retorna None si cv2 no está disponible (permiten tests sin OCR)
        pytest.skip(f"Pipeline requires cv2: {str(e)}", allow_module_level=False)
        return None


@pytest.fixture
def sample_text_with_emails():
    """
    Texto de muestra con múltiples emails.
    """
    return """
    Contacto principal: john.doe@example.com
    Email secundario: jane.smith@company.org
    Para más info: info@domain.co.uk
    """


@pytest.fixture
def sample_text_with_phones():
    """
    Texto de muestra con múltiples teléfonos.
    """
    return """
    Teléfono: +34 912 345 678
    Celular: 555-1234-5678
    Otro: (202) 555-0173
    Mobil: +1 555 123 4567
    """


@pytest.fixture
def sample_text_with_dates():
    """
    Texto de muestra con múltiples fechas.
    """
    return """
    Fecha de emisión: 2024-03-15
    Vencimiento: 03/15/2024
    Día de pago: 15-03-2024
    Desde: 2024/03/15
    """


@pytest.fixture
def sample_text_with_urls():
    """
    Texto de muestra con URLs.
    """
    return """
    Sitio web: https://www.example.com
    URL: http://domain.org/page
    Portal: https://secure.company.com/api/v1
    FTP: ftp://files.example.net
    """


@pytest.fixture
def sample_text_with_currency():
    """
    Texto de muestra con valores monetarios.
    """
    return """
    Precio: $199.99
    Monto: €1,234.50
    Importe: 500.00 USD
    Total: £299.95
    """


@pytest.fixture
def sample_text_with_dni():
    """
    Texto de muestra con DNI (documentos españoles).
    """
    return """
    DNI: 12345678A
    Cédula: 87654321Z
    Identificación: 11223344B
    """


@pytest.fixture
def sample_text_with_rfc():
    """
    Texto de muestra con RFC (México).
    """
    return """
    RFC: AAA010101ABC
    RFC del vendedor: XYZ920815ABC
    Registro: ABP901215LB1
    """


@pytest.fixture
def empty_text():
    """
    Texto vacío.
    """
    return ""


@pytest.fixture
def none_text():
    """
    None (para probar robustez).
    """
    return None
