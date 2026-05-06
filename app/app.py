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

/* ── Responsive ─────────────────────────────────────────────────────────── */
@media (max-width: 768px) {
    .hero { padding: 1.75rem 1.25rem; }
    .hero-title { font-size: 1.6rem; }
    .hero-stats { gap: 0.5rem; }
    .stat-pill { min-width: 70px; padding: 0.5rem 0.75rem; }
    .stat-val { font-size: 1.2rem; }
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
            uploaded_file = st.file_uploader(
                "Arrastra o selecciona tu archivo",
                type=["jpg", "jpeg", "png", "pdf", "bmp", "gif"],
                key="file_uploader",
                help="Formatos soportados: JPG, PNG, BMP, GIF, PDF",
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

        # ── Info del archivo cargado ────────────────────────────────────────
        if uploaded_file is not None:
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
                process_button = st.button(
                    "🚀 PROCESAR",
                    use_container_width=True,
                    type="primary",
                )

            if process_button:
                with tempfile.NamedTemporaryFile(
                    suffix=f".{uploaded_file.name.split('.')[-1]}",
                    delete=False,
                ) as tmp_file:
                    tmp_file.write(uploaded_file.getbuffer())
                    temp_path = tmp_file.name

                try:
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    status_text.info("⏳ Iniciando reconocimiento óptico…")
                    progress_bar.progress(25)

                    result = st.session_state.pipeline.process_file(
                        temp_path, lang=ocr_lang
                    )
                    progress_bar.progress(75)
                    st.session_state.last_result = result
                    st.session_state.last_filename = uploaded_file.name
                    progress_bar.progress(100)

                    if result.get("status") == "success":
                        status_text.success("✅ ¡Documento procesado correctamente!")

                        st.divider()
                        st.markdown('<div class="section-chip">📊 Resumen rápido</div>', unsafe_allow_html=True)

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
                        st.markdown('<div class="section-chip">📋 Texto extraído (OCR)</div>', unsafe_allow_html=True)

                        extracted_text = result.get("extracted_text", "").strip()
                        pages = result.get("pages", [])

                        if extracted_text:
                            st.text_area(
                                "Contenido del documento:",
                                value=extracted_text,
                                height=350,
                                disabled=True,
                                key="ocr_output_single",
                            )

                        elif pages:
                            num_pages = len(pages)
                            st.markdown(f"""
<div class="nx-card nx-info">
    📑 <strong>PDF con {num_pages} página(s)</strong> · navegación instantánea entre páginas.
</div>
""", unsafe_allow_html=True)

                            if num_pages <= 5:
                                page_tabs = st.tabs([f"📄 Pág. {i+1}" for i in range(num_pages)])
                                for idx, page_tab in enumerate(page_tabs):
                                    with page_tab:
                                        page_data = pages[idx]
                                        page_text = page_data.get("text", "").strip()
                                        col_a, col_b = st.columns([3, 1])
                                        with col_a:
                                            st.markdown(f"**Texto extraído — Página {idx+1}:**")
                                        with col_b:
                                            if page_text:
                                                wc = len(page_text.split())
                                                st.markdown(
                                                    f"<span style='float:right;font-size:0.82rem;"
                                                    f"color:#059669;'>✅ {wc} palabras</span>",
                                                    unsafe_allow_html=True,
                                                )
                                        if page_text:
                                            st.text_area(
                                                f"Contenido pág. {idx+1}:",
                                                value=page_text,
                                                height=300,
                                                disabled=True,
                                                key=f"ocr_page_{idx}",
                                                label_visibility="collapsed",
                                            )
                                        else:
                                            st.markdown(
                                                '<div class="nx-card nx-warn">⚠️ Sin texto en esta página.</div>',
                                                unsafe_allow_html=True,
                                            )

                                        page_clf = page_data.get("classification", {})
                                        if page_clf:
                                            pc = (page_clf.get("predicted_class") or page_clf.get("class", "?"))
                                            pconf = page_clf.get("confidence", 0) or 0
                                            st.markdown(
                                                f"**Clasificación:** `{pc.upper()}` "
                                                f"({pconf:.1%} confianza)"
                                            )
                            else:
                                selected_page = st.selectbox(
                                    "Selecciona página:",
                                    options=list(range(1, num_pages + 1)),
                                    format_func=lambda x: f"📄 Página {x} / {num_pages}",
                                    key="page_selector",
                                )
                                page_data = pages[selected_page - 1]
                                page_text = page_data.get("text", "").strip()
                                if page_text:
                                    st.text_area(
                                        f"Contenido página {selected_page}:",
                                        value=page_text,
                                        height=300,
                                        disabled=True,
                                        key=f"ocr_multi_{selected_page}",
                                    )
                                    cols = st.columns(3)
                                    with cols[0]:
                                        st.metric("📝 Palabras", len(page_text.split()))
                                    with cols[1]:
                                        st.metric("📏 Caracteres", len(page_text))
                                    with cols[2]:
                                        pc_data = page_data.get("classification", {})
                                        pc_name = pc_data.get("predicted_class") or pc_data.get("class", "?")
                                        st.metric("🏷️ Tipo", pc_name.upper() if pc_name else "N/A")
                                else:
                                    st.markdown(
                                        f'<div class="nx-card nx-warn">⚠️ Sin texto en página {selected_page}.</div>',
                                        unsafe_allow_html=True,
                                    )

                            # Resumen multi-página
                            st.divider()
                            st.markdown('<div class="section-chip">📊 Resumen del documento</div>', unsafe_allow_html=True)
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
                            clase_dom, freq = Counter(clases).most_common(1)[0] if clases else ("N/A", 0)

                            sc = st.columns(4)
                            with sc[0]: st.metric("📑 Páginas", num_pages)
                            with sc[1]: st.metric("✅ Con texto", paginas_con_texto)
                            with sc[2]: st.metric("📝 Palabras tot.", f"{total_palabras:,}")
                            with sc[3]:
                                st.metric(
                                    "🏷️ Tipo dominante",
                                    clase_dom.upper() if clase_dom != "N/A" else "N/A",
                                    delta=f"{freq}/{num_pages} páginas",
                                )

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
                        err = result.get("error", "Error desconocido")
                        status_text.error(f"❌ Error: {err}")

                except (ValueError, TypeError, FileNotFoundError, OSError, RuntimeError) as e:
                    status_text.error(f"❌ Excepción: {e}")

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
                if not result.get("extracted_text"):
                    result["extracted_text"] = _primera.get("text", "") or ""
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
                        st.markdown('<div class="nx-card nx-warn">⚠️ Datos OCR no disponibles.</div>',
                                    unsafe_allow_html=True)

                # ── PASO 2: EXTRACCIÓN ──────────────────────────────────────
                extraction = result.get("steps", {}).get("extraction", {})
                with st.expander("🔍 Paso 2 · Extracción de Datos", expanded=True):
                    if extraction:
                        # Doc type drives contextual rendering
                        _clf_s = result.get("steps", {}).get("classification", {})
                        _raw_cls = (_clf_s.get("predicted_class") or _clf_s.get("class", "otro")).lower()
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
                            ("nit",        "🆔", "NIT — Número de Identificación Tributaria", "db-nit",    "🆔"),
                            ("dpi",        "🪪", "DPI / CUI",                                 "db-dpi",    "🪪"),
                            ("moneda",     "💱", "Moneda del documento",                       "db-moneda", "💱"),
                            ("serie_dte",  "📑", _serie_label,                                 "db-serie",  "📑"),
                            ("serie_sat",  "🔑", "Serie FEL / SAT (hex)",                     "db-auth",   "🔑"),
                            ("forma_pago", "💳", "Forma de pago",                             "db-pago",   "💳"),
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

                        if not _active_contact and not _active_trib and not auth_list and not dte_list:
                            st.markdown("""
<div class="nx-card nx-info">
    ℹ️ <strong>Sin datos estructurados encontrados.</strong>
    El texto fue extraído pero no contiene patrones reconocibles.
</div>
""", unsafe_allow_html=True)

                    else:
                        st.markdown("""
<div class="nx-card nx-warn">
    ⚠️ <strong>Extracción no disponible.</strong>
    Asegúrate de procesar primero el documento.
</div>
""", unsafe_allow_html=True)

                # ── PASO 3: CLASIFICACIÓN ────────────────────────────────────
                classification = result.get("steps", {}).get("classification", {})
                with st.expander("🏷️ Paso 3 · Clasificación de Documento", expanded=True):
                    if classification:
                        class_name = _resolve_cls_label(
                            (
                                classification.get("predicted_class")
                                or classification.get("class", "desconocida")
                            ).lower()
                        )
                        confidence = classification.get("confidence", 0) or 0

                        badge_css, badge_icon = _BADGE_MAP.get(class_name, ("badge-otro", "📁"))
                        _display_name = _CAT_DISPLAY.get(class_name, class_name.replace("_", " ").title())
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
                                    _disp = _CAT_DISPLAY.get(_resolved, _resolved.replace("_", " ").title())
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
                                    '<div class="nx-card nx-info">Probabilidades no disponibles.</div>',
                                    unsafe_allow_html=True,
                                )
                    else:
                        st.markdown(
                            '<div class="nx-card nx-warn">⚠️ Clasificación no disponible.</div>',
                            unsafe_allow_html=True,
                        )

            st.divider()

            # ── Exportar ────────────────────────────────────────────────────
            st.markdown('<div class="section-chip">💾 Exportar resultados</div>', unsafe_allow_html=True)
            ec1, ec2, ec3 = st.columns(3)

            with ec1:
                json_str = json.dumps(result, indent=2, ensure_ascii=False)
                st.download_button(
                    label="📥 Descargar JSON",
                    data=json_str,
                    file_name=f"resultado_ocr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True,
                )
            with ec2:
                st.markdown(
                    '<div class="nx-card nx-success" style="margin:0;">✅ JSON generado correctamente.</div>',
                    unsafe_allow_html=True,
                )
            with ec3:
                if st.button("🔄 Limpiar resultados", use_container_width=True):
                    st.session_state.last_result = None
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
### 🚀 Versión
**OCR IA Project v1.0.0** · Python 3.13 · Tesseract 5.5.0

### 👨‍💻 Desarrollo
Universidad Mariano Gálvez de Guatemala — Curso 045, Inteligencia Artificial

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
