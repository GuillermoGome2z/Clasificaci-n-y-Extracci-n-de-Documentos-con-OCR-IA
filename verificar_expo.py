"""
verificar_expo.py — Checklist automatizado del día de la expo.

Ejecutar 30 minutos antes de presentar:
    python verificar_expo.py

Si todo es [OK], estás listo. Si hay [FAIL], sabes qué resolver.
"""
from pathlib import Path

OK   = "  [OK]  "
FAIL = "  [FAIL]"
WARN = "  [WARN]"


def check(cond, msg_ok, msg_fail, es_critico=True):
    """Verifica una condición y muestra el resultado."""
    if cond:
        print(f"{OK} {msg_ok}")
        return True
    else:
        marca = FAIL if es_critico else WARN
        print(f"{marca} {msg_fail}")
        return cond or not es_critico


def main():
    """Función principal."""
    print("=" * 70)
    print(" CHECKLIST DE EXPO — OCR IA PROYECTO")
    print(" Ejecuta esto 30 min antes de presentar")
    print("=" * 70)

    criticos_ok = True

    # ─ BLOQUE 1: Archivos críticos ─────────────────────────────────────
    print("\n[1] ARCHIVOS CRITICOS")
    print("-" * 70)
    criticos_ok &= check(
        Path("models/classifier_model.joblib").exists(),
        "Modelo ML existe",
        "MODELO NO EXISTE — ejecuta train_classifier.py"
    )
    criticos_ok &= check(
        Path("app/app.py").exists(),
        "app/app.py existe",
        "app/app.py NO EXISTE"
    )
    criticos_ok &= check(
        Path("demo_plan_b.py").exists(),
        "Plan B existe (demo_plan_b.py)",
        "Plan B NO EXISTE — riesgo sin respaldo"
    )
    criticos_ok &= check(
        Path("smoke_test.py").exists(),
        "smoke_test.py existe",
        "smoke_test.py NO EXISTE"
    )
    criticos_ok &= check(
        Path("src/classifier.py").exists(),
        "src/classifier.py existe",
        "src/classifier.py NO EXISTE"
    )

    # ─ BLOQUE 2: Entorno Python ────────────────────────────────────────
    print("\n[2] ENTORNO PYTHON")
    print("-" * 70)
    try:
        import streamlit
        check(True, f"Streamlit {streamlit.__version__}", "")
    except ImportError:
        criticos_ok &= check(False, "", "Streamlit NO instalado")

    try:
        import sklearn
        check(True, f"scikit-learn {sklearn.__version__}", "")
    except ImportError:
        criticos_ok &= check(False, "", "scikit-learn NO instalado")

    try:
        import pytesseract
        check(True, "pytesseract importa correctamente", "")
    except ImportError:
        check(False, "", "pytesseract NO instalado", es_critico=False)

    try:
        import pdfplumber
        check(True, "pdfplumber importa correctamente", "")
    except ImportError:
        check(False, "", "pdfplumber NO instalado", es_critico=False)

    # ─ BLOQUE 3: Tesseract OCR ─────────────────────────────────────────
    print("\n[3] TESSERACT OCR (OPCIONAL)")
    print("-" * 70)
    try:
        from config import TESSERACT_PATH
        if TESSERACT_PATH:
            check(True, f"Tesseract en: {TESSERACT_PATH}", "")
            try:
                import pytesseract
                ver = pytesseract.get_tesseract_version()
                check(True, f"Tesseract version: {ver}", "")
            except Exception as e:
                check(False, "", f"Tesseract no responde: {e}", es_critico=False)
        else:
            check(False, "", "Tesseract NO detectado — usará Plan B", es_critico=False)
    except Exception as e:
        print(f"{WARN} Error verificando Tesseract: {e}")

    # ─ BLOQUE 4: Modelo ML ──────────────────────────────────────────────
    print("\n[4] MODELO DE MACHINE LEARNING")
    print("-" * 70)
    model_path = Path("models/classifier_model.joblib")
    if model_path.exists():
        size_kb = model_path.stat().st_size / 1024
        check(size_kb > 10, f"Modelo OK ({size_kb:.1f} KB)", "Modelo muy pequeño")
        try:
            from src.classifier import DocumentClassifier
            clf = DocumentClassifier(str(model_path))
            check(clf.is_trained, "Modelo cargado (is_trained=True)",
                  "Modelo NO cargó correctamente")

            # Prueba con texto de factura
            r = clf.predict("FACTURA ELECTRONICA NIT SAT IVA Total Q500 contribuyente")
            clase = r.get("predicted_class") or r.get("class", "?")
            conf = r.get("confidence", 0) or 0

            check(clase == "factura", f"Predicción correcta: {clase}",
                  f"Predicción incorrecta: {clase}", es_critico=False)
            check(conf > 0.70, f"Confianza aceptable ({conf:.1%})",
                  f"Confianza baja ({conf:.1%})", es_critico=False)
            check(conf > 0.80, f"Confianza EXCELENTE ({conf:.1%})",
                  "", es_critico=False)
        except Exception as e:
            criticos_ok &= check(False, "", f"Error cargando modelo: {e}")
    else:
        criticos_ok &= check(False, "", "Modelo NO existe")

    # ─ BLOQUE 5: Extractor de Datos ────────────────────────────────────
    print("\n[5] EXTRACTOR DE DATOS (REGEX)")
    print("-" * 70)
    try:
        from src.extractor import DataExtractor
        ext = DataExtractor()

        # Prueba con texto que contiene todos los tipos de datos
        texto_prueba = (
            "email@test.com Tel: 5432-1098 Fecha: 22/04/2026 "
            "Total Q1500.00 RFC: ABC123456XYZ"
        )
        r = ext.extract_all(texto_prueba)

        check(len(r.get("emails", [])) > 0, "Extrae emails", "NO extrae emails")
        check(len(r.get("phones", [])) > 0, "Extrae telefonos (OK)",
              "NO extrae telefonos", es_critico=False)
        check(len(r.get("dates", [])) > 0, "Extrae fechas", "NO extrae fechas")
        check(len(r.get("currency", [])) > 0, "Extrae montos Q (OK)",
              "NO extrae montos Q", es_critico=False)
        check(len(r.get("rfc", [])) > 0, "Extrae RFC (OK)", "NO extrae RFC",
              es_critico=False)
    except Exception as e:
        criticos_ok &= check(False, "", f"Error en extractor: {e}")

    # ─ BLOQUE 6: Archivos de Demo ──────────────────────────────────────
    print("\n[6] ARCHIVOS DE DEMO")
    print("-" * 70)
    demos_dir = Path("demos")
    if demos_dir.exists():
        pdfs = list(demos_dir.glob("*.pdf"))
        txts = list(demos_dir.glob("*.txt"))
        check(len(txts) >= 4, f"Archivos de demo: {len(txts)} .txt (OK)",
              f"Solo {len(txts)} .txt (necesitas 4)", es_critico=False)
        check(len(pdfs) >= 3, f"PDFs para expo: {len(pdfs)} (OK)",
              f"Solo {len(pdfs)} PDF (ideal: 3-4)", es_critico=False)
    else:
        print(f"{WARN} Carpeta demos/ no existe — crea archivos de demo")

    # ─ BLOQUE 7: Plan B (Respaldo) ─────────────────────────────────────
    print("\n[7] PLAN B (RESPALDO SIN TESSERACT)")
    print("-" * 70)
    check(Path("demo_plan_b.py").exists(),
          "demo_plan_b.py existe", "Plan B NO existe")
    check(Path("arrancar_expo.py").exists(),
          "arrancar_expo.py existe", "Script de arranque no existe",
          es_critico=False)
    check(Path("verificar_expo.py").exists(),
          "verificar_expo.py (este script) existe", "Este script no existe")

    # ─ BLOQUE 8: Tests ─────────────────────────────────────────────────
    print("\n[8] TEST SUITES")
    print("-" * 70)
    check(Path("tests/").exists(),
          "Carpeta tests/ existe", "tests/ NO EXISTE", es_critico=False)
    check(Path("smoke_test.py").exists(),
          "smoke_test.py existe", "smoke_test.py NO EXISTE", es_critico=False)
    check(Path("end_to_end_test.py").exists(),
          "end_to_end_test.py existe", "end_to_end_test.py NO EXISTE",
          es_critico=False)

    # ─ RESUMEN ──────────────────────────────────────────────────────────
    print()
    print("=" * 70)

    if criticos_ok:
        print("  ✅ RESULTADO: LISTO PARA EXPO")
        print()
        print("  Próximos pasos:")
        print("    1. Ejecuta: python arrancar_expo.py")
        print("       — o —")
        print("       streamlit run app/app.py")
        print()
        print("  Si Tesseract falla:")
        print("    streamlit run demo_plan_b.py --server.port 8502")
        print()
        print("  Última verificación: Prueba cargando un PDF demo.")
    else:
        print("  ❌ RESULTADO: HAY PROBLEMAS CRITICOS")
        print()
        print("  Resuelve todos los [FAIL] antes de presentar.")
        print("  Los [WARN] son informativos, no bloquean la ejecución.")

    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
