"""
Aplicación Streamlit para OCR IA Project
"""

import streamlit as st
import json
import os
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipeline import OCRPipeline

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
    .info-box {
        padding: 20px;
        background-color: #d1ecf1;
        border-radius: 5px;
        border: 1px solid #bee5eb;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar sesión
if "pipeline" not in st.session_state:
    st.session_state.pipeline = None
if "last_result" not in st.session_state:
    st.session_state.last_result = None

# Sidebar - Configuración
with st.sidebar:
    st.title("⚙️ Configuración")
    
    # Ruta de Tesseract (solo para Windows)
    st.subheader("Configuración de Tesseract")
    tesseract_installed = st.checkbox(
        "Tengo Tesseract instalado",
        value=False,
        help="Marca si ya instalaste Tesseract-OCR en Windows"
    )
    
    tesseract_path = None
    if tesseract_installed:
        tesseract_path = st.text_input(
            "Ruta de Tesseract (opcional)",
            value="C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
            help="Por defecto: C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
        )
    
    # Inicializar pipeline
    if st.button("🚀 Inicializar Pipeline", use_container_width=True):
        try:
            st.session_state.pipeline = OCRPipeline(tesseract_path=tesseract_path)
            st.success("✅ Pipeline inicializado correctamente")
        except Exception as e:
            st.error(f"❌ Error al inicializar: {e}")
    
    st.divider()
    
    # Seleccionar idioma
    st.subheader("Opciones de OCR")
    ocr_language = st.selectbox(
        "Idioma para OCR",
        options=["spa", "eng", "fra", "deu"],
        format_func=lambda x: {
            "spa": "Español",
            "eng": "Inglés",
            "fra": "Francés",
            "deu": "Alemán"
        }[x],
        key="ocr_language"
    )
    
    st.divider()
    st.markdown("**Desarrollado con ❤️**")
    st.markdown("OCR IA Project v1.0.0")


# Header principal
st.title("📄 OCR IA Project")
st.markdown("**Extrae texto de imágenes y PDFs, extrae datos estructurados y clasifica documentos**")

# Verificar si el pipeline está inicializado
if st.session_state.pipeline is None:
    st.warning("""
    ⚠️ **Pipeline no inicializado**
    
    Por favor, sigue estos pasos:
    1. En la barra lateral, marca "Tengo Tesseract instalado" si ya lo instalaste
    2. Haz clic en "Inicializar Pipeline"
    
    Si no tienes Tesseract instalado, sigue las instrucciones en la pestaña "Instalación"
    """)
    
    # Mostrar instrucciones de instalación
    with st.expander("📋 Ver instrucciones de Instalación", expanded=False):
        st.markdown("""
        ### Instalación de Tesseract-OCR en Windows
        
        1. **Descargar el instalador**
           - Ve a: https://github.com/UB-Mannheim/tesseract/wiki
           - Descarga el instalador más reciente (ej: tesseract-ocr-w64-setup-v5.x.x.exe)
        
        2. **Instalar**
           - Ejecuta el instalador
           - Selecciona la carpeta de instalación (por defecto: C:\\Program Files\\Tesseract-OCR)
           - Instala los lenguajes que necesites (español, inglés, etc.)
        
        3. **Verificar instalación**
           - Abre PowerShell y ejecuta:
           ```
           tesseract --version
           ```
        
        4. **Configurar en Python**
           - La ruta por defecto es: C:\\Program Files\\Tesseract-OCR\\tesseract.exe
           - Si instalaste en otra carpeta, actualiza la ruta en la configuración
        """)

else:
    # Tabs principales
    tab1, tab2, tab3, tab4 = st.tabs([
        "📤 Procesar Archivo",
        "📊 Resultados",
        "📖 Guía de Uso",
        "ℹ️ Información"
    ])
    
    # TAB 1: Procesar Archivo
    with tab1:
        st.header("Procesar Archivo")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Sube tu archivo")
            uploaded_file = st.file_uploader(
                "Selecciona una imagen (JPG, PNG) o PDF",
                type=["jpg", "jpeg", "png", "pdf", "bmp"],
                key="file_uploader"
            )
        
        with col2:
            st.subheader("Opciones")
            extract_data = st.checkbox("Extraer datos", value=True, help="Extrae emails, teléfonos, etc.")
            classify_doc = st.checkbox("Clasificar documento", value=True, help="Clasifica el tipo de documento")
        
        # Procesar archivo
        if uploaded_file is not None:
            with st.spinner("⏳ Procesando archivo..."):
                # Guardar archivo temporal
                temp_path = f"/tmp/{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                try:
                    # Procesar
                    result = st.session_state.pipeline.process_file(
                        temp_path,
                        lang=st.session_state.ocr_language
                    )
                    st.session_state.last_result = result
                    
                    if result["status"] == "success":
                        st.markdown('<div class="success-box">', unsafe_allow_html=True)
                        st.success("✅ Archivo procesado exitosamente")
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Mostrar resumen
                        with st.expander("📋 Ver Resumen", expanded=True):
                            if "extracted_text" in result:
                                st.text_area(
                                    "Texto Extraído (OCR)",
                                    value=result["extracted_text"],
                                    height=200,
                                    disabled=True
                                )
                            else:
                                # Para PDFs, mostrar primer página
                                if result.get("pages"):
                                    st.text_area(
                                        "Texto de la Primera Página",
                                        value=result["pages"][0]["text"],
                                        height=200,
                                        disabled=True
                                    )
                    else:
                        st.error(f"❌ Error: {result.get('error', 'Error desconocido')}")
                
                except Exception as e:
                    st.error(f"❌ Error durante el procesamiento: {e}")
                finally:
                    # Limpiar archivo temporal
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
    
    # TAB 2: Resultados Detallados
    with tab2:
        st.header("Resultados del Procesamiento")
        
        if st.session_state.last_result is None:
            st.info("💡 Procesa un archivo en la pestaña 'Procesar Archivo' para ver resultados")
        else:
            result = st.session_state.last_result
            
            # Mostrar en JSON
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("JSON Completo")
                json_str = json.dumps(result, indent=2, ensure_ascii=False)
                st.json(result)
            
            with col2:
                st.subheader("Descarga")
                st.download_button(
                    label="📥 Descargar JSON",
                    data=json_str,
                    file_name="resultado_ocr.json",
                    mime="application/json"
                )
            
            st.divider()
            
            # Desglose detallado
            if "steps" in result:
                st.subheader("Desglose del Procesamiento")
                
                # OCR
                if "ocr" in result["steps"]:
                    with st.expander("🔤 Resultados OCR"):
                        ocr_data = result["steps"]["ocr"]
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Confianza", f"{ocr_data.get('confidence', 0)}%")
                        with col2:
                            st.metric("Idioma", ocr_data.get('language', 'N/A'))
                
                # Extracción
                if "extraction" in result["steps"]:
                    with st.expander("📍 Datos Extraídos"):
                        extraction = result["steps"]["extraction"]
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if extraction.get("emails"):
                                st.write("**📧 Emails:**")
                                for email in extraction["emails"]:
                                    st.write(f"  • {email}")
                            
                            if extraction.get("phones"):
                                st.write("**📱 Teléfonos:**")
                                for phone in extraction["phones"]:
                                    st.write(f"  • {phone}")
                            
                            if extraction.get("urls"):
                                st.write("**🔗 URLs:**")
                                for url in extraction["urls"]:
                                    st.write(f"  • {url}")
                        
                        with col2:
                            if extraction.get("dates"):
                                st.write("**📅 Fechas:**")
                                for date in extraction["dates"]:
                                    st.write(f"  • {date}")
                            
                            if extraction.get("currency"):
                                st.write("**💰 Valores:**")
                                for val in extraction["currency"]:
                                    st.write(f"  • {val}")
                            
                            if extraction.get("dni"):
                                st.write("**🆔 DNI/NIE:**")
                                for dni in extraction["dni"]:
                                    st.write(f"  • {dni}")
                
                # Clasificación
                if "classification" in result["steps"]:
                    with st.expander("🏷️ Clasificación"):
                        classification = result["steps"]["classification"]
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric(
                                "Clase Detectada",
                                classification.get("class", "desconocida").upper()
                            )
                        
                        with col2:
                            st.metric(
                                "Confianza",
                                f"{classification.get('confidence', 0) * 100:.1f}%"
                            )
                        
                        if classification.get("probabilities"):
                            st.write("**Probabilidades por Clase:**")
                            probs = classification["probabilities"]
                            for cls, prob in sorted(probs.items(), key=lambda x: x[1], reverse=True):
                                st.write(f"  • {cls}: {prob * 100:.1f}%")
    
    # TAB 3: Guía de Uso
    with tab3:
        st.header("📖 Guía de Uso")
        
        st.markdown("""
        ## ¿Cómo usar la aplicación?
        
        ### 1️⃣ Configuración Inicial
        - Asegúrate de tener Tesseract-OCR instalado en Windows
        - Si es la primera vez, haz clic en "Inicializar Pipeline" en la barra lateral
        
        ### 2️⃣ Procesar Archivo
        - Ve a la pestaña "Procesar Archivo"
        - Carga una imagen (JPG, PNG) o PDF
        - Selecciona el idioma deseado
        - Haz clic en "Procesar"
        
        ### 3️⃣ Ver Resultados
        - En la pestaña "Resultados" verás:
          - **OCR**: Texto extraído y confianza
          - **Extracción de Datos**: Emails, teléfonos, fechas, URLs, monedas, DNI, RFC
          - **Clasificación**: Tipo de documento y probabilidades
        
        ### 4️⃣ Descargar Resultados
        - Descarga los resultados en formato JSON
        - Úsalos en otros sistemas
        
        ## 🎯 Casos de Uso
        
        - **Facturas y Recibos**: Extrae montos, fechas, datos de contacto
        - **Contratos**: Identifica y extrae cláusulas importantes
        - **Documentos de Identidad**: Extrae DNI, RFC y datos personales
        - **Correspondencia**: Clasifica automáticamente tipos de documentos
        
        ## ⚠️ Limitaciones
        
        - La precisión del OCR depende de la calidad de la imagen
        - Documentos escaneados dan mejores resultados que fotos
        - Imágenes claras y bien iluminadas producen mejores extracciones
        """)
    
    # TAB 4: Información
    with tab4:
        st.header("ℹ️ Información del Proyecto")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📦 Dependencias Principales")
            st.write("""
            - **Pytesseract**: OCR usando Tesseract
            - **OpenCV**: Procesamiento de imágenes
            - **Scikit-learn**: Machine Learning
            - **Pandas**: Análisis de datos
            - **Streamlit**: Interfaz web
            - **Pillow**: Manipulación de imágenes
            """)
        
        with col2:
            st.subheader("🔧 Características")
            st.write("""
            - ✅ OCR de imágenes y PDFs
            - ✅ Extracción de datos (emails, teléfonos, etc.)
            - ✅ Clasificación de documentos
            - ✅ Interfaz web amigable
            - ✅ Exportación de resultados JSON
            - ✅ Multi-idioma
            """)
        
        st.divider()
        
        st.markdown("""
        ### 🚀 Versión
        **OCR IA Project v1.0.0**
        
        ### 👨‍💻 Autor
        Desarrollo Senior en Python, ML y OCR
        
        ### 📝 Licencia
        Este proyecto es de código abierto
        """)
