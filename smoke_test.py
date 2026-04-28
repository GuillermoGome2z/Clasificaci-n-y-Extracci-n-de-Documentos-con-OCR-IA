"""
smoke_test.py — Diagnóstico de integración del proyecto OCR IA.

Ejecutar desde la raíz del proyecto:
    python smoke_test.py

NO es un test de pytest. Verifica que los módulos se comunican
correctamente entre sí con datos reales, sin mocks.
"""
import sys
import json
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.WARNING,  # Solo warnings y errores en smoke test
    format="[%(levelname)s] %(name)s: %(message)s"
)

OK = "  [OK]"
FAIL = "  [FAIL]"
WARN = "  [WARN]"

def check(condition: bool, msg_ok: str, msg_fail: str) -> bool:
    if condition:
        print(f"{OK}  {msg_ok}")
    else:
        print(f"{FAIL} {msg_fail}")
    return condition


def test_01_imports():
    print("\n[TEST 1] Imports de módulos")
    try:
        from config import TESSERACT_PATH
        check(True, "config.py importado", "")
        check(
            TESSERACT_PATH is not None,
            f"Tesseract encontrado en: {TESSERACT_PATH}",
            "Tesseract NO encontrado — OCR no funcionará"
        )
    except ImportError as e:
        print(f"{FAIL} config.py no importa: {e}")
        return False

    for modulo in ["src.ocr", "src.extractor", "src.classifier", "src.pipeline"]:
        try:
            __import__(modulo)
            print(f"{OK}  {modulo} importado")
        except ImportError as e:
            print(f"{FAIL} {modulo} falla al importar: {e}")
            return False
    return True


def test_02_classifier_sin_modelo():
    print("\n[TEST 2] Classifier sin modelo entrenado")
    try:
        from src.classifier import DocumentClassifier
        clf = DocumentClassifier()

        check(hasattr(clf, 'is_trained'), "is_trained flag existe", "is_trained NO existe")
        check(not clf.is_trained, "is_trained=False sin modelo (correcto)", "is_trained=True sin modelo (incorrecto)")

        result = clf.predict("texto de prueba sin modelo")
        check(isinstance(result, dict), "predict() retorna dict", "predict() NO retorna dict")
        check("is_trained" in result, "is_trained en respuesta de predict()", "is_trained NO en respuesta")

        # Verificar que existe al menos una de las dos claves de clase
        tiene_clave = ("predicted_class" in result) or ("class" in result)
        check(tiene_clave, "Clave de clase presente en resultado", "Ninguna clave de clase en resultado")

        return True
    except Exception as e:
        print(f"{FAIL} Error en test classifier: {e}")
        return False


def test_03_classifier_con_modelo():
    print("\n[TEST 3] Classifier con modelo entrenado")
    model_path = Path("models/classifier_model.joblib")

    if not model_path.exists():
        print(f"{WARN}  models/classifier_model.joblib no existe")
        print(f"        Ejecuta: python train_classifier.py")
        print(f"        Este test se omite hasta que el modelo exista")
        return None  # Warning, no fallo

    try:
        from src.classifier import DocumentClassifier
        clf = DocumentClassifier(model_path=str(model_path))

        check(clf.is_trained, "Modelo cargado (is_trained=True)", "Modelo NO cargó (is_trained=False)")

        texto_factura = "FACTURA ELECTRONICA No. 001 Subtotal Q500 IVA Q60 Total Q560 NIT 1234567-8"
        result = clf.predict(texto_factura)

        check(isinstance(result, dict), "predict() retorna dict", "predict() NO retorna dict")
        check(result.get("is_trained") == True, "is_trained=True en resultado", "is_trained != True en resultado")

        clase = result.get("predicted_class") or result.get("class", "NINGUNA")
        confianza = result.get("confidence", 0)
        print(f"{OK}  Predicción: '{clase}' (confianza: {confianza:.2%})")

        check(
            clase in ["factura", "recibo", "contrato", "otro"],
            f"Clase válida: {clase}",
            f"Clase inesperada: {clase}"
        )
        return True

    except Exception as e:
        print(f"{FAIL} Error en test con modelo: {e}")
        return False


def test_04_extractor():
    print("\n[TEST 4] Extractor con texto real")
    try:
        from src.extractor import DataExtractor
        ext = DataExtractor()

        texto = (
            "Factura para juan@empresa.com "
            "Tel: 2345-6789 Fecha: 22/04/2026 "
            "Total: Q1500.00 URL: https://empresa.gt"
        )
        result = ext.extract_all(texto)

        check(isinstance(result, dict), "extract_all() retorna dict", "extract_all() NO retorna dict")
        check(len(result.get("emails", [])) > 0, "Email detectado", "Email NO detectado")
        check(len(result.get("phones", [])) > 0, "Teléfono detectado", "Teléfono NO detectado")
        check(len(result.get("dates", [])) > 0, "Fecha detectada", "Fecha NO detectada")
        check(len(result.get("currency", [])) > 0, "Monto detectado", "Monto NO detectado")

        return True
    except Exception as e:
        print(f"{FAIL} Error en extractor: {e}")
        return False


def test_05_pipeline_sin_archivo():
    print("\n[TEST 5] Pipeline con archivo inexistente (error boundary)")
    try:
        from src.pipeline import OCRPipeline
        pipe = OCRPipeline()

        result = pipe.process_image("/archivo/que/no/existe.jpg")

        check(isinstance(result, dict), "process_image() retorna dict (no excepción)", "process_image() lanzó excepción")
        check("errors" in result, "Campo 'errors' en resultado", "Campo 'errors' FALTA en resultado")
        check(len(result.get("errors", [])) > 0, "Error registrado en 'errors'", "Lista 'errors' vacía (debería tener error)")
        check(result.get("status") in ["error", "partial"], "Status es 'error' o 'partial'", f"Status inesperado: {result.get('status')}")

        return True
    except Exception as e:
        print(f"{FAIL} Pipeline lanzó excepción sin capturar: {e}")
        print(f"        El error boundary no está funcionando correctamente")
        return False


def test_06_formato_salida_pipeline():
    print("\n[TEST 6] Formato de salida del pipeline")
    try:
        from src.pipeline import OCRPipeline
        pipe = OCRPipeline()

        # Llama con archivo inexistente — nos interesa el formato del dict, no el contenido
        result = pipe.process_image("/fake.jpg")

        campos_esperados = ["status", "errors", "input_file"]
        for campo in campos_esperados:
            check(campo in result, f"Campo '{campo}' presente", f"Campo '{campo}' FALTA")

        return True
    except Exception as e:
        print(f"{FAIL} Error verificando formato: {e}")
        return False


def test_07_compatibilidad_train_classifier():
    print("\n[TEST 7] Compatibilidad train_classifier.py → classifier.py")
    model_path = Path("models/classifier_model.joblib")

    if not model_path.exists():
        print(f"{WARN}  Modelo no existe — omitiendo test de compatibilidad")
        print(f"        Ejecuta: python train_classifier.py")
        return None

    try:
        import joblib
        loaded = joblib.load(str(model_path))

        if hasattr(loaded, 'predict'):
            print(f"{OK}  Modelo es Pipeline de scikit-learn directo")
            print(f"        classifier.py debe usar sklearn_pipeline.predict()")
        elif isinstance(loaded, dict):
            print(f"{OK}  Modelo es dict con llaves: {list(loaded.keys())}")
            llaves_requeridas = ["model", "vectorizer"]
            for llave in llaves_requeridas:
                check(llave in loaded, f"Llave '{llave}' presente en dict", f"Llave '{llave}' FALTA en dict")
        else:
            print(f"{FAIL} Tipo de modelo desconocido: {type(loaded)}")
            return False

        # Verificar que classifier.py lo puede cargar correctamente
        from src.classifier import DocumentClassifier
        clf = DocumentClassifier(model_path=str(model_path))
        check(clf.is_trained, "classifier.py carga el modelo correctamente", "classifier.py NO pudo cargar el modelo")

        return True

    except Exception as e:
        print(f"{FAIL} Error en test de compatibilidad: {e}")
        return False


# ── EJECUCIÓN ─────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print(" SMOKE TEST — OCR IA PROYECTO")
    print(" Diagnóstico de integración entre módulos")
    print("=" * 60)

    tests = [
        ("Imports", test_01_imports),
        ("Classifier sin modelo", test_02_classifier_sin_modelo),
        ("Classifier con modelo", test_03_classifier_con_modelo),
        ("Extractor", test_04_extractor),
        ("Pipeline error boundary", test_05_pipeline_sin_archivo),
        ("Formato salida pipeline", test_06_formato_salida_pipeline),
        ("Compatibilidad train↔classifier", test_07_compatibilidad_train_classifier),
    ]

    resultados = []
    for nombre, test_fn in tests:
        try:
            r = test_fn()
            resultados.append((nombre, r))
        except Exception as e:
            print(f"\n{FAIL} Test '{nombre}' falló con excepción: {e}")
            resultados.append((nombre, False))

    print("\n" + "=" * 60)
    print(" RESUMEN")
    print("=" * 60)

    ok = sum(1 for _, r in resultados if r is True)
    warn = sum(1 for _, r in resultados if r is None)
    fail = sum(1 for _, r in resultados if r is False)

    for nombre, r in resultados:
        if r is True:
            print(f"  [OK]   {nombre}")
        elif r is None:
            print(f"  [WARN] {nombre} — omitido (modelo no existe)")
        else:
            print(f"  [FAIL] {nombre}")

    print()
    print(f"  Pasados: {ok}/{len(tests)}   Omitidos: {warn}   Fallidos: {fail}")
    print("=" * 60)

    if fail == 0:
        print("\n  El proyecto está listo para entrenar el modelo y hacer demo.")
        print("  Siguiente paso: python generar_dataset.py && python train_classifier.py")
    else:
        print(f"\n  Hay {fail} problema(s) que resolver antes de la expo.")
        print("  Revisa los [FAIL] arriba y corrígelos antes de continuar.")
    print()


if __name__ == "__main__":
    main()
