"""
Aplicación Streamlit para OCR IA Project
"""

import html as _html
import json
import logging
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# Agregar raíz del proyecto al path antes de cualquier import local.
# Necesario cuando Streamlit se ejecuta desde app/ o desde cualquier CWD distinto a la raíz.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

logger = logging.getLogger(__name__)

import streamlit as st  # pylint: disable=wrong-import-position

from src.pipeline import OCRPipeline  # pylint: disable=wrong-import-position


def _build_export_json(result: dict, original_filename: str) -> str:
    """Build clean, professional export JSON from a pipeline result dict.

    Replaces the temp input_file path with the original filename, adds
    processed_at timestamp, flattens the steps nesting, and ensures
    classification probabilities use category names as keys.
    """
    export: dict = {
        "original_filename": original_filename,
        "processed_at": datetime.now().isoformat(timespec="seconds"),
        "format": result.get("format", "unknown"),
        "status": result.get("status", "unknown"),
    }

    fmt = result.get("format", "")

    if fmt == "image":
        ocr_step = result.get("steps", {}).get("ocr", {})
        export["ocr"] = {
            "confidence": ocr_step.get("confidence"),
            "language": ocr_step.get("language"),
            "has_text": ocr_step.get("has_text"),
        }
        export["extraction"] = result.get("steps", {}).get("extraction", {})
        clf = result.get("steps", {}).get("classification", {})
        export["classification"] = {
            "class": clf.get("class"),
            "confidence": clf.get("confidence"),
            "probabilities": clf.get("probabilities", {}),
            "model_type": clf.get("model_type"),
        }
        export["extracted_text"] = result.get("extracted_text", "")
        export["lines"] = result.get("lines", [])
    else:
        # PDF — one entry per page
        pages_out = []
        for p in result.get("pages", []):
            clf_p = p.get("classification", {})
            pages_out.append({
                "page_number": p.get("page_number"),
                "extraction": p.get("extraction", {}),
                "classification": {
                    "class": clf_p.get("class"),
                    "confidence": clf_p.get("confidence"),
                    "probabilities": clf_p.get("probabilities", {}),
                    "model_type": clf_p.get("model_type"),
                },
                "text": p.get("text", ""),
            })
        export["total_pages"] = len(pages_out)
        export["pages"] = pages_out

    errors = result.get("errors", [])
    if errors:
        export["errors"] = errors

    return json.dumps(export, indent=2, ensure_ascii=False)

# ── Configuración de la página ───────────────────────────────────────────────
st.set_page_config(
    page_title="Sistema Inteligente OCR + IA",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════════════════════
#  SISTEMA DE DISEÑO "NEXUS PREMIUM"
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── Google Fonts (Inter) ───────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Variables del sistema ──────────────────────────────────────────────── */
:root {
    --p900: #1e1b4b;
    --p700: #4338ca;
    --p500: #6366f1;
    --p300: #a5b4fc;
    --p100: #e0e7ff;

    --accent:  #f59e0b;
    --accent2: #0ea5e9;
    --emerald: #059669;
    --rose:    #e11d48;
    --teal:    #0d9488;

    --surface:  #ffffff;
    --surf-alt: #f8f7ff;
    --surf-dark:#0f0e1a;

    --border:   rgba(99,102,241,0.15);
    --border-strong: rgba(99,102,241,0.35);

    --txt-1:  #111827;
    --txt-2:  #4b5563;
    --txt-3:  #9ca3af;

    --shadow-sm:  0 2px 8px rgba(67,56,202,0.08);
    --shadow-md:  0 8px 24px rgba(67,56,202,0.13);
    --shadow-lg:  0 20px 48px rgba(67,56,202,0.18);
    --shadow-glow:0 0 40px rgba(99,102,241,0.25);

    --radius-sm: 10px;
    --radius-md: 16px;
    --radius-lg: 24px;
    --radius-xl: 32px;

    --transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ── Base & font ─────────────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, sans-serif !important;
}

/* ── Ocultar chrome de Streamlit ────────────────────────────────────────── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ═══════════════════════════════════════════════════════════════════════════
   SIDEBAR PREMIUM
══════════════════════════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #0f0e1a 0%, #1a1730 50%, #0f1623 100%) !important;
    border-right: 1px solid rgba(99,102,241,0.2);
}

[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

[data-testid="stSidebar"] h1 {
    font-size: 1.1rem !important;
    font-weight: 800 !important;
    background: linear-gradient(90deg, #818cf8, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 0.5px;
}

[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown li {
    font-size: 0.85rem !important;
    opacity: 0.85;
    line-height: 1.7;
}

[data-testid="stSidebar"] hr {
    border-color: rgba(99,102,241,0.25) !important;
    margin: 0.75rem 0 !important;
}

[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #4338ca, #6366f1) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px !important;
    box-shadow: 0 4px 16px rgba(99,102,241,0.35) !important;
    transition: var(--transition) !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(99,102,241,0.5) !important;
}

[data-testid="stSidebar"] .stSelectbox,
[data-testid="stSidebar"] .stTextInput {
    background: rgba(255,255,255,0.06) !important;
    border-radius: var(--radius-sm) !important;
}

/* ═══════════════════════════════════════════════════════════════════════════
   HERO HEADER
══════════════════════════════════════════════════════════════════════════════ */
.hero {
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 30%, #4338ca 60%, #0891b2 100%);
    padding: 2.75rem 2.5rem;
    border-radius: var(--radius-xl);
    color: white;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
    box-shadow: var(--shadow-lg), 0 0 60px rgba(67,56,202,0.3);
}

/* Círculos de fondo decorativos */
.hero::before {
    content: '';
    position: absolute;
    top: -80px; right: -80px;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(129,140,248,0.18) 0%, transparent 70%);
    pointer-events: none;
}
.hero::after {
    content: '';
    position: absolute;
    bottom: -60px; left: -60px;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(8,145,178,0.15) 0%, transparent 70%);
    pointer-events: none;
}

/* Shimmer line animado */
@keyframes shimmer-line {
    0%   { transform: translateX(-100%); }
    100% { transform: translateX(400%); }
}
.hero-shimmer {
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.6), transparent);
    animation: shimmer-line 3s ease-in-out infinite;
}

.hero-content { position: relative; z-index: 1; }

.hero-eyebrow {
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
    margin-bottom: 1rem;
}
.hero-eyebrow-uni {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    opacity: 0.9;
    color: #c7d2fe;
}
.hero-eyebrow-course {
    font-size: 0.8rem;
    opacity: 0.75;
    font-weight: 500;
    color: #a5b4fc;
}

.hero-title {
    font-size: clamp(1.8rem, 4vw, 2.8rem);
    font-weight: 900;
    letter-spacing: -1.5px;
    line-height: 1.05;
    margin: 0 0 0.75rem 0;
    background: linear-gradient(90deg, #ffffff 0%, #c7d2fe 60%, #7dd3fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-subtitle {
    font-size: 0.95rem;
    line-height: 1.65;
    max-width: 640px;
    color: rgba(255,255,255,0.75);
    margin-bottom: 1.75rem;
}

/* ── Stat pills ─────────────────────────────────────────────────────────── */
.hero-stats { display: flex; gap: 0.75rem; flex-wrap: wrap; }

@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}

.stat-pill {
    background: rgba(255,255,255,0.1);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.2);
    padding: 0.65rem 1.2rem;
    border-radius: 14px;
    text-align: center;
    min-width: 90px;
    transition: var(--transition);
    animation: fadeSlideUp 0.6s ease-out both;
    cursor: default;
}
.stat-pill:nth-child(1){ animation-delay: 0.1s; }
.stat-pill:nth-child(2){ animation-delay: 0.2s; }
.stat-pill:nth-child(3){ animation-delay: 0.3s; }
.stat-pill:nth-child(4){ animation-delay: 0.4s; }

.stat-pill:hover {
    background: rgba(255,255,255,0.2);
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.2);
}
.stat-val {
    font-size: 1.45rem;
    font-weight: 800;
    color: #ffffff;
    line-height: 1;
}
.stat-lbl {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.65);
    margin-top: 0.25rem;
}

/* ═══════════════════════════════════════════════════════════════════════════
   TABS PREMIUM
══════════════════════════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surf-alt);
    padding: 6px;
    border-radius: 16px;
    gap: 4px;
    border: 1px solid var(--border);
}

.stTabs [data-baseweb="tab"] {
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    padding: 0.5rem 1.25rem !important;
    color: var(--txt-2) !important;
    transition: var(--transition) !important;
}

.stTabs [aria-selected="true"] {
    background: white !important;
    color: var(--p700) !important;
    box-shadow: var(--shadow-sm) !important;
    font-weight: 700 !important;
}

/* ═══════════════════════════════════════════════════════════════════════════
   BOTONES PRINCIPALES
══════════════════════════════════════════════════════════════════════════════ */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #4338ca 0%, #6366f1 100%) !important;
    color: white !important;
    border: none !important;
    padding: 0.7rem 2rem !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 16px rgba(67,56,202,0.35) !important;
    transition: var(--transition) !important;
}

.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 8px 28px rgba(67,56,202,0.5) !important;
}

.stButton > button:not([kind="primary"]) {
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: var(--transition) !important;
}

/* ═══════════════════════════════════════════════════════════════════════════
   FILE UPLOADER
══════════════════════════════════════════════════════════════════════════════ */
[data-testid="stFileUploader"] {
    background: linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%);
    border-radius: var(--radius-md);
    border: 2px dashed var(--p300);
    transition: var(--transition);
}

[data-testid="stFileUploader"]:hover {
    border-color: var(--p500);
    background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
    box-shadow: 0 4px 20px rgba(99,102,241,0.15);
}

/* ═══════════════════════════════════════════════════════════════════════════
   METRIC CARDS
══════════════════════════════════════════════════════════════════════════════ */
[data-testid="stMetric"] {
    background: white;
    border-radius: var(--radius-sm);
    padding: 1rem 1.25rem;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--border);
    border-top: 3px solid var(--p500);
    transition: var(--transition);
}

[data-testid="stMetric"]:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-1px);
}

[data-testid="stMetricLabel"] { color: var(--txt-2) !important; font-size: 0.8rem !important; }
[data-testid="stMetricValue"] { color: var(--txt-1) !important; font-weight: 700 !important; }

/* ═══════════════════════════════════════════════════════════════════════════
   SECCIÓN PREMIUM LABELS
══════════════════════════════════════════════════════════════════════════════ */
.section-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: var(--p100);
    color: var(--p700);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 0.35rem 0.85rem;
    border-radius: 20px;
    border: 1px solid var(--border-strong);
    margin-bottom: 0.75rem;
}

.section-title-premium {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--txt-1);
    margin: 0 0 0.25rem 0;
}

.section-subtitle-premium {
    font-size: 0.8rem;
    color: var(--txt-3);
    margin: 0 0 1rem 0;
}

/* ═══════════════════════════════════════════════════════════════════════════
   DATA BADGES — corazón del rediseño
══════════════════════════════════════════════════════════════════════════════ */
.badges-wrap {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin: 0.4rem 0 1rem 0;
}

.data-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.4rem 0.85rem;
    border-radius: 10px;
    font-size: 0.82rem;
    font-weight: 600;
    font-family: 'Inter', monospace;
    transition: var(--transition);
    cursor: default;
    border: 1.5px solid transparent;
    max-width: 100%;
    word-break: break-all;
}

.data-badge:hover {
    transform: translateY(-2px);
    filter: brightness(1.08);
    box-shadow: 0 4px 14px rgba(0,0,0,0.12);
}

/* ── Colores por tipo de campo ──────────────────────────────────────────── */
.db-email  { background:#e0f2fe; border-color:#7dd3fc; color:#0369a1; }
.db-phone  { background:#d1fae5; border-color:#6ee7b7; color:#065f46; }
.db-url    { background:#ede9fe; border-color:#c4b5fd; color:#5b21b6; }
.db-date   { background:#fef3c7; border-color:#fcd34d; color:#92400e; }
.db-currency{ background:#dcfce7; border-color:#86efac; color:#14532d; }
.db-nit    { background:#e0e7ff; border-color:#a5b4fc; color:#3730a3; }
.db-dpi    { background:#ccfbf1; border-color:#5eead4; color:#134e4a; }
.db-serie  { background:#f3e8ff; border-color:#d8b4fe; color:#6b21a8; }
.db-uuid   { background:#dbeafe; border-color:#93c5fd; color:#1e3a8a; }
.db-dte    { background:#fae8ff; border-color:#e879f9; color:#701a75; }
.db-moneda { background:#fff7ed; border-color:#fdba74; color:#9a3412; }
.db-pago   { background:#f0fdf4; border-color:#86efac; color:#166534; }
.db-auth   { background:#eff6ff; border-color:#bfdbfe; color:#1d4ed8; }

/* ── Empty state ────────────────────────────────────────────────────────── */
.empty-state {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.55rem 0.9rem;
    background: #f9fafb;
    border: 1px dashed #d1d5db;
    border-radius: 8px;
    margin: 0.4rem 0 1rem 0;
    color: #9ca3af;
    font-size: 0.8rem;
    font-style: italic;
}

/* ── Field label ────────────────────────────────────────────────────────── */
.field-lbl {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: var(--txt-2);
    margin: 0.85rem 0 0.35rem 0;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

/* ═══════════════════════════════════════════════════════════════════════════
   EXPANDERS / STEPS
══════════════════════════════════════════════════════════════════════════════ */
.step-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem 1.25rem;
    background: linear-gradient(135deg, var(--surf-alt), white);
    border-radius: var(--radius-md);
    border: 1px solid var(--border);
    margin-bottom: 0.5rem;
    box-shadow: var(--shadow-sm);
}

.step-number {
    width: 32px; height: 32px;
    background: linear-gradient(135deg, var(--p700), var(--p500));
    color: white;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 0.85rem;
    box-shadow: 0 2px 8px rgba(67,56,202,0.3);
    flex-shrink: 0;
}

.step-info { flex: 1; }
.step-title { font-weight: 700; color: var(--txt-1); font-size: 0.95rem; }
.step-desc  { font-size: 0.78rem; color: var(--txt-3); margin-top: 0.1rem; }

.step-status-ok  { color: #059669; font-weight: 700; font-size: 0.8rem; }
.step-status-err { color: #dc2626; font-weight: 700; font-size: 0.8rem; }

/* ═══════════════════════════════════════════════════════════════════════════
   CONFIDENCE METER
══════════════════════════════════════════════════════════════════════════════ */
.conf-meter-wrap {
    background: white;
    border-radius: var(--radius-md);
    border: 1px solid var(--border);
    padding: 1.25rem;
    box-shadow: var(--shadow-sm);
}
.conf-label {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--txt-2);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.5rem;
}
.conf-value {
    font-size: 2.25rem;
    font-weight: 900;
    line-height: 1;
    margin-bottom: 0.6rem;
}
.conf-bar-bg {
    height: 8px;
    background: #f3f4f6;
    border-radius: 99px;
    overflow: hidden;
}
.conf-bar-fill {
    height: 100%;
    border-radius: 99px;
    transition: width 0.8s cubic-bezier(0.4,0,0.2,1);
}

/* ═══════════════════════════════════════════════════════════════════════════
   BADGE DE CLASIFICACIÓN (grande)
══════════════════════════════════════════════════════════════════════════════ */
.class-badge-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.75rem;
    padding: 1.5rem;
    background: var(--surf-alt);
    border-radius: var(--radius-md);
    border: 1px solid var(--border);
    min-height: 120px;
}

.class-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.65rem 1.75rem;
    border-radius: 40px;
    font-weight: 800;
    font-size: 1.05rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: white;
    box-shadow: 0 6px 20px rgba(0,0,0,0.2);
    animation: fadeSlideUp 0.4s ease-out;
}

.badge-factura       { background: linear-gradient(135deg,#059669,#10b981); }
.badge-recibo        { background: linear-gradient(135deg,#d97706,#f59e0b); }
.badge-contrato      { background: linear-gradient(135deg,#7c3aed,#8b5cf6); }
.badge-constancia    { background: linear-gradient(135deg,#0891b2,#06b6d4); }
.badge-carta_formal  { background: linear-gradient(135deg,#db2777,#ec4899); }
.badge-identificacion{ background: linear-gradient(135deg,#4f46e5,#6366f1); }
.badge-otro          { background: linear-gradient(135deg,#4b5563,#6b7280); }

.class-conf-text {
    font-size: 0.85rem;
    color: var(--txt-2);
    font-weight: 500;
}

/* ── Probability bars ───────────────────────────────────────────────────── */
.prob-row {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 0.65rem;
}
.prob-label {
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--txt-2);
    width: 110px;
    flex-shrink: 0;
}
.prob-bar-bg {
    flex: 1;
    height: 10px;
    background: #f3f4f6;
    border-radius: 99px;
    overflow: hidden;
}
.prob-bar-fill {
    height: 100%;
    border-radius: 99px;
    transition: width 0.7s cubic-bezier(0.4,0,0.2,1);
}
.prob-pct {
    font-size: 0.8rem;
    font-weight: 700;
    width: 42px;
    text-align: right;
    flex-shrink: 0;
}

/* ═══════════════════════════════════════════════════════════════════════════
   CARDS GENERALES (info, success, warning)
══════════════════════════════════════════════════════════════════════════════ */
.nx-card {
    padding: 1.1rem 1.4rem;
    border-radius: var(--radius-md);
    margin: 0.75rem 0;
    border: 1px solid;
    transition: var(--transition);
}
.nx-card:hover { box-shadow: var(--shadow-md); }

.nx-info    { background:#eff6ff; border-color:#bfdbfe; color:#1e40af; }
.nx-success { background:#f0fdf4; border-color:#86efac; color:#166534; }
.nx-warn    { background:#fffbeb; border-color:#fde68a; color:#92400e; }
.nx-danger  { background:#fff1f2; border-color:#fecdd3; color:#9f1239; }

/* ── Info-card (compatible con código anterior) ─────────────────────────── */
.info-card { background:#eff6ff; border-left:4px solid #60a5fa; padding:1rem 1.4rem;
             border-radius:var(--radius-sm); margin:0.75rem 0; color:#1e3a8a; }
.success-card { background:#f0fdf4; border-left:4px solid #34d399; padding:1rem 1.4rem;
                border-radius:var(--radius-sm); margin:0.75rem 0; color:#065f46; }

/* ═══════════════════════════════════════════════════════════════════════════
   FOOTER
══════════════════════════════════════════════════════════════════════════════ */
.nx-footer {
    background: linear-gradient(135deg, #0f0e1a 0%, #1a1730 100%);
    color: white;
    text-align: center;
    padding: 2.25rem 2rem;
    border-radius: var(--radius-xl);
    margin-top: 3rem;
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(99,102,241,0.2);
}
.nx-footer::before {
    content:'';
    position:absolute; inset:0;
    background: radial-gradient(ellipse at 50% 0%, rgba(99,102,241,0.15) 0%, transparent 70%);
}
.nx-footer * { position: relative; z-index: 1; }
.nx-footer-title {
    font-size:1.15rem; font-weight:800; letter-spacing:0.5px;
    background: linear-gradient(90deg,#818cf8,#c084fc);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
    margin-bottom:0.5rem;
}
.nx-footer-info  { opacity:0.7; font-size:0.85rem; line-height:1.7; }
.nx-footer-stack {
    opacity:0.5; font-size:0.75rem; margin-top:1rem;
    padding-top:1rem; border-top:1px solid rgba(255,255,255,0.1);
}

/* ═══════════════════════════════════════════════════════════════════════════
   ANIMACIONES
══════════════════════════════════════════════════════════════════════════════ */
@keyframes pulse-ring {
    0%   { box-shadow: 0 0 0 0 rgba(99,102,241,0.4); }
    70%  { box-shadow: 0 0 0 10px rgba(99,102,241,0); }
    100% { box-shadow: 0 0 0 0 rgba(99,102,241,0); }
}

.animate-pulse-once { animation: pulse-ring 1.5s ease-out 1; }

/* ── Responsive base ─────────────────────────────────────────────────────── */
@media (max-width: 768px) {
    .hero { padding: 1.75rem 1.25rem; }
    .hero-title { font-size: 1.6rem; }
    .hero-stats { gap: 0.5rem; }
    .stat-pill { min-width: 70px; padding: 0.5rem 0.75rem; }
    .stat-val { font-size: 1.2rem; }
}

/* ══════════════════════════════════════════════════════════════════════════════
   DARK PREMIUM UPGRADE — expoferia edition
   Overrides CSS: reglas posteriores ganan sin tocar las anteriores.
══════════════════════════════════════════════════════════════════════════════ */

/* ── Nuevas keyframes ────────────────────────────────────────────────────── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(22px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes glowPulse {
    0%,100% { box-shadow: 0 4px 16px rgba(67,56,202,0.35); }
    50%      { box-shadow: 0 4px 36px rgba(99,102,241,0.75),
                           0 0  60px rgba(99,102,241,0.22); }
}
@keyframes neonBorder {
    0%,100% { border-color: rgba(99,102,241,0.25); }
    50%      { border-color: rgba(99,102,241,0.55); }
}
@keyframes slideInRight {
    from { opacity: 0; transform: translateX(16px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes scaleIn {
    from { opacity: 0; transform: scale(0.94); }
    to   { opacity: 1; transform: scale(1); }
}

/* ── Fondo principal oscuro ──────────────────────────────────────────────── */
.stApp {
    background:
        radial-gradient(ellipse at 20% 0%,   rgba(99,102,241,0.07) 0%, transparent 55%),
        radial-gradient(ellipse at 80% 100%,  rgba(14,165,233,0.06) 0%, transparent 55%),
        linear-gradient(160deg, #09081f 0%, #0d0b28 50%, #090f1c 100%) !important;
    background-attachment: fixed !important;
}
.main .block-container {
    max-width: 1240px !important;
    padding-top: 1.25rem !important;
}

/* Scrollbar personalizado */
::-webkit-scrollbar              { width: 5px; height: 5px; }
::-webkit-scrollbar-track        { background: rgba(255,255,255,0.02); }
::-webkit-scrollbar-thumb        { background: rgba(99,102,241,0.3); border-radius: 99px; }
::-webkit-scrollbar-thumb:hover  { background: rgba(99,102,241,0.5); }

/* ── Texto base ──────────────────────────────────────────────────────────── */
h1, h2, h3, h4, h5 { color: #f1f5f9 !important; }
p  { color: #cbd5e1; }
label { color: #94a3b8 !important; }
[data-testid="stMarkdownContainer"] p { color: #cbd5e1; }
[data-testid="stCaptionContainer"]    { color: #64748b !important; }
hr { border-color: rgba(99,102,241,0.14) !important; }

/* ── Streamlit widgets — dark override ───────────────────────────────────── */

/* Text area */
.stTextArea textarea {
    background: rgba(13,11,38,0.92) !important;
    color: #e2e8f0 !important;
    border: 1px solid rgba(99,102,241,0.22) !important;
    border-radius: var(--radius-sm) !important;
    caret-color: #818cf8;
}
.stTextArea textarea:focus {
    border-color: rgba(99,102,241,0.5) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.1) !important;
}

/* Selectbox */
[data-testid="stSelectbox"] > div > div,
[data-testid="stSelectbox"] [data-baseweb="select"] {
    background: rgba(13,11,38,0.88) !important;
    border: 1px solid rgba(99,102,241,0.22) !important;
    border-radius: var(--radius-sm) !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] div { color: #e2e8f0 !important; }

/* Expander */
[data-testid="stExpander"] {
    background: rgba(13,11,38,0.55) !important;
    border: 1px solid rgba(99,102,241,0.18) !important;
    border-radius: var(--radius-md) !important;
    backdrop-filter: blur(10px) !important;
    margin-bottom: 1rem !important;
    animation: fadeInUp 0.4s ease-out !important;
}
[data-testid="stExpander"] summary {
    color: #e2e8f0 !important;
    font-weight: 600 !important;
}
[data-testid="stExpander"] summary:hover { color: #a5b4fc !important; }
[data-testid="stExpander"] details > div { animation: fadeInUp 0.3s ease-out; }

/* Metric cards */
[data-testid="stMetric"] {
    background: rgba(13,11,38,0.6) !important;
    border: 1px solid rgba(99,102,241,0.2) !important;
    border-top: 3px solid var(--p500) !important;
    border-radius: var(--radius-sm) !important;
    backdrop-filter: blur(8px) !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.35) !important;
}
[data-testid="stMetric"]:hover {
    border-color: rgba(99,102,241,0.4) !important;
    box-shadow: 0 4px 24px rgba(99,102,241,0.18) !important;
    transform: translateY(-2px) !important;
}
[data-testid="stMetricLabel"] { color: #94a3b8 !important; }
[data-testid="stMetricValue"] { color: #f1f5f9 !important; }
[data-testid="stMetricDelta"]  { color: #64748b !important; }

/* Radio buttons */
.stRadio [data-testid="stWidgetLabel"],
.stRadio label { color: #cbd5e1 !important; }
.stRadio > div[role="radiogroup"] {
    background: rgba(13,11,38,0.55);
    border-radius: var(--radius-sm);
    padding: 0.3rem;
    border: 1px solid rgba(99,102,241,0.18);
    gap: 0.25rem;
}

/* Checkbox */
.stCheckbox label > span:last-child { color: #cbd5e1 !important; }

/* DataFrame */
[data-testid="stDataFrame"] {
    border-radius: var(--radius-sm) !important;
    border: 1px solid rgba(99,102,241,0.18) !important;
    overflow: hidden !important;
    animation: scaleIn 0.35s ease-out !important;
}

/* ── Tabs premium dark ───────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(13,11,38,0.7) !important;
    border: 1px solid rgba(99,102,241,0.2) !important;
    backdrop-filter: blur(8px) !important;
}
.stTabs [data-baseweb="tab"] { color: #64748b !important; }
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(67,56,202,0.35), rgba(99,102,241,0.2)) !important;
    color: #a5b4fc !important;
    box-shadow: 0 0 14px rgba(99,102,241,0.22) !important;
    border: 1px solid rgba(99,102,241,0.32) !important;
}
.stTabs [data-baseweb="tab-panel"] { animation: fadeInUp 0.35s ease-out; }

/* ── NX Cards — versión dark ─────────────────────────────────────────────── */
.nx-card { backdrop-filter: blur(8px) !important; }
.nx-info  {
    background: rgba(29,78,216,0.13) !important;
    border-color: rgba(96,165,250,0.35) !important;
    color: #93c5fd !important;
}
.nx-success {
    background: rgba(5,150,105,0.13) !important;
    border-color: rgba(52,211,153,0.35) !important;
    color: #6ee7b7 !important;
}
.nx-warn {
    background: rgba(217,119,6,0.13) !important;
    border-color: rgba(251,191,36,0.35) !important;
    color: #fcd34d !important;
}
.nx-danger {
    background: rgba(225,29,72,0.13) !important;
    border-color: rgba(252,165,165,0.35) !important;
    color: #fca5a5 !important;
}
.nx-card:hover { box-shadow: 0 8px 28px rgba(0,0,0,0.4) !important; }

/* ── Section chip dark glow ──────────────────────────────────────────────── */
.section-chip {
    background: rgba(99,102,241,0.12) !important;
    color: #a5b4fc !important;
    border-color: rgba(99,102,241,0.32) !important;
    box-shadow: 0 0 14px rgba(99,102,241,0.1);
    animation: slideInRight 0.3s ease-out;
}

/* ── Textos de helpers ───────────────────────────────────────────────────── */
.section-title-premium    { color: #f1f5f9 !important; }
.section-subtitle-premium { color: #64748b !important; }
.field-lbl    { color: #94a3b8 !important; }
.step-title   { color: #f1f5f9 !important; }
.step-desc    { color: #64748b !important; }
.prob-label   { color: #94a3b8 !important; }

/* ── Cards auxiliares dark ───────────────────────────────────────────────── */
.step-header {
    background: rgba(13,11,38,0.55) !important;
    border-color: rgba(99,102,241,0.2) !important;
    backdrop-filter: blur(8px) !important;
}
.conf-meter-wrap {
    background: rgba(13,11,38,0.6) !important;
    border-color: rgba(99,102,241,0.2) !important;
    backdrop-filter: blur(8px) !important;
}
.conf-label  { color: #94a3b8 !important; }
.conf-bar-bg { background: rgba(255,255,255,0.06) !important; }

.class-badge-wrap {
    background: rgba(13,11,38,0.6) !important;
    border-color: rgba(99,102,241,0.2) !important;
    backdrop-filter: blur(8px) !important;
}
.class-conf-text { color: #94a3b8 !important; }

.prob-bar-bg { background: rgba(255,255,255,0.06) !important; }

.empty-state {
    background: rgba(255,255,255,0.03) !important;
    border-color: rgba(255,255,255,0.08) !important;
    color: #475569 !important;
}
.info-card    { background: rgba(29,78,216,0.1) !important; color: #93c5fd !important; }
.success-card { background: rgba(5,150,105,0.1) !important; color: #6ee7b7 !important; }

/* ── Glass card class (nueva utilidad) ───────────────────────────────────── */
.glass-card {
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: var(--radius-md);
    padding: 1.25rem 1.5rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.32);
    transition: var(--transition);
}
.glass-card:hover {
    background: rgba(255,255,255,0.06);
    border-color: rgba(99,102,241,0.3);
    box-shadow: 0 8px 32px rgba(0,0,0,0.42), 0 0 20px rgba(99,102,241,0.09);
    transform: translateY(-2px);
}

/* ── PROCESAR — glow pulse ───────────────────────────────────────────────── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #3730a3 0%, #4f46e5 50%, #6366f1 100%) !important;
    border: 1px solid rgba(99,102,241,0.5) !important;
    font-size: 1rem !important;
    letter-spacing: 2px !important;
    padding: 0.8rem 2.5rem !important;
    cursor: pointer !important;
    animation: glowPulse 3s ease-in-out infinite !important;
}
.stButton > button[kind="primary"]:hover {
    animation: none !important;
    background: linear-gradient(135deg, #4f46e5 0%, #6366f1 50%, #818cf8 100%) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.28),
                0 8px 32px rgba(99,102,241,0.52) !important;
    transform: translateY(-3px) scale(1.035) !important;
}

/* ── Descargar JSON — teal themed ────────────────────────────────────────── */
[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #0f766e, #0d9488) !important;
    color: #f0fdfa !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px !important;
    box-shadow: 0 4px 16px rgba(13,148,136,0.38) !important;
    transition: var(--transition) !important;
    cursor: pointer !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: linear-gradient(135deg, #0d9488, #14b8a6) !important;
    box-shadow: 0 8px 28px rgba(13,148,136,0.55) !important;
    transform: translateY(-2px) !important;
}

/* ── Botones secundarios dark ────────────────────────────────────────────── */
.stButton > button:not([kind="primary"]) {
    background: rgba(13,11,38,0.65) !important;
    color: #a5b4fc !important;
    border: 1px solid rgba(99,102,241,0.28) !important;
    cursor: pointer !important;
}
.stButton > button:not([kind="primary"]):hover {
    background: rgba(67,56,202,0.22) !important;
    border-color: rgba(99,102,241,0.5) !important;
    color: #c7d2fe !important;
    transform: translateY(-1px) !important;
}

/* ── File uploader dark + neon border ────────────────────────────────────── */
[data-testid="stFileUploader"] {
    background: rgba(13,11,38,0.55) !important;
    border: 2px dashed rgba(99,102,241,0.35) !important;
    border-radius: var(--radius-md) !important;
    backdrop-filter: blur(8px) !important;
    animation: neonBorder 4s ease-in-out infinite !important;
}
[data-testid="stFileUploader"]:hover {
    animation: none !important;
    background: rgba(67,56,202,0.09) !important;
    border-color: rgba(99,102,241,0.65) !important;
    box-shadow: 0 0 20px rgba(99,102,241,0.15) !important;
}
[data-testid="stFileUploader"] section * { color: #a5b4fc !important; }
[data-testid="stFileUploader"] button { color: #a5b4fc !important; }

/* ── Sidebar widgets dark overrides ──────────────────────────────────────── */
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.08) !important;
    border-color: rgba(99,102,241,0.25) !important;
    color: #e2e8f0 !important;
}
[data-testid="stSidebar"] .stCheckbox label > span:last-child {
    color: #cbd5e1 !important;
}
[data-testid="stSidebar"] .stTextInput input {
    background: rgba(255,255,255,0.06) !important;
    color: #e2e8f0 !important;
    border-color: rgba(99,102,241,0.25) !important;
    border-radius: var(--radius-sm) !important;
}

/* ── Animación de entrada para paneles y expanders ───────────────────────── */
.stTabs [data-baseweb="tab-panel"] > div { animation: fadeInUp 0.38s ease-out; }
[data-testid="stExpander"] > details > div > div { animation: fadeInUp 0.3s ease-out; }
[data-testid="stMetric"]     { animation: scaleIn 0.3s ease-out; }

/* ── Responsive dark ─────────────────────────────────────────────────────── */
@media (max-width: 1024px) {
    .main .block-container { padding: 1.25rem !important; }
}
@media (max-width: 768px) {
    .glass-card { padding: 1rem; }
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS VISUALES
# ══════════════════════════════════════════════════════════════════════════════

def _field_label(icon: str, title: str) -> None:
    """Renderiza una etiqueta de campo con icono."""
    st.markdown(
        f'<div class="field-lbl"><span>{icon}</span><span>{_html.escape(title)}</span></div>',
        unsafe_allow_html=True,
    )


def _badges(items: list, css_cls: str, icon: str = "") -> None:
    """Renderiza una lista de items como badges premium o un estado vacío elegante."""
    if items:
        inner = "".join(
            f'<span class="data-badge {css_cls}">'
            f'{("<span>" + icon + "</span>") if icon else ""}'
            f'<span>{_html.escape(str(v))}</span>'
            f'</span>'
            for v in items
        )
        st.markdown(f'<div class="badges-wrap">{inner}</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="empty-state">'
            '<span>○</span><span>Sin datos detectados</span>'
            '</div>',
            unsafe_allow_html=True,
        )


def _conf_meter(value, label: str = "Confianza OCR") -> None:
    """Renderiza un medidor de confianza con barra animada.

    value=None  → PDF con texto nativo (no aplica OCR)
    value<0     → Sin texto detectado
    value 0-100 → Porcentaje de confianza Tesseract
    """
    if value is None:
        st.markdown(f"""
    <div class="conf-meter-wrap">
        <div class="conf-label">{_html.escape(label)}</div>
        <div class="conf-value" style="color:#6366f1;">Texto digital</div>
        <div style="font-size:0.75rem;color:#9ca3af;margin-top:0.35rem;">
            Extraído directamente del PDF · sin OCR
        </div>
        <div class="conf-bar-bg" style="margin-top:0.55rem;">
            <div class="conf-bar-fill"
                 style="width:100%;background:linear-gradient(90deg,#818cf888,#6366f1);"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
        return

    if value < 0:
        color, text = "#9ca3af", "— Sin texto"
        pct = 0
    elif value >= 80:
        color, text = "#059669", f"{value:.0f}%"
        pct = value
    elif value >= 60:
        color, text = "#d97706", f"{value:.0f}%"
        pct = value
    else:
        color, text = "#dc2626", f"{value:.0f}%"
        pct = value

    st.markdown(f"""
    <div class="conf-meter-wrap">
        <div class="conf-label">{_html.escape(label)}</div>
        <div class="conf-value" style="color:{color};">{text}</div>
        <div class="conf-bar-bg">
            <div class="conf-bar-fill"
                 style="width:{pct}%; background:linear-gradient(90deg,{color}88,{color});"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _show_field(extraction: dict, key: str, icon: str, label: str,
                css_cls: str, badge_icon: str) -> bool:
    """Renderiza etiqueta + badges solo si hay datos. Devuelve True si renderizó."""
    items = extraction.get(key, [])
    if items:
        _field_label(icon, label)
        _badges(items, css_cls, badge_icon)
        return True
    return False


# Categorías en orden canónico para mapear índices numéricos → nombres
_CATEGORIES = ['factura', 'recibo', 'contrato', 'constancia',
               'carta_formal', 'identificacion', 'otro']

_CAT_DISPLAY = {
    'factura':        'Factura',
    'recibo':         'Recibo',
    'contrato':       'Contrato',
    'constancia':     'Constancia',
    'carta_formal':   'Carta Formal',
    'identificacion': 'Identificación',
    'otro':           'Otro',
}


def _resolve_cls_label(cls: str) -> str:
    """Traduce índice numérico (ej. '4') a nombre de categoría ('carta_formal')."""
    try:
        idx = int(cls)
        if 0 <= idx < len(_CATEGORIES):
            return _CATEGORIES[idx]
    except (ValueError, TypeError):
        pass
    return cls


_LANG_MAP = {
    "spa":     "🇪🇸 Español",
    "eng":     "🇬🇧 Inglés",
    "spa+eng": "🇬🇹 Español + Inglés",
    "fra":     "🇫🇷 Francés",
    "deu":     "🇩🇪 Alemán",
}

_COLOR_MAP = {
    'factura':        '#10b981',
    'recibo':         '#f59e0b',
    'contrato':       '#8b5cf6',
    'constancia':     '#06b6d4',
    'carta_formal':   '#ec4899',
    'identificacion': '#6366f1',
    'otro':           '#6b7280',
}

_BADGE_MAP = {
    "factura":        ("badge-factura",        "📄"),
    "recibo":         ("badge-recibo",         "🧾"),
    "contrato":       ("badge-contrato",       "📋"),
    "constancia":     ("badge-constancia",     "📜"),
    "carta_formal":   ("badge-carta_formal",   "✉️"),
    "identificacion": ("badge-identificacion", "🆔"),
    "otro":           ("badge-otro",           "📁"),
}


# ══════════════════════════════════════════════════════════════════════════════
#  ESTADO DE SESIÓN
# ══════════════════════════════════════════════════════════════════════════════
if "pipeline" not in st.session_state:
    st.session_state.pipeline = None
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "last_filename" not in st.session_state:
    st.session_state.last_filename = None
# Tracks which file was last processed to detect new uploads and avoid stale results
if "processed_file_id" not in st.session_state:
    st.session_state.processed_file_id = None
# Named result vars — completely independent from widget keys to prevent re-processing
if "resultado_actual" not in st.session_state:
    st.session_state.resultado_actual = None
if "pages_actuales" not in st.session_state:
    st.session_state.pages_actuales = []
# Page selector stored independently; 1-indexed page number
if "selected_page_idx" not in st.session_state:
    st.session_state.selected_page_idx = 1
if "upload_key_counter" not in st.session_state:
    st.session_state.upload_key_counter = 0
if "upload_error" not in st.session_state:
    st.session_state.upload_error = None


def load_pipeline(tesseract_path=None):
    """Crea una instancia del pipeline por sesión (no compartida entre usuarios)."""
    return OCRPipeline(tesseract_path=tesseract_path)


# ── AUTO-INICIALIZACIÓN ──────────────────────────────────────────────────────
if st.session_state.pipeline is None:
    try:
        from config import TESSERACT_PATH as _TESS_PATH
        if _TESS_PATH:
            st.session_state.pipeline = load_pipeline(tesseract_path=_TESS_PATH)
    except (ImportError, OSError, RuntimeError):
        pass


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR PREMIUM
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.title("⚙️ Configuración")

    st.markdown("---")
    st.markdown("""
<div style="font-size:0.7rem;font-weight:700;letter-spacing:1.5px;
            text-transform:uppercase;color:#818cf8;margin-bottom:0.6rem;">
    Stack Tecnológico
</div>
""", unsafe_allow_html=True)
    st.markdown("""
- **Pytesseract** · OCR óptico
- **Scikit-learn** · Clasificación ML
- **OpenCV** · Preprocesado
- **Streamlit** · Interfaz
""")

    st.markdown("---")
    st.markdown("""
<div style="font-size:0.7rem;font-weight:700;letter-spacing:1.5px;
            text-transform:uppercase;color:#818cf8;margin-bottom:0.6rem;">
    Capacidades
</div>
""", unsafe_allow_html=True)
    st.markdown("""
✅ OCR multi-idioma (spa+eng)
✅ Extracción FEL guatemalteca
✅ Clasificación · 7 categorías
✅ Autorización SAT / UUID
✅ Exportación JSON
""")

    st.markdown("---")
    st.subheader("Tesseract OCR")
    tesseract_installed = st.checkbox(
        "Tesseract instalado",
        value=False,
        help="Marca si ya instalaste Tesseract-OCR en Windows",
    )

    tesseract_path = None
    if tesseract_installed:
        tesseract_path = st.text_input(
            "Ruta del ejecutable",
            value=r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            help="Ruta por defecto en Windows",
        )

    if st.button("🚀 Inicializar Pipeline", use_container_width=True):
        try:
            pipeline = load_pipeline(tesseract_path=tesseract_path)
            st.session_state.pipeline = pipeline
            st.success("✅ Pipeline listo")
        except (ValueError, TypeError, FileNotFoundError, OSError) as e:
            st.error(f"❌ Error: {e}")

    st.divider()
    st.subheader("Idioma OCR")
    ocr_language = st.selectbox(
        "Selecciona idioma",
        options=["spa", "eng", "fra", "deu"],
        format_func=lambda x: {
            "spa": "🇪🇸 Español",
            "eng": "🇬🇧 Inglés",
            "fra": "🇫🇷 Francés",
            "deu": "🇩🇪 Alemán",
        }[x],
        key="ocr_language",
    )

    st.divider()
    st.markdown("""
<div style="text-align:center;padding:0.5rem 0;">
    <div style="font-size:0.75rem;opacity:0.6;">OCR IA Project</div>
    <div style="font-size:0.7rem;color:#818cf8;font-weight:700;margin-top:0.25rem;">v1.0.0</div>
    <div style="font-size:0.7rem;opacity:0.5;margin-top:0.25rem;">
        Confianza modelo <strong style="color:#10b981;">99.4%</strong>
    </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div style="
    background:rgba(234,179,8,0.07);
    border:1px solid rgba(234,179,8,0.28);
    border-left:3px solid #f59e0b;
    border-radius:8px;
    padding:0.65rem 0.8rem;
    margin-top:0.5rem;
    font-size:0.69rem;
    color:#fde68a;
    line-height:1.55;
">
<div style="font-weight:700;margin-bottom:0.3rem;letter-spacing:0.3px;">
    ⚠️ Aviso Ético
</div>
Usar únicamente documentos <strong>ficticios, propios o anonimizados</strong>.
Los resultados de OCR e IA deben ser <strong>verificados por un humano</strong>
antes de tomar decisiones. No procesar datos sensibles sin autorización.
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  HERO HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
    <div class="hero-shimmer"></div>
    <div class="hero-content">
        <div class="hero-eyebrow">
            <span class="hero-eyebrow-uni">UNIVERSIDAD MARIANO GÁLVEZ DE GUATEMALA</span>
            <span class="hero-eyebrow-course">Curso 045 · Inteligencia Artificial · Proyecto 04</span>
        </div>
        <h1 class="hero-title">Sistema Inteligente<br>OCR + IA</h1>
        <p class="hero-subtitle">
            Clasificación automática y extracción de datos en documentos guatemaltecos
            mediante Reconocimiento Óptico de Caracteres y Machine Learning.
            Compatible con facturas FEL / SAT.
        </p>
        <div class="hero-stats">
            <div class="stat-pill">
                <div class="stat-val">7</div>
                <div class="stat-lbl">Categorías</div>
            </div>
            <div class="stat-pill">
                <div class="stat-val">99.4%</div>
                <div class="stat-lbl">F1-Macro</div>
            </div>
            <div class="stat-pill">
                <div class="stat-val">490</div>
                <div class="stat-lbl">Documentos</div>
            </div>
            <div class="stat-pill">
                <div class="stat-val">158</div>
                <div class="stat-lbl">Tests ✅</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PANTALLA SIN PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.pipeline is None:
    st.markdown("""
<div class="nx-card nx-warn">
    <strong>⚠️ Pipeline no inicializado</strong><br/>
    <span style="font-size:0.88rem;">
        Marca "Tesseract instalado" en la barra lateral y presiona
        <strong>Inicializar Pipeline</strong>.
    </span>
</div>
""", unsafe_allow_html=True)

    with st.expander("📋 Instrucciones de instalación de Tesseract", expanded=False):
        st.markdown("""
### Instalación de Tesseract-OCR en Windows

1. **Descargar**
   Visita [github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
   Descarga el instalador `.exe` más reciente.

2. **Instalar**
   Ejecuta el instalador → selecciona la carpeta por defecto → instala los idiomas (español, inglés).

3. **Verificar**
```
tesseract --version
```

4. **Configurar**
   La ruta por defecto es `C:\\Program Files\\Tesseract-OCR\\tesseract.exe`.
        """)

else:
    # ── TABS ────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "📤  Procesar Archivo",
        "📊  Resultados",
        "📖  Guía de Uso",
        "ℹ️  Información",
    ])

    # ════════════════════════════════════════════════════════════════════════
    #  TAB 1 — PROCESAR ARCHIVO
    # ════════════════════════════════════════════════════════════════════════
    with tab1:
        st.markdown("""
<div class="section-chip">📤 Carga de documento</div>
<p class="section-title-premium">Procesar Archivo</p>
<p class="section-subtitle-premium">
    Sube una imagen (JPG, PNG, BMP) o un PDF y obtén texto, datos extraídos y clasificación en segundos.
</p>
""", unsafe_allow_html=True)

        col1, col2 = st.columns([2, 1])

        with col1:
            uploaded_files = st.file_uploader(
                "Arrastra o selecciona tu archivo",
                type=["pdf", "jpg", "jpeg", "png", "bmp"],
                accept_multiple_files=True,
                key=f"file_uploader_{st.session_state.upload_key_counter}",
                help="Sube un único archivo: PDF, JPG, PNG o BMP. No se permiten carpetas.",
            )

        with col2:
            st.markdown('<div class="field-lbl">⚙️ Idioma OCR</div>', unsafe_allow_html=True)
            ocr_lang = st.selectbox(
                "Idioma",
                options=["spa", "eng", "fra", "deu"],
                format_func=lambda x: {
                    "spa": "🇪🇸 Español",
                    "eng": "🇬🇧 Inglés",
                    "fra": "🇫🇷 Francés",
                    "deu": "🇩🇪 Alemán",
                }[x],
                key="tab1_ocr_language",
                index=0,
                label_visibility="collapsed",
            )

        # ── Normalizar: lista → archivo único validado ──────────────────────
        uploaded_file = None
        file_valid = False

        if not uploaded_files:
            pass
        elif len(uploaded_files) > 1:
            st.session_state.upload_error = (
                "No se permiten carpetas ni múltiples archivos. "
                "Sube únicamente un archivo PDF o una imagen individual."
            )
            st.session_state.upload_key_counter += 1
            st.session_state.resultado_actual = None
            st.session_state.pages_actuales = []
            st.session_state.processed_file_id = None
            st.session_state.selected_page_idx = 1
            st.rerun()
        else:
            _candidate = uploaded_files[0]
            _ext = _candidate.name.rsplit(".", 1)[-1].lower() if "." in _candidate.name else ""
            _mime = (_candidate.type or "").lower()
            _allowed_ext = {"jpg", "jpeg", "png", "pdf", "bmp"}
            _allowed_mime = {
                "image/jpeg", "image/png", "application/pdf",
                "image/bmp", "image/x-bmp", "image/x-ms-bmp",
            }
            if _ext in _allowed_ext and (_mime in _allowed_mime or not _mime):
                uploaded_file = _candidate
                file_valid = True
                st.session_state.upload_error = None
            else:
                st.session_state.upload_error = (
                    "⛔ Formato no permitido. "
                    "Sube únicamente PDF o imágenes JPG, PNG o BMP."
                )
                st.session_state.upload_key_counter += 1
                st.rerun()

        # ── Mostrar error (múltiples archivos o formato no válido) ──────────
        if st.session_state.upload_error:
            st.error(st.session_state.upload_error)
            st.markdown("""
<div class="nx-card nx-danger">
    <strong>⛔ Formatos no permitidos:</strong> carpetas, archivos múltiples, ZIP, DOC, DOCX, XLS, etc.<br/>
    <strong>✅ Formatos permitidos:</strong> PDF, JPG, JPEG, PNG, BMP (un archivo a la vez).
</div>
""", unsafe_allow_html=True)

        # ── Info del archivo cargado ────────────────────────────────────────
        if file_valid and uploaded_file is not None:
            col1, col2, col3 = st.columns(3)
            with col1:
                _nm = uploaded_file.name
                st.metric(
                    "📄 Nombre",
                    _nm[:24] + ("…" if len(_nm) > 24 else ""),
                    help=_nm if len(_nm) > 24 else None,
                )
            with col2:
                file_size_mb = uploaded_file.size / (1024 * 1024)
                st.metric("📦 Tamaño", f"{file_size_mb:.2f} MB")
            with col3:
                st.metric("🔠 Tipo", uploaded_file.name.split(".")[-1].upper())

            st.divider()

            col_btn, _ = st.columns([1, 4])
            with col_btn:
                # key= explícito evita que el contador auto-generado se desplace
                # cuando upload_error cambia entre reruns, lo que causaría que
                # Streamlit trate el botón como recién clickeado en un rerun posterior.
                process_button = st.button(
                    "🚀 PROCESAR",
                    key="procesar_btn",
                    use_container_width=True,
                    type="primary",
                )

            # Identifier changes when a different file is uploaded
            _file_id = f"{uploaded_file.name}_{uploaded_file.size}"

            # ── PROCESS (only runs on button click) ─────────────────────
            if process_button and file_valid and uploaded_file is not None:
                # Guard de idempotencia: si este archivo ya fue procesado y el
                # resultado está en session_state, no volver a llamar al pipeline.
                # Protege contra reruns espurios donde process_button puede ser
                # True más de una vez (ej. key-shift por widgets condicionales,
                # o interacciones del usuario durante un procesamiento largo).
                _already_processed = (
                    st.session_state.processed_file_id == _file_id
                    and st.session_state.resultado_actual is not None
                )

                if _already_processed:
                    st.caption(
                        "✅ Documento ya procesado. Usando resultados guardados."
                    )
                else:
                    with tempfile.NamedTemporaryFile(
                        suffix=f".{uploaded_file.name.split('.')[-1]}",
                        delete=False,
                    ) as tmp_file:
                        tmp_file.write(uploaded_file.getbuffer())
                        temp_path = tmp_file.name

                    _proc_status = st.empty()
                    _prog_bar = st.progress(0)
                    try:
                        _proc_status.info("⏳ Iniciando reconocimiento óptico…")
                        _prog_bar.progress(25)

                        result = st.session_state.pipeline.process_file(
                            temp_path, lang=ocr_lang
                        )
                        _prog_bar.progress(75)

                        # Persist result in named session state — decoupled from widget keys
                        st.session_state.resultado_actual = result
                        st.session_state.last_result = result           # Tab 2 compat
                        st.session_state.last_filename = uploaded_file.name
                        st.session_state.processed_file_id = _file_id
                        st.session_state.pages_actuales = result.get("pages", [])
                        # Reset page to 1 for new document (set BEFORE selectbox renders)
                        st.session_state.selected_page_idx = 1

                        _prog_bar.progress(100)
                        if result.get("status") == "success":
                            _proc_status.success("✅ ¡Documento procesado correctamente!")
                        else:
                            _proc_status.error(
                                f"❌ Error: {result.get('error', 'Error desconocido')}"
                            )

                    except (ValueError, TypeError, FileNotFoundError, OSError, RuntimeError) as e:
                        _proc_status.error(f"❌ Excepción: {e}")
                        st.session_state.processed_file_id = None

                    finally:
                        for _ in range(3):
                            try:
                                Path(temp_path).unlink(missing_ok=True)
                                break
                            except PermissionError:
                                import time as _time
                                _time.sleep(0.1)
                        else:
                            logger.warning("No se pudo eliminar temp: %s", temp_path)

            # ── SHOW RESULTS (reads session_state; persists across ALL reruns) ──
            # This block is completely independent from process_button.
            # It runs on page-selector changes, tab switches, any rerun —
            # pipeline.process_file() is NEVER called from this block.
            _result_for_this_file = (
                st.session_state.get("processed_file_id") == _file_id
                and st.session_state.resultado_actual is not None
            )
            if _result_for_this_file:
                result = st.session_state.resultado_actual or {}
                if result.get("status") == "success":
                    st.divider()
                    st.markdown(
                        '<div class="section-chip">📊 Resumen rápido</div>',
                        unsafe_allow_html=True,
                    )

                    sc1, sc2, sc3, sc4 = st.columns(4)

                    with sc1:
                        ocr_data = result.get("steps", {}).get("ocr", {})
                        confidence = ocr_data.get("confidence") if ocr_data else None
                        if confidence is None:
                            st.metric("🔤 Confianza OCR", "Texto digital")
                        elif confidence < 0:
                            st.metric("🔤 Confianza OCR", "—")
                        else:
                            st.metric("🔤 Confianza OCR", f"{confidence:.0f}%")

                    with sc2:
                        ext_text = result.get("extracted_text", "") or ""
                        if not ext_text.strip():
                            # PDF: aggregate text from all pages
                            ext_text = " ".join(
                                (p.get("text", "") or "")
                                for p in result.get("pages", [])
                            )
                        st.metric("📝 Caracteres", f"{len(ext_text.strip()):,}")

                    with sc3:
                        extraction = result.get("steps", {}).get("extraction", {})
                        if not extraction:
                            _pgs = result.get("pages", [])
                            if _pgs:
                                _fp = _pgs[0]
                                extraction = (
                                    _fp.get("extraction")
                                    or _fp.get("extracted_data")
                                    or {}
                                )
                        total_items = sum(
                            len(v) for v in extraction.values() if isinstance(v, list)
                        ) if extraction else 0
                        st.metric("🔍 Datos extraídos", str(total_items))

                    with sc4:
                        clf = result.get("steps", {}).get("classification", {})
                        if not clf:
                            pages = result.get("pages", [])
                            if pages:
                                clf = pages[0].get("classification", {})
                        if clf:
                            cn = (clf.get("predicted_class") or clf.get("class", "N/A"))
                            _cn_r = _resolve_cls_label(str(cn).lower())
                            _cn_d = _CAT_DISPLAY.get(_cn_r, _cn_r.replace("_", " ").title())
                            st.metric("🏷️ Tipo doc.", _cn_d)
                        else:
                            st.metric("🏷️ Tipo doc.", "N/A")

                    # ── Texto OCR ──────────────────────────────────────
                    st.divider()
                    st.markdown(
                        '<div class="section-chip">📋 Texto extraído (OCR)</div>',
                        unsafe_allow_html=True,
                    )

                    # pages_actuales tiene prioridad absoluta sobre extracted_text (PDF > imagen).
                    pages = st.session_state.pages_actuales or (result or {}).get("pages", [])

                    if pages:
                        num_pages = len(pages)
                        st.markdown(
                            f'<div class="nx-card nx-info">'
                            f'📑 <strong>PDF con {num_pages} página(s)</strong>'
                            f' · navega entre páginas en la pestaña'
                            f' <strong>📊 Resultados</strong>.</div>',
                            unsafe_allow_html=True,
                        )

                        # Selector sincronizado con Tab 2.
                        # Usa key distinto (_ocr_page_sel); on_change copia a selected_page_idx.
                        # Tab 2 usa key="selected_page_idx" como fuente de verdad;
                        # pre-set aquí para evitar valor obsoleto al cambiar de documento.
                        _ocr_clamped = max(1, min(st.session_state.selected_page_idx, num_pages))
                        st.session_state["_ocr_page_sel"] = _ocr_clamped

                        def _sync_ocr_page_cb():
                            st.session_state.selected_page_idx = st.session_state["_ocr_page_sel"]

                        _ocr_sel = st.selectbox(
                            "Selecciona página / factura:",
                            options=list(range(1, num_pages + 1)),
                            index=_ocr_clamped - 1,
                            format_func=lambda x: f"📄 Página {x} de {num_pages}",
                            key="_ocr_page_sel",
                            on_change=_sync_ocr_page_cb,
                        )
                        st.caption(
                            f"📄 Mostrando página {_ocr_sel} de {num_pages}"
                            " · sin reprocesar."
                        )
                        logger.debug("OCR tab: página %d de %d", _ocr_sel, num_pages)

                        _ocr_pg_idx = _ocr_sel - 1
                        _ocr_pd = (
                            st.session_state.pages_actuales[_ocr_pg_idx]
                            if 0 <= _ocr_pg_idx < len(st.session_state.pages_actuales)
                            else {}
                        )
                        _ocr_txt = (_ocr_pd.get("text", "") or "").strip()

                        if _ocr_txt:
                            st.text_area(
                                f"Texto OCR — Página {_ocr_sel}:",
                                value=_ocr_txt,
                                height=300,
                                disabled=True,
                                key=f"ocr_txt_{_ocr_sel}",
                                label_visibility="collapsed",
                            )
                            _ocr_clf_d = _ocr_pd.get("classification", {}) or {}
                            _ocr_ext_d = _ocr_pd.get("extraction", {}) or {}
                            _ocr_items = (
                                sum(len(v) for v in _ocr_ext_d.values() if isinstance(v, list))
                                if _ocr_ext_d else 0
                            )
                            _ocr_cls_n = (
                                _ocr_clf_d.get("predicted_class")
                                or _ocr_clf_d.get("class", "")
                                or "N/A"
                            )
                            _ocr_conf_v = _ocr_clf_d.get("confidence", 0) or 0
                            _oc1, _oc2, _oc3, _oc4 = st.columns(4)
                            with _oc1:
                                st.metric("📝 Palabras", len(_ocr_txt.split()))
                            with _oc2:
                                st.metric("📏 Caracteres", len(_ocr_txt))
                            with _oc3:
                                st.metric(
                                    "🏷️ Tipo pág.",
                                    _ocr_cls_n.upper() if _ocr_cls_n != "N/A" else "N/A",
                                )
                            with _oc4:
                                st.metric("🔍 Datos ext.", str(_ocr_items))
                            if _ocr_conf_v:
                                st.caption(f"Confianza clasificación: {_ocr_conf_v:.1%}")
                        else:
                            st.markdown(
                                '<div class="nx-card nx-warn">'
                                f'⚠️ Sin texto en página {_ocr_sel}.</div>',
                                unsafe_allow_html=True,
                            )

                        # Resumen multi-página
                        st.divider()
                        st.markdown(
                            '<div class="section-chip">📊 Resumen del documento</div>',
                            unsafe_allow_html=True,
                        )
                        total_palabras = sum(
                            len((p.get("text", "") or "").split()) for p in pages
                        )
                        paginas_con_texto = sum(
                            1 for p in pages if (p.get("text", "") or "").strip()
                        )
                        clases = [
                            (p.get("classification", {}).get("predicted_class")
                             or p.get("classification", {}).get("class", "?"))
                            for p in pages
                        ]
                        from collections import Counter
                        _most_common = Counter(clases).most_common(1)
                        clase_dom, freq = _most_common[0] if _most_common else ("N/A", 0)

                        sc = st.columns(4)
                        with sc[0]:
                            st.metric("📑 Páginas", num_pages)
                        with sc[1]:
                            st.metric("✅ Con texto", paginas_con_texto)
                        with sc[2]:
                            st.metric("📝 Palabras tot.", f"{total_palabras:,}")
                        with sc[3]:
                            st.metric(
                                "🏷️ Tipo dominante",
                                clase_dom.upper() if clase_dom != "N/A" else "N/A",
                                delta=f"{freq}/{num_pages} páginas",
                            )

                    elif (result or {}).get("extracted_text", "").strip():
                        _img_text = (result or {}).get("extracted_text", "").strip()
                        st.text_area(
                            "Contenido del documento:",
                            value=_img_text,
                            height=300,
                            disabled=True,
                            label_visibility="collapsed",
                        )
                        _wc = len(_img_text.split())
                        _cc = len(_img_text)
                        ic1, ic2 = st.columns(2)
                        with ic1:
                            st.metric("📝 Palabras", _wc)
                        with ic2:
                            st.metric("📏 Caracteres", _cc)
                    else:
                        st.markdown("""
<div class="nx-card nx-warn">
    ⚠️ <strong>OCR no extrajo texto.</strong><br/>
    <ul style="margin-top:0.4rem;font-size:0.87rem;">
        <li>Imagen de baja resolución o muy borrosa</li>
        <li>PDF sin contenido reconocible</li>
        <li>Idioma no soportado por el modelo</li>
    </ul>
</div>
""", unsafe_allow_html=True)

                    st.divider()
                    st.markdown("""
<div class="nx-card nx-success">
    💡 <strong>Procesamiento completo.</strong>
    Ve a <strong>📊 Resultados</strong> para ver los datos extraídos y la clasificación.
</div>
""", unsafe_allow_html=True)

                else:
                    st.error(
                        f"❌ Error al procesar: "
                        f"{(result or {}).get('error', 'Error desconocido')}"
                    )

    # ════════════════════════════════════════════════════════════════════════
    #  TAB 2 — RESULTADOS DETALLADOS
    # ════════════════════════════════════════════════════════════════════════
    with tab2:
        st.markdown("""
<div class="section-chip">📊 Análisis completo</div>
<p class="section-title-premium">Resultados Detallados</p>
""", unsafe_allow_html=True)

        if st.session_state.last_result is None:
            st.markdown("""
<div class="nx-card nx-info">
    💡 Procesa un archivo en la pestaña <strong>📤 Procesar Archivo</strong> para ver los resultados aquí.
</div>
""", unsafe_allow_html=True)
        else:
            result = st.session_state.last_result

            # ── FIX PDF: sincronizar steps desde pages ──────────────────────
            _pages = result.get("pages") or []
            _steps = result.get("steps") or {}

            if _pages:
                _primera = _pages[0]
                if not _steps:
                    result["steps"] = {}
                    _steps = result["steps"]
                if not _steps.get("ocr"):
                    _page_text = _primera.get("text", "") or ""
                    _steps["ocr"] = {
                        "status": "success" if _page_text.strip() else "warning",
                        "confidence": _primera.get("confidence"),
                        "language": _primera.get("language", "eng"),
                    }
                    result["steps"] = _steps
                if not _steps.get("extraction"):
                    _ext = _primera.get("extraction") or _primera.get("extracted_data") or {}
                    if _ext:
                        _steps["extraction"] = _ext
                        result["steps"] = _steps
                if not _steps.get("classification"):
                    _clf = _primera.get("classification") or {}
                    if _clf:
                        _steps["classification"] = _clf
                        result["steps"] = _steps
            # ── FIN DEL FIX ────────────────────────────────────────────────

            # ── Info general ────────────────────────────────────────────────
            gc1, gc2, gc3 = st.columns(3)
            with gc1:
                fn = st.session_state.get("last_filename") or ""
                if not fn:
                    inp = result.get("input_file", "N/A")
                    fn = Path(inp).name if inp and inp != "N/A" else "N/A"
                st.metric(
                    "📁 Archivo",
                    fn[:22] + ("…" if len(fn) > 22 else ""),
                    help=fn if len(fn) > 22 else None,
                )
            with gc2:
                fmt = result.get("format", "N/A")
                st.metric("🔠 Formato", fmt.upper() if fmt else "N/A")
            with gc3:
                ok = result.get("status") == "success"
                st.metric("✅ Estado", "✅ Éxito" if ok else "❌ Error")

            st.divider()

            steps = result.get("steps", {})
            if steps:

                # ── PASO 1: OCR ─────────────────────────────────────────────
                ocr_data = steps.get("ocr", {})
                with st.expander("🔬 Paso 1 · OCR — Reconocimiento Óptico", expanded=True):
                    if ocr_data:
                        oc1, oc2, oc3 = st.columns(3)
                        with oc1:
                            conf = ocr_data.get("confidence")
                            _conf_meter(conf)
                        with oc2:
                            lang_raw = ocr_data.get("language", "—")
                            lang_label = _LANG_MAP.get(lang_raw, f"🌐 {lang_raw}")
                            st.markdown(f"""
<div class="conf-meter-wrap">
    <div class="conf-label">Idioma</div>
    <div style="font-size:1.4rem;font-weight:800;color:#4338ca;margin-bottom:0.5rem;">
        {lang_label}
    </div>
</div>
""", unsafe_allow_html=True)
                        with oc3:
                            status_ok = ocr_data.get("status") == "success"
                            st.markdown(f"""
<div class="conf-meter-wrap">
    <div class="conf-label">Estado OCR</div>
    <div style="font-size:1.4rem;font-weight:800;
                color:{'#059669' if status_ok else '#dc2626'};margin-bottom:0.5rem;">
        {'✅ Éxito' if status_ok else '❌ Error'}
    </div>
</div>
""", unsafe_allow_html=True)
                    else:
                        st.markdown(
                            '<div class="nx-card nx-warn">'
                            '⚠️ Datos OCR no disponibles.</div>',
                            unsafe_allow_html=True,
                        )

                # ── PASO 2: EXTRACCIÓN ──────────────────────────────────────
                extraction = result.get("steps", {}).get("extraction", {})
                with st.expander("🔍 Paso 2 · Extracción de Datos", expanded=True):
                    _t2_pages        = st.session_state.pages_actuales
                    _t2_multi        = len(_t2_pages) > 1
                    _t2_clf_override = None
                    _t2_suppress_no_data = False

                    if _t2_multi:
                        _t2_mode = st.radio(
                            "",
                            ["📄 Ver factura seleccionada", "📋 Ver todas las facturas"],
                            horizontal=True,
                            key="t2_view_mode",
                            label_visibility="collapsed",
                        )

                        if _t2_mode == "📋 Ver todas las facturas":
                            st.caption(
                                "Esta tabla es un resumen por página. "
                                "Para ver todos los campos extraídos, selecciona una factura "
                                "en el modo **Ver factura seleccionada**."
                            )

                            # Selector "Ir al detalle": cambia modo y página en un solo paso
                            def _goto_detail_cb():
                                _gp = st.session_state.get("_t2_goto_pg")
                                if _gp is not None:
                                    st.session_state.selected_page_idx = _gp
                                    st.session_state["t2_view_mode"] = "📄 Ver factura seleccionada"
                                    st.session_state["_t2_goto_pg"] = None

                            _gc1, _ = st.columns([2, 3])
                            with _gc1:
                                st.selectbox(
                                    "Ir al detalle de la página:",
                                    options=[None] + list(range(1, len(_t2_pages) + 1)),
                                    format_func=lambda x: (
                                        "— selecciona para ver detalle —"
                                        if x is None else f"📄 Ir a página {x}"
                                    ),
                                    key="_t2_goto_pg",
                                    on_change=_goto_detail_cb,
                                )

                            # ── Tabla resumen mejorada ─────────────────────────
                            st.markdown(
                                '<div class="section-chip">📋 Resumen de todas las páginas</div>',
                                unsafe_allow_html=True,
                            )
                            _GT_FISCAL = {"factura", "recibo", "constancia", "contrato"}
                            _t2_rows = []
                            for _t2r in _t2_pages:
                                _t2ext  = _t2r.get("extraction", {}) or {}
                                _t2clf  = _t2r.get("classification", {}) or {}
                                _t2num  = _t2r.get("page_number", "?")

                                _t2tipo_raw = (
                                    _t2clf.get("predicted_class") or _t2clf.get("class", "")
                                ) or ""
                                _t2tipo_r = (
                                    _resolve_cls_label(str(_t2tipo_raw).lower())
                                    if _t2tipo_raw else ""
                                )
                                _t2tipo_d = (
                                    _CAT_DISPLAY.get(_t2tipo_r, _t2tipo_r.replace("_", " ").title())
                                    if _t2tipo_r else "—"
                                )
                                _t2conf = _t2clf.get("confidence", 0) or 0

                                # NIT: hasta 3 valores
                                _t2nit = _t2ext.get("nit", []) or []

                                # Fecha: fecha_texto prioridad; combinar con dates si aplica
                                _t2ft  = _t2ext.get("fecha_texto", []) or []
                                _t2dt  = _t2ext.get("dates", []) or []
                                _t2fecha = (_t2ft + [d for d in _t2dt if d not in _t2ft])[:2]

                                # Serie: combinar serie_sat + serie_dte (sin corto-circuito)
                                _t2sat = _t2ext.get("serie_sat", []) or []
                                _t2dte_s = _t2ext.get("serie_dte", []) or []
                                _t2serie = (_t2sat + [s for s in _t2dte_s if s not in _t2sat])[:2]

                                # Autorización: xxxxxxxx-xxxx… (13 chars, segmentos 1+2 del UUID)
                                _t2auth = _t2ext.get("autorizacion_sat", []) or []
                                if _t2auth:
                                    _a = _t2auth[0]
                                    _auth_str = (_a[:13] + "…") if len(_a) > 13 else _a
                                else:
                                    _auth_str = "—"

                                # No. DTE
                                _t2dte = _t2ext.get("numero_dte", []) or []

                                # Moneda: campo MONEDA primero, luego inferir de currency
                                _t2mon = _t2ext.get("moneda", []) or []

                                # Valores: para docs GT priorizar Q/GTQ; filtrar ruido simbólico
                                _t2cur_all = _t2ext.get("currency", []) or []
                                if _t2tipo_r in _GT_FISCAL:
                                    _t2cur_gt = [
                                        v for v in _t2cur_all
                                        if str(v).startswith(("Q ", "Q", "GTQ"))
                                    ]
                                    _t2cur = (_t2cur_gt or _t2cur_all)[:3]
                                else:
                                    _t2cur = _t2cur_all[:3]

                                _t2items = sum(
                                    len(v) for v in _t2ext.values() if isinstance(v, list)
                                )

                                _t2_rows.append({
                                    "Página":        _t2num,
                                    "Tipo":          _t2tipo_d,
                                    "Confianza":     f"{_t2conf:.0%}" if _t2conf else "—",
                                    "NIT":           ", ".join(_t2nit[:3]) if _t2nit else "—",
                                    "Fecha":         ", ".join(_t2fecha) if _t2fecha else "—",
                                    "Serie FEL/SAT": ", ".join(_t2serie) if _t2serie else "—",
                                    "Autorización":  _auth_str,
                                    "No. DTE":       ", ".join(_t2dte[:2]) if _t2dte else "—",
                                    "Moneda":        ", ".join(_t2mon[:2]) if _t2mon else "—",
                                    "Valores":       ", ".join(_t2cur) if _t2cur else "—",
                                    "Datos ext.":    _t2items,
                                })
                            if _t2_rows:
                                import pandas as _t2_pd
                                st.dataframe(
                                    _t2_pd.DataFrame(_t2_rows),
                                    use_container_width=True,
                                    hide_index=True,
                                )
                            extraction = {}
                            _t2_suppress_no_data = True

                        else:
                            # ── Selector + detalle con cards/badges ───────────
                            _t2_np = len(_t2_pages)
                            _t2_clamped = max(1, min(st.session_state.selected_page_idx, _t2_np))
                            _t2_sel = st.selectbox(
                                "Selecciona la página/factura que deseas revisar:",
                                options=list(range(1, _t2_np + 1)),
                                index=_t2_clamped - 1,
                                format_func=lambda x: f"📄 Página {x} de {_t2_np}",
                                key="selected_page_idx",
                            )
                            _t2_seldata      = _t2_pages[_t2_sel - 1]
                            extraction       = _t2_seldata.get("extraction", {}) or {}
                            _t2_clf_override = _t2_seldata.get("classification", {}) or {}
                            st.markdown(
                                f'<div class="section-chip">📋 Detalle de la página {_t2_sel}</div>',
                                unsafe_allow_html=True,
                            )
                            st.divider()

                    if extraction:
                        # Doc type drives contextual rendering;
                        # for multi-page PDFs uses the selected page's classification.
                        _clf_s = (
                            _t2_clf_override
                            or result.get("steps", {}).get("classification", {})
                        )
                        _raw_cls = (
                            _clf_s.get("predicted_class")
                            or _clf_s.get("class", "otro")
                        ).lower()
                        _doc_type = _resolve_cls_label(_raw_cls)
                        _fiscal_types = {"factura", "recibo", "contrato", "constancia"}

                        # ── Sección A: Contacto y generales ─────────────────
                        _contact_defs = [
                            ("emails",      "📧", "Correos electrónicos", "db-email",    "📧"),
                            ("phones",      "📱", "Teléfonos",            "db-phone",    "📱"),
                            ("urls",        "🔗", "URLs",                 "db-url",      "🔗"),
                            ("dates",       "📅", "Fechas numéricas",     "db-date",     "📅"),
                            ("fecha_texto", "📆", "Fechas en español",    "db-date",     "📆"),
                            ("currency",    "💰", "Moneda / Valores",     "db-currency", "💰"),
                        ]
                        _active_contact = [
                            (k, ic, lb, cs, bi)
                            for k, ic, lb, cs, bi in _contact_defs
                            if extraction.get(k)
                        ]
                        if _active_contact:
                            st.markdown(
                                '<div class="section-chip">📬 Contacto y generales</div>',
                                unsafe_allow_html=True,
                            )
                            _mid = (len(_active_contact) + 1) // 2
                            ca1, ca2 = st.columns(2)
                            for _fi, (_fk, _fic, _flb, _fcs, _fbi) in enumerate(_active_contact):
                                with (ca1 if _fi < _mid else ca2):
                                    _show_field(extraction, _fk, _fic, _flb, _fcs, _fbi)

                        # ── Sección B: Tributaria Guatemala ──────────────────
                        # Shown only for fiscal doc types; for carta_formal only "Referencia"
                        _serie_label = (
                            "Referencia del documento"
                            if _doc_type == "carta_formal"
                            else "Serie DTE clásica"
                        )
                        _trib_defs = [
                            ("nit", "🆔",
                             "NIT — Número de Identificación Tributaria",
                             "db-nit", "🆔"),
                            ("dpi", "🪪", "DPI / CUI",
                             "db-dpi", "🪪"),
                            ("moneda", "💱", "Moneda del documento",
                             "db-moneda", "💱"),
                            ("serie_dte", "📑", _serie_label,
                             "db-serie", "📑"),
                            ("serie_sat", "🔑", "Serie FEL / SAT (hex)",
                             "db-auth", "🔑"),
                            ("forma_pago", "💳", "Forma de pago",
                             "db-pago", "💳"),
                        ]
                        _active_trib = [
                            (k, ic, lb, cs, bi)
                            for k, ic, lb, cs, bi in _trib_defs
                            if extraction.get(k)
                        ]

                        if _active_trib and _doc_type in _fiscal_types:
                            st.divider()
                            st.markdown(
                                '<div class="section-chip">🇬🇹 Datos tributarios Guatemala</div>',
                                unsafe_allow_html=True,
                            )
                            _mid2 = (len(_active_trib) + 1) // 2
                            cb1, cb2 = st.columns(2)
                            for _fi, (_fk, _fic, _flb, _fcs, _fbi) in enumerate(_active_trib):
                                with (cb1 if _fi < _mid2 else cb2):
                                    _show_field(extraction, _fk, _fic, _flb, _fcs, _fbi)

                        elif _doc_type == "carta_formal":
                            # Only show serie_dte as "Referencia del documento"
                            _carta_ref = [
                                (k, ic, lb, cs, bi)
                                for k, ic, lb, cs, bi in _active_trib
                                if k == "serie_dte"
                            ]
                            if _carta_ref:
                                st.divider()
                                st.markdown(
                                    '<div class="section-chip">📄 Datos del documento</div>',
                                    unsafe_allow_html=True,
                                )
                                for (_fk, _fic, _flb, _fcs, _fbi) in _carta_ref:
                                    _show_field(extraction, _fk, _fic, _flb, _fcs, _fbi)

                        elif _active_trib and _doc_type not in {"carta_formal"}:
                            # otro / identificacion — show whatever data is there
                            st.divider()
                            st.markdown(
                                '<div class="section-chip">🇬🇹 Datos tributarios Guatemala</div>',
                                unsafe_allow_html=True,
                            )
                            _mid2 = (len(_active_trib) + 1) // 2
                            cb1, cb2 = st.columns(2)
                            for _fi, (_fk, _fic, _flb, _fcs, _fbi) in enumerate(_active_trib):
                                with (cb1 if _fi < _mid2 else cb2):
                                    _show_field(extraction, _fk, _fic, _flb, _fcs, _fbi)

                        # ── Sección C: Autorización SAT / FEL ────────────────
                        auth_list = extraction.get("autorizacion_sat", [])
                        dte_list  = extraction.get("numero_dte", [])
                        if (auth_list or dte_list) and _doc_type in (_fiscal_types | {"otro"}):
                            st.divider()
                            st.markdown(
                                '<div class="section-chip">🏛️ Autorización SAT · FEL</div>',
                                unsafe_allow_html=True,
                            )
                            cc1, cc2 = st.columns(2)
                            with cc1:
                                _field_label("🔐", "Número de Autorización SAT")
                                _badges(auth_list, "db-uuid", "🔐")
                            with cc2:
                                _field_label("📟", "Número DTE")
                                _badges(dte_list, "db-dte", "📟")

                        if (
                            not _active_contact
                            and not _active_trib
                            and not auth_list
                            and not dte_list
                        ):
                            st.markdown("""
<div class="nx-card nx-info">
    ℹ️ <strong>Sin datos estructurados encontrados.</strong>
    El texto fue extraído pero no contiene patrones reconocibles.
</div>
""", unsafe_allow_html=True)

                    elif not _t2_suppress_no_data:
                        st.markdown("""
<div class="nx-card nx-warn">
    ⚠️ <strong>Extracción no disponible.</strong>
    Asegúrate de procesar primero el documento.
</div>
""", unsafe_allow_html=True)

                # ── PASO 3: CLASIFICACIÓN ────────────────────────────────────
                # Para PDFs multipágina, usa la clasificación de la página seleccionada.
                _t3_pages = st.session_state.pages_actuales
                if len(_t3_pages) > 1:
                    _t3_raw = st.session_state.selected_page_idx - 1
                    _t3_idx = max(0, min(_t3_raw, len(_t3_pages) - 1))
                    classification = _t3_pages[_t3_idx].get("classification", {}) or {}
                    if not classification:
                        classification = result.get("steps", {}).get("classification", {})
                else:
                    classification = result.get("steps", {}).get("classification", {})
                with st.expander("🏷️ Paso 3 · Clasificación de Documento", expanded=True):
                    if len(_t3_pages) > 1:
                        st.caption(
                            f"Mostrando clasificación de página "
                            f"{st.session_state.selected_page_idx} de {len(_t3_pages)}"
                        )
                    if classification:
                        class_name = _resolve_cls_label(
                            (
                                classification.get("predicted_class")
                                or classification.get("class", "desconocida")
                            ).lower()
                        )
                        confidence = classification.get("confidence", 0) or 0

                        badge_css, badge_icon = _BADGE_MAP.get(class_name, ("badge-otro", "📁"))
                        _display_name = _CAT_DISPLAY.get(
                            class_name, class_name.replace("_", " ").title()
                        )
                        safe_label = _html.escape(_display_name.upper())

                        cl1, cl2 = st.columns([1, 2])

                        with cl1:
                            # Badge grande
                            conf_color = (
                                "#059669" if confidence > 0.8
                                else "#d97706" if confidence > 0.6
                                else "#dc2626"
                            )
                            st.markdown(f"""
<div class="class-badge-wrap animate-pulse-once">
    <div class="class-badge {badge_css}">
        <span style="font-size:1.4rem;">{badge_icon}</span>
        <span>{safe_label}</span>
    </div>
    <div class="class-conf-text">
        Confianza:
        <strong style="color:{conf_color};">{confidence*100:.1f}%</strong>
    </div>
</div>
""", unsafe_allow_html=True)

                        with cl2:
                            st.markdown("""
<div class="section-chip">📊 Probabilidades por categoría</div>
""", unsafe_allow_html=True)
                            probs = classification.get("probabilities", {})
                            if probs:
                                sorted_probs = sorted(
                                    probs.items(), key=lambda x: x[1], reverse=True
                                )
                                rows_html = ""
                                for cls, prob in sorted_probs:
                                    _resolved = _resolve_cls_label(str(cls))
                                    _disp = _CAT_DISPLAY.get(
                                        _resolved,
                                        _resolved.replace("_", " ").title(),
                                    )
                                    color = _COLOR_MAP.get(_resolved.lower(), "#6b7280")
                                    pct = prob * 100
                                    rows_html += f"""
<div class="prob-row">
    <div class="prob-label">{_html.escape(_disp)}</div>
    <div class="prob-bar-bg">
        <div class="prob-bar-fill"
             style="width:{pct:.1f}%;background:linear-gradient(90deg,{color}88,{color});"></div>
    </div>
    <div class="prob-pct" style="color:{color};">{pct:.1f}%</div>
</div>"""
                                st.markdown(rows_html, unsafe_allow_html=True)
                            else:
                                st.markdown(
                                    '<div class="nx-card nx-info">'
                                    'Probabilidades no disponibles.</div>',
                                    unsafe_allow_html=True,
                                )
                    else:
                        st.markdown(
                            '<div class="nx-card nx-warn">⚠️ Clasificación no disponible.</div>',
                            unsafe_allow_html=True,
                        )

            st.divider()

            # ── Exportar ────────────────────────────────────────────────────
            st.markdown(
                '<div class="section-chip">💾 Exportar resultados</div>',
                unsafe_allow_html=True,
            )
            ec1, ec2, ec3 = st.columns(3)

            with ec1:
                _orig_fn = st.session_state.get("last_filename") or "resultado"
                _base_fn = Path(_orig_fn).stem
                json_str = _build_export_json(result, _orig_fn)
                st.download_button(
                    label="📥 Descargar JSON",
                    data=json_str,
                    file_name=f"resultado_ocr_ia_{_base_fn}.json",
                    mime="application/json",
                    use_container_width=True,
                )
            with ec2:
                st.markdown("✅ **Resultado listo para exportar.**")
            with ec3:
                if st.button("🔄 Limpiar resultados", use_container_width=True):
                    st.session_state.last_result = None
                    st.session_state.resultado_actual = None
                    st.session_state.pages_actuales = []
                    st.session_state.processed_file_id = None
                    st.session_state.selected_page_idx = 1
                    st.rerun()

    # ════════════════════════════════════════════════════════════════════════
    #  TAB 3 — GUÍA DE USO
    # ════════════════════════════════════════════════════════════════════════
    with tab3:
        st.markdown("""
<div class="section-chip">📖 Documentación</div>
<p class="section-title-premium">Guía de Uso</p>
""", unsafe_allow_html=True)

        st.markdown("""
## ¿Cómo usar la aplicación?

### 1️⃣ Configuración Inicial
- Marca **"Tesseract instalado"** en la barra lateral
- Haz clic en **🚀 Inicializar Pipeline**

### 2️⃣ Procesar Archivo
- Ve a **📤 Procesar Archivo**
- Sube una imagen JPG/PNG/BMP o un PDF
- Selecciona el idioma y presiona **PROCESAR**

### 3️⃣ Ver Resultados
En la pestaña **📊 Resultados** encontrarás:
- **OCR** · Texto extraído y confianza del reconocimiento
- **Extracción** · Emails, teléfonos GT, fechas, URLs, moneda Q/GTQ,
  NIT (con/sin guion), DPI/CUI, Serie DTE, Serie SAT/FEL,
  Autorización SAT (UUID), Número DTE, Forma de pago
- **Clasificación** · Tipo de documento y probabilidades por categoría

### 4️⃣ Exportar
- Descarga los resultados en **JSON** para integrar con otros sistemas

---

## 🎯 Casos de Uso

| Tipo de documento | Campos extraídos |
|---|---|
| **Factura FEL** | NIT Emisor/Receptor, UUID SAT, Serie FEL, DTE, GTQ, Total |
| **Recibo** | Fecha, montos, forma de pago |
| **Contrato** | Partes, fechas, cláusulas |
| **Identificación** | NIT, DPI/CUI |
| **Carta formal** | Emails, fechas, URLs |

---

## ⚠️ Limitaciones

- La precisión OCR depende de la calidad de la imagen
- Documentos escaneados dan mejores resultados que fotos
- Imágenes claras y bien iluminadas producen mejores extracciones
        """)

    # ════════════════════════════════════════════════════════════════════════
    #  TAB 4 — INFORMACIÓN
    # ════════════════════════════════════════════════════════════════════════
    with tab4:
        st.markdown("""
<div class="section-chip">ℹ️ Proyecto</div>
<p class="section-title-premium">Información del Sistema</p>
""", unsafe_allow_html=True)

        ic1, ic2 = st.columns(2)

        with ic1:
            st.subheader("📦 Stack Tecnológico")
            st.markdown("""
| Librería | Uso |
|---|---|
| **Pytesseract** | OCR — Tesseract 5.5.0 |
| **OpenCV** | Preprocesado de imagen |
| **Scikit-learn** | LinearSVC + TF-IDF |
| **Streamlit** | Interfaz web |
| **Pillow** | Manipulación de imágenes |
| **pdfplumber** | Extracción de PDFs |
""")

        with ic2:
            st.subheader("🔧 Características")
            st.markdown("""
- ✅ OCR multi-idioma (`spa+eng` por defecto)
- ✅ Facturas FEL / SAT Guatemala
- ✅ Extracción de UUID de autorización SAT
- ✅ NIT con y sin guion verificador
- ✅ Clasificación en 7 categorías (F1 = 0.9940)
- ✅ Exportación JSON
- ✅ 158 tests automatizados
""")

        st.divider()
        st.markdown("""
<div style="
    background:rgba(234,179,8,0.07);
    border:1px solid rgba(234,179,8,0.3);
    border-left:4px solid #f59e0b;
    border-radius:12px;
    padding:1.1rem 1.4rem;
    color:#fde68a;
    font-size:0.88rem;
    line-height:1.7;
">
<div style="font-weight:700;font-size:0.95rem;margin-bottom:0.6rem;">
    ⚠️ Aviso Ético y de Privacidad
</div>
<ul style="margin:0;padding-left:1.2rem;">
<li>Usar <strong>únicamente</strong> documentos ficticios, sintéticos, propios
    o debidamente anonimizados. Nunca documentos reales de terceros.</li>
<li>Los resultados de OCR e IA deben ser <strong>verificados por una persona</strong>
    antes de tomar cualquier decisión basada en ellos.</li>
<li>No procesar documentos con datos sensibles o confidenciales
    sin la autorización correspondiente.</li>
<li><strong>Sin almacenamiento</strong>: los archivos se procesan en memoria
    y se descartan tras mostrar el resultado (privacidad por diseño).</li>
<li>Proyecto académico — no apto para uso en producción
    sin validación profesional adicional.</li>
</ul>
</div>
""", unsafe_allow_html=True)

        st.markdown("""
### 🚀 Versión
**OCR IA Project v1.0.0** · Python 3.13 · Tesseract 5.5.0

### 👨‍💻 Desarrollo
Universidad Mariano Gálvez de Guatemala — Curso 045, Inteligencia Artificial
Catedrático: Ing. MA. Carmelo Estuardo Mayén Monterroso

### 📝 Licencia
Proyecto académico de código abierto
""")


# ══════════════════════════════════════════════════════════════════════════════
#  FOOTER PREMIUM
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("""
<div class="nx-footer">
    <div class="nx-footer-title">🤖 SISTEMA INTELIGENTE OCR + IA</div>
    <div class="nx-footer-info">
        Universidad Mariano Gálvez de Guatemala · Facultad de Ingeniería
    </div>
    <div class="nx-footer-info">
        Curso 045 — Inteligencia Artificial ·
        Catedrático: Ing. MA. Carmelo Estuardo Mayén Monterroso
    </div>
    <div class="nx-footer-info">
        Proyecto 04 — Clasificación y Extracción de Documentos con OCR + IA
    </div>
    <div class="nx-footer-stack">
        Python 3.13 · Tesseract 5.5.0 · scikit-learn LinearSVC + TF-IDF · Streamlit ·
        7 categorías · 490 documentos · F1-macro 0.9940 · 158 tests ✅
    </div>
</div>
""", unsafe_allow_html=True)
