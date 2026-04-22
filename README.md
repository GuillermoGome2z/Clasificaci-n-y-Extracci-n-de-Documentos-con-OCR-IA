# OCR IA Proyecto

MVP (Minimum Viable Product) profesional de OCR con Machine Learning en Python.

## 🎯 Características

- ✅ **OCR avanzado** con Pytesseract (soporte multi-idioma)
- ✅ **Extracción de datos** (emails, teléfonos, fechas, URLs, DNI, RFC, etc.)
- ✅ **Clasificación de documentos** con Machine Learning
- ✅ **Interfaz web** interactiva con Streamlit
- ✅ **Procesamiento de PDFs** e imágenes
- ✅ **Exportación JSON** de resultados
- ✅ **Pipeline integrado** y extensible

## 📋 Estructura del Proyecto

```
ocr-ia-proyecto/
├── src/                      # Código principal
│   ├── __init__.py
│   ├── ocr.py               # Procesamiento OCR
│   ├── classifier.py        # Clasificación ML
│   ├── extractor.py         # Extracción de datos
│   └── pipeline.py          # Pipeline integrado
├── app/                      # Aplicación Streamlit
│   └── app.py
├── data/                     # Datos (imágenes, PDFs)
│   ├── raw/
│   └── processed/
├── models/                   # Modelos entrenados
├── config.py               # Configuración
├── requirements.txt        # Dependencias
└── README.md

```

## 🚀 Instalación Rápida (Windows)

### Paso 1: Crear Entorno Virtual

```powershell
# Abre PowerShell en la carpeta del proyecto
cd "C:\Users\ACER\OneDrive\Escritorio\ocr-ia-proyecto"

# Crear el entorno virtual
python -m venv venv

# Activar el entorno
.\venv\Scripts\Activate.ps1
```

Si recibes un error de permisos en PowerShell, ejecuta esto primero:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Paso 2: Instalar Tesseract (Obligatorio)

**⚠️ Tesseract debe estar instalado en Windows primero**

1. Descarga el instalador desde:
   https://github.com/UB-Mannheim/tesseract/wiki

2. Ejecuta el instalador (descarga algo como: `tesseract-ocr-w64-setup-v5.x.x.exe`)

3. **IMPORTANTE**: Durante la instalación:
   - Selecciona "Additional language data"
   - Instala al menos "Spanish" y "English"
   - Anota la carpeta de instalación (normalmente: `C:\Program Files\Tesseract-OCR`)

4. Verifica la instalación en PowerShell:
```powershell
tesseract --version
```

### Paso 3: Instalar Dependencias Python

```powershell
# Asegúrate de que el entorno virtual está activado
pip install -r requirements.txt
```

### Paso 4: Ejecutar la Aplicación

```powershell
# Desde el directorio del proyecto
streamlit run app/app.py
```

La aplicación se abrirá en tu navegador en `http://localhost:8501`

## 📖 Uso de la Aplicación

### 1. Configuración Inicial
- En la barra lateral, marca "Tengo Tesseract instalado"
- Verifica la ruta (por defecto: `C:\Program Files\Tesseract-OCR\tesseract.exe`)
- Haz clic en "Inicializar Pipeline"

### 2. Procesar Archivo
- Ve a la pestaña "Procesar Archivo"
- Carga una imagen (JPG, PNG) o PDF
- Selecciona el idioma
- Haz clic en "Procesar"

### 3. Ver Resultados
- Los resultados aparecen en la pestaña "Resultados"
- Puedes descargar los datos en JSON

## 💻 Uso en Python

```python
from src.pipeline import OCRPipeline
from config import TESSERACT_PATH

# Crear pipeline
pipeline = OCRPipeline(tesseract_path=TESSERACT_PATH)

# Procesar una imagen
resultado = pipeline.process_image("ruta/a/imagen.jpg", lang="spa")

# Procesar un PDF
resultado = pipeline.process_pdf("ruta/a/documento.pdf", lang="spa")

# Ver resultado en JSON
import json
print(json.dumps(resultado, indent=2, ensure_ascii=False))
```

### Resultado de ejemplo:
```json
{
  "status": "success",
  "extracted_text": "Factura #001234...",
  "steps": {
    "ocr": {
      "text": "...",
      "confidence": 95.5,
      "language": "spa"
    },
    "extraction": {
      "emails": ["cliente@email.com"],
      "phones": ["(123) 456-7890"],
      "dates": ["15/03/2024"],
      "currency": ["$1,500.00"],
      "dni": ["12345678-A"]
    },
    "classification": {
      "class": "factura",
      "confidence": 0.92
    }
  }
}
```

## 🔧 Uso Avanzado

### Entrenar el Clasificador

```python
from src.pipeline import OCRPipeline

pipeline = OCRPipeline(tesseract_path=TESSERACT_PATH)

# Datos de entrenamiento (texto, etiqueta)
datos_entrenamiento = [
    ("Factura #001... Total: $1000", "factura"),
    ("Recibí la cantidad de...", "recibo"),
    ("Por este medio...", "contrato"),
]

# Entrenar
pipeline.train_classifier(datos_entrenamiento)

# Guardar modelo
pipeline.save_classifier("models/classifier.pkl")
```

### Usar OCR directamente

```python
from src.ocr import OCRProcessor

ocr = OCRProcessor(tesseract_path=TESSERACT_PATH)

# Extraer texto de imagen
resultado = ocr.extract_text_from_image("imagen.jpg", lang="spa")
print(resultado["text"])

# Extraer texto de PDF
resultado = ocr.extract_text_from_pdf("documento.pdf", lang="spa")
for pagina in resultado["pages"]:
    print(f"Página {pagina['page']}: {pagina['text']}")
```

### Extraer datos específicos

```python
from src.extractor import DataExtractor

extractor = DataExtractor()

texto = "Contacto: juan@email.com, Tel: (123) 456-7890, RFC: ABC123456DEF"

# Extraer tipos específicos
emails = extractor.extract_emails(texto)
telefonos = extractor.extract_phones(texto)
rfc = extractor.extract_rfc(texto)

# O extraer todo de una vez
datos = extractor.extract_all(texto)
print(datos)
```

## ⚠️ Solución de Problemas

### Error: "pytesseract.TesseractNotFoundError"
**Solución**: Tesseract no está instalado o la ruta es incorrecta.
- Verifica que Tesseract esté instalado en Windows
- Actualiza la ruta en `config.py` si lo instalaste en otra carpeta
- Reinicia VS Code después de instalar Tesseract

### Error: "No module named 'cv2'"
**Solución**: Las dependencias no se instalaron correctamente.
```powershell
pip install --upgrade opencv-python
```

### Error en OCR: Texto pobre o confianza baja
**Soluciones**:
- Usa imágenes de alta resolución (mínimo 150 DPI)
- Asegúrate de que el documento esté bien iluminado
- Usa imágenes escaneadas en lugar de fotos
- Verifica el idioma seleccionado

### El PDF no se procesa
**Solución**: Instala el complemento de PDF:
```powershell
pip install pdf2image
# También necesitarás poppler instalado en Windows
```

## 📦 Dependencias

- **pytesseract** (0.3.10): Interfaz de Tesseract para Python
- **pdfplumber** (0.10.3): Extracción de PDFs
- **opencv-python** (4.8.1.78): Procesamiento de imágenes
- **scikit-learn** (1.3.2): Machine Learning
- **streamlit** (1.30.0): Interfaz web
- **Pillow** (10.1.0): Manipulación de imágenes
- **pandas** (2.1.3): Análisis de datos
- **joblib** (1.3.2): Serialización de modelos
- **fpdf2** (2.7.0): Generación de PDFs
- **numpy** (1.24.3): Computación numérica

## 🎓 Ejemplos de Casos de Uso

### Procesamiento de Facturas
```python
resultado = pipeline.process_image("factura.jpg")
# Extrae: Monto, fecha, RFC del vendedor, datos del cliente
```

### Clasificación Automática
```python
resultado = pipeline.process_file("documento.pdf")
clase = resultado["steps"]["classification"]["class"]
# Valores posibles: factura, recibo, contrato, otro
```

### Pipeline Batch
```python
import os

carpeta = "datos/raw"
for archivo in os.listdir(carpeta):
    ruta = os.path.join(carpeta, archivo)
    resultado = pipeline.process_file(ruta)
    # Guardar resultado
    with open(f"resultados/{archivo}.json", "w") as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)
```

## 🚀 Próximas Mejoras

- [ ] API REST con FastAPI
- [ ] Procesamiento paralelo de múltiples archivos
- [ ] Mejora de modelos ML con más datos
- [ ] Soporte para OCR de tablas complejas
- [ ] Interfaz de administración para entrenar modelos
- [ ] Cache de resultados
- [ ] Validación de datos extraídos

## 📝 Notas Importantes

1. **Tesseract es obligatorio**: Sin él, no funcionará el OCR
2. **Primer uso**: La primera ejecución puede tardar mientras se carga el modelo
3. **Calidad de imágenes**: A mejor calidad, mejores resultados de OCR
4. **Memoria**: Procesar PDFs grandes puede consumir memoria
5. **Idiomas**: Asegúrate de instalar los idiomas necesarios en Tesseract

## 🤝 Contribuciones

Este es un proyecto educativo. Siéntete libre de modificar y expandir.

## 📄 Licencia

Código abierto - Úsalo libremente

---

**¿Necesitas ayuda?** Revisa la sección "Solución de Problemas" o consulta la documentación de las librerías utilizadas.
