"""
Crea un PDF multi-página para pruebas del fix de navegación.
"""
from pathlib import Path
from fpdf import FPDF

demos = Path("demos")
txts = sorted(demos.glob("demo_*.txt"))[:4]

if not txts:
    print("❌ No hay archivos demo_*.txt en demos/")
    exit(1)

pdf = FPDF()
pdf.set_margins(20, 20, 20)
pdf.set_font("Courier", size=11)

for idx, txt_file in enumerate(txts, 1):
    pdf.add_page()
    content = txt_file.read_text(encoding="utf-8")
    
    # Normalizar caracteres para evitar errores de encoding
    content = (content.replace("á", "a").replace("é", "e")
                      .replace("í", "i").replace("ó", "o")
                      .replace("ú", "u").replace("ñ", "n"))
    
    # Agregar título de página
    pdf.set_font("Courier", "B", size=12)
    pdf.cell(0, 10, text=f"PAGINA {idx}: {txt_file.stem.upper()}", 
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Courier", size=10)
    pdf.ln(5)
    
    for linea in content.split("\n"):
        linea = linea.rstrip()[:80]  # truncar líneas largas
        if linea:
            pdf.cell(0, 5, text=linea, new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.ln(3)

output_path = "demos/demo_multipagina.pdf"
pdf.output(output_path)
print(f"✅ Creado: {output_path} con {len(txts)} páginas")
print(f"Archivos usados:")
for idx, txt_file in enumerate(txts, 1):
    print(f"  {idx}. {txt_file.name}")
