"""
Configuración central de pytest con fixtures compartidas.
"""
import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def extractor():
    """Instancia reutilizable de DataExtractor (nueva por cada test)."""
    from src.extractor import DataExtractor
    return DataExtractor()


@pytest.fixture
def config():
    """Módulo de configuración del proyecto."""
    return sys.modules.get('config') or __import__('config')


@pytest.fixture
def pipeline():
    """Instancia reutilizable de OCRPipeline (lazy, skip si cv2 no disponible)."""
    try:
        from src.pipeline import OCRPipeline
        return OCRPipeline()
    except (ImportError, AttributeError) as e:
        pytest.skip(f"Pipeline requires cv2: {str(e)}", allow_module_level=False)
        return None


@pytest.fixture
def sample_text_with_emails():
    """Texto con múltiples emails válidos."""
    return """
    Contacto principal: john.doe@example.com
    Email secundario: jane.smith@company.org
    Para más info: info@domain.co.uk
    """


@pytest.fixture
def sample_text_with_phones():
    """Texto con múltiples teléfonos guatemaltecos (XXXX-XXXX, prefijo 2-5)."""
    return """
    Teléfono oficina: 2345-6789
    Celular: 5123-4567
    Emergencias: +502 3456-7890
    """


@pytest.fixture
def sample_text_with_dates():
    """Texto con múltiples fechas numéricas."""
    return """
    Fecha de emisión: 2024-03-15
    Vencimiento: 03/15/2024
    Día de pago: 15-03-2024
    Desde: 2024/03/15
    """


@pytest.fixture
def sample_text_with_urls():
    """Texto con múltiples URLs HTTP/HTTPS."""
    return """
    Sitio web: https://www.example.com
    URL: http://domain.org/page
    Portal SAT: https://portal.sat.gob.gt/portal/
    """


@pytest.fixture
def sample_text_with_currency():
    """Texto con valores monetarios variados."""
    return """
    Precio: $199.99
    Monto: €1,234.50
    Importe: 500.00 USD
    Total: £299.95
    """


@pytest.fixture
def sample_text_with_nit():
    """Texto con múltiples NITs guatemaltecos."""
    return """
    NIT vendedor: 5356261-9
    N.I.T. cliente: 12345678-1
    Registro: 987654-3
    """


@pytest.fixture
def sample_text_with_dpi():
    """Texto con DPI/CUI guatemalteco en distintos formatos."""
    return """
    DPI titular: 2468 13579 2468
    CUI representante: 1234-56789-1234
    """


@pytest.fixture
def sample_text_factura_gt():
    """Texto representativo de una factura electrónica guatemalteca."""
    return """
    FACTURA ELECTRÓNICA
    Serie: FAC-2026-0001
    Fecha: 15 de marzo de 2026

    Emisor
    NIT: 5356261-9
    Nombre: Comercial Los Alpes S.A.
    Dirección: 6a Av. 4-12 zona 1, Guatemala

    Cliente
    NIT: 12345678-1
    Nombre: María García López
    DPI: 2468 13579 2468

    DESCRIPCIÓN          CANTIDAD    PRECIO UNIT.    TOTAL
    Servicio contable       1          Q 1,088.15    Q 1,088.15
    IVA 12%                                          Q   130.58
    TOTAL                                            Q 1,218.73

    Forma de pago: TRANSFERENCIA BANCARIA
    Web: https://portal.sat.gob.gt
    """


@pytest.fixture
def empty_text():
    """Texto vacío."""
    return ""


@pytest.fixture
def none_text():
    """None (para probar robustez)."""
    return None
