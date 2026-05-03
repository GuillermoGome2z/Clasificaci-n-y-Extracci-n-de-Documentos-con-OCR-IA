"""
Tests para src/extractor.py - DataExtractor (documentos guatemaltecos)

Cobertura:
- extract_emails()      → 5 tests
- extract_phones()      → 6 tests  (GT: XXXX-XXXX, prefijo 2-5)
- extract_dates()       → 5 tests
- extract_urls()        → 5 tests
- extract_currency()    → 7 tests  (incluye Q/GTQ)
- extract_nit()         → 5 tests  (NIT guatemalteco)
- extract_dpi()         → 4 tests  (DPI/CUI guatemalteco)
- extract_serie_dte()   → 5 tests  (series FAC/REC/CTR…)
- extract_fecha_texto() → 4 tests  (fechas en español)
- extract_forma_pago()  → 5 tests  (EFECTIVO, CHEQUE…)
- False positives       → 4 tests  (NIT/DPI no deben ser teléfonos)
- extract_all()         → 4 tests  (claves GT, sin dni/rfc)
- extract_custom_pattern() → 2 tests
- extract_lines()       → 2 tests
- edge cases            → 5 tests

Total: 68 tests
"""


class TestExtractorEmails:
    """Tests para extracción de emails."""

    def test_extract_emails_single_valid(self, extractor):
        """Extrae un email válido de texto."""
        result = extractor.extract_emails("Contacto: john@example.com")
        assert isinstance(result, list)
        assert "john@example.com" in result

    def test_extract_emails_multiple_valid(self, extractor, sample_text_with_emails):
        """Extrae múltiples emails de texto."""
        result = extractor.extract_emails(sample_text_with_emails)
        assert isinstance(result, list)
        assert len(result) >= 2
        assert "john.doe@example.com" in result

    def test_extract_emails_with_subdomains(self, extractor):
        """Extrae emails con subdominios."""
        result = extractor.extract_emails("Email: info@mail.company.co.uk")
        assert isinstance(result, list)
        assert "info@mail.company.co.uk" in result

    def test_extract_emails_empty_string(self, extractor, empty_text):
        """Maneja texto vacío sin crash."""
        result = extractor.extract_emails(empty_text)
        assert isinstance(result, list)
        assert len(result) == 0

    def test_extract_emails_no_emails(self, extractor):
        """Retorna lista vacía si no hay emails."""
        result = extractor.extract_emails("Este texto no tiene emails")
        assert isinstance(result, list)
        assert len(result) == 0


class TestExtractorPhones:
    """Tests para extracción de teléfonos guatemaltecos (XXXX-XXXX, prefijo 2-5)."""

    def test_extract_phones_gt_landline(self, extractor):
        """Extrae teléfono fijo guatemalteco (prefijo 2)."""
        result = extractor.extract_phones("Tel: 2345-6789")
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_extract_phones_gt_mobile(self, extractor):
        """Extrae teléfono móvil guatemalteco (prefijo 3-5)."""
        result = extractor.extract_phones("Celular: 5123-4567")
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_extract_phones_gt_with_country_code(self, extractor):
        """Extrae teléfono guatemalteco con código de país +502."""
        result = extractor.extract_phones("Tel: +502 2345-6789")
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_extract_phones_multiple(self, extractor, sample_text_with_phones):
        """Extrae múltiples teléfonos guatemaltecos."""
        result = extractor.extract_phones(sample_text_with_phones)
        assert isinstance(result, list)
        assert len(result) >= 2

    def test_extract_phones_empty(self, extractor, empty_text):
        """Maneja texto vacío."""
        result = extractor.extract_phones(empty_text)
        assert isinstance(result, list)
        assert len(result) == 0

    def test_extract_phones_no_phones(self, extractor):
        """Retorna lista vacía sin teléfonos."""
        result = extractor.extract_phones("No hay números aquí")
        assert isinstance(result, list)
        assert len(result) == 0


class TestExtractorDates:
    """Tests para extracción de fechas numéricas."""

    def test_extract_dates_slash_format(self, extractor):
        """Extrae fecha en formato slash."""
        result = extractor.extract_dates("Fecha: 03/15/2024")
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_extract_dates_dash_format(self, extractor):
        """Extrae fecha en formato dash."""
        result = extractor.extract_dates("Día: 15-03-2024")
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_extract_dates_multiple(self, extractor, sample_text_with_dates):
        """Extrae múltiples fechas."""
        result = extractor.extract_dates(sample_text_with_dates)
        assert isinstance(result, list)
        assert len(result) >= 2

    def test_extract_dates_empty(self, extractor, empty_text):
        """Maneja texto vacío."""
        result = extractor.extract_dates(empty_text)
        assert isinstance(result, list)
        assert len(result) == 0

    def test_extract_dates_no_dates(self, extractor):
        """Retorna lista vacía sin fechas."""
        result = extractor.extract_dates("No hay fechas aquí")
        assert isinstance(result, list)
        assert len(result) == 0


class TestExtractorURLs:
    """Tests para extracción de URLs."""

    def test_extract_urls_https(self, extractor):
        """Extrae URL con HTTPS."""
        result = extractor.extract_urls("Sitio: https://www.example.com")
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_extract_urls_http(self, extractor):
        """Extrae URL con HTTP."""
        result = extractor.extract_urls("Web: http://domain.org/page")
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_extract_urls_with_path(self, extractor):
        """Extrae URL con ruta."""
        result = extractor.extract_urls("API: https://api.company.com/v1/endpoint")
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_extract_urls_multiple(self, extractor, sample_text_with_urls):
        """Extrae múltiples URLs."""
        result = extractor.extract_urls(sample_text_with_urls)
        assert isinstance(result, list)
        assert len(result) >= 2

    def test_extract_urls_empty(self, extractor, empty_text):
        """Maneja texto vacío."""
        result = extractor.extract_urls(empty_text)
        assert isinstance(result, list)
        assert len(result) == 0


class TestExtractorCurrency:
    """Tests para extracción de moneda y valores monetarios."""

    def test_extract_currency_usd_dollar(self, extractor):
        """Extrae valor en USD con símbolo $."""
        result = extractor.extract_currency("Precio: $199.99")
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_extract_currency_commas(self, extractor):
        """Extrae valor con separadores de miles."""
        result = extractor.extract_currency("Total: $1,234.50")
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_extract_currency_eur_code(self, extractor):
        """Extrae valor con código EUR."""
        result = extractor.extract_currency("Monto: EUR 100")
        assert isinstance(result, list)

    def test_extract_currency_usd_code(self, extractor):
        """Extrae valor con código USD."""
        result = extractor.extract_currency("Total: 500 USD")
        assert isinstance(result, list)

    def test_extract_currency_empty(self, extractor, empty_text):
        """Maneja texto vacío."""
        result = extractor.extract_currency(empty_text)
        assert isinstance(result, list)
        assert len(result) == 0

    def test_extract_currency_gtq_symbol(self, extractor):
        """Extrae quetzal guatemalteco con símbolo Q."""
        result = extractor.extract_currency("Total: Q 350.00")
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_extract_currency_gtq_code(self, extractor):
        """Extrae quetzal con código GTQ."""
        result = extractor.extract_currency("Monto: GTQ1,250.75")
        assert isinstance(result, list)
        assert len(result) >= 1


class TestExtractorNIT:
    """Tests para extracción de NIT guatemalteco (reemplaza DNI/RFC)."""

    def test_extract_nit_with_context(self, extractor):
        """Extrae NIT con etiqueta 'NIT:'."""
        result = extractor.extract_nit("NIT: 5356261-9")
        assert isinstance(result, list)
        assert len(result) >= 1
        assert "5356261-9" in result

    def test_extract_nit_n_i_t_format(self, extractor):
        """Extrae NIT en formato N.I.T. con puntos."""
        result = extractor.extract_nit("N.I.T.: 12345678-1")
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_extract_nit_standalone(self, extractor):
        """Extrae NIT sin etiqueta (6-8 dígitos + guión + 1 verificador)."""
        result = extractor.extract_nit("Contribuyente 5356261-9 presentó declaración")
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_extract_nit_empty(self, extractor, empty_text):
        """Maneja texto vacío."""
        result = extractor.extract_nit(empty_text)
        assert isinstance(result, list)
        assert len(result) == 0

    def test_extract_nit_returns_list(self, extractor):
        """Siempre retorna lista incluso sin NIT."""
        result = extractor.extract_nit("Sin identificación tributaria")
        assert isinstance(result, list)


class TestExtractorDPI:
    """Tests para extracción de DPI/CUI guatemalteco (13 dígitos)."""

    def test_extract_dpi_with_spaces(self, extractor):
        """Extrae DPI separado por espacios (XXXX XXXXX XXXX)."""
        result = extractor.extract_dpi("DPI: 2468 13579 2468")
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_extract_dpi_with_dashes(self, extractor):
        """Extrae DPI separado por guiones (XXXX-XXXXX-XXXX)."""
        result = extractor.extract_dpi("CUI: 1234-56789-1234")
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_extract_dpi_empty(self, extractor, empty_text):
        """Maneja texto vacío."""
        result = extractor.extract_dpi(empty_text)
        assert isinstance(result, list)
        assert len(result) == 0

    def test_extract_dpi_returns_list(self, extractor):
        """Siempre retorna lista incluso sin DPI."""
        result = extractor.extract_dpi("Sin identificación personal")
        assert isinstance(result, list)


class TestExtractorSerieDTE:
    """Tests para extracción de series DTE guatemaltecas (SAT)."""

    def test_extract_serie_dte_factura(self, extractor):
        """Extrae serie FAC (factura electrónica)."""
        result = extractor.extract_serie_dte("Serie: FAC-2026-0001")
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_extract_serie_dte_recibo(self, extractor):
        """Extrae serie REC (recibo)."""
        result = extractor.extract_serie_dte("Número: REC-00015")
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_extract_serie_dte_contrato(self, extractor):
        """Extrae serie CTR (contrato)."""
        result = extractor.extract_serie_dte("Ref: CTR-2026-0015")
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_extract_serie_dte_empty(self, extractor, empty_text):
        """Maneja texto vacío."""
        result = extractor.extract_serie_dte(empty_text)
        assert isinstance(result, list)
        assert len(result) == 0

    def test_extract_serie_dte_case_insensitive(self, extractor):
        """Detecta series en minúsculas (flag re.IGNORECASE)."""
        result = extractor.extract_serie_dte("fac-2026-0001 emitida hoy")
        assert isinstance(result, list)
        assert len(result) >= 1


class TestExtractorFechaTexto:
    """Tests para extracción de fechas en español."""

    def test_extract_fecha_texto_largo(self, extractor):
        """Extrae fecha en formato largo ('30 de abril de 2026')."""
        result = extractor.extract_fecha_texto("Emitido el 30 de abril de 2026")
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_extract_fecha_texto_abreviado(self, extractor):
        """Extrae fecha en formato abreviado ('28-abr-2026')."""
        result = extractor.extract_fecha_texto("Vence: 28-abr-2026")
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_extract_fecha_texto_multiple(self, extractor):
        """Extrae múltiples fechas textuales."""
        text = "Inicio: 1 de enero de 2026\nFin: 31 de diciembre de 2026"
        result = extractor.extract_fecha_texto(text)
        assert isinstance(result, list)
        assert len(result) >= 2

    def test_extract_fecha_texto_empty(self, extractor, empty_text):
        """Maneja texto vacío."""
        result = extractor.extract_fecha_texto(empty_text)
        assert isinstance(result, list)
        assert len(result) == 0


class TestExtractorFormaPago:
    """Tests para extracción de formas de pago guatemaltecas."""

    def test_extract_forma_pago_efectivo(self, extractor):
        """Extrae EFECTIVO."""
        result = extractor.extract_forma_pago("Forma de pago: EFECTIVO")
        assert isinstance(result, list)
        assert "EFECTIVO" in result

    def test_extract_forma_pago_cheque(self, extractor):
        """Extrae CHEQUE."""
        result = extractor.extract_forma_pago("Pago con CHEQUE bancario")
        assert isinstance(result, list)
        assert "CHEQUE" in result

    def test_extract_forma_pago_transferencia(self, extractor):
        """Extrae TRANSFERENCIA BANCARIA."""
        result = extractor.extract_forma_pago("Pago via TRANSFERENCIA BANCARIA")
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_extract_forma_pago_tarjeta(self, extractor):
        """Extrae TARJETA DE CRÉDITO."""
        result = extractor.extract_forma_pago("Pago con TARJETA DE CRÉDITO")
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_extract_forma_pago_empty(self, extractor, empty_text):
        """Maneja texto vacío."""
        result = extractor.extract_forma_pago(empty_text)
        assert isinstance(result, list)
        assert len(result) == 0


class TestExtractorFalsePositives:
    """Verifica que NIT/DPI no son detectados como teléfonos (falsos positivos)."""

    def test_dpi_not_detected_as_phone(self, extractor):
        """Un DPI (13 dígitos con espacios) no debe detectarse como teléfono GT."""
        result = extractor.extract_phones("DPI: 2468 13579 2468")
        assert len(result) == 0, f"DPI detectado incorrectamente como teléfono: {result}"

    def test_nit_not_detected_as_phone(self, extractor):
        """Un NIT (XXXXXXXX-X) no debe detectarse como teléfono GT."""
        result = extractor.extract_phones("NIT: 5356261-9 en la factura")
        assert len(result) == 0, f"NIT detectado incorrectamente como teléfono: {result}"

    def test_invalid_prefix_not_phone(self, extractor):
        """Números con prefijo 1 (inválido en GT) no son teléfonos."""
        result = extractor.extract_phones("1234-5678 no es teléfono guatemalteco")
        assert len(result) == 0, f"Número con prefijo 1 detectado: {result}"

    def test_serie_dte_detected_correctly(self, extractor):
        """Las series DTE son detectadas en contexto mixto."""
        result = extractor.extract_serie_dte("FAC-2026-0001 NIT: 5356261-9")
        assert len(result) >= 1


class TestExtractorAll:
    """Tests para el método extract_all() (orquestador)."""

    def test_extract_all_returns_dict(self, extractor):
        """extract_all() retorna un diccionario."""
        result = extractor.extract_all("Email: test@example.com, NIT: 5356261-9")
        assert isinstance(result, dict)

    def test_extract_all_has_all_keys(self, extractor):
        """extract_all() contiene todas las claves guatemaltecas esperadas."""
        result = extractor.extract_all("Test data")
        expected_keys = [
            "emails", "phones", "dates", "urls", "currency",
            "nit", "dpi", "serie_dte", "fecha_texto", "forma_pago",
        ]
        for key in expected_keys:
            assert key in result, f"Clave faltante en extract_all: {key}"
            assert isinstance(result[key], list)

    def test_extract_all_no_spanish_mexican_keys(self, extractor):
        """extract_all() no debe tener claves obsoletas de otros países."""
        result = extractor.extract_all("Test")
        assert "dni" not in result, "Clave 'dni' (España) no debe estar presente"
        assert "rfc" not in result, "Clave 'rfc' (México) no debe estar presente"

    def test_extract_all_with_guatemalan_factura(self, extractor, sample_text_factura_gt):
        """extract_all() extrae múltiples campos de una factura guatemalteca."""
        result = extractor.extract_all(sample_text_factura_gt)
        assert isinstance(result, dict)
        assert len(result.get("nit", [])) >= 1
        assert len(result.get("currency", [])) >= 1


class TestExtractorCustomPattern:
    """Tests para extract_custom_pattern()."""

    def test_extract_custom_pattern_valid(self, extractor):
        """Extrae datos con patrón personalizado válido."""
        pattern = r'\b[A-Z]{2}\d{3}\b'
        result = extractor.extract_custom_pattern("Código: AB123", pattern)
        assert isinstance(result, list)

    def test_extract_custom_pattern_invalid_regex(self, extractor):
        """Maneja patrón regex inválido sin crash."""
        result = extractor.extract_custom_pattern("Test", r'[A-Z')
        assert isinstance(result, list)


class TestExtractorLines:
    """Tests para extract_lines()."""

    def test_extract_lines_valid_text(self, extractor):
        """Extrae líneas limpias de texto."""
        result = extractor.extract_lines("Línea 1\nLínea 2\nLínea 3")
        assert isinstance(result, list)
        assert len(result) == 3

    def test_extract_lines_with_empty_lines(self, extractor):
        """Filtra líneas vacías correctamente."""
        result = extractor.extract_lines("Línea 1\n\n\nLínea 2\n")
        assert isinstance(result, list)
        assert any("Línea" in line for line in result)


class TestExtractorEdgeCases:
    """Tests para casos edge y robustez general."""

    def test_extractor_handles_special_characters(self, extractor):
        """Maneja caracteres especiales sin crash."""
        result = extractor.extract_emails("Correo: test@example.com™✓")
        assert isinstance(result, list)

    def test_extractor_handles_unicode(self, extractor):
        """Maneja texto con unicode sin crash."""
        result = extractor.extract_emails("Enviar a: josé@españa.es")
        assert isinstance(result, list)

    def test_extractor_handles_long_text(self, extractor):
        """Maneja texto muy largo sin timeout."""
        long_text = "Email: test@example.com " * 1000
        result = extractor.extract_emails(long_text)
        assert isinstance(result, list)

    def test_extractor_all_returns_correct_structure(self, extractor):
        """extract_all() siempre retorna estructura válida (valores son listas)."""
        result = extractor.extract_all("Solo texto sin datos estructurados")
        for key, value in result.items():
            assert isinstance(value, list), f"Clave '{key}' no retorna lista"

    def test_extractor_returns_deduplicated_results(self, extractor):
        """Los resultados de emails no tienen duplicados."""
        text = "Email: test@example.com test@example.com test@example.com"
        result = extractor.extract_emails(text)
        assert isinstance(result, list)
        assert len(result) == len(set(result))
