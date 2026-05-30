"""
Punto de entrada para Streamlit Cloud
Redirige a la aplicación principal en app/app.py
"""
import subprocess
import sys
from pathlib import Path

# Ejecutar la app desde app/app.py
app_path = Path(__file__).parent / "app" / "app.py"
sys.argv = ["streamlit", "run", str(app_path)]

# Importar la app
import streamlit as st
import platform
import tempfile
import json
import os
from pathlib import Path

# Agregar src al path
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

from src.pipeline import OCRPipeline

IS_CLOUD = platform.system() != "Windows"
MODEL_PATH = ROOT_DIR / "models" / "classifier_model.joblib"

# Configuración de la página
st.set_page_config(
    page_title="OCR IA Project",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 18px;
    }
    .success-box {
        padding: 20px;
        background-color: #d4edda;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    .error-box {
        padding: 20px;
        background-color: #f8d7da;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

st.title("📄 OCR & Document Classification IA")
st.markdown("---")

# Inicializar pipeline
@st.cache_resource
def load_pipeline():
    try:
        pipeline = OCRPipeline(model_path=str(MODEL_PATH))
        return pipeline
    except Exception as e:
        st.error(f"Error cargando el pipeline: {e}")
        return None

pipeline = load_pipeline()

if pipeline is None:
    st.error("No se pudo cargar el pipeline. Verifica que el modelo existe.")
    st.stop()

# Sidebar para navegación
with st.sidebar:
    st.header("⚙️ Opciones")
    option = st.radio(
        "Selecciona una opción:",
        ["📤 Extraer Texto OCR", "🏷️ Clasificar Documento", "📊 Demo Completo"]
    )

# Tab 1: OCR
if option == "📤 Extraer Texto OCR":
    st.header("Extracción de Texto OCR")
    uploaded_file = st.file_uploader("Sube una imagen o PDF", type=["png", "jpg", "jpeg", "pdf"])
    
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
            tmp.write(uploaded_file.getbuffer())
            tmp_path = tmp.name
        
        try:
            with st.spinner("Procesando..."):
                result = pipeline.extract(tmp_path)
            
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.markdown("### ✅ Texto Extraído")
            st.text_area("Resultado OCR:", result.get("text", ""), height=300)
            st.markdown('</div>', unsafe_allow_html=True)
            
            if st.button("📥 Descargar Resultado"):
                st.download_button(
                    label="Descargar TXT",
                    data=result.get("text", ""),
                    file_name="ocr_result.txt"
                )
        except Exception as e:
            st.markdown('<div class="error-box">', unsafe_allow_html=True)
            st.error(f"Error: {str(e)}")
            st.markdown('</div>', unsafe_allow_html=True)
        finally:
            os.unlink(tmp_path)

# Tab 2: Clasificación
elif option == "🏷️ Clasificar Documento":
    st.header("Clasificación de Documentos")
    uploaded_file = st.file_uploader("Sube un documento", type=["png", "jpg", "jpeg", "pdf", "txt"])
    
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
            tmp.write(uploaded_file.getbuffer())
            tmp_path = tmp.name
        
        try:
            with st.spinner("Clasificando..."):
                result = pipeline.classify(tmp_path)
            
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.markdown("### ✅ Clasificación Completada")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Clase", result.get("label", "N/A"))
            with col2:
                confidence = result.get("confidence", 0) * 100
                st.metric("Confianza", f"{confidence:.2f}%")
            st.markdown('</div>', unsafe_allow_html=True)
            
            if st.button("📋 Ver Detalles JSON"):
                st.json(result)
        except Exception as e:
            st.markdown('<div class="error-box">', unsafe_allow_html=True)
            st.error(f"Error: {str(e)}")
            st.markdown('</div>', unsafe_allow_html=True)
        finally:
            os.unlink(tmp_path)

# Tab 3: Demo Completo
else:
    st.header("Demo Completo")
    st.markdown("""
    ### Funcionalidades Disponibles:
    - ✅ Extracción de texto con OCR
    - ✅ Clasificación automática de documentos
    - ✅ Análisis contextual de contenido
    - ✅ Soporte para múltiples formatos (PDF, PNG, JPG)
    """)
    
    st.markdown("---")
    st.info("📌 Sube un documento en las pestañas anteriores para empezar.")
