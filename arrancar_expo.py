"""
arrancar_expo.py — Script de inicio para el dia de la exposicion.

Verifica que todo está en orden y lanza la aplicación.

Ejecutar:
    python arrancar_expo.py
"""
import sys
import subprocess
from pathlib import Path


def verificar_modelo():
    """Verifica que el modelo ML existe y está cargable."""
    model = Path("models/classifier_model.joblib")
    if not model.exists():
        print("[ERROR] Modelo no encontrado: models/classifier_model.joblib")
        print("        Ejecuta: python train_classifier.py")
        return False
    size_kb = model.stat().st_size / 1024
    print(f"[OK]  Modelo encontrado ({size_kb:.1f} KB)")
    return True


def verificar_tesseract():
    """Verifica disponibilidad de Tesseract para OCR."""
    try:
        from config import TESSERACT_PATH
        import pytesseract

        if TESSERACT_PATH:
            try:
                pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
                ver = pytesseract.get_tesseract_version()
                print(f"[OK]  Tesseract {ver} en: {TESSERACT_PATH}")
                return True
            except Exception as e:
                print(f"[WARN] Tesseract encontrado pero falla: {e}")
                return False
        else:
            print("[WARN] Tesseract NO detectado — usará Plan B")
            return False
    except Exception:
        print("[WARN] No se pudo verificar Tesseract")
        return False


def verificar_dependencias():
    """Verifica que todos los paquetes necesarios están instalados."""
    paquetes = ["streamlit", "pytesseract", "sklearn", "cv2", "PIL", "pdfplumber"]
    faltantes = []
    for pkg in paquetes:
        try:
            __import__(pkg if pkg != "sklearn" else "sklearn")
        except ImportError:
            faltantes.append(pkg)
    if faltantes:
        print(f"[ERROR] Dependencias faltantes: {faltantes}")
        print("        Ejecuta: pip install -r requirements.txt")
        return False
    print("[OK]  Todas las dependencias instaladas")
    return True


def verificar_demos():
    """Verifica que hay archivos de demo preparados."""
    demos_dir = Path("demos")
    if demos_dir.exists():
        txt_files = list(demos_dir.glob("*.txt"))
        pdf_files = list(demos_dir.glob("*.pdf"))
        print(f"[INFO] Archivos de demo: {len(txt_files)} TXT, {len(pdf_files)} PDF")
        if len(txt_files) >= 4:
            print("[OK]  Archivos de demo (.txt) disponibles")
            if len(pdf_files) >= 3:
                print("[OK]  PDFs de demo listos para presentar")
                return True
            else:
                print("[WARN] Convierte los .txt a PDF para la demo (instructions en demos/)")
                return True
        else:
            print("[WARN] No hay suficientes archivos de demo (.txt)")
            return False
    else:
        print("[WARN] Carpeta demos/ no existe")
        return False


def main():
    """Función principal."""
    print("=" * 60)
    print(" VERIFICACIÓN PRE-EXPO — OCR IA PROYECTO")
    print(" Inicia la aplicación después de validar todo")
    print("=" * 60)
    print()

    modelo_ok = verificar_modelo()
    tess_ok = verificar_tesseract()
    deps_ok = verificar_dependencias()
    demos_ok = verificar_demos()

    print()
    print("=" * 60)

    # Determinar si hay problemas críticos
    criticos_ok = modelo_ok and deps_ok

    if not criticos_ok:
        print("[ERROR] Hay problemas CRITICOS que impiden la ejecución.")
        print()
        print("Resuelve los [ERROR] antes de intentar de nuevo.")
        print()
        sys.exit(1)

    print()
    if tess_ok:
        print("[OK] Tesseract disponible. Lanzando aplicación principal con OCR real...")
        print()
        print("      URL principal:    http://localhost:8501")
        print("      Para detener:     Ctrl + C")
        print()
        try:
            subprocess.run(
                [sys.executable, "-m", "streamlit", "run",
                 "app/app.py", "--server.port", "8501"],
                check=False
            )
        except KeyboardInterrupt:
            print()
            print("Aplicación cerrada.")
    else:
        print("[WARN] Tesseract no disponible. Lanzando Plan B (respaldo)...")
        print()
        print("      URL Plan B:       http://localhost:8502")
        print("      Para detener:     Ctrl + C")
        print()
        print("      Nota: Usa los documentos pre-cargados para la demo.")
        print()
        try:
            subprocess.run(
                [sys.executable, "-m", "streamlit", "run",
                 "demo_plan_b.py", "--server.port", "8502"],
                check=False
            )
        except KeyboardInterrupt:
            print()
            print("Plan B cerrado.")

    print()
    print("=" * 60)
    print("Aplicación finalizada.")
    print("=" * 60)


if __name__ == "__main__":
    main()
