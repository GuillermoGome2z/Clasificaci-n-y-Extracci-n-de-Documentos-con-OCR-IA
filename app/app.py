"""
Aplicación Streamlit para OCR IA Project
"""

import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import streamlit as st

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
        except (ValueError, TypeError, FileNotFoundError, OSError) as e:
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
        
        # Verificar si pipeline está inicializado
        if st.session_state.pipeline is None:
            st.error("❌ Pipeline no inicializado. Por favor, inicialízalo en la barra lateral.")
        else:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("📤 Sube tu archivo")
                uploaded_file = st.file_uploader(
                    "Selecciona una imagen (JPG, PNG, BMP) o PDF",
                    type=["jpg", "jpeg", "png", "pdf", "bmp", "gif"],
                    key="file_uploader"
                )
            
            with col2:
                st.subheader("⚙️ Opciones")
                ocr_lang = st.selectbox(
                    "Idioma OCR",
                    options=["spa", "eng", "fra", "deu"],
                    format_func=lambda x: {
                        "spa": "🇪🇸 Español",
                        "eng": "🇬🇧 Inglés",
                        "fra": "🇫🇷 Francés",
                        "deu": "🇩🇪 Alemán"
                    }[x],
                    key="tab1_ocr_language",
                    index=0
                )
            
            # Procesar archivo si se cargó uno
            if uploaded_file is not None:
                # Mostrar información del archivo
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📄 Archivo", uploaded_file.name)
                with col2:
                    file_size_mb = uploaded_file.size / (1024 * 1024)
                    st.metric("📊 Tamaño", f"{file_size_mb:.2f} MB")
                with col3:
                    st.metric("🔤 Tipo", uploaded_file.name.split('.')[-1].upper())
                
                st.divider()
                
                # Botón de procesamiento
                col_process, col_space = st.columns([1, 4])
                with col_process:
                    process_button = st.button("🚀 PROCESAR", use_container_width=True, type="primary")
                
                if process_button:
                    # Usar tempfile para compatibilidad Windows
                    with tempfile.NamedTemporaryFile(
                        suffix=f".{uploaded_file.name.split('.')[-1]}",
                        delete=False
                    ) as tmp_file:
                        tmp_file.write(uploaded_file.getbuffer())
                        temp_path = tmp_file.name
                    
                    try:
                        # Procesamiento con indicador visual
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        status_text.info("⏳ Iniciando OCR...")
                        progress_bar.progress(25)
                        
                        # Procesar archivo
                        result = st.session_state.pipeline.process_file(
                            temp_path,
                            lang=ocr_lang
                        )
                        progress_bar.progress(75)
                        
                        # Guardar resultado en sesión
                        st.session_state.last_result = result
                        progress_bar.progress(100)
                        
                        if result["status"] == "success":
                            status_text.success("✅ ¡Procesamiento completado exitosamente!")
                            
                            # Mostrar estadísticas rápidas
                            st.divider()
                            st.subheader("📊 Estadísticas de Procesamiento")
                            
                            stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
                            
                            with stats_col1:
                                ocr_data = result.get("steps", {}).get("ocr", {})
                                if ocr_data:
                                    confidence = ocr_data.get("confidence", 0)
                                    st.metric("🔤 Confianza OCR", f"{confidence:.0f}%")
                                else:
                                    st.metric("🔤 Confianza OCR", "N/A")
                            
                            with stats_col2:
                                extracted_text = result.get("extracted_text", "")
                                if extracted_text:
                                    char_count = len(extracted_text.strip())
                                    st.metric("📝 Caracteres", f"{char_count:,}")
                                else:
                                    st.metric("📝 Caracteres", "0")
                            
                            with stats_col3:
                                extraction = result.get("steps", {}).get("extraction", {})
                                if extraction:
                                    total_items = sum(len(v) for v in extraction.values() if isinstance(v, list))
                                    st.metric("🔍 Datos Extraídos", f"{total_items}")
                                else:
                                    st.metric("🔍 Datos Extraídos", "0")
                            
                            with stats_col4:
                                classification = result.get("steps", {}).get("classification", {})
                                if classification:
                                    class_name = classification.get("class", "N/A")
                                    st.metric("🏷️ Clasificación", class_name.title())
                                else:
                                    st.metric("🏷️ Clasificación", "N/A")
                            
                            # Mostrar texto extraído
                            st.divider()
                            st.subheader("📋 Texto Extraído (OCR)")
                            
                            extracted_text = result.get("extracted_text", "").strip()
                            
                            if extracted_text:
                                st.text_area(
                                    "Contenido del documento:",
                                    value=extracted_text,
                                    height=250,
                                    disabled=True,
                                    key="ocr_output"
                                )
                            else:
                                # Para PDFs multipage
                                pages = result.get("pages", [])
                                if pages and len(pages) > 0:
                                    num_pages = len(pages)
                                    st.info(f"📑 Documento PDF de {num_pages} página(s)")
                                    
                                    page_num = st.slider(
                                        "Selecciona la página",
                                        min_value=1,
                                        max_value=num_pages,
                                        value=1
                                    )
                                    
                                    page_text = pages[page_num - 1].get("text", "").strip()
                                    
                                    if page_text:
                                        st.text_area(
                                            f"Página {page_num}:",
                                            value=page_text,
                                            height=250,
                                            disabled=True,
                                            key=f"ocr_page_{page_num}"
                                        )
                                    else:
                                        st.warning(f"⚠️ No se extrajo texto en la página {page_num}")
                                else:
                                    st.warning("⚠️ OCR no extrajo texto del documento")
                                    st.info("Posibles razones:\n- Imagen de muy baja calidad\n- PDF sin contenido de texto\n- Idioma no soportado")
                            
                            # Navegar a resultados detallados
                            st.divider()
                            st.success("💡 Ve a la pestaña **'Resultados'** para ver análisis detallado")
                        
                        else:
                            status_text.error(f"❌ Error durante el procesamiento: {result.get('error', 'Error desconocido')}")
                    
                    except (ValueError, TypeError, FileNotFoundError, OSError, RuntimeError) as e:
                        status_text.error(f"❌ Error: {str(e)}")
                    
                    finally:
                        # Limpiar archivo temporal de forma segura
                        try:
                            if os.path.exists(temp_path):
                                os.remove(temp_path)
                        except (OSError, PermissionError, FileNotFoundError) as cleanup_error:
                            st.warning(f"⚠️ Advertencia: No se pudo limpiar el archivo temporal. {str(cleanup_error)}")
    
    # TAB 2: Resultados Detallados
    with tab2:
        st.header("📊 Resultados Detallados")
        
        if st.session_state.last_result is None:
            st.info("💡 Procesa un archivo en la pestaña **'Procesar Archivo'** para ver resultados detallados")
        else:
            result = st.session_state.last_result
            
            # Información general
            st.subheader("📋 Información General")
            gen_col1, gen_col2, gen_col3 = st.columns(3)
            
            with gen_col1:
                input_file = result.get("input_file", "N/A")
                if input_file and input_file != "N/A":
                    file_name = Path(input_file).name
                else:
                    file_name = "N/A"
                st.metric("📁 Archivo", file_name)
            with gen_col2:
                st.metric("🔤 Formato", result.get("format", "N/A").upper() if result.get("format") else "N/A")
            with gen_col3:
                status = "✅ Éxito" if result.get("status") == "success" else "❌ Error"
                st.metric("✅ Estado", status)
            
            st.divider()
            
            # Desglose por pasos
            steps = result.get("steps", {})
            if steps:
                st.subheader("🔧 Desglose del Procesamiento")
                
                # OCR Results
                ocr_data = steps.get("ocr", {})
                if ocr_data:
                    with st.expander("🔤 Paso 1: OCR (Reconocimiento Óptico de Caracteres)", expanded=True):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("✅ Estado", "Éxito" if ocr_data.get("status") == "success" else "Error")
                        with col2:
                            confidence = ocr_data.get("confidence", 0)
                            color = "🟢" if confidence > 80 else "🟡" if confidence > 60 else "🔴"
                            st.metric("📊 Confianza", f"{color} {confidence:.0f}%")
                        with col3:
                            st.metric("🗣️ Idioma", {
                                "spa": "🇪🇸 Español",
                                "eng": "🇬🇧 Inglés",
                                "fra": "🇫🇷 Francés",
                                "deu": "🇩🇪 Alemán"
                            }.get(ocr_data.get("language"), "N/A"))
                else:
                    st.warning("⚠️ Datos de OCR no disponibles")
                
                # Data Extraction Results
                extraction = result.get("steps", {}).get("extraction", {})
                if extraction:
                    with st.expander("🔍 Paso 2: Extracción de Datos", expanded=True):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**📧 Emails encontrados:**")
                            emails = extraction.get("emails", [])
                            if emails:
                                for email in emails:
                                    st.code(email, language="text")
                            else:
                                st.info("No se encontraron emails")
                            
                            st.write("**📱 Teléfonos encontrados:**")
                            phones = extraction.get("phones", [])
                            if phones:
                                for phone in phones:
                                    st.code(phone, language="text")
                            else:
                                st.info("No se encontraron teléfonos")
                            
                            st.write("**🔗 URLs encontradas:**")
                            urls = extraction.get("urls", [])
                            if urls:
                                for url in urls:
                                    st.code(url, language="text")
                            else:
                                st.info("No se encontraron URLs")
                        
                        with col2:
                            st.write("**📅 Fechas encontradas:**")
                            dates = extraction.get("dates", [])
                            if dates:
                                for date in dates:
                                    st.code(date, language="text")
                            else:
                                st.info("No se encontraron fechas")
                            
                            st.write("**💰 Valores monetarios:**")
                            currency = extraction.get("currency", [])
                            if currency:
                                for val in currency:
                                    st.code(val, language="text")
                            else:
                                st.info("No se encontraron valores")
                            
                            st.write("**🆔 DNI/RFC encontrados:**")
                            dni_list = extraction.get("dni", [])
                            rfc_list = extraction.get("rfc", [])
                            if dni_list or rfc_list:
                                if dni_list:
                                    for dni in dni_list:
                                        st.code(f"DNI: {dni}", language="text")
                                if rfc_list:
                                    for rfc in rfc_list:
                                        st.code(f"RFC: {rfc}", language="text")
                            else:
                                st.info("No se encontraron DNI/RFC")
                else:
                    st.warning("⚠️ Extracción de datos no disponible")
                
                # Classification Results
                classification = result.get("steps", {}).get("classification", {})
                if classification:
                    with st.expander("🏷️ Paso 3: Clasificación de Documento", expanded=True):
                        col1, col2 = st.columns([1, 2])
                        
                        with col1:
                            class_name = classification.get("class", "desconocida").upper()
                            confidence = classification.get("confidence", 0)
                            
                            # Color según confianza
                            if confidence > 0.8:
                                color = "🟢"
                            elif confidence > 0.6:
                                color = "🟡"
                            else:
                                color = "🔴"
                            
                            st.metric("🏷️ Clase", class_name)
                            st.metric("📊 Confianza", f"{color} {confidence * 100:.1f}%")
                        
                        with col2:
                            st.write("**Probabilidades por Clase:**")
                            probabilities = classification.get("probabilities", {})
                            if probabilities:
                                # Ordenar por probabilidad
                                for cls, prob in sorted(probabilities.items(), key=lambda x: x[1], reverse=True):
                                    # Barra de progreso para cada clase
                                    st.write(f"{cls.upper()}")
                                    st.progress(prob, text=f"{prob * 100:.1f}%")
                            else:
                                st.info("Probabilidades no disponibles")
                else:
                    st.warning("⚠️ Clasificación no disponible")
            
            st.divider()
            
            # Exportar resultados
            st.subheader("💾 Exportar Resultados")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                json_str = json.dumps(result, indent=2, ensure_ascii=False)
                st.download_button(
                    label="📥 Descargar JSON",
                    data=json_str,
                    file_name=f"resultado_ocr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            with col2:
                # Copiar JSON al portapapeles
                st.info("📋 JSON disponible arriba para copiar")
            
            with col3:
                if st.button("🔄 Limpiar Resultados", use_container_width=True):
                    st.session_state.last_result = None
                    st.rerun()
    
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
