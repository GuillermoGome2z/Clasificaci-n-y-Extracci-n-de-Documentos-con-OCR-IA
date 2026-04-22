# 🧪 Guía de Tests Unitarios

## Resumen

Este proyecto incluye una suite de tests unitarios usando **pytest** para validar la funcionalidad del módulo de extracción de datos y configuración.

### Estadísticas

```
Total de tests:    60
✅ Pasando:        57
⏭️  Skipped:       3 (requieren cv2/OCR real)
❌ Fallos:         0
```

---

## 📦 Instalación de Dependencias

### 1. Instalar pytest y herramientas de testing

```bash
pip install pytest pytest-cov
```

O usa el archivo `requirements-dev.txt`:

```bash
pip install -r requirements-dev.txt
```

### 2. Verificar instalación

```bash
pytest --version
```

---

## 🚀 Ejecutar los Tests

### Ejecutar TODOS los tests

```bash
pytest tests/
```

### Ejecutar con VERBOSIDAD (recomendado)

```bash
pytest tests/ -v
```

### Ejecutar tests ESPECÍFICOS

```bash
# Solo tests de extractor
pytest tests/test_extractor.py -v

# Solo tests de config
pytest tests/test_config.py -v

# Solo una clase de tests
pytest tests/test_extractor.py::TestExtractorEmails -v

# Solo un test específico
pytest tests/test_extractor.py::TestExtractorEmails::test_extract_emails_single_valid -v
```

### Ejecutar con REPORTE DE COBERTURA

```bash
pytest tests/ --cov=src --cov-report=html
```

Luego abre `htmlcov/index.html` en el navegador para ver cobertura visual.

### Ejecutar y MOSTRAR SALIDA DE PRINT

```bash
pytest tests/ -v -s
```

---

## 📋 Estructura de Tests

### test_config.py (9 tests)

Valida que la configuración del proyecto esté correcta:

- ✅ Importación del módulo config
- ✅ Existencia de rutas requeridas (PROJECT_ROOT, DATA_DIR, MODELS_DIR)
- ✅ Existencia de configuración OCR y Clasificador
- ✅ Consistencia de tipos en configuración

**Comando:**
```bash
pytest tests/test_config.py -v
```

### test_extractor.py (46 tests)

Valida la funcionalidad de extracción de datos (DataExtractor):

**Categorías de tests:**

- **Emails** (5 tests): Extrae emails válidos, múltiples, con subdominios
- **Teléfonos** (5 tests): Extrae formatos USA, con puntos, múltiples
- **Fechas** (5 tests): Formatos slash, dash, múltiples
- **URLs** (5 tests): HTTPS, HTTP, con rutas, múltiples
- **Moneda** (5 tests): USD $, EUR, códigos, separadores de miles
- **DNI** (4 tests): Formato válido, con puntos, vacío
- **RFC** (4 tests): Formato válido, patrón matching, vacío
- **Método extract_all()** (3 tests): Orquestación de todas extracciones
- **Patrones personalizados** (2 tests): Regex válido, inválido
- **Líneas** (2 tests): Extrae líneas, filtra vacías
- **Edge cases** (5 tests): Caracteres especiales, unicode, textos largos

**Comando:**
```bash
pytest tests/test_extractor.py -v
```

### test_pipeline.py (5 tests, 3 skipped)

Valida importaciones y estructura del pipeline:

- ✅ Importación de extractor
- ✅ Importación de pipeline (skipped si cv2 no disponible)
- ✅ Clase DataExtractor existe y se instantía
- ⏭️ Documentclassifier tests (skipped hasta entrenar modelo)

**Comando:**
```bash
pytest tests/test_pipeline.py -v
```

---

## 🔍 Casos de Prueba - Ejemplos

### Extracción de Emails

```python
# Test: email válido
text = "Contacto: john@example.com"
result = extractor.extract_emails(text)
# → ["john@example.com"]

# Test: email con subdominios
text = "Email: info@mail.company.co.uk"
result = extractor.extract_emails(text)
# → ["info@mail.company.co.uk"]
```

### Extracción de Teléfonos

```python
# Test: formato USA
text = "Teléfono: (202) 555-0173"
result = extractor.extract_phones(text)
# → ["(202) 555-0173"]

# Test: con puntos
text = "Tel: 555.123.4567"
result = extractor.extract_phones(text)
# → ["(555) 123-4567"]
```

### Extracción de Todas (extract_all)

```python
text = """
Contacto: juan@empresa.com
Teléfono: (202) 555-0173
Web: https://www.empresa.com
"""
result = extractor.extract_all(text)
# → {
#   "emails": ["juan@empresa.com"],
#   "phones": ["(202) 555-0173"],
#   "urls": ["https://www.empresa.com"],
#   "dates": [],
#   "currency": [],
#   "dni": [],
#   "rfc": []
# }
```

---

## ⚠️ Tests Skipped (Esperados)

Algunos tests se saltan porque requieren dependencias que no están completamente configuradas:

```
SKIPPED tests/test_pipeline.py::TestPipelineImports::test_pipeline_module_imports_or_skips
  → Razón: cv2/numpy no compatible (Phase 1 de testing)

SKIPPED tests/test_pipeline.py::TestClassifierImports::test_document_classifier_class_exists
  → Razón: Clasificador aún sin entrenar (Phase 2 de testing)

SKIPPED tests/test_pipeline.py::TestClassifierImports::test_classifier_can_be_instantiated
  → Razón: Clasificador aún sin entrenar (Phase 2 de testing)
```

Estos tests se habilitarán en fases futuras cuando:
1. Se resuelva NumPy 2.x ↔ OpenCV compat
2. Se entrene el modelo del clasificador ML

---

## 🛠️ Fixtures Disponibles (conftest.py)

Todos los tests tienen acceso a estos fixtures compartidos:

### `extractor`
Instancia fresca de `DataExtractor` para cada test

```python
def test_example(extractor):
    result = extractor.extract_emails("test@example.com")
    assert isinstance(result, list)
```

### `config`
Módulo de configuración del proyecto

```python
def test_example(config):
    assert config.PROJECT_ROOT is not None
```

### `pipeline`
Instancia de OCRPipeline (con skip si cv2 no disponible)

### Textos de Muestra

- `sample_text_with_emails`: Texto con múltiples emails
- `sample_text_with_phones`: Texto con múltiples teléfonos
- `sample_text_with_dates`: Texto con múltiples fechas
- `sample_text_with_urls`: Texto con múltiples URLs
- `sample_text_with_currency`: Texto con múltiples valores monetarios
- `sample_text_with_dni`: Texto con múltiples DNI
- `sample_text_with_rfc`: Texto con múltiples RFC
- `empty_text`: String vacío ("")
- `none_text`: None

---

## 📊 Mostrar Resumen

```bash
# Resumen corto
pytest tests/ --tb=no

# Resumen con tiempo
pytest tests/ -v --durations=10

# Mostrar solo fallos
pytest tests/ --tb=short --failed-first
```

---

## ✅ Checklist Pre-Commit

Antes de hacer commit de cambios:

```bash
# 1. Ejecutar todos los tests
pytest tests/ -v

# 2. Verificar cobertura
pytest tests/ --cov=src

# 3. Limpiar cache
pytest --cache-clear

# 4. Ejecutar specific module si se cambió
pytest tests/test_extractor.py -v
```

---

## 🔬 Agregar Nuevos Tests

### Template de Nuevo Test

```python
# En tests/test_module.py

def test_new_feature(extractor):
    """Descripción de qué se prueba."""
    # Arrange
    test_data = "datos de entrada"
    
    # Act
    result = extractor.method_to_test(test_data)
    
    # Assert
    assert isinstance(result, list)
    assert len(result) > 0
```

### Para Agregar Nueva Fixture

```python
# En tests/conftest.py

@pytest.fixture
def new_sample_data():
    """Descripción de los datos."""
    return "data here"
```

---

## 📈 Próximos Pasos - Fase 2

Cuando se complete:

1. **Entrenar Clasificador ML** → Habilitar tests de classifier
2. **Resolver NumPy 2.x** → Habilitar tests OCR real (cv2)
3. **Agregar más tests** → UI, Integration tests, Performance tests

---

## 🆘 Troubleshooting

### Problema: "ModuleNotFoundError: No module named 'pytest'"
**Solución:** Instala pytest
```bash
pip install pytest
```

### Problema: "assert 0 >= 1" en test de currency
**Posible causa:** El patrón regex de moneda es muy específico
**Solución:** Verificar en `src/extractor.py` el patrón "currency"

### Problema: Tests muy lentos
**Solución:** Ejecuta solo tests rápidos
```bash
pytest tests/ -v --durations=5
```

### Problema: cv2 import errors
**Posible causa:** NumPy 2.x incompatibilidad
**Solución:** Está en tracking, estos tests se saltan (SKIPPED)

---

**Last Updated:** 22 de Abril de 2026  
**Status:** ✅ 57/60 tests passing  
**Next Review:** Post-entrenamiento Clasificador
