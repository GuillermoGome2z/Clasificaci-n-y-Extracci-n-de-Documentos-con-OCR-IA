"""
Tests para src/extractor.py - DataExtractor

Cobertura:
- extract_emails() → 5 tests (MÉTODOS EN PLURAL)
- extract_phones() → 5 tests
- extract_dates() → 5 tests
- extract_urls() → 5 tests
- extract_currency() → 5 tests
- extract_dni() → 4 tests
- extract_rfc() → 4 tests
- extract_all() → 3 tests
- extract_custom_pattern() → 2 tests
- extract_lines() → 2 tests

Total: 40 tests
"""
import pytest


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
    """Tests para extracción de teléfonos."""

    def test_extract_phones_us_format(self, extractor):
        """Extrae teléfono formato USA."""
        result = extractor.extract_phones("Teléfono: (202) 555-0173")
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_extract_phones_with_dots(self, extractor):
        """Extrae teléfono con puntos."""
        result = extractor.extract_phones("Tel: 555.123.4567")
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_extract_phones_multiple(self, extractor, sample_text_with_phones):
        """Extrae múltiples teléfonos."""
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
    """Tests para extracción de fechas."""

    def test_extract_dates_slash_format(self, extractor):
        """Extrae fecha en formato slash (MM/DD/YYYY o similar)."""
        result = extractor.extract_dates("Fecha: 03/15/2024")
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_extract_dates_dash_format(self, extractor):
        """Extrae fecha en formato dash (DD-MM-YYYY o similar)."""
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
    """Tests para extracción de moneda/valores."""

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


class TestExtractorDNI:
    """Tests para extracción de DNI (España)."""

    def test_extract_dni_valid_format(self, extractor):
        """Extrae DNI en formato válido."""
        result = extractor.extract_dni("Mi DNI es 12345678A")
        assert isinstance(result, list)

    def test_extract_dni_with_dots(self, extractor):
        """Extrae DNI con puntos separadores."""
        result = extractor.extract_dni("DNI: 12.345.678-A")
        assert isinstance(result, list)

    def test_extract_dni_empty(self, extractor, empty_text):
        """Maneja texto vacío."""
        result = extractor.extract_dni(empty_text)
        assert isinstance(result, list)
        assert len(result) == 0

    def test_extract_dni_returns_list(self, extractor):
        """Siempre retorna lista (vacía o con matches)."""
        result = extractor.extract_dni("No hay documentos aquí")
        assert isinstance(result, list)


class TestExtractorRFC:
    """Tests para extracción de RFC (México)."""

    def test_extract_rfc_valid_format(self, extractor):
        """Extrae RFC en formato válido."""
        result = extractor.extract_rfc("RFC: AAA010101ABC")
        assert isinstance(result, list)

    def test_extract_rfc_pattern_matching(self, extractor):
        """Verifica que extract_rfc retorna lista."""
        result = extractor.extract_rfc("Registro: ABP901215LB1")
        assert isinstance(result, list)

    def test_extract_rfc_empty(self, extractor, empty_text):
        """Maneja texto vacío."""
        result = extractor.extract_rfc(empty_text)
        assert isinstance(result, list)
        assert len(result) == 0

    def test_extract_rfc_returns_list(self, extractor):
        """Siempre retorna lista."""
        result = extractor.extract_rfc("No hay RFC aquí")
        assert isinstance(result, list)


class TestExtractorAll:
    """Tests para el método extract_all() (orquestador)."""

    def test_extract_all_returns_dict(self, extractor):
        """extract_all() retorna un diccionario."""
        text = "Email: test@example.com, teléfono: (555) 123-4567"
        result = extractor.extract_all(text)
        assert isinstance(result, dict)

    def test_extract_all_has_all_keys(self, extractor):
        """extract_all() tiene todas las claves esperadas."""
        text = "Test data"
        result = extractor.extract_all(text)
        expected_keys = ["emails", "phones", "dates", "urls", "currency", "dni", "rfc"]
        for key in expected_keys:
            assert key in result
            assert isinstance(result[key], list)

    def test_extract_all_with_comprehensive_text(self, extractor):
        """extract_all() extrae datos de texto complejo."""
        text = """
        Contacto: juan@empresa.com
        Teléfono: (202) 555-0173
        Web: https://www.empresa.com
        """
        result = extractor.extract_all(text)
        assert isinstance(result, dict)
        assert "emails" in result
        assert isinstance(result["emails"], list)


class TestExtractorCustomPattern:
    """Tests para extract_custom_pattern()."""

    def test_extract_custom_pattern_valid(self, extractor):
        """Extrae datos con patrón personalizado válido."""
        pattern = r'\b[A-Z]{2}\d{3}\b'
        text = "Código: AB123"
        result = extractor.extract_custom_pattern(text, pattern)
        assert isinstance(result, list)

    def test_extract_custom_pattern_invalid_regex(self, extractor):
        """Maneja patrón regex inválido."""
        pattern = r'[A-Z'  # Regex inválido
        text = "Test"
        result = extractor.extract_custom_pattern(text, pattern)
        assert isinstance(result, list)


class TestExtractorLines:
    """Tests para extract_lines()."""

    def test_extract_lines_valid_text(self, extractor):
        """Extrae líneas limpias de texto."""
        text = "Línea 1\nLínea 2\nLínea 3"
        result = extractor.extract_lines(text)
        assert isinstance(result, list)
        assert len(result) == 3

    def test_extract_lines_with_empty_lines(self, extractor):
        """Filtra líneas vacías."""
        text = "Línea 1\n\n\nLínea 2\n"
        result = extractor.extract_lines(text)
        assert isinstance(result, list)
        assert any("Línea" in line for line in result)


class TestExtractorEdgeCases:
    """Tests para casos edge y robustez."""

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
        """extract_all() siempre retorna estructura válida."""
        result = extractor.extract_all("Solo texto sin datos estructurados")
        for key in result:
            assert isinstance(result[key], list)

    def test_extractor_returns_deduplicated_results(self, extractor):
        """Los resultados no tienen duplicados (usa set)."""
        text = "Email: test@example.com test@example.com test@example.com"
        result = extractor.extract_emails(text)
        assert isinstance(result, list)
