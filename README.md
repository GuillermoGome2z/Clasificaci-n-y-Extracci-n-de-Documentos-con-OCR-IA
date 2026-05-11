<div align="center">

# 🤖 Sistema Inteligente OCR + IA

### Clasificación y Extracción de Documentos con OCR + Machine Learning

*Extrae, clasifica y estructura documentos guatemaltecos con Tesseract OCR e Inteligencia Artificial*

---

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Tesseract OCR](https://img.shields.io/badge/Tesseract_OCR-5.x-4A90D9?style=for-the-badge&logo=googletranslate&logoColor=white)](https://github.com/UB-Mannheim/tesseract)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)
[![Tests](https://img.shields.io/badge/Tests-158%20passing-22c55e?style=for-the-badge&logo=pytest&logoColor=white)]()
[![OCR + IA](https://img.shields.io/badge/OCR%20%2B%20IA-spa%2Beng-6366f1?style=for-the-badge&logo=openai&logoColor=white)]()
[![Estado](https://img.shields.io/badge/Estado-Funcional-10b981?style=for-the-badge)]()
[![Proyecto](https://img.shields.io/badge/Proyecto-04-f59e0b?style=for-the-badge)]()

</div>

---

<!-- BANNER: descomenta y reemplaza cuando tengas la imagen lista
<div align="center">
  <img src="assets/banner.png" alt="Banner OCR IA" width="100%"/>
</div>
-->

## 🏛️ Información Institucional

<div align="center">

| Campo | Detalle |
|:---:|:---|
| 🏫 **Universidad** | Universidad Mariano Gálvez de Guatemala |
| 🎓 **Facultad** | Ingeniería en Sistemas |
| 📚 **Curso** | 045 — Inteligencia Artificial |
| 📁 **Proyecto** | Proyecto 04 |
| 👨‍🏫 **Catedrático** | Ing. MA. Carmelo Estuardo Mayén Monterroso |
| 📅 **Ciclo** | 2026 |

</div>

---

## 👥 Integrantes del Equipo

<div align="center">

| Nombre Completo | Carné | Rol |
|:---|:---:|:---:|
| Guillermo Jose Gomez Aguilera | `1790-22-16429` | 🧭 Scrum Master |
| Wilson Eduardo Hernandez Lopez | `1790-22-7315` | 💻 Desarrollador |
| Bagner Francisco Ojeda Esquite | `1790-18-25212` | 💻 Desarrollador |
| Amner Alberto Perez Marroquin | `1790-22-7230` | 📝 Documentación |
| Teddy Leonardo Hernandez Perez | `1790-22-2563` | 📝 Documentación |

</div>

---

## 📖 Descripción del Proyecto

Sistema inteligente que recibe una imagen (`JPG`, `PNG`, `BMP`) o un `PDF` de un documento guatemalteco, extrae su texto mediante OCR con Tesseract, identifica campos relevantes usando expresiones regulares especializadas (NIT, DPI, facturas FEL/SAT, montos en GTQ, fechas) y clasifica automáticamente el tipo de documento usando un modelo de Machine Learning (`TF-IDF + LinearSVC`). El resultado se exporta como JSON descargable.

---

## ⚡ Flujo del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   📄 Documento   →   🔍 OCR   →   🧩 Extracción   →   🏷️ Clasificación IA   →   📦 JSON   │
│  (PDF / Imagen)     Tesseract    Regex Guatemaltecos  TF-IDF + SVC    Descargable  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

<div align="center">

```
     📄 PDF / JPG / PNG / BMP
            │
            ▼
     🔍 Tesseract OCR
      (spa + eng)
            │
            ▼
     🧩 Extractor Regex
      NIT · DPI · GTQ · SAT
            │
            ▼
     🤖 Clasificador IA
      TF-IDF + LinearSVC
            │
            ▼
     📦 JSON Estructurado
      + Exportación / UI
```

</div>

---

## ✨ Características Destacadas

| Característica | Detalle |
|:---|:---|
| 🌐 **OCR Español + Inglés** | `spa+eng` con Tesseract 5, configurado automáticamente |
| 📑 **PDF Multipágina** | Procesa todas las páginas de un solo PDF, navega sin reprocesar |
| 🇬🇹 **Datos Guatemaltecos** | NIT (FEL + clásico), DPI/CUI, GTQ, UUID SAT, fechas en español |
| 🤖 **Clasificación IA** | TF-IDF + LinearSVC, 7 categorías, F1-macro: **0.9940** |
| 📦 **Exportación JSON** | Resultado estructurado con `original_filename` y `processed_at` |
| 🧪 **Tests Automatizados** | 158 tests con pytest, todos pasando |
| 🎨 **UI Premium** | Interfaz Streamlit con tema oscuro y diseño moderno |
| 🛡️ **Validación Estricta** | Bloqueo de carpetas, múltiples archivos y formatos no soportados |

---

## 🏷️ Categorías de Documentos

<div align="center">

| Categoría | Emoji | Descripción |
|:---:|:---:|:---|
| `factura` | 🧾 | Facturas de empresa, FEL/SAT Guatemala |
| `recibo` | 🧾 | Recibos de pago |
| `contrato` | 📜 | Contratos y acuerdos |
| `constancia` | 📋 | Constancias de trabajo, estudio, etc. |
| `carta_formal` | 📩 | Cartas formales y oficios |
| `identificacion` | 🪪 | DPI, pasaportes, documentos de identidad |
| `otro` | 📄 | Documentos no clasificados en las categorías anteriores |

</div>

---

## 🛠️ Tecnologías Utilizadas

<details>
<summary><strong>Ver stack completo</strong></summary>

<br>

| Librería | Versión | Uso |
|:---|:---:|:---|
| **Python** | 3.10+ | Lenguaje principal |
| **Streamlit** | 1.x | Interfaz web interactiva |
| **Tesseract OCR** | 5.x | Reconocimiento óptico de caracteres (spa + eng) |
| **pytesseract** | — | Wrapper Python para Tesseract |
| **OpenCV** | — | Preprocesamiento de imágenes |
| **pdfplumber** | — | Extracción de texto nativo de PDFs |
| **Pillow** | — | Carga y conversión de imágenes |
| **scikit-learn** | — | TF-IDF + LinearSVC (clasificación ML) |
| **joblib** | — | Serialización del modelo entrenado |
| **pandas** | — | Organización del dataset y ground truth |
| **numpy** | — | Cómputo numérico |
| **fpdf2** | — | Generación de PDFs sintéticos para el dataset |
| **pytest** | — | Tests automatizados (158 tests) |

</details>

---

## 🚀 Instalación en Windows

### 1️⃣ Clonar el repositorio

```powershell
git clone https://github.com/GuillermoGome2z/Clasificaci-n-y-Extracci-n-de-Documentos-con-OCR-IA.git
cd Clasificaci-n-y-Extracci-n-de-Documentos-con-OCR-IA
```

### 2️⃣ Crear y activar entorno virtual

```powershell
python -m venv venv
venv\Scripts\activate
```

> Si hay error de permisos en PowerShell:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### 3️⃣ Instalar dependencias

```powershell
pip install -r requirements.txt
```

### 4️⃣ Instalar Tesseract OCR (obligatorio)

> ⚠️ El OCR no funcionará sin Tesseract instalado en el sistema.

1. Descargar el instalador desde:
   **[github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)**
   (buscar `tesseract-ocr-w64-setup-v5.x.x.exe`)

2. Ejecutar el instalador:
   - Marcar **Additional language data**
   - Seleccionar **Spanish** e **English**
   - Ruta recomendada: `C:\Program Files\Tesseract-OCR`

3. Verificar instalación:

```powershell
tesseract --list-langs
```

Resultado esperado: `eng`, `spa` en la lista.

4. La app auto-detecta la ruta de Tesseract. Si está en ruta distinta, configúrala en la barra lateral.

### 5️⃣ Ejecutar la aplicación

```powershell
streamlit run app/app.py
```

La app se abre automáticamente en **`http://localhost:8501`** 🎉

---

## 🖥️ Capturas de Pantalla

> Las capturas se agregarán en `assets/` antes de la entrega final.

<!-- CAPTURAS: descomenta cuando tengas las imágenes en assets/
<div align="center">
  <img src="assets/screenshot_home.png" alt="Pantalla principal" width="80%"/>
  <br><em>Pantalla principal — Carga y procesamiento de documentos</em>
  <br><br>
  <img src="assets/screenshot_results.png" alt="Resultados OCR" width="80%"/>
  <br><em>Resultados — Texto extraído, datos estructurados y clasificación</em>
  <br><br>
  <img src="assets/screenshot_json.png" alt="Exportación JSON" width="80%"/>
  <br><em>Exportación JSON — Resultado estructurado descargable</em>
</div>
-->

---

## 📂 Estructura del Proyecto

<details>
<summary><strong>Ver árbol de directorios completo</strong></summary>

```
ocr-ia-proyecto/
├── 📁 app/
│   └── app.py                   # Interfaz Streamlit (UI premium)
├── 📁 src/
│   ├── ocr.py                   # Módulo OCR con Tesseract (spa+eng)
│   ├── extractor.py             # Extracción regex — documentos Guatemala
│   ├── classifier.py            # Clasificación ML (TF-IDF + LinearSVC)
│   ├── pipeline.py              # Pipeline OCR → Extracción → Clasificación
│   ├── preprocess.py            # Preprocesamiento de imágenes
│   ├── predict.py               # Utilidades de predicción
│   └── dataset_validator.py     # Validación del dataset
├── 📁 data/
│   ├── training/                # ~500 documentos sintéticos (70+ por categoría)
│   ├── ground_truth.csv         # Etiquetas del dataset
│   └── README.md                # Descripción del dataset
├── 📁 models/
│   └── classifier_model.joblib  # Modelo SVM entrenado (incluido en el repo)
├── 📁 demos/
│   ├── demo_*.pdf               # PDFs de demostración por categoría
│   └── _gen_demos.py            # Script de generación de demos
├── 📁 tests/
│   ├── test_classifier.py       # Tests del clasificador
│   ├── test_extractor.py        # Tests del extractor regex
│   ├── test_pipeline.py         # Tests del pipeline integrado
│   ├── test_config.py           # Tests de configuración
│   └── test_trainer.py          # Tests del entrenador
├── 📁 notebooks/
│   ├── 01_EDA.ipynb             # Análisis exploratorio del dataset
│   ├── 02_train.ipynb           # Entrenamiento del modelo
│   └── 03_evaluation.ipynb      # Evaluación, métricas, matriz de confusión
├── 📁 docs/                     # Documentación técnica (en preparación)
├── config.py                    # Configuración global del proyecto
├── train_classifier.py          # Script de entrenamiento del clasificador
├── requirements.txt             # Dependencias del proyecto
└── README.md
```

</details>

---

## 🎮 Uso Básico

1. **Inicializar** el pipeline en la barra lateral → presionar **Inicializar Pipeline**
2. Ir a la pestaña **📤 Procesar Archivo**
3. **Subir** una imagen (`JPG`, `PNG`, `BMP`) o `PDF` individual
4. Presionar **🚀 PROCESAR**
5. Ver resultados en la pestaña **📊 Resultados**:
   - 📋 Texto OCR extraído
   - 🧩 Datos estructurados (NIT, fechas, montos, series SAT...)
   - 🏷️ Clasificación automática del tipo de documento
6. **Descargar** el resultado como `JSON` desde la sección de exportación

---

## 📊 Estado Actual del Proyecto

<div align="center">

| Métrica | Valor |
|:---|:---:|
| 🏷️ Categorías de documentos | **7** |
| 📄 Documentos de entrenamiento | **~500** |
| 🎯 Accuracy del modelo | **100%** |
| 📈 F1-macro | **0.9940** |
| 🧪 Tests automatizados | **158 pasando** |
| 📑 Soporte PDF multipágina | **✅ Sí** |
| 🌐 Idiomas OCR | **Español + Inglés** |
| 📦 Exportación | **JSON** |

</div>

---

## 🔄 Reentrenar el Modelo

El modelo ya está entrenado e incluido en `models/classifier_model.joblib`. Para reentrenarlo:

```powershell
python train_classifier.py
```

Genera un nuevo `classifier_model.joblib` en `models/` con las métricas actualizadas del dataset.

---

## 🧪 Ejecutar Tests

```powershell
python -m pytest tests/ -v
```

Resultado esperado: **`158 passed`** ✅

---

## 🔧 Solución de Problemas Comunes

<details>
<summary><strong>Ver errores comunes y soluciones</strong></summary>

<br>

| Error | Causa | Solución |
|:---|:---|:---|
| `TesseractNotFoundError` | Tesseract no instalado o ruta incorrecta | Instalar desde UB-Mannheim, verificar ruta en barra lateral |
| `spa` no disponible | Idioma español no instalado en Tesseract | Reinstalar marcando "Spanish" en las opciones del instalador |
| `ModuleNotFoundError` | Entorno virtual no activado | `venv\Scripts\activate` y `pip install -r requirements.txt` |
| La app no abre | Puerto 8501 ocupado | `streamlit run app/app.py --server.port 8502` |
| PDF sin texto | PDF escaneado sin capa de texto | El sistema aplica OCR automáticamente como fallback |

</details>

---

## ⚠️ Aviso Ético

> **Este sistema debe usarse únicamente con documentos ficticios, sintéticos, propios
> o debidamente anonimizados. Nunca con documentos reales de terceros sin autorización.**

- 🔍 Los resultados generados por OCR e IA deben ser **verificados por una persona** antes de tomar cualquier decisión basada en ellos.
- 🔒 No procesar documentos con datos sensibles o confidenciales sin la autorización correspondiente.
- 🛡️ Los archivos se procesan en memoria y no se almacenan en el servidor *(privacidad por diseño)*.
- 🎓 Proyecto académico — no apto para uso en producción sin validación adicional.

---

## 🎬 Video de Demostración

> **Pendiente** — Enlace al video demostrativo (3–5 min) será agregado antes de la entrega final.

---

<div align="center">

---

*🏫 Universidad Mariano Gálvez de Guatemala · 🎓 Facultad de Ingeniería*
*📚 Curso 045 — Inteligencia Artificial · 📁 Proyecto 04 · 📅 2026*

</div>
