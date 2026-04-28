"""
crear_pdfs_demo.py — Genera PDFs de demo desde demos/*.txt
Ejecutar: python crear_pdfs_demo.py
"""
from pathlib import Path
from fpdf import FPDF


def txt_a_pdf(txt_path: Path, pdf_path: Path) -> bool:
    """Convierte .txt a PDF con Courier New 12pt — ideal para OCR."""
    try:
        content = txt_path.read_text(encoding="utf-8")
        pdf = FPDF()
        pdf.set_margins(20, 20, 20)
        pdf.add_page()
        pdf.set_font("Courier", size=12)

        reemplazos = str.maketrans(
            "áéíóúñÁÉÍÓÚÑ",
            "aeiounAEIOUN"
        )

        for linea in content.split("\n"):
            linea = linea.rstrip().translate(reemplazos)
            if linea:
                pdf.cell(0, 7, txt=linea, ln=True)
            else:
                pdf.ln(3)

        pdf.output(str(pdf_path))
        return True
    except Exception as e:
        print(f"  Error en {txt_path.name}: {e}")
        return False


def main():
    demos_dir = Path("demos")
    txts = sorted(demos_dir.glob("*.txt"))

    if not txts:
        print("ERROR: No hay archivos .txt en demos/")
        return

    print(f"Generando {len(txts)} PDFs...")
    ok_count = 0
    for txt in txts:
        pdf = txt.with_suffix(".pdf")
        ok = txt_a_pdf(txt, pdf)
        kb = pdf.stat().st_size / 1024 if pdf.exists() else 0
        print(f"  {'OK' if ok else 'FALLO'} {pdf.name} ({kb:.1f} KB)")
        if ok:
            ok_count += 1

    print(f"\nTotal: {ok_count}/{len(txts)} PDFs generados en demos/")


if __name__ == "__main__":
    main()
