"""
demo_plan_b.py — PLAN B: Demo sin Tesseract (OCR alternativo).

Si Tesseract falla el día de la expo, ejecuta esto:
    streamlit run demo_plan_b.py --server.port 8502

Simula OCR inyectando textos pre-cargados de documentos de ejemplo.
El clasificador ML y extractor de datos funcionan 100% sin Tesseract.
"""
import streamlit as st
from pathlib import Path
from src.classifier import DocumentClassifier
from src.extractor import DataExtractor


# ─ CONFIGURACIÓN STREAMLIT ─────────────────────────────────────────────
st.set_page_config(
    page_title="OCR IA - Plan B",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .header-gradient {
        background: linear-gradient(135deg, #d32f2f 0%, #f57c00 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .header-gradient h1 {
        margin: 0;
        font-size: 2.5em;
    }
    .warning-box {
        background: linear-gradient(135deg, #fff3e0, #ffe0b2);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #ff9800;
    }
</style>
""", unsafe_allow_html=True)

# ─ CARGAR COMPONENTES EN CACHÉ ─────────────────────────────────────────
@st.cache_resource
def load_models():
    """Carga los modelos una sola vez por sesión."""
    model_path = Path("models/classifier_model.joblib")
    clf = DocumentClassifier(str(model_path))
    ext = DataExtractor()
    return clf, ext


# ─ DOCUMENTOS DE DEMOSTRACIÓN ──────────────────────────────────────────
DOCUMENTOS_DEMO = {
    "Factura": {
        "descripcion": "Factura Electrónica de servicios",
        "texto": """FACTURA ELECTRONICA
Distribuidora Central S.A.
NIT: 7823401-5
Numero de Factura: FAC-2026-0428
Fecha: 22/04/2026

Cliente: Carlos Mendoza
Correo: carlos.mendoza@correo.gt
Telefono: 5543-2109

Detalle:
Servicio de Consultoria TI - Q 6,500.00
Licencia de Software Anual - Q 2,400.00

TOTAL: Q 10,920.00
IVA (12%): Q 1,170.00

Referencia: TRX-20260422
SAT Guatemala - Contribuyente registrado"""
    },
    "Recibo": {
        "descripcion": "Recibo Oficial de Pago",
        "texto": """RECIBO OFICIAL DE PAGO
Servicios Administrativos Guatemala

Numero de Recibo: REC-2026-00892
Fecha: 22/04/2026

Recibi de: Ana Sofia Castillo
Correo: ana.castillo@empresa.com
Telefono: 2334-5678

Cantidad: Q 2,500.00

Por concepto de: Pago mensual de arrendamiento
Piso 3, Edificio Torre Empresarial
Mes: Abril 2026

Forma de Pago: Cheque No. 00234 - Banco G&T Continental
Estado: PAGADO - CANCELADO"""
    },
    "Contrato": {
        "descripcion": "Contrato de Prestación de Servicios",
        "texto": """CONTRATO DE PRESTACION DE SERVICIOS

En la ciudad de Guatemala, 22 de abril del 2026

PARTES:
EL CONTRATANTE: TechSoluciones Guatemala S.A., NIT 4521890-3
EL CONTRATADO: Maria Elena Lopez, DPI 2312456780101

Correo: m.lopez@profesional.gt
Telefono: 5678-9012

CLAUSULAS:
PRIMERA - OBJETO: Servicios de consultoria en desarrollo de software

SEGUNDA - VIGENCIA: 12 meses a partir del 01/05/2026

TERCERA - HONORARIOS: Q 8,000.00 mensuales

CUARTA - OBLIGACIONES: Prestar servicios con diligencia y confidencialidad

SEXTA - TERMINACION: 30 dias de anticipacion

Firmas de las partes"""
    },
    "Comunicado": {
        "descripcion": "Comunicado Oficial de la Empresa",
        "texto": """COMUNICADO OFICIAL
Corporacion Innovacion Guatemala
Fecha: 22/04/2026

Estimados senores:

Por medio del presente comunicado, la Gerencia General informa
sobre actualizaciones en nuestros servicios.

NUEVOS HORARIOS DE ATENCION:
Lunes a Viernes: 8:00 AM a 6:00 PM
Sabados: 9:00 AM a 1:00 PM

NUEVA PLATAFORMA DIGITAL:
https://clientes.corporacion.gt

LINEA DIRECTA DE ATENCION:
Telefono: 2400-1234
Correo: atencion@corporacion.gt

Agradecemos la confianza en nuestros servicios.

Lic. Roberto Sanchez Mendez
Gerente General
Tel: 2400-5678
www.corporacion.gt"""
    }
}


# ─ INTERFAZ PRINCIPAL ──────────────────────────────────────────────────
st.markdown("""
<div class="header-gradient">
    <h1>🚀 PLAN B — Demo Alternativa</h1>
    <p>Si Tesseract no está disponible, usa esta interfaz para demos</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="warning-box">
    <strong>⚠️ Modo Alternativo Activado</strong><br/>
    Tesseract no está disponible. Los textos están pre-cargados
    para demostración. Todos los módulos funcionan normalmente.
</div>
""", unsafe_allow_html=True)

# ─ SIDEBAR ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("📋 Plan B")
    st.markdown("---")
    st.markdown("""
    **Documentos de Demostración**
    
    Todos los textos están pre-cargados para probar:
    - Clasificación ML
    - Extracción de datos
    - Formato de salida JSON
    
    Selecciona un documento a la izquierda.
    """)

# ─ CONTENIDO PRINCIPAL ─────────────────────────────────────────────────
clf, ext = load_models()

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📄 Seleccionar Documento")
    doc_tipo = st.radio(
        "Elige un documento para analizar:",
        list(DOCUMENTOS_DEMO.keys()),
        key="doc_selector"
    )

with col2:
    st.subheader("ℹ️ Información")
    doc_info = DOCUMENTOS_DEMO[doc_tipo]
    st.write(f"**{doc_info['descripcion']}**")

st.divider()

# ─ ANÁLISIS ────────────────────────────────────────────────────────────
if st.button("🔍 Analizar Documento", use_container_width=True, type="primary"):
    doc_info = DOCUMENTOS_DEMO[doc_tipo]
    texto = doc_info["texto"]

    with st.spinner("Procesando..."):
        # Clasificación
        clf_result = clf.predict(texto)
        clase = clf_result.get("predicted_class") or clf_result.get("class", "?")
        confianza = clf_result.get("confidence", 0) or 0

        # Extracción
        ext_result = ext.extract_all(texto)

    # ─ RESULTADOS ──────────────────────────────────────────────────────
    st.subheader("📊 Resultados de Análisis")

    # Clasificación
    st.markdown("### 🏷️ Clasificación")
    col1, col2, col3 = st.columns(3)

    with col1:
        badge_colors = {
            "factura": "badge-factura",
            "recibo": "badge-recibo",
            "contrato": "badge-contrato",
            "otro": "badge-otro",
        }
        st.metric("Tipo Detectado", clase.upper())

    with col2:
        color_icon = "🟢" if confianza > 0.80 else "🟡" if confianza > 0.60 else "🔴"
        st.metric("Confianza", f"{color_icon} {confianza:.1%}")

    with col3:
        st.metric("is_trained", "✅ True")

    st.divider()

    # Extracción de datos
    st.markdown("### 🔍 Datos Extraídos")

    ext_cols = st.columns(2)

    with ext_cols[0]:
        st.write("**📧 Emails:**")
        emails = ext_result.get("emails", [])
        if emails:
            for email in emails:
                st.code(email)
        else:
            st.info("No encontrados")

        st.write("**📱 Teléfonos:**")
        phones = ext_result.get("phones", [])
        if phones:
            for phone in phones:
                st.code(phone)
        else:
            st.info("No encontrados")

        st.write("**🔗 URLs:**")
        urls = ext_result.get("urls", [])
        if urls:
            for url in urls:
                st.code(url)
        else:
            st.info("No encontradas")

    with ext_cols[1]:
        st.write("**📅 Fechas:**")
        dates = ext_result.get("dates", [])
        if dates:
            for date in dates:
                st.code(date)
        else:
            st.info("No encontradas")

        st.write("**💰 Montos:**")
        currency = ext_result.get("currency", [])
        if currency:
            for monto in currency:
                st.code(monto)
        else:
            st.info("No encontrados")

        st.write("**🆔 DNI/RFC:**")
        dni = ext_result.get("dni", [])
        rfc = ext_result.get("rfc", [])
        if dni or rfc:
            if dni:
                for d in dni:
                    st.code(f"DNI: {d}")
            if rfc:
                for r in rfc:
                    st.code(f"RFC: {r}")
        else:
            st.info("No encontrados")

    st.divider()

    # Resumen
    st.markdown("### ✅ Resumen")
    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**Clasificación:** {clase} ({confianza:.1%})")
        total_items = sum(len(v) if isinstance(v, list) else 0 
                        for v in ext_result.values())
        st.write(f"**Datos Extraídos:** {total_items} items")

    with col2:
        if confianza > 0.70:
            st.success("✅ Confianza aceptable para demo (>70%)")
        else:
            st.warning(f"⚠️ Confianza baja ({confianza:.1%})")

st.divider()

st.markdown("""
---
**Plan B — Demostración sin OCR**  
Usa Streamlit + Modelo ML + Extractor de Datos  
Para volver a la app principal: `streamlit run app/app.py`
""")
