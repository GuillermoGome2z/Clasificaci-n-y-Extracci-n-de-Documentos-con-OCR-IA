"""
Aplicación Streamlit para OCR IA Project
"""

import html as _html
import json
import logging
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# Agregar raíz del proyecto al path antes de cualquier import local.
# Necesario cuando Streamlit se ejecuta desde app/ o desde cualquier CWD distinto a la raíz.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

logger = logging.getLogger(__name__)

import streamlit as st

from src.pipeline import OCRPipeline

# Configuración de la página
st.set_page_config(
    page_title="Sistema Inteligente OCR + IA",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    /* ── Variables de color ────────────────────────────── */
    :root {
        --primary: #1e3a8a;
        --primary-light: #3b82f6;
        --accent: #06b6d4;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --gray-50: #f9fafb;
        --gray-100: #f3f4f6;
        --gray-800: #1f2937;
        --gray-900: #111827;
    }

    /* ── Header institucional ───────────────────────────── */
    .header-institucional {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #06b6d4 100%);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(30, 58, 138, 0.3);
        position: relative;
        overflow: hidden;
    }

    .header-institucional::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 600px;
        height: 600px;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        pointer-events: none;
    }

    .header-content {
        position: relative;
        z-index: 1;
    }

    .header-uni {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
        margin-bottom: 1rem;
    }

    .uni-tag {
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 2px;
        opacity: 0.95;
    }

    .curso-tag {
        font-size: 0.85rem;
        opacity: 0.85;
        font-weight: 500;
    }

    .header-title {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0.5rem 0 1rem 0;
        letter-spacing: -1px;
        line-height: 1.1;
    }

    .header-subtitle {
        font-size: 1rem;
        opacity: 0.9;
        max-width: 700px;
        margin-bottom: 1.5rem;
        line-height: 1.5;
    }

    .header-stats {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
    }

    .stat-pill {
        background: rgba(255,255,255,0.15);
        backdrop-filter: blur(10px);
        padding: 0.75rem 1.25rem;
        border-radius: 12px;
        display: flex;
        flex-direction: column;
        align-items: center;
        min-width: 100px;
        border: 1px solid rgba(255,255,255,0.2);
        transition: transform 0.2s;
    }

    .stat-pill:hover {
        transform: translateY(-2px);
        background: rgba(255,255,255,0.25);
    }

    .stat-value {
        font-size: 1.5rem;
        font-weight: 800;
        line-height: 1;
    }

    .stat-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.25rem;
        opacity: 0.9;
    }

    /* ── Badges de categoría con gradientes ──────────────── */
    .badge-resultado {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.6rem 1.5rem;
        border-radius: 30px;
        font-weight: 700;
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        color: white;
    }

    .badge-factura       { background: linear-gradient(135deg, #10b981, #059669); }
    .badge-recibo        { background: linear-gradient(135deg, #f59e0b, #d97706); }
    .badge-contrato      { background: linear-gradient(135deg, #8b5cf6, #7c3aed); }
    .badge-constancia    { background: linear-gradient(135deg, #06b6d4, #0891b2); }
    .badge-carta_formal  { background: linear-gradient(135deg, #ec4899, #db2777); }
    .badge-identificacion{ background: linear-gradient(135deg, #6366f1, #4f46e5); }
    .badge-otro          { background: linear-gradient(135deg, #6b7280, #4b5563); }

    /* ── Cards de resultados ────────────────────────────── */
    .result-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid var(--primary-light);
        margin-bottom: 1rem;
        transition: transform 0.2s, box-shadow 0.2s;
    }

    .result-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.12);
    }

    .result-card-header {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: var(--primary);
        margin-bottom: 0.5rem;
    }

    .result-card-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--gray-900);
    }

    /* ── Botón de procesar mejorado ──────────────────────── */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-weight: 700;
        font-size: 1rem;
        letter-spacing: 1px;
        text-transform: uppercase;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(30, 58, 138, 0.3);
        transition: all 0.2s;
    }

    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(30, 58, 138, 0.4);
    }

    /* ── Tabs mejoradas ──────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: var(--gray-100);
        padding: 0.5rem;
        border-radius: 12px;
    }

    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        padding: 0.5rem 1.5rem;
        border-radius: 8px;
        transition: all 0.2s;
    }

    .stTabs [aria-selected="true"] {
        background: white;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }

    /* ── File uploader ────────────────────────────────────── */
    [data-testid="stFileUploader"] {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        padding: 2rem;
        border-radius: 12px;
        border: 2px dashed var(--primary-light);
        transition: all 0.2s;
    }

    [data-testid="stFileUploader"]:hover {
        border-color: var(--primary);
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
    }

    /* ── Métricas ────────────────────────────────────────── */
    [data-testid="stMetric"] {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        border-top: 3px solid var(--primary-light);
    }

    /* ── Sidebar ─────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f9fafb 0%, #f3f4f6 100%);
    }

    [data-testid="stSidebar"] h1 {
        color: var(--primary);
        font-weight: 800;
    }

    /* ── Status boxes ────────────────────────────────────── */
    .info-card {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        padding: 1rem 1.5rem;
        border-radius: 10px;
        border-left: 4px solid var(--primary-light);
        margin: 1rem 0;
    }

    .success-card {
        background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
        padding: 1rem 1.5rem;
        border-radius: 10px;
        border-left: 4px solid var(--success);
        margin: 1rem 0;
    }

    /* ── Footer ──────────────────────────────────────────── */
    .footer-institucional {
        background: linear-gradient(135deg, var(--gray-900) 0%, var(--gray-800) 100%);
        color: white;
        text-align: center;
        padding: 2rem;
        border-radius: 16px;
        margin-top: 3rem;
    }

    .footer-title {
        font-weight: 800;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
        letter-spacing: 0.5px;
    }

    .footer-info {
        opacity: 0.85;
        font-size: 0.9rem;
        margin-bottom: 0.25rem;
    }

    .footer-credits {
        opacity: 0.7;
        font-size: 0.8rem;
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(255,255,255,0.15);
    }

    /* ── Animaciones ─────────────────────────────────────── */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .header-institucional, .result-card {
        animation: fadeInUp 0.5s ease-out;
    }

    /* ── Esconder elementos default de Streamlit ────────── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# Inicializar sesión
if "pipeline" not in st.session_state:
    st.session_state.pipeline = None
if "last_result" not in st.session_state:
    st.session_state.last_result = None

def load_pipeline(tesseract_path=None):
    """Crea una instancia del pipeline por sesión (no compartida entre usuarios)."""
    return OCRPipeline(tesseract_path=tesseract_path)

# ── AUTO-INICIALIZACIÓN ──────────────────────────────────────────
# Si Tesseract está disponible y el pipeline no se ha inicializado,
# lo inicializa automáticamente al abrir la app.
if st.session_state.pipeline is None:
    try:
        from config import TESSERACT_PATH as _TESS_PATH
        if _TESS_PATH:
            st.session_state.pipeline = load_pipeline(
                tesseract_path=_TESS_PATH
            )
    except (ImportError, OSError, RuntimeError):
        pass  # Si falla, el usuario lo inicializa manualmente
# ────────────────────────────────────────────────────────────────

# Sidebar - Configuración
with st.sidebar:
    st.title("⚙️ Configuración")
    
    st.markdown("---")
    st.markdown("### 📚 Stack Tecnológico")
    st.markdown("""
    - **Pytesseract**: Reconocimiento óptico
    - **Scikit-learn**: Clasificación ML
    - **Streamlit**: Interfaz web
    - **OpenCV**: Procesamiento imagen
    """)
    
    st.markdown("---")
    st.markdown("### 🎯 Capacidades")
    st.markdown("""
    ✅ OCR múltiples idiomas
    ✅ Extracción de datos
    ✅ Clasificación 7 categorías
    ✅ JSON exportable
    """)
    
    st.markdown("---")

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
            pipeline = load_pipeline(tesseract_path=tesseract_path)
            st.session_state.pipeline = pipeline
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
    st.markdown("Confianza modelo: **83.76%** ✅")


# Header principal institucional
st.markdown("""
<div class="header-institucional">
    <div class="header-content">
        <div class="header-uni">
            <span class="uni-tag">UNIVERSIDAD MARIANO GÁLVEZ DE GUATEMALA</span>
            <span class="curso-tag">Curso 045 · Inteligencia Artificial · Proyecto 04</span>
        </div>
        <h1 class="header-title">Sistema Inteligente OCR + IA</h1>
        <p class="header-subtitle">
            Clasificación automática y extracción de datos en documentos
            mediante Reconocimiento Óptico de Caracteres y Machine Learning
        </p>
        <div class="header-stats">
            <div class="stat-pill">
                <span class="stat-value">7</span>
                <span class="stat-label">Categorías</span>
            </div>
            <div class="stat-pill">
                <span class="stat-value">99.4%</span>
                <span class="stat-label">F1-Macro</span>
            </div>
            <div class="stat-pill">
                <span class="stat-value">245</span>
                <span class="stat-label">Documentos</span>
            </div>
            <div class="stat-pill">
                <span class="stat-value">119/119</span>
                <span class="stat-label">Tests</span>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

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
    with st.expander(
        "📋 Ver instrucciones de Instalación",
        expanded=False
    ):
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
                    process_button = st.button(
                        "🚀 PROCESAR",
                        use_container_width=True,
                        type="primary"
                    )

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

                        if result.get("status") == "success":
                            status_text.success("✅ ¡Procesamiento completado exitosamente!")

                            # Mostrar estadísticas rápidas
                            st.divider()
                            st.subheader("📊 Estadísticas de Procesamiento")

                            stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)

                            with stats_col1:
                                ocr_data = result.get("steps", {}).get("ocr", {})
                                if ocr_data:
                                    confidence = ocr_data.get("confidence", 0)
                                    if confidence < 0:
                                        st.metric("🔤 Confianza OCR", "Sin texto")
                                    else:
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
                                # Para PDFs buscar también en pages[0]
                                if not classification:
                                    pages = result.get("pages", [])
                                    if pages:
                                        classification = pages[0].get("classification", {})
                                if classification:
                                    # El clasificador puede devolver "predicted_class" o "class"
                                    class_name = (classification.get("predicted_class")
                                                 or classification.get("class", "N/A"))
                                    st.metric("🏷️ Clasificación", class_name.title())
                                else:
                                    st.metric("🏷️ Clasificación", "N/A")

                            # Mostrar texto extraído (FIX multi-página)
                            st.divider()
                            st.subheader("📋 Texto Extraído (OCR)")

                            extracted_text = result.get("extracted_text", "").strip()
                            pages = result.get("pages", [])

                            if extracted_text:
                                # Caso 1: Imagen única (no es PDF multi-página)
                                st.text_area(
                                    "Contenido del documento:",
                                    value=extracted_text,
                                    height=300,
                                    disabled=True,
                                    key="ocr_output_single"
                                )

                            elif pages and len(pages) > 0:
                                # Caso 2: PDF multi-página (FIX aplicado aquí)
                                num_pages = len(pages)

                                # Info del documento
                                st.markdown(f"""
                                <div class="info-card">
                                    📑 <strong>Documento PDF con {num_pages} página(s)</strong><br/>
                                    <span style="font-size: 0.9rem; opacity: 0.85;">
                                        Usa el selector para navegar entre páginas. Todas las páginas
                                        ya fueron procesadas — la navegación es instantánea.
                                    </span>
                                </div>
                                """, unsafe_allow_html=True)

                                # Selector con tabs si hay pocas páginas, o selectbox si hay muchas
                                if num_pages <= 5:
                                    # Tabs para 1-5 páginas (más visual)
                                    page_tabs = st.tabs([f"📄 Página {i+1}" for i in range(num_pages)])

                                    for idx, page_tab in enumerate(page_tabs):
                                        with page_tab:
                                            page_data = pages[idx]
                                            page_text = page_data.get("text", "").strip()

                                            col_a, col_b = st.columns([3, 1])
                                            with col_a:
                                                st.markdown(f"**Texto extraído (Página {idx+1}):**")
                                            with col_b:
                                                if page_text:
                                                    st.markdown(f"<span style='float:right; font-size:0.85rem; color:#10b981;'>"
                                                               f"✅ {len(page_text.split())} palabras</span>",
                                                               unsafe_allow_html=True)

                                            if page_text:
                                                st.text_area(
                                                    f"Contenido página {idx+1}:",
                                                    value=page_text,
                                                    height=250,
                                                    disabled=True,
                                                    key=f"ocr_page_{idx}",
                                                    label_visibility="collapsed"
                                                )
                                            else:
                                                st.warning(f"⚠️ No se extrajo texto en la página {idx+1}")

                                            # Mostrar clasificación de esa página si existe
                                            page_classification = page_data.get("classification", {})
                                            if page_classification:
                                                page_class = (page_classification.get("predicted_class")
                                                             or page_classification.get("class", "?"))
                                                page_conf = page_classification.get("confidence", 0) or 0
                                                st.markdown(
                                                    f"**Clasificación de esta página:** "
                                                    f"`{page_class.upper()}` "
                                                    f"({page_conf:.1%} confianza)"
                                                )
                                else:
                                    # Selectbox para 6+ páginas
                                    selected_page = st.selectbox(
                                        "Selecciona la página a visualizar:",
                                        options=list(range(1, num_pages + 1)),
                                        format_func=lambda x: f"📄 Página {x} de {num_pages}",
                                        key="page_selector"
                                    )

                                    page_data = pages[selected_page - 1]
                                    page_text = page_data.get("text", "").strip()

                                    if page_text:
                                        st.text_area(
                                            f"Contenido página {selected_page}:",
                                            value=page_text,
                                            height=300,
                                            disabled=True,
                                            key=f"ocr_multi_{selected_page}"
                                        )

                                        # Estadísticas de la página
                                        cols = st.columns(3)
                                        with cols[0]:
                                            st.metric("📝 Palabras", len(page_text.split()))
                                        with cols[1]:
                                            st.metric("📏 Caracteres", len(page_text))
                                        with cols[2]:
                                            page_classification = page_data.get("classification", {})
                                            page_class = (page_classification.get("predicted_class")
                                                         or page_classification.get("class", "?"))
                                            st.metric("🏷️ Tipo", page_class.upper() if page_class else "N/A")
                                    else:
                                        st.warning(f"⚠️ No se extrajo texto en la página {selected_page}")

                                # Resumen general del PDF multi-página
                                st.divider()
                                st.markdown("### 📊 Resumen del Documento Completo")

                                # Calcular estadísticas globales
                                total_palabras = sum(
                                    len((p.get("text", "") or "").split())
                                    for p in pages
                                )
                                paginas_con_texto = sum(
                                    1 for p in pages
                                    if (p.get("text", "") or "").strip()
                                )

                                # Clasificaciones por página
                                clases_por_pagina = []
                                for p in pages:
                                    c = p.get("classification", {})
                                    clase = c.get("predicted_class") or c.get("class", "?")
                                    clases_por_pagina.append(clase)

                                # Categoría dominante (la que más se repite)
                                from collections import Counter
                                if clases_por_pagina:
                                    contador = Counter(clases_por_pagina)
                                    clase_dominante, freq = contador.most_common(1)[0]
                                else:
                                    clase_dominante, freq = "N/A", 0

                                summary_cols = st.columns(4)
                                with summary_cols[0]:
                                    st.metric("📑 Páginas totales", num_pages)
                                with summary_cols[1]:
                                    st.metric("✅ Con texto", paginas_con_texto)
                                with summary_cols[2]:
                                    st.metric("📝 Palabras totales", f"{total_palabras:,}")
                                with summary_cols[3]:
                                    st.metric(
                                        "🏷️ Categoría dominante",
                                        clase_dominante.upper() if clase_dominante != "N/A" else "N/A",
                                        delta=f"{freq}/{num_pages} páginas"
                                    )

                            else:
                                # Caso 3: Sin texto extraído
                                st.warning("⚠️ OCR no extrajo texto del documento")
                                st.markdown("""
                                <div class="info-card">
                                    <strong>Posibles razones:</strong>
                                    <ul style="margin-top: 0.5rem;">
                                        <li>Imagen de muy baja calidad o muy borrosa</li>
                                        <li>PDF sin contenido de texto reconocible</li>
                                        <li>Documento en idioma no soportado</li>
                                        <li>Resolución insuficiente para OCR</li>
                                    </ul>
                                </div>
                                """, unsafe_allow_html=True)

                            # Navegar a resultados detallados
                            st.divider()
                            st.success("💡 Ve a la pestaña **'Resultados'** para ver análisis detallado")

                        else:
                            status_text.error(f"❌ Error durante el procesamiento: {result.get('error', 'Error desconocido')}")

                    except (ValueError, TypeError, FileNotFoundError, OSError, RuntimeError) as e:
                        status_text.error(f"❌ Error: {str(e)}")

                    finally:
                        # Limpiar archivo temporal — missing_ok evita error si ya fue borrado
                        try:
                            Path(temp_path).unlink(missing_ok=True)
                        except PermissionError:
                            # Windows puede mantener el archivo bloqueado brevemente;
                            # el SO lo eliminará de AppData\Local\Temp al reiniciar.
                            logger.warning("No se pudo eliminar temp: %s", temp_path)

    # TAB 2: Resultados Detallados
    with tab2:
        st.header("📊 Resultados Detallados")

        if st.session_state.last_result is None:
            st.info("💡 Procesa un archivo en la pestaña **'Procesar Archivo'** para ver resultados detallados")
        else:
            result = st.session_state.last_result

            # ── FIX PDF: Normalizar estructura para que TAB 2 encuentre los datos ──
            # El pipeline guarda datos de PDFs en result["pages"][0]
            # pero la UI los busca en result["steps"]. Este bloque los sincroniza.
            _pages = result.get("pages") or []
            _steps = result.get("steps") or {}

            if _pages:
                _primera = _pages[0]

                # Inicializar steps si no existe
                if not _steps:
                    result["steps"] = {}
                    _steps = result["steps"]

                # Copiar OCR
                if not _steps.get("ocr"):
                    _page_text = _primera.get("text", "") or ""
                    _steps["ocr"] = {
                        "status": "success" if _page_text.strip() else "warning",
                        "confidence": _primera.get("confidence", 80),
                        "language": _primera.get("language", "eng"),
                    }
                    result["steps"] = _steps

                # Copiar extracción
                if not _steps.get("extraction"):
                    _ext = (_primera.get("extraction")
                            or _primera.get("extracted_data")
                            or {})
                    if _ext:
                        _steps["extraction"] = _ext
                        result["steps"] = _steps

                # Copiar clasificación
                if not _steps.get("classification"):
                    _clf = _primera.get("classification") or {}
                    if _clf:
                        _steps["classification"] = _clf
                        result["steps"] = _steps

                # Asegurar extracted_text para otras partes de la UI
                if not result.get("extracted_text"):
                    result["extracted_text"] = _primera.get("text", "") or ""
            # ── FIN DEL FIX ────────────────────────────────────────────────────

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
                            if confidence < 0:
                                st.metric("📊 Confianza", "⚠️ Sin texto")
                            else:
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

                        # ── Sección 1: Datos de Contacto y Generales ──────────────────
                        st.markdown("#### 📬 Datos de Contacto y Generales")
                        col1, col2 = st.columns(2)

                        with col1:
                            st.write("**📧 Emails:**")
                            emails = extraction.get("emails", [])
                            if emails:
                                for email in emails:
                                    st.code(email, language="text")
                            else:
                                st.caption("No se encontraron datos")

                            st.write("**📱 Teléfonos (Guatemala):**")
                            phones = extraction.get("phones", [])
                            if phones:
                                for phone in phones:
                                    st.code(phone, language="text")
                            else:
                                st.caption("No se encontraron datos")

                            st.write("**🔗 URLs:**")
                            urls = extraction.get("urls", [])
                            if urls:
                                for url in urls:
                                    st.code(url, language="text")
                            else:
                                st.caption("No se encontraron datos")

                        with col2:
                            st.write("**📅 Fechas (numéricas):**")
                            dates = extraction.get("dates", [])
                            if dates:
                                for date in dates:
                                    st.code(date, language="text")
                            else:
                                st.caption("No se encontraron datos")

                            st.write("**📅 Fechas (en español):**")
                            fechas_texto = extraction.get("fecha_texto", [])
                            if fechas_texto:
                                for ft in fechas_texto:
                                    st.code(ft, language="text")
                            else:
                                st.caption("No se encontraron datos")

                            st.write("**💰 Moneda / Valores monetarios:**")
                            currency = extraction.get("currency", [])
                            if currency:
                                for val in currency:
                                    st.code(val, language="text")
                            else:
                                st.caption("No se encontraron datos")

                        st.divider()

                        # ── Sección 2: Datos Tributarios Guatemala ─────────────────────
                        st.markdown("#### 🇬🇹 Datos Tributarios (Guatemala)")
                        col3, col4 = st.columns(2)

                        with col3:
                            st.write("**🆔 NIT (Número de Identificación Tributaria):**")
                            nit_list = extraction.get("nit", [])
                            if nit_list:
                                for nit in nit_list:
                                    st.code(nit, language="text")
                            else:
                                st.caption("No se encontraron datos")

                            st.write("**🪪 DPI / CUI:**")
                            dpi_list = extraction.get("dpi", [])
                            if dpi_list:
                                for dpi in dpi_list:
                                    st.code(dpi, language="text")
                            else:
                                st.caption("No se encontraron datos")

                            st.write("**💱 Moneda:**")
                            moneda_list = extraction.get("moneda", [])
                            if moneda_list:
                                for m in moneda_list:
                                    st.code(m, language="text")
                            else:
                                st.caption("No se encontraron datos")

                        with col4:
                            st.write("**📑 Serie DTE (SAT):**")
                            serie_dte = extraction.get("serie_dte", [])
                            if serie_dte:
                                for s in serie_dte:
                                    st.code(s, language="text")
                            else:
                                st.caption("No se encontraron datos")

                            st.write("**🔑 Serie FEL (SAT):**")
                            serie_sat = extraction.get("serie_sat", [])
                            if serie_sat:
                                for s in serie_sat:
                                    st.code(s, language="text")
                            else:
                                st.caption("No se encontraron datos")

                            st.write("**💳 Forma de Pago:**")
                            forma_pago = extraction.get("forma_pago", [])
                            if forma_pago:
                                for fp in forma_pago:
                                    st.code(fp, language="text")
                            else:
                                st.caption("No se encontraron datos")

                        # ── Sección 3: FEL — Autorización y DTE ───────────────────────
                        auth_list = extraction.get("autorizacion_sat", [])
                        dte_list = extraction.get("numero_dte", [])
                        if auth_list or dte_list:
                            st.divider()
                            st.markdown("#### 🏛️ Autorización SAT / FEL")
                            fel_col1, fel_col2 = st.columns(2)

                            with fel_col1:
                                st.write("**🔐 Número de Autorización SAT:**")
                                if auth_list:
                                    for auth in auth_list:
                                        st.code(auth, language="text")
                                else:
                                    st.caption("No se encontraron datos")

                            with fel_col2:
                                st.write("**📟 Número DTE:**")
                                if dte_list:
                                    for dte in dte_list:
                                        st.code(dte, language="text")
                                else:
                                    st.caption("No se encontraron datos")
                else:
                    st.warning("⚠️ Extracción de datos no disponible")

                # Classification Results
                classification = result.get("steps", {}).get("classification", {})
                if classification:
                    with st.expander("🏷️ Paso 3: Clasificación de Documento", expanded=True):
                        col1, col2 = st.columns([1, 2])

                        with col1:
                            # El clasificador puede devolver "predicted_class" o "class"
                            class_name = (classification.get("predicted_class")
                                         or classification.get("class", "desconocida")).lower()
                            confidence = classification.get("confidence", 0) or 0

                            # Seleccionar badge según clase con iconos
                            badge_map = {
                                "factura":        ("badge-factura",        "📄"),
                                "recibo":         ("badge-recibo",         "🧾"),
                                "contrato":       ("badge-contrato",       "📋"),
                                "constancia":     ("badge-constancia",     "📜"),
                                "carta_formal":   ("badge-carta_formal",   "✉️"),
                                "identificacion": ("badge-identificacion", "🆔"),
                                "otro":           ("badge-otro",           "📁"),
                            }
                            badge_class, badge_icon = badge_map.get(class_name, ("badge-otro", "📁"))

                            # Mostrar badge HTML mejorado (class_name escapado para evitar XSS)
                            _safe_label = _html.escape(class_name.upper().replace("_", " "))
                            st.markdown(
                                f'<div class="badge-resultado {badge_class}">'
                                f'<span style="font-size: 1.3rem;">{badge_icon}</span>'
                                f'<span>{_safe_label}</span>'
                                f'</div>',
                                unsafe_allow_html=True
                            )

                            # Color según confianza
                            if confidence > 0.8:
                                color = "🟢"
                            elif confidence > 0.6:
                                color = "🟡"
                            else:
                                color = "🔴"

                            st.markdown("")  # Espacio
                            st.metric("📊 Confianza", f"{color} {confidence * 100:.1f}%")

                        with col2:
                            st.write("### 📊 Probabilidades por Categoría")
                            probabilities = classification.get("probabilities", {})
                            if probabilities:
                                # Ordenar de mayor a menor
                                sorted_probs = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)

                                # Mostrar como barras visuales con colores
                                color_map = {
                                    'factura': '#10b981',
                                    'recibo': '#f59e0b',
                                    'contrato': '#8b5cf6',
                                    'constancia': '#06b6d4',
                                    'carta_formal': '#ec4899',
                                    'identificacion': '#6366f1',
                                    'otro': '#6b7280',
                                }

                                for cls, prob in sorted_probs:
                                    color = color_map.get(cls.lower(), '#6b7280')
                                    pct = prob * 100
                                    # Barra HTML personalizada
                                    st.markdown(f"""
                                    <div style="margin-bottom: 0.75rem;">
                                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                                            <span style="font-weight: 600; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 0.5px;">
                                                {cls}
                                            </span>
                                            <span style="font-weight: 700; color: {color};">
                                                {pct:.1f}%
                                            </span>
                                        </div>
                                        <div style="background: #f3f4f6; border-radius: 6px; height: 12px; overflow: hidden;">
                                            <div style="
                                                background: linear-gradient(90deg, {color}aa, {color});
                                                width: {pct}%;
                                                height: 100%;
                                                border-radius: 6px;
                                                transition: width 0.5s ease;
                                            "></div>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
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
          - **Extracción de Datos**: Emails, teléfonos GT, fechas, URLs, moneda Q/GTQ, NIT, DPI/CUI, Serie DTE, Forma de pago
          - **Clasificación**: Tipo de documento y probabilidades

        ### 4️⃣ Descargar Resultados
        - Descarga los resultados en formato JSON
        - Úsalos en otros sistemas

        ## 🎯 Casos de Uso

        - **Facturas y Recibos**: Extrae montos, fechas, datos de contacto
        - **Contratos**: Identifica y extrae cláusulas importantes
        - **Documentos de Identidad**: Extrae NIT, DPI/CUI y datos personales guatemaltecos
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

# Footer institucional
st.markdown("---")
st.markdown("""
<div class="footer-institucional">
    <div class="footer-title">🤖 SISTEMA INTELIGENTE OCR + IA</div>
    <div class="footer-info">
        Universidad Mariano Gálvez de Guatemala · Facultad de Ingeniería
    </div>
    <div class="footer-info">
        Curso 045 — Inteligencia Artificial · Catedrático: Ing. MA. Carmelo Estuardo Mayén Monterroso
    </div>
    <div class="footer-info">
        Proyecto 04 — Clasificación y Extracción de Documentos con OCR + IA
    </div>
    <div class="footer-credits">
        Stack: Python 3.13 · Tesseract 5.5.0 · scikit-learn (LinearSVC + TF-IDF) · Streamlit<br/>
        7 categorías · 490 documentos · F1-macro 0.9940 · 120/120 tests · Versión 1.0.0
    </div>
</div>
""", unsafe_allow_html=True)

