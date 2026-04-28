# 🚀 GUÍA: SUBIR OCR IA A CLOUD (PASO A PASO)

**Objetivo:** Llevar el proyecto de local a cloud en 2-3 semanas

---

## PRERREQUISITOS

```
✅ Código: Ya está en local + GitHub
✅ Tests: 96 tests pasando
✅ Python: 3.13 instalado
❌ Dataset: NECESARIO (80-100 documentos)
❌ Modelo: Se genera automáticamente con dataset
```

---

## FASE 1: PREPARACIÓN LOCAL (3-4 días)

### PASO 1: Recolectar Dataset 📂

**¿Qué necesitas?**
- 80-100 documentos reales (imágenes o PDFs)
- Distribuidos en 4 categorías:
  - 20-30 facturas
  - 20-30 recibos
  - 20-30 contratos
  - 10-20 otros

**¿Cómo preparar?**

```bash
# 1. Crear estructura
mkdir -p data/training/{factura,recibo,contrato,otro}

# 2. Por cada documento:
#    a. Scanear/fotografiar
#    b. Convertir a imagen o PDF
#    c. Guardar en carpeta correspondiente

# 3. Para cada documento, extraer texto:
#    - Abrirlo con OCR local
#    - Copiar resultado
#    - Guardar en .txt con mismo nombre

# Ejemplo:
data/training/
├── factura/
│   ├── documento_1.jpg
│   ├── documento_1.txt (contenido OCR)
│   ├── documento_2.jpg
│   ├── documento_2.txt
│   └── ...
├── recibo/
│   ├── ...
└── ...
```

**Alternativa rápida:** Si tienes 200+ documentos escaneados, usar script para OCR automático:

```python
# auto_extract_ocr.py
from src.ocr import OCRProcessor
import os
from pathlib import Path

ocr = OCRProcessor()
categories = ['factura', 'recibo', 'contrato', 'otro']

for category in categories:
    folder = f'data/training/{category}'
    for file in os.listdir(folder):
        if file.endswith(('.jpg', '.png', '.pdf')):
            result = ocr.extract_text_from_image(
                f'{folder}/{file}',
                lang='spa'
            )
            with open(f'{folder}/{Path(file).stem}.txt', 'w') as f:
                f.write(result['text'])
```

**Tiempo estimado:** 2-3 días (depende disponibilidad documentos)

---

### PASO 2: Entrenar Modelo 🤖

```bash
# En terminal local
cd C:\Users\ACER\OneDrive\Escritorio\ocr-ia-proyecto
.\venv\Scripts\Activate.ps1

python train_classifier.py
```

**¿Qué genera?**
```
models/
├── classifier_model.joblib      ← Modelo ML (5-10 MB)
├── classifier_vectorizer.pkl    ← Vectorizador TF-IDF
└── training_metrics.json        ← Resultados entrenamiento
```

**Tiempo:** 30-60 minutos (automático)

**Salida esperada:**
```
=== MÉTRICAS DE ENTRENAMIENTO ===
Accuracy: 0.85 (±0.08)
Precision: 0.84
Recall: 0.82
F1-Score: 0.83
Clases: factura, recibo, contrato, otro
```

---

### PASO 3: Probar Localmente ✅

```bash
# Test 1: Verificar dataset
python -c "
from src.dataset_validator import validate_dataset
report = validate_dataset()
print(report.summary())
"

# Test 2: Ejecutar tests
pytest tests/ -q
# Resultado esperado: 96 passed

# Test 3: Probar app
streamlit run app/app.py
# Abrir http://localhost:8501
```

---

## FASE 2: PREPARAR PARA CLOUD (3-4 días)

### PASO 4: Crear Dockerfile 🐳

```dockerfile
# Dockerfile
FROM python:3.13-slim

# Instalar Tesseract (crítico)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    ffmpeg \
    libsm6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar código
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Exponer puerto para Streamlit
EXPOSE 8501

# Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Comando por defecto
CMD ["streamlit", "run", "app/app.py", "--server.port=8501"]
```

**Build & test:**
```bash
# Build (toma 5-10 minutos primera vez)
docker build -t ocr-ia:latest .

# Test local
docker run -p 8501:8501 ocr-ia:latest
# Acceder a http://localhost:8501
```

---

### PASO 5: Docker Compose 🐳📦

```yaml
# docker-compose.yml
version: '3.8'

services:
  ocr-app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - TESSERACT_PATH=/usr/bin/tesseract
      - STREAMLIT_SERVER_HEADLESS=true
    volumes:
      - ./data:/app/data
      - ./models:/app/models
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:  # Opcional para fase 2
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ocr_db
      POSTGRES_USER: ocr_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

**Test:**
```bash
docker-compose up
# Acceder a http://localhost:8501
```

---

### PASO 6: Preparar para Git 📦

```bash
# Ver cambios locales
git status

# Agregar archivos necesarios
git add data/training/  # Dataset
git add models/         # Modelos entrenados
git add Dockerfile docker-compose.yml
git add ANALISIS_PROYECTO_CLOUD.md
git add RESUMEN_TECNICO_CLOUD.md
git add RESUMEN_EJECUTIVO.md

# Commit
git commit -m "feat(cloud): agregar dataset, modelo y configuración docker

- Dataset de entrenamiento en data/training/ (80+ documentos)
- Modelo entrenado: models/classifier_model.joblib
- Dockerfile para containerización
- Docker Compose para orquestación local
- Documentación para cloud deployment"

# Push
git push origin Guillermo
```

---

## FASE 3: DEPLOY A CLOUD (2-3 días)

### OPCIÓN A: AWS (Recomendado MVP) 🟠

#### Paso 7A: Crear repositorio ECR

```bash
# 1. Ir a AWS Console → ECR → Create repository
# Nombre: ocr-ia
# Acceso: Private

# 2. Autenticar Docker con AWS
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  123456789.dkr.ecr.us-east-1.amazonaws.com

# 3. Build y push
docker build -t ocr-ia:latest .
docker tag ocr-ia:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/ocr-ia:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/ocr-ia:latest
```

#### Paso 7B: Deploy a ECS Fargate

```bash
# Crear task definition (JSON)
aws ecs register-task-definition \
  --family ocr-ia \
  --network-mode awsvpc \
  --requires-compatibilities FARGATE \
  --cpu 1024 \
  --memory 2048 \
  --container-definitions '[{
    "name": "ocr-ia",
    "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/ocr-ia:latest",
    "portMappings": [{"containerPort": 8501}],
    "environment": [
      {"name": "STREAMLIT_SERVER_HEADLESS", "value": "true"}
    ]
  }]'

# Crear servicio ECS
aws ecs create-service \
  --cluster ocr-cluster \
  --service-name ocr-ia-service \
  --task-definition ocr-ia \
  --desired-count 1 \
  --launch-type FARGATE
```

**Resultado:**
```
✅ App en vivo en: http://[IP-AWS]:8501
```

---

### OPCIÓN B: GCP (Más simple) 🔵

#### Paso 7B: Deploy a Cloud Run

```bash
# 1. Autenticar
gcloud auth login

# 2. Deploy (¡Una línea!)
gcloud run deploy ocr-ia \
  --source . \
  --platform managed \
  --region us-central1 \
  --memory 4Gi \
  --timeout 3600 \
  --set-env-vars STREAMLIT_SERVER_HEADLESS=true

# ✅ Resultado: https://ocr-ia-[hash].run.app
```

---

### OPCIÓN C: Azure 🔷

```bash
# 1. Crear resource group
az group create -n ocr-rg -l eastus

# 2. Container registry
az acr create --resource-group ocr-rg --name ocria --sku Basic

# 3. Build en cloud
az acr build --registry ocria --image ocr-ia:latest .

# 4. App Service
az appservice plan create -n ocr-plan -g ocr-rg --sku B1 --is-linux
az webapp create -n ocr-ia-app -g ocr-rg --plan ocr-plan \
  -i ocria.azurecr.io/ocr-ia:latest

# ✅ Resultado: https://ocr-ia-app.azurewebsites.net
```

---

## FASE 4: POST-DEPLOYMENT (1-2 días)

### Paso 8: Configurar Monitoreo 📊

```yaml
# CloudWatch / Stackdriver / Application Insights
Métricas importantes:
  - Requests/segundo
  - Error rate
  - Response time
  - CPU usage
  - Memory usage
  - Tesseract availability

Alertas:
  - Error rate > 5%
  - Response time > 60s
  - CPU > 80%
  - Memory > 90%
```

### Paso 9: Documentación 📚

```
Crear/actualizar:
├── DEPLOYMENT.md           ← Cómo deployar
├── ARCHITECTURE.md         ← Arquitectura cloud
├── API.md (FUTURA)         ← Documentación API
├── TROUBLESHOOTING.md      ← Solución de problemas
└── SECURITY.md             ← Políticas seguridad
```

### Paso 10: Usuario Inicial 👤

```
1. Crear cuenta de prueba
2. Compartir URL
3. Test con documentos reales
4. Recolectar feedback
```

---

## PRÓXIMO PASO: API REST (FASE 2)

Una vez que MVP en cloud esté estable:

### Paso 11: Convertir a FastAPI

```python
# app/api.py
from fastapi import FastAPI, UploadFile, File
from src.pipeline import OCRPipeline

app = FastAPI(title="OCR IA API")
pipeline = OCRPipeline()

@app.post("/process")
async def process_document(file: UploadFile = File(...)):
    result = pipeline.process_file(file.filename)
    return result

@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

**Deploy:**
```bash
# Cambiar CMD en Dockerfile
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0"]

# Build, push, redeploy
```

---

## 📋 CHECKLIST RÁPIDO

```
[ ] Paso 1: Dataset recolectado (80+ docs)
[ ] Paso 2: Modelo entrenado (script corrió)
[ ] Paso 3: Tests pasando 96/96
[ ] Paso 4: Dockerfile creado
[ ] Paso 5: Docker Compose testado localmente
[ ] Paso 6: Cambios commiteados a GitHub
[ ] Paso 7A/B/C: App en cloud viva
[ ] Paso 8: Monitoreo configurado
[ ] Paso 9: Documentación actualizada
[ ] Paso 10: Usuario inicial testeando

🎉 ¡LISTO PARA PRODUCCIÓN!

Próximo: Implementar API REST (Phase 2)
```

---

## ⏱️ TIMELINE ESTIMADO

```
Semana 1:
  Lunes-Miércoles:   Dataset recolección (3 días)
  Jueves:            Entrenamiento modelo (2 horas)
  Viernes:           Tests + Dockerfile (4 horas)

Semana 2:
  Lunes-Martes:      Docker Compose setup (8 horas)
  Miércoles:         Git push + Git commits (2 horas)
  Jueves-Viernes:    Deploy cloud + testing (16 horas)

✅ TOTAL: ~2 semanas
```

---

## 💾 ARCHIVOS CRÍTICOS

```
Para cloud necesitas:
├── requirements.txt          ← Dependencias
├── Dockerfile               ← Container
├── docker-compose.yml       ← Orquestación
├── data/training/*          ← Dataset
├── models/*                 ← Modelo entrenado
├── src/                     ← Código core
├── app/app.py              ← UI Streamlit
└── config.py               ← Configuración
```

---

## 🔧 TROUBLESHOOTING COMÚN

| Problema | Solución |
|----------|----------|
| Tesseract no encontrado | Verificar ruta en Dockerfile |
| Dataset no carga | Verificar estructura carpetas |
| Modelo no entrena | Verificar tamaño/formato dataset |
| Docker no inicia | Revisar logs: `docker logs [container]` |
| OOM (Out of Memory) | Aumentar memoria en cloud (4GB → 8GB) |
| Timeout en OCR | Reducir tamaño imagen o timeout config |

---

## 📞 SIGUIENTE ACCIÓN

**¿Listo?**

1. Reúnete con equipo
2. Prioriza dataset (el blocker)
3. Asigna recursos
4. ¡Empieza semana que viene!

**¿Dudas?**

Consulta:
- `ANALISIS_PROYECTO_CLOUD.md` - Arquitectura
- `RESUMEN_TECNICO_CLOUD.md` - Detalles técnicos
- README.md - Instalación local

---

**Última actualización:** Abril 2026  
**Versión:** 1.0.0  
**Estado:** ✅ Listo para implementar
