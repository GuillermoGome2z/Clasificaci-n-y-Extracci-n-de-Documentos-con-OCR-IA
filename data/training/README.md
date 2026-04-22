# 📚 Dataset de Entrenamiento para Clasificador de Documentos

Estructura de directorios para almacenar documentos de entrenamiento clasificados.

## 📁 Estructura

```
data/training/
├── factura/        # Facturas de venta/compra
├── recibo/         # Recibos de pago
├── contrato/       # Contratos y acuerdos
└── otro/           # Otros documentos no clasificables
```

## 📝 Cómo Agregar Datos de Entrenamiento

### 1. Formato de Archivo
- **Formato**: Archivos de texto plano (`.txt`)
- **Codificación**: UTF-8
- **Nombre**: Descriptivo, ej: `factura_001.txt`, `recibo_venta_202301.txt`

### 2. Contenido de Archivo
Cada archivo `.txt` debe contener el **texto OCR extraído** del documento:

```
Empresa: ACME S.A.
RFC: ACS200101ABC
Fecha: 2024-01-15
...
```

### 3. Requisitos Mínimos de Datos

Para obtener un modelo con confianza razonable:

| Categoría | Mínimo Recomendado | Ideal |
|-----------|-------------------|-------|
| Facturas | 30-50 | 100+ |
| Recibos | 30-50 | 100+ |
| Contratos | 30-50 | 100+ |
| Otros | 20-30 | 50+ |
| **TOTAL** | **110-180** | **350+** |

### 4. Pasos para Agregar Datos

1. Extrae texto OCR de documentos reales usando `app.py` o `src/ocr.py`
2. Copia el texto extraído a un archivo `.txt`
3. Coloca el archivo en la carpeta correspondiente:
   - `data/training/factura/` para facturas
   - `data/training/recibo/` para recibos
   - `data/training/contrato/` para contratos
   - `data/training/otro/` para otros

4. Ejecuta el entrenamiento:
   ```bash
   python train_classifier.py
   ```

### 5. Ejemplo de Contenido

**`data/training/factura/factura_001.txt`:**
```
FACTURA #F-2024-001
Empresa: Tech Solutions S.A.
RFC: TSO240101ABC
NIF: 12.345.678-A

CONCEPTO                CANTIDAD    UNITARIO    TOTAL
Asesoría técnica            10         100        1000
Desarrollo software          5        1000        5000
Total:                                          6000.00
```

**`data/training/recibo/recibo_001.txt`:**
```
RECIBO DE PAGO
Número: RCP-2024-001
Fecha: 15 de enero de 2024
Concepto: Pago por servicios de consultoría
Monto: $5,000.00
Recibido por: Juan Pérez
```

---

## 🔧 Entrenar el Modelo

```bash
# Desde el directorio raíz del proyecto
python train_classifier.py
```

### Salida Esperada
```
📊 Iniciando entrenamiento del clasificador...
✅ Datos cargados exitosamente
   - Facturas: 50 documentos
   - Recibos: 45 documentos
   - Contratos: 40 documentos
   - Otros: 25 documentos
   - Total: 160 documentos

🔄 Extrayendo características (TF-IDF)...
🤖 Entrenando modelo (Naive Bayes)...
📈 Accuracy en validación: 0.92 (92%)
📉 Matriz de confusión:
   Facturas  Recibos  Contratos  Otros
Facturas     48        1          1      0
Recibos       0       42          2      1
Contratos     1        2         36      1
Otros         0        0          1     24

💾 Modelo guardado en: models/classifier_model.joblib
✨ Entrenamiento completado en 2.34s
```

---

## 📊 Monitoreo

Después de entrenar, revisa:

- **Modelo**: `models/classifier_model.joblib` (debe existir)
- **Vectorizador**: `models/classifier_model.joblib` (incluido con el modelo)
- **Logs**: Console output del script
- **Métricas**: Se guardan en el entrenamiento

---

## 🚀 Uso en Predicción

Una vez entrenado, el modelo se carga automáticamente:

```python
from src.pipeline import OCRPipeline

pipeline = OCRPipeline()
result = pipeline.process_image("documento.png")

# result["steps"]["classification"]["predicted_class"] → "factura", "recibo", etc.
# result["steps"]["classification"]["confidence"] → 0.92
```

---

## ⚠️ Troubleshooting

### "No se encontraron archivos de entrenamiento"
- Verifica que los `.txt` están en `data/training/categoría/`
- Usa rutas relativas correctas

### Accuracy muy bajo (< 0.70)
- Agrega más datos de entrenamiento
- Verifica que los textos son representativos
- Revisa que las categorías están bien separadas

### Modelo no se carga
- Verifica permisos de escritura en `models/`
- Ejecuta de nuevo: `python train_classifier.py`

---

## 📚 Referencias

- [Scikit-learn Naive Bayes](https://scikit-learn.org/stable/modules/naive_bayes.html)
- [TF-IDF Vectorizer](https://scikit-learn.org/stable/modules/feature_extraction.html#text-feature-extraction)
- [Model Persistence](https://scikit-learn.org/stable/modules/model_persistence.html)
