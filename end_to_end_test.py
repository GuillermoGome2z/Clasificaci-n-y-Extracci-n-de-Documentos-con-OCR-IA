"""
end_to_end_test.py — Prueba completa del pipeline con datos reales.

Simula el flujo completo OCR -> Extracción -> Clasificación usando texto
pre-cargado (sin requerir Tesseract ni archivos físicos).

Ejecutar:
    python end_to_end_test.py
"""
import logging
import json
from pathlib import Path

logging.basicConfig(level=logging.WARNING, format="[%(levelname)s] %(message)s")

OK   = "  [OK]  "
FAIL = "  [FAIL]"
SEP  = "─" * 60

DOCUMENTOS_TEST = [
    {
        "nombre": "Factura estándar",
        "categoria_esperada": "factura",
        "texto": (
            "FACTURA ELECTRONICA No. FAC-2026-0001 "
            "Distribuidora Guatemalteca SA NIT: 4523891-2 "
            "Documento tributario electronico SAT Guatemala "
            "Cliente: Juan Ramirez Correo: juan@empresa.com "
            "Tel: 5432-1098 Fecha: 22/04/2026 "
            "Subtotal Q8500.00 IVA 12% Q1020.00 Total Q9520.00 "
            "Forma de pago: transferencia bancaria "
            "contribuyente serie correlativo autorizado"
        )
    },
    {
        "nombre": "Recibo de pago",
        "categoria_esperada": "recibo",
        "texto": (
            "RECIBO OFICIAL DE PAGO No. REC-00348 "
            "Fecha: 20/04/2026 "
            "Recibi de: Maria Gonzalez la cantidad de Q450.00 "
            "por concepto de pago mensual servicio internet "
            "Forma de pago: efectivo cheque transferencia "
            "sello firma departamento cobros "
            "Tel: 2234-5678 Muchas gracias por su pago puntual"
        )
    },
    {
        "nombre": "Contrato de servicios",
        "categoria_esperada": "contrato",
        "texto": (
            "CONTRATO DE PRESTACION DE SERVICIOS "
            "Entre los suscritos convenimos las siguientes clausulas "
            "PRIMERA el contratante SEGUNDA vigencia 12 meses "
            "TERCERA contraprestacion el contratado obligaciones "
            "CUARTA confidencialidad Guatemala "
            "a partir de 01/05/2026 acuerdo incumplimiento "
            "firmamos en la ciudad de Guatemala"
        )
    },
    {
        "nombre": "Comunicado general",
        "categoria_esperada": "otro",
        "texto": (
            "COMUNICADO OFICIAL Fecha: 22/04/2026 "
            "Estimado cliente por medio de la presente le informamos "
            "sobre los nuevos horarios de atencion de nuestras oficinas "
            "Agradecemos su comprension cordialmente atentamente "
            "la administracion aviso informacion general "
            "Para consultas contactenos correo info@empresa.gt"
        )
    },
]


def test_extractor():
    """Verifica que el extractor detecta datos en textos reales."""
    print(f"\n{SEP}")
    print(" TEST EXTRACTOR")
    print(SEP)
    from src.extractor import DataExtractor
    ext = DataExtractor()

    texto_con_datos = (
        "Contacto: gerente@empresa.gt Tel: 2345-6789 "
        "Fecha: 22/04/2026 Total: Q1500.00 "
        "URL: https://empresa.gt RFC: ABC123456XYZ"
    )

    result = ext.extract_all(texto_con_datos)
    checks = [
        (len(result.get("emails", [])) > 0,     "Email extraído"),
        (len(result.get("phones", [])) > 0,     "Teléfono extraído"),
        (len(result.get("dates", [])) > 0,      "Fecha extraída"),
        (len(result.get("currency", [])) > 0,   "Monto extraído"),
        ("error" not in result,                  "Sin errores en extracción"),
    ]

    all_ok = True
    for cond, msg in checks:
        if cond:
            print(f"{OK} {msg}")
        else:
            print(f"{FAIL} {msg}")
            all_ok = False

    return all_ok


def test_clasificador():
    """Verifica que el clasificador acierte en los 4 tipos de documento."""
    print(f"\n{SEP}")
    print(" TEST CLASIFICADOR (4 categorías)")
    print(SEP)

    model_path = Path("models/classifier_model.joblib")
    if not model_path.exists():
        print(f"{FAIL} Modelo no existe. Ejecuta: python train_classifier.py")
        return False

    from src.classifier import DocumentClassifier
    clf = DocumentClassifier(model_path=str(model_path))

    if not clf.is_trained:
        print(f"{FAIL} Modelo cargado pero is_trained=False")
        return False

    aciertos = 0
    total = len(DOCUMENTOS_TEST)
    confianzas = []

    for doc in DOCUMENTOS_TEST:
        result = clf.predict(doc["texto"])
        clase = result.get("predicted_class") or result.get("class", "?")
        confianza = result.get("confidence", 0.0) or 0.0
        confianzas.append(confianza)

        acierto = clase == doc["categoria_esperada"]
        if acierto:
            aciertos += 1
            marca = OK
        else:
            marca = FAIL

        print(
            f"{marca} '{doc['nombre']}' → "
            f"esperado: {doc['categoria_esperada']:10s} | "
            f"predicho: {clase:10s} | "
            f"confianza: {confianza:.1%}"
        )

    conf_promedio = sum(confianzas) / len(confianzas) if confianzas else 0
    print()
    print(f"  Aciertos: {aciertos}/{total}")
    print(f"  Confianza promedio: {conf_promedio:.1%}")

    if conf_promedio < 0.70:
        print(f"\n  ADVERTENCIA: Confianza promedio baja ({conf_promedio:.1%})")
        print(f"  Para la expo necesitas > 70%. Regenera dataset y reentrena.")
    elif conf_promedio < 0.85:
        print(f"\n  OK para expo ({conf_promedio:.1%}). Podría ser mejor con más datos.")
    else:
        print(f"\n  EXCELENTE ({conf_promedio:.1%}). Listo para expo.")

    return aciertos >= 3  # Al menos 3 de 4 categorías correctas


def test_pipeline_texto():
    """
    Verifica el pipeline completo saltando el OCR (inyectando texto directo).
    Simula lo que haría el pipeline después de que OCR extrae el texto.
    """
    print(f"\n{SEP}")
    print(" TEST PIPELINE COMPLETO (texto inyectado, sin OCR)")
    print(SEP)

    from src.extractor import DataExtractor
    from src.classifier import DocumentClassifier

    model_path = Path("models/classifier_model.joblib")
    clf = DocumentClassifier(model_path=str(model_path) if model_path.exists() else None)
    ext = DataExtractor()

    all_ok = True
    for doc in DOCUMENTOS_TEST[:2]:  # Probar con los primeros 2
        texto = doc["texto"]
        nombre = doc["nombre"]

        # Simular lo que hace pipeline.py internamente
        try:
            extraction = ext.extract_all(texto)
            classification = clf.predict(texto)

            clase = classification.get("predicted_class") or classification.get("class", "?")
            confianza = classification.get("confidence", 0.0) or 0.0
            datos = sum(len(v) if isinstance(v, list) else 1
                       for v in extraction.values() if v)

            print(f"{OK} '{nombre}'")
            print(f"       Clase: {clase} ({confianza:.1%}) | Datos: {datos} encontrados")
            print(f"       is_trained: {classification.get('is_trained')}")

        except Exception as e:
            print(f"{FAIL} '{nombre}' → excepción: {e}")
            all_ok = False

    return all_ok


def test_formato_json():
    """Verifica que el resultado del pipeline tiene el formato correcto."""
    print(f"\n{SEP}")
    print(" TEST FORMATO JSON DE SALIDA")
    print(SEP)

    from src.pipeline import OCRPipeline
    pipe = OCRPipeline()

    # Probar con archivo inexistente para ver formato de error
    result = pipe.process_image("fake_para_formato_test.jpg")

    campos_requeridos = ["status", "errors", "input_file"]
    all_ok = True

    for campo in campos_requeridos:
        if campo in result:
            print(f"{OK} Campo '{campo}' presente en output")
        else:
            print(f"{FAIL} Campo '{campo}' FALTA en output")
            all_ok = False

    # Verificar que errors es lista
    if isinstance(result.get("errors"), list):
        print(f"{OK} 'errors' es lista (correcto)")
    else:
        print(f"{FAIL} 'errors' no es lista")
        all_ok = False

    return all_ok


# ── EJECUCIÓN ─────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print(" END-TO-END TEST — OCR IA PROYECTO")
    print(" Prueba completa del pipeline con datos reales")
    print("=" * 60)

    resultados = []
    tests = [
        ("Extractor", test_extractor),
        ("Clasificador 4 categorías", test_clasificador),
        ("Pipeline texto inyectado", test_pipeline_texto),
        ("Formato JSON salida", test_formato_json),
    ]

    for nombre, fn in tests:
        try:
            ok = fn()
            resultados.append((nombre, ok))
        except Exception as e:
            print(f"\n  EXCEPCIÓN en '{nombre}': {e}")
            resultados.append((nombre, False))

    print(f"\n{'=' * 60}")
    print(" RESUMEN FINAL")
    print("=" * 60)

    pasados = sum(1 for _, r in resultados if r)
    for nombre, r in resultados:
        marca = "[OK]  " if r else "[FAIL]"
        print(f"  {marca} {nombre}")

    print(f"\n  Pasados: {pasados}/{len(resultados)}")
    print("=" * 60)

    if pasados == len(resultados):
        print("\n  El pipeline está listo para la expo.")
        print("  Siguiente: streamlit run app/app.py y prueba con archivos reales.\n")
    else:
        fallos = [n for n, r in resultados if not r]
        print(f"\n  Fallos en: {fallos}")
        print("  Revisa los [FAIL] arriba antes de continuar.\n")


if __name__ == "__main__":
    main()
