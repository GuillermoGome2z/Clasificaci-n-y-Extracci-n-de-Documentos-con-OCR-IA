"""
Tests para src/semantic_analyzer.py — SemanticAnalyzer

Cobertura:
- Estructura de salida (6 tests)
- Facturas — todas las categorías de gasto (21 tests)
- Identificaciones — todos los subtipos (8 tests)
- Confianza semántica (4 tests)
- Edge cases (12 tests)

Total: 51 tests
"""

import pytest

from src.semantic_analyzer import SemanticAnalyzer

_EXPECTED_KEYS = frozenset({
    "categoria_contenido",
    "descripcion_detectada",
    "subtipo_documento",
    "confianza_semantica",
    "indicadores",
})


@pytest.fixture
def analyzer():
    """Instancia limpia de SemanticAnalyzer por cada test."""
    return SemanticAnalyzer()


# ─────────────────────────────────────────────────────────────────────────────
# Estructura de salida — el dict siempre tiene las 5 claves, sin excepciones
# ─────────────────────────────────────────────────────────────────────────────

class TestOutputStructure:

    def test_keys_for_factura(self, analyzer):
        result = analyzer.analyze("Restaurante El Buen Sabor", document_class="factura")
        assert set(result.keys()) == _EXPECTED_KEYS

    def test_keys_for_identificacion(self, analyzer):
        result = analyzer.analyze("RENAP DPI Guatemala", document_class="identificacion")
        assert set(result.keys()) == _EXPECTED_KEYS

    def test_keys_for_otro(self, analyzer):
        result = analyzer.analyze("texto genérico sin categoría", document_class="otro")
        assert set(result.keys()) == _EXPECTED_KEYS

    def test_keys_for_empty_text(self, analyzer):
        result = analyzer.analyze("", document_class="factura")
        assert set(result.keys()) == _EXPECTED_KEYS

    def test_descripcion_detectada_is_list(self, analyzer):
        result = analyzer.analyze("Restaurante menú desayuno", document_class="factura")
        assert isinstance(result["descripcion_detectada"], list)

    def test_indicadores_is_list(self, analyzer):
        result = analyzer.analyze("Hotel habitacion alojamiento", document_class="factura")
        assert isinstance(result["indicadores"], list)


# ─────────────────────────────────────────────────────────────────────────────
# Facturas — detección de categoría de gasto
# ─────────────────────────────────────────────────────────────────────────────

class TestFacturasCategorias:
    """Una categoria por método; verifica que el clasificador semántico acierta."""

    def test_alimentacion_restaurante(self, analyzer):
        text = "Restaurante El Fogón\nDesayuno típico\nAlmuerzo del día\nTotal Q 85.00"
        result = analyzer.analyze(text, document_class="factura")
        assert result["categoria_contenido"] == "Alimentación"

    def test_alimentacion_cafeteria_menu(self, analyzer):
        text = "Cafetería Central\nMenú del día\nBebida\nPlatillo especial Q50"
        result = analyzer.analyze(text, document_class="factura")
        assert result["categoria_contenido"] == "Alimentación"

    def test_hospedaje_hotel(self, analyzer):
        text = (
            "Hotel Conquistador\nHabitación doble\n"
            "Check-in: 15/05/2026\nCheck-out: 17/05/2026\nTotal Q 650.00"
        )
        result = analyzer.analyze(text, document_class="factura")
        assert result["categoria_contenido"] == "Hospedaje"

    def test_hospedaje_hostal_alojamiento(self, analyzer):
        text = "Hostal Quetzal\nAlojamiento por noche\nHuésped registrado\nQ 200.00"
        result = analyzer.analyze(text, document_class="factura")
        assert result["categoria_contenido"] == "Hospedaje"

    def test_transporte_taxi_traslado(self, analyzer):
        text = "Servicio de Taxi Express\nTraslado del cliente\nRecorrido zona 1 a zona 10\nQ 45.00"
        result = analyzer.analyze(text, document_class="factura")
        assert result["categoria_contenido"] == "Transporte"

    def test_transporte_uber_pasaje(self, analyzer):
        text = "Uber Guatemala\nViaje completado\nPasaje Q 32.50"
        result = analyzer.analyze(text, document_class="factura")
        assert result["categoria_contenido"] == "Transporte"

    def test_combustible_gasolina_litros(self, analyzer):
        text = "Gasolinera La Estrella\nGasolina Super\n15 litros a Q 29.50/galón\nTotal Q 442.50"
        result = analyzer.analyze(text, document_class="factura")
        assert result["categoria_contenido"] == "Combustible"

    def test_combustible_diesel_estacion(self, analyzer):
        text = "Estación de Servicio Nacional\nDiesel\n20 litros\nCombustible Q 580.00"
        result = analyzer.analyze(text, document_class="factura")
        assert result["categoria_contenido"] == "Combustible"

    def test_salud_farmacia_medicamento(self, analyzer):
        text = "Farmacia Cruz Verde\nMedicamento: Amoxicilina 500mg\nReceta médica #2045\nTotal Q 125.00"
        result = analyzer.analyze(text, document_class="factura")
        assert result["categoria_contenido"] == "Salud"

    def test_salud_clinica_doctor(self, analyzer):
        text = "Clínica Médica San Rafael\nConsulta médica\nDoctor García\nQ 350.00"
        result = analyzer.analyze(text, document_class="factura")
        assert result["categoria_contenido"] == "Salud"

    def test_educacion_matricula_inscripcion(self, analyzer):
        text = (
            "Universidad Mariano Gálvez\nMatrícula semestre I-2026\n"
            "Inscripción de estudiante\nQ 2,500.00"
        )
        result = analyzer.analyze(text, document_class="factura")
        assert result["categoria_contenido"] == "Educación"

    def test_educacion_academia_capacitacion(self, analyzer):
        text = "Academia de Idiomas Guatemala\nCapacitación en Inglés\nCurso intensivo\nQ 800.00"
        result = analyzer.analyze(text, document_class="factura")
        assert result["categoria_contenido"] == "Educación"

    def test_servicios_electricidad_enel(self, analyzer):
        text = "ENEL Guatemala\nServicio de electricidad\nEnergía eléctrica consumida\nQ 380.00"
        result = analyzer.analyze(text, document_class="factura")
        assert result["categoria_contenido"] == "Servicios"

    def test_servicios_internet_honorarios(self, analyzer):
        text = (
            "Servicio de Internet\nConexión mensual\n"
            "Honorarios por servicio básico profesional\nQ 250.00"
        )
        result = analyzer.analyze(text, document_class="factura")
        assert result["categoria_contenido"] == "Servicios"

    def test_compras_ferreteria_mercaderia(self, analyzer):
        text = "Ferretería El Clavo\nMercadería: tornillos, clavos\nInventario Q 1,200.00"
        result = analyzer.analyze(text, document_class="factura")
        assert result["categoria_contenido"] == "Compras"

    def test_compras_ropa_calzado(self, analyzer):
        text = "Tienda Fashion\nRopa casual\nCalzado deportivo\nAccesorios Q 450.00"
        result = analyzer.analyze(text, document_class="factura")
        assert result["categoria_contenido"] == "Compras"

    def test_mantenimiento_reparacion_repuesto(self, analyzer):
        text = (
            "Taller Mecánico Rodríguez\nReparación de motor\n"
            "Repuesto original\nServicio técnico Q 1,500.00"
        )
        result = analyzer.analyze(text, document_class="factura")
        assert result["categoria_contenido"] == "Mantenimiento"

    def test_mantenimiento_plomeria(self, analyzer):
        text = "Mantenimiento del hogar\nPlomería y reparación\nInstalación de tubería\nQ 300.00"
        result = analyzer.analyze(text, document_class="factura")
        assert result["categoria_contenido"] == "Mantenimiento"

    def test_no_determinado_texto_sin_keywords(self, analyzer):
        text = "Documento de cobro número 1234\nFecha: 10/05/2026\nTotal: Q 100.00"
        result = analyzer.analyze(text, document_class="factura")
        assert result["categoria_contenido"] == "No determinado"

    def test_subtipo_documento_es_none_para_facturas(self, analyzer):
        text = "Restaurante El Buen Sabor\nDesayuno Q 50.00"
        result = analyzer.analyze(text, document_class="factura")
        assert result["subtipo_documento"] is None

    def test_recibo_usa_reglas_de_factura(self, analyzer):
        """La clase 'recibo' también activa el análisis de categoría de gasto."""
        text = "Recibo de pago\nGasolina Super\n10 litros\nQ 250.00"
        result = analyzer.analyze(text, document_class="recibo")
        assert result["categoria_contenido"] == "Combustible"


# ─────────────────────────────────────────────────────────────────────────────
# Identificaciones — detección de subtipo
# ─────────────────────────────────────────────────────────────────────────────

class TestIdentificacionSubtipos:

    def test_dpi_renap_keywords(self, analyzer):
        text = (
            "Registro Nacional de las Personas\nDPI\n"
            "Documento Personal de Identificación\nCUI: 2345678901234"
        )
        result = analyzer.analyze(text, document_class="identificacion")
        assert result["subtipo_documento"] == "DPI"

    def test_dpi_refuerzo_por_extracted_fields(self, analyzer):
        """Cuando el extractor ya encontró un DPI, se refuerza la señal."""
        text = "Documento de identidad Guatemala"
        ef = {"dpi": ["2345 56789 1234"]}
        result = analyzer.analyze(text, extracted_fields=ef, document_class="identificacion")
        assert result["subtipo_documento"] == "DPI"

    def test_licencia_conducir_keywords(self, analyzer):
        text = (
            "Licencia de Conducir\nDepartamento de Tránsito\n"
            "Categoría B\nMotorista"
        )
        result = analyzer.analyze(text, document_class="identificacion")
        assert result["subtipo_documento"] == "Licencia de conducir"

    def test_licencia_conducir_motorista(self, analyzer):
        text = "Licencia de Manejo\nCategoría de Licencia: B\nMotorista Guatemala"
        result = analyzer.analyze(text, document_class="identificacion")
        assert result["subtipo_documento"] == "Licencia de conducir"

    def test_pasaporte_keywords(self, analyzer):
        text = (
            "PASAPORTE\nRepública de Guatemala\n"
            "Ministerio de Relaciones Exteriores\nDocumento de Viaje"
        )
        result = analyzer.analyze(text, document_class="identificacion")
        assert result["subtipo_documento"] == "Pasaporte"

    def test_carne_universitario(self, analyzer):
        text = (
            "Universidad de San Carlos\nCarné Universitario\n"
            "Número de Estudiante\nCredencial de identificación"
        )
        result = analyzer.analyze(text, document_class="identificacion")
        assert result["subtipo_documento"] == "Carné"

    def test_carne_empleado(self, analyzer):
        text = "Empresa XYZ\nCarné de Trabajo\nNúmero de Empleado: 00123\nCredencial"
        result = analyzer.analyze(text, document_class="identificacion")
        assert result["subtipo_documento"] == "Carné"

    def test_no_determinado_identificacion_sin_keywords(self, analyzer):
        text = "Número: 12345\nFecha de emisión: 01/01/2020"
        result = analyzer.analyze(text, document_class="identificacion")
        assert result["subtipo_documento"] == "No determinado"

    def test_categoria_contenido_es_none_para_identificacion(self, analyzer):
        text = "RENAP DPI Guatemala"
        result = analyzer.analyze(text, document_class="identificacion")
        assert result["categoria_contenido"] is None


# ─────────────────────────────────────────────────────────────────────────────
# Confianza semántica
# ─────────────────────────────────────────────────────────────────────────────

class TestConfianza:

    def test_confianza_alta_multiples_keywords(self, analyzer):
        text = (
            "Restaurante Familiar\nDesayuno completo\nAlmuerzo ejecutivo\n"
            "Cena especial\nMenú variado\nPlatillo del día\nBebida incluida"
        )
        result = analyzer.analyze(text, document_class="factura")
        assert result["confianza_semantica"] == "alta"

    def test_confianza_media_o_alta_dos_keywords_fuertes(self, analyzer):
        """Dos keywords de peso 2 = score 4 → alta; una sola = media."""
        text = "Gasolinera Central\nDiesel Q 250.00"
        result = analyzer.analyze(text, document_class="factura")
        assert result["confianza_semantica"] in ("media", "alta")

    def test_confianza_baja_un_keyword_peso1(self, analyzer):
        """Una sola keyword de peso 1 debe devolver confianza 'baja'."""
        text = "Descripción: viaje de trabajo\nTotal Q 100.00"
        result = analyzer.analyze(text, document_class="factura")
        assert result["confianza_semantica"] == "baja"

    def test_confianza_no_determinado_sin_match(self, analyzer):
        text = "Cobro número 1234\nTotal Q 50.00"
        result = analyzer.analyze(text, document_class="factura")
        assert result["confianza_semantica"] == "no_determinado"


# ─────────────────────────────────────────────────────────────────────────────
# Edge cases — robustez ante entradas inesperadas
# ─────────────────────────────────────────────────────────────────────────────

class TestEdgeCases:

    def test_texto_vacio_factura_retorna_no_determinado(self, analyzer):
        result = analyzer.analyze("", document_class="factura")
        assert result["categoria_contenido"] == "No determinado"
        assert result["confianza_semantica"] == "no_determinado"

    def test_texto_vacio_identificacion_retorna_no_determinado(self, analyzer):
        result = analyzer.analyze("", document_class="identificacion")
        assert result["subtipo_documento"] == "No determinado"

    def test_texto_solo_espacios(self, analyzer):
        result = analyzer.analyze("   \n\t  ", document_class="factura")
        assert result["categoria_contenido"] == "No determinado"

    def test_clase_otro_no_produce_categoria(self, analyzer):
        result = analyzer.analyze("Restaurante comida desayuno", document_class="otro")
        assert result["categoria_contenido"] is None
        assert result["subtipo_documento"] is None

    def test_clase_contrato_no_aplica(self, analyzer):
        result = analyzer.analyze("Contrato de arrendamiento", document_class="contrato")
        assert result["categoria_contenido"] is None

    def test_clase_carta_formal_no_aplica(self, analyzer):
        result = analyzer.analyze("Estimado señor, por medio de la presente...", document_class="carta_formal")
        assert result["categoria_contenido"] is None

    def test_clase_constancia_no_aplica(self, analyzer):
        result = analyzer.analyze("Constancia de trabajo del empleado", document_class="constancia")
        assert result["categoria_contenido"] is None

    def test_extracted_fields_none_no_crash(self, analyzer):
        result = analyzer.analyze("RENAP DPI Guatemala", extracted_fields=None, document_class="identificacion")
        assert result["subtipo_documento"] is not None

    def test_document_class_none_no_crash(self, analyzer):
        result = analyzer.analyze("texto cualquiera", document_class=None)  # type: ignore[arg-type]
        assert result["categoria_contenido"] is None

    def test_acentos_en_texto_no_impiden_deteccion(self, analyzer):
        """El normalizador elimina acentos antes de comparar."""
        text = "Farmacia Médica\nMedicamento recetado\nClínica privada"
        result = analyzer.analyze(text, document_class="factura")
        assert result["categoria_contenido"] == "Salud"

    def test_mayusculas_no_impiden_deteccion(self, analyzer):
        """La normalización convierte a minúsculas."""
        text = "HOTEL PLAZA\nHABITACION DOBLE\nALOJAMIENTO NOCTURNO"
        result = analyzer.analyze(text, document_class="factura")
        assert result["categoria_contenido"] == "Hospedaje"

    def test_descripcion_detectada_max_cinco(self, analyzer):
        """descripcion_detectada nunca supera los 5 elementos."""
        text = (
            "Restaurante El Buen Sabor\nDesayuno completo\nAlmuerzo ejecutivo\n"
            "Cena especial\nMenú variado\nPlatillo del día\nBebida\nCafetería"
        )
        result = analyzer.analyze(text, document_class="factura")
        assert len(result["descripcion_detectada"]) <= 5
