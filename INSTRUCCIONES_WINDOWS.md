

# 🚀 GUÍA DE EJECUCIÓN PASO A PASO - Windows PowerShell

## ⚠️ REQUISITO PREVIO: Instalar Tesseract-OCR

**ESTO ES OBLIGATORIO ANTES DE CUALQUIER PASO**

### Paso 0.1: Descargar Tesseract

1. Ve a: https://github.com/UB-Mannheim/tesseract/wiki
2. Busca "Downloads" en la página
3. Descarga el instalador más reciente para Windows (busca `tesseract-ocr-w64-setup-v5.x.x.exe`)

### Paso 0.2: Instalar Tesseract

1. Ejecuta el instalador descargado
2. Cuando se pida la carpeta de instalación, usa la default:
   ```
   C:\Program Files\Tesseract-OCR
   ```
3. **IMPORTANTE**: Selecciona estos idiomas durante la instalación:
   - Spanish (Español) ✓
   - English ✓
4. Completa la instalación

### Paso 0.3: Verificar Instalación

Abre PowerShell y ejecuta:
```powershell
tesseract --version
```

Deberías ver algo como:
```
tesseract 5.x.x
...
```

Si ves un error, Tesseract no está instalado correctamente. **Repite los pasos 0.1-0.2**

---

## ✅ PASOS DE INSTALACIÓN DEL PROYECTO

### Paso 1: Abre PowerShell en la Carpeta del Proyecto

```powershell
# Opción A: Abre PowerShell, luego navega a:
cd "C:\Users\ACER\OneDrive\Escritorio\ocr-ia-proyecto"

# Opción B: Desde VS Code
# - Abre VS Code
# - Abre la carpeta ocr-ia-proyecto
# - Presiona Ctrl+` para abrir la terminal integrada
# - Ya estás en la carpeta correcta
```

### Paso 2: Crear el Entorno Virtual

```powershell
# Ejecuta este comando
python -m venv venv

# Deberías ver que se crea una carpeta "venv"
```

**⚠️ Si recibes error "Set-ExecutionPolicy":**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Presiona 's' y luego Enter
```

### Paso 3: Activar el Entorno Virtual

```powershell
# En Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Si usas Cmd.exe en lugar de PowerShell:
.\venv\Scripts\activate.bat

# Sabrás que está activado cuando veas "(venv)" al inicio de la línea
```

Ejemplo:
```
(venv) PS C:\Users\ACER\OneDrive\Escritorio\ocr-ia-proyecto>
```

### Paso 4: Actualizar pip

```powershell
python -m pip install --upgrade pip
```

### Paso 5: Instalar Todas las Dependencias

```powershell
# Asegúrate de que el entorno virtual está activado (debe decir "(venv)" en la línea)

pip install -r requirements.txt
```

**Esto tardará unos 2-5 minutos.** Espera a que termine.

Si ves errores al final, intenta de nuevo:
```powershell
pip install -r requirements.txt --default-timeout=1000
```

### Paso 6: Verificar Instalación

```powershell
# Prueba importar los módulos principales
python -c "import pytesseract; import cv2; import sklearn; print('✓ Todo instalado correctamente')"
```

Deberías ver:
```
✓ Todo instalado correctamente
```

---

## 🎯 EJECUTAR LA APLICACIÓN

### Opción A: Ejecutar Streamlit (RECOMENDADO)

```powershell
# Asegúrate de que el entorno virtual está activado
# Debes ver "(venv)" al inicio de la línea

streamlit run app/app.py
```

Verás algo como:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501

  For better performance, install watchdog.
```

**La aplicación se abrirá automáticamente en tu navegador.**

Si no se abre automáticamente, ve a: http://localhost:8501

### Opción B: Usar la Aplicación en Python Directamente

```powershell
# Crear un archivo de prueba (test.py)
# Con este contenido:

from src.pipeline import OCRPipeline
from config import TESSERACT_PATH
import json

# Crear pipeline
pipeline = OCRPipeline(tesseract_path=TESSERACT_PATH)

# Procesar una imagen (reemplaza la ruta)
resultado = pipeline.process_image("ruta/a/tu/imagen.jpg", lang="spa")

# Ver resultado
print(json.dumps(resultado, indent=2, ensure_ascii=False))

# Ejecutar:
python test.py
```

---

## 🔄 COMANDO RÁPIDO: Reiniciar Todo

Si necesitas reiniciar después de haber trabajado:

```powershell
# 1. Desactiva el entorno
deactivate

# 2. Vuelve a activarlo
.\venv\Scripts\Activate.ps1

# 3. Ejecuta la app
streamlit run app/app.py
```

---

## ❌ SOLUCIÓN DE PROBLEMAS COMUNES

### Error 1: "Cannot find Tesseract"

```
pytesseract.TesseractNotFoundError: tesseract is not installed
```

**Solución**:
1. Verifica que Tesseract esté instalado: ejecuta `tesseract --version`
2. Si no funciona, reinstala Tesseract
3. Asegúrate de que está en: `C:\Program Files\Tesseract-OCR\tesseract.exe`
4. Si lo instalaste en otra carpeta, edita `config.py`:
   ```python
   TESSERACT_PATH = r"C:\Tu\Ruta\Aqui\tesseract.exe"
   ```

### Error 2: "Module not found"

```
ModuleNotFoundError: No module named 'cv2'
```

**Solución**:
```powershell
# Verifica que el entorno virtual esté activado
pip install --upgrade opencv-python scikit-learn
```

### Error 3: "Permission denied" al activar el entorno

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Presiona 's' y Enter
```

### Error 4: OCR produce texto vacío o con muy baja confianza

**Posibles causas:**
- Imagen de baja resolución
- Idioma incorrecto seleccionado
- Imagen borrosa

**Soluciones:**
- Usa imágenes de al menos 150 DPI
- Verifica haber seleccionado el idioma correcto
- Usa imágenes escaneadas en lugar de fotos
- Verifica que Tesseract descargó los datos del idioma (durante la instalación)

### Error 5: "Streamlit not found"

```powershell
# El entorno virtual no está activado o streamlit no se instaló
pip install streamlit
```

---

## 📊 VERIFICACIÓN FINAL

Para verificar que TODO está correctamente instalado:

```powershell
# 1. Verifica que el entorno está activado (debe decir "(venv)")
# 2. Ejecuta:

python -c "
import sys
print('✓ Python:', sys.version)

import pytesseract
print('✓ Pytesseract:', pytesseract.__version__)

import cv2
print('✓ OpenCV:', cv2.__version__)

import sklearn
print('✓ Scikit-learn:', sklearn.__version__)

import streamlit
print('✓ Streamlit:', streamlit.__version__)

print('')
print('✓✓✓ TODO ESTÁ LISTO ✓✓✓')
"
```

Deberías ver todas las versiones sin errores.

---

## 🎨 PRIMERA EJECUCIÓN

Cuando ejecutes por primera vez:

```powershell
streamlit run app/app.py
```

1. La app se abrirá en `http://localhost:8501`
2. En la barra lateral izquierda:
   - Marca ✓ "Tengo Tesseract instalado"
   - Verifica que la ruta sea: `C:\Program Files\Tesseract-OCR\tesseract.exe`
   - Haz clic en "Inicializar Pipeline"
3. Espera a que diga "✅ Pipeline inicializado correctamente"
4. Ya puedes subir archivos y procesar

---

## 📁 ARCHIVOS IMPORTANTES

Después de la instalación, deberías tener:

```
ocr-ia-proyecto/
├── venv/                    ← Creado en Paso 2
├── src/
│   ├── ocr.py
│   ├── classifier.py
│   ├── extractor.py
│   └── pipeline.py
├── app/
│   └── app.py
├── data/
├── models/
├── config.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 📞 RESUMEN DE COMANDOS

```powershell
# Abrir carpeta en terminal
cd "C:\Users\ACER\OneDrive\Escritorio\ocr-ia-proyecto"

# Crear entorno
python -m venv venv

# Activar entorno
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
streamlit run app/app.py

# Desactivar entorno (cuando termines)
deactivate
```

---

## ✅ TODO COMPLETADO

Si llegaste aquí sin errores, ¡tu proyecto está 100% funcional! 🎉

**Próximos pasos:**
1. Sube imágenes o PDFs a procesar
2. Entrena el clasificador con tus propios datos
3. Exporta los resultados en JSON
4. Integra en tu pipeline de producción

---

**¿Problemas?** Verifica:
1. ¿Tesseract está instalado? → `tesseract --version`
2. ¿El entorno está activado? → Busca "(venv)" en la línea
3. ¿Las dependencias están instaladas? → `pip list | grep pytesseract`
4. ¿Estás en la carpeta correcta? → `pwd` o `Get-Location`
