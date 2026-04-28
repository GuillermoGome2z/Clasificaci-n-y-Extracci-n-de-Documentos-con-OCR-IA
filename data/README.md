# Dataset — OCR IA Proyecto 04

## Fuente
Documentos sintéticos generados con Python (fpdf2 + texto plano).

## Categorías (7 tipos)
- **factura**: Facturas electrónicas guatemaltecas (NIT, IVA, SAT)
- **recibo**: Recibos oficiales de pago
- **contrato**: Contratos de prestación de servicios
- **constancia**: Constancias de trabajo y estudios
- **carta_formal**: Cartas y comunicados formales
- **identificacion**: Documentos de identidad (DPI simulado)
- **otro**: Comunicados generales y otros documentos

## Cantidad
- 35 documentos por categoría = 245 documentos totales
- 30 completos + 5 cortos por categoría

## Archivos
- `data/training/<categoría>/*.txt` — Textos de entrenamiento
- `data/ground_truth.csv` — Valores de campos por documento

## Licencia
Dataset sintético generado automáticamente. No contiene datos reales.
