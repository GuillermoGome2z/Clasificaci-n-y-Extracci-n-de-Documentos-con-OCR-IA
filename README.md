# Sistema Inteligente OCR + IA para Clasificación y Extracción de Documentos

> **Proyecto 04** — Clasificación y Extracción de Documentos con OCR + Inteligencia Artificial

---

## Información Institucional

| Campo | Detalle |
|---|---|
| **Universidad** | Universidad Mariano Gálvez de Guatemala |
| **Facultad** | Ingeniería en Sistemas |
| **Curso** | 045 — Inteligencia Artificial |
| **Proyecto** | Proyecto 04 |
| **Catedrático** | Ing. MA. Carmelo Estuardo Mayén Monterroso |
| **Ciclo** | 2026 |

---

## Integrantes del Equipo

| Nombre | Carné | Rol |
|---|---|---|
| Guillermo Jose Gomez Aguilera | 1790-22-16429 | Scrum Master |
| Wilson Eduardo Hernandez Lopez | 1790-22-7315 | Desarrollador |
| Bagner Francisco Ojeda Esquite | 1790-18-25212 | Desarrollador |
| Amner Alberto Perez Marroquin | 1790-22-7230 | Documentación |
| Teddy Leonardo Hernandez Perez | 1790-22-2563 | Documentación |

---

## Descripción del Proyecto

Sistema que recibe una imagen (JPG/PNG/BMP) o un PDF de un documento guatemalteco,
extrae el texto mediante OCR con Tesseract, extrae campos relevantes usando expresiones
regulares especializadas en documentos guatemaltecos (NIT, DPI, facturas FEL/SAT, montos
en GTQ, fechas) y clasifica automáticamente el tipo de documento usando un modelo de
Machine Learning (TF-IDF + LinearSVC). El resultado se exporta como JSON descargable.

**Pipeline completo:**
```
Imagen / PDF  →  OCR (Tesseract)  →  Extracción Regex  →  Clasificación ML  →  JSON
```

---

## Categorías de Documentos Soportadas

| Categoría | Descripción |
|---|---|
| `factura` | Facturas de empresa, FEL/SAT Guatemala |
| `recibo` | Recibos de pago |
| `contrato` | Contratos y acuerdos |
| `constancia` | Constancias de trabajo, estudio, etc. |
| `carta_formal` | Cartas formales y oficios |
| `identificacion` | DPI, pasaportes, documentos de identidad |
| `otro` | Documentos no clasificados en las categorías anteriores |

---

## Tecnologías Utilizadas

| Librería | Uso |
|---|---|
| **Python 3.10+** | Lenguaje principal |
| **Streamlit** | Interfaz web interactiva |
| **Tesseract OCR** | Reconocimiento óptico de caracteres (español + inglés) |
| **pytesseract** | Wrapper Python para Tesseract |
| **OpenCV** | Preprocesamiento de imágenes (escala de grises, binarización) |
| **pdfplumber** | Extracción de texto nativo de PDFs |
| **Pillow** | Carga y conversión de imágenes |
| **scikit-learn** | TF-IDF + LinearSVC (clasificación ML) |
| **joblib** | Serialización del modelo entrenado |
| **pandas** | Organización del dataset y ground truth |
| **numpy** | Cómputo numérico |
| **fpdf2** | Generación de documentos PDF sintéticos para el dataset |
| **pytest** | Tests automatizados (158 tests) |

---

## Características Principales

- OCR en **español + inglés** (`spa+eng`) con Tesseract 5
- Soporte de imágenes: **JPG, PNG, BMP**
- Soporte de **PDF** con texto nativo y fallback a OCR
- Soporte de **PDF multipágina** con navegación por página/factura
- Extracción de datos guatemaltecos:
  - **NIT** — formato clásico con guion y FEL sin guion
  - **DPI / CUI** — 13 dígitos (`XXXX XXXXX XXXX`)
  - **Moneda GTQ** — valores con Q, GTQ, símbolo
  - **Serie y UUID SAT/FEL** — autorización y número DTE
  - **Fechas** — numéricas y en español (`28-abr-2026`)
  - **Forma de pago** — efectivo, cheque, transferencia, tarjeta
- Clasificación automática en 7 categorías (F1-macro: 0.9940)
- Exportación JSON profesional con `original_filename` y `processed_at`
- Interfaz Streamlit con tema oscuro y diseño premium
- Validación de archivos y manejo de errores robusto
- 158 tests automatizados (pytest)

---

## Instalación en Windows

### Paso 1 — Clonar el repositorio

```powershell
git clone <URL_DEL_REPOSITORIO>
cd ocr-ia-proyecto
```

> Reemplazar `<URL_DEL_REPOSITORIO>` con la URL real del repositorio en GitHub.

### Paso 2 — Crear y activar el entorno virtual

```powershell
python -m venv venv
venv\Scripts\activate
```

Si hay error de permisos en PowerShell:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Paso 3 — Instalar dependencias

```powershell
pip install -r requirements.txt
```

### Paso 4 — Ejecutar la aplicación

```powershell
streamlit run app/app.py
```

La app se abre automáticamente en `http://localhost:8501`

---

## Instalación de Tesseract OCR (obligatorio)

El OCR no funcionará sin Tesseract instalado en el sistema.

1. Descargar el instalador desde:
   [github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
   (buscar `tesseract-ocr-w64-setup-v5.x.x.exe`)

2. Ejecutar el instalador:
   - Marcar **Additional language data**
   - Seleccionar **Spanish** e **English**
   - Ruta recomendada: `C:\Program Files\Tesseract-OCR`

3. Verificar instalación:

```powershell
tesseract --list-langs
```

Resultado esperado:
```
eng
spa
```

4. La aplicación auto-detecta la ruta de Tesseract. Si está en una ruta distinta,
   se puede configurar en la barra lateral de la app.

---

## Estructura del Proyecto

```
ocr-ia-proyecto/
├── app/
│   └── app.py               # Interfaz Streamlit
├── src/
│   ├── ocr.py               # Módulo OCR con Tesseract
│   ├── extractor.py         # Extracción de datos con regex (Guatemala)
│   ├── classifier.py        # Clasificación ML (TF-IDF + LinearSVC)
│   ├── pipeline.py          # Pipeline integrado OCR → Extracción → Clasificación
│   ├── preprocess.py        # Preprocesamiento de imágenes
│   ├── predict.py           # Utilidades de predicción
│   └── dataset_validator.py # Validación del dataset
├── data/
│   ├── training/            # 500 documentos sintéticos (70 por categoría)
│   ├── ground_truth.csv     # Etiquetas del dataset
│   └── README.md            # Descripción del dataset
├── models/
│   └── classifier_model.joblib  # Modelo SVM entrenado (incluido en el repo)
├── demos/
│   ├── demo_*.pdf           # PDFs de demostración por categoría
│   └── _gen_demos.py        # Script de generación de demos
├── tests/
│   ├── test_classifier.py
│   ├── test_extractor.py
│   ├── test_pipeline.py
│   ├── test_config.py
│   └── test_trainer.py
├── notebooks/
│   ├── 01_EDA.ipynb         # Análisis exploratorio del dataset
│   ├── 02_train.ipynb       # Entrenamiento del modelo
│   └── 03_evaluation.ipynb  # Evaluación, métricas, matriz de confusión
├── docs/                    # Documentación técnica (en preparación)
├── config.py                # Configuración global del proyecto
├── train_classifier.py      # Script de entrenamiento del clasificador
├── requirements.txt         # Dependencias del proyecto
└── README.md
```

---

## Uso Básico

1. Inicializar el pipeline en la barra lateral (marcar "Tesseract instalado" y presionar **Inicializar Pipeline**)
2. Ir a la pestaña **Procesar Archivo**
3. Subir una imagen (JPG/PNG/BMP) o PDF
4. Presionar **Procesar**
5. Ver resultados en la pestaña **Resultados**:
   - Texto OCR extraído
   - Datos estructurados (NIT, fechas, montos, series SAT...)
   - Clasificación automática del tipo de documento
6. Descargar el resultado como **JSON** desde la sección de exportación

---

## Entrenar o Reentrenar el Modelo

El modelo ya está entrenado e incluido en `models/classifier_model.joblib`.
Para reentrenarlo con los datos del dataset:

```powershell
python train_classifier.py
```

Esto genera un nuevo `classifier_model.joblib` en `models/` con el rendimiento actual del dataset.

---

## Ejecutar Tests

```powershell
python -m pytest tests/ -q
```

Resultado esperado: **158 tests pasando**.

---

## Estado Actual del Proyecto

| Métrica | Valor |
|---|---|
| Categorías de documentos | 7 |
| Documentos sintéticos de entrenamiento | ~500 |
| Accuracy del modelo (test set) | 100% |
| F1-macro | 0.9940 |
| Tests automatizados | 158 pasando |
| Soporte PDF multipágina | Sí |
| Idiomas OCR | Español + Inglés |
| Exportación | JSON |

---

## Errores Comunes

| Error | Causa | Solución |
|---|---|---|
| `TesseractNotFoundError` | Tesseract no instalado o ruta incorrecta | Instalar Tesseract desde UB-Mannheim, verificar ruta |
| `spa` no disponible | Idioma español no instalado en Tesseract | Reinstalar Tesseract marcando "Spanish" en opciones |
| `ModuleNotFoundError` | Entorno virtual no activado o sin dependencias | `venv\Scripts\activate` y `pip install -r requirements.txt` |
| La app no abre | Puerto 8501 ocupado | `streamlit run app/app.py --server.port 8502` |
| PDF sin texto | PDF escaneado sin capa de texto | El sistema aplica OCR automáticamente como fallback |

---

## Aviso Ético

> **Este sistema debe usarse únicamente con documentos ficticios, sintéticos, propios
> o debidamente anonimizados. Nunca con documentos reales de terceros sin autorización.**
>
> - Los resultados generados por OCR e IA deben ser **verificados por una persona**
>   antes de tomar cualquier decisión basada en ellos.
> - No procesar documentos con datos sensibles o confidenciales sin la autorización
>   correspondiente.
> - Los archivos se procesan en memoria y no se almacenan en el servidor
>   (privacidad por diseño).
> - Proyecto académico — no apto para uso en producción sin validación adicional.

---

## Video de Demostración

> **Pendiente** — Enlace al video demostrativo (3–5 min) será agregado antes de la entrega final.

---

*Universidad Mariano Gálvez de Guatemala · Facultad de Ingeniería · Curso 045 — Inteligencia Artificial · Proyecto 04 · 2026*
