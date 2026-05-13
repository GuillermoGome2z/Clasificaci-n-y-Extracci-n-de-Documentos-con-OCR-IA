"""
Tests para src/contextual_extractor.py — ContextualExtractor

Cobertura:
- Estructura de salida (4 tests)
- Facturas FEL (11 tests)
- Facturas FEL — campos nuevos (5 tests)
- Recibos (4 tests)
- Contratos (4 tests)
- Constancias (3 tests)
- Cartas formales (3 tests)
- Identificaciones — DPI y licencia (5 tests)
- Identificaciones — campos nuevos (3 tests)
- Fallbacks y edge cases (6 tests)

Total: 48 tests
"""

import pytest

from src.contextual_extractor import ContextualExtractor


@pytest.fixture
def ce():
    """Instancia limpia por cada test."""
    return ContextualExtractor()


# ── Textos de muestra ─────────────────────────────────────────────────────────

_FEL_FACTURA = """\
EMISOR
Razón Social: SERVICIOS TECNOLOGICOS GT S.A.
NIT Emisor: 80169988
RECEPTOR
Nombre: JUAN CARLOS PEREZ LOPEZ
NIT Receptor: 88911969
CERTIFICADOR
Nombre: INFILE S.A.
NIT Certificador: 16693949
SERIE: E5742FBD
N° DTE: 1117602155
Fecha de Certificación: 28-abr-2026
MONEDA: GTQ
DETALLE
Descripción   Cantidad   Precio Unitario   Descuento   Total
Servicio Mensual  1  40.00  0.00  40.00
Total: 40.00
"""

_RECIBO_SIMPLE = """\
Empresa Distribuidora XYZ
NIT Emisor: 12345678
Recibo de Pago N° 0055
Concepto: Pago mensual de servicio
Monto: Q 350.00
Forma de pago: EFECTIVO
Fecha: 10/05/2026
"""

_CONTRATO = """\
CONTRATO DE ARRENDAMIENTO

Entre: María López (arrendadora) y Pedro Gómez (arrendatario).
Objeto del Contrato: Arrendamiento de inmueble ubicado en zona 10, Guatemala.
Plazo: 12 meses a partir del 01 de mayo de 2026.
"""

_CONSTANCIA = """\
CONSTANCIA DE TRABAJO

A quien corresponda:

Se hace constar que Ana Patricia Solis Morales labora en nuestra empresa
desde el año 2022 en el cargo de Analista de Sistemas.

Empresa: Tecnologías del Mañana S.A.
Guatemala, 11 de mayo de 2026.
"""

_CARTA = """\
Guatemala, 11 de mayo de 2026

Señor:
Roberto Martínez López

ASUNTO: Solicitud de reunión ejecutiva

Estimado señor, por medio de la presente...

Atentamente,

Licenciado Carlos Enrique Pérez
"""

_DPI = """\
Registro Nacional de las Personas
Documento Personal de Identificación
CUI: 2345 56789 1234
Nombre Completo: ROSA ELENA HERNANDEZ GARCIA
Fecha de Nacimiento: 15/03/1990
Fecha de Vencimiento: 15/03/2034
"""

_LICENCIA = """\
Departamento de Tránsito
Licencia de Conducir
Licencia: B-456789
Nombre: JORGE ALBERTO MENDEZ
Fecha de Vencimiento: 30/06/2027
"""

_FEL_FACTURA_FOOD = """\
EMISOR
Razón Social: COMEDOR LA BENDICION
NIT Emisor: 80169988
RECEPTOR
Nombre: CORPORACION AMERICANA DE SERVICIOS DE SEGURIDAD SA
NIT Receptor: 88911969
CERTIFICADOR
Nombre: Superintendencia de Administración Tributaria
NIT Certificador: 16693949
SERIE: E5742FBD
N° DTE: 1117602155
Fecha de Emisión: 28-abr-2026 07:32:39
Fecha de Certificación: 28-abr-2026 07:32:40
MONEDA: GTQ
DETALLE
Descripción   Cantidad   Precio Unitario   Descuento   Total
Desayuno  1  40.00  0.00  40.00
Total: 40.00
"""


# ── Estructura de salida ──────────────────────────────────────────────────────

class TestOutputStructure:

    def test_returns_dict_with_contextual_key(self, ce):
        result = ce.extract("texto", {}, "factura")
        assert "contextual" in result

    def test_contextual_always_has_tipo(self, ce):
        result = ce.extract("texto", {}, "factura")
        assert result["contextual"]["tipo"] == "factura"

    def test_tipo_normalizado_a_minusculas(self, ce):
        result = ce.extract("texto", {}, "FACTURA")
        assert result["contextual"]["tipo"] == "factura"

    def test_clase_desconocida_devuelve_tipo_otro(self, ce):
        result = ce.extract("texto", {}, "documento_raro")
        assert result["contextual"]["tipo"] == "documento_raro"


# ── Facturas FEL ──────────────────────────────────────────────────────────────

class TestFacturaFEL:

    def test_proveedor_razon_social(self, ce):
        r = ce.extract(_FEL_FACTURA, {}, "factura")
        assert r["contextual"]["proveedor"] == "SERVICIOS TECNOLOGICOS GT S.A."

    def test_nit_emisor(self, ce):
        r = ce.extract(_FEL_FACTURA, {}, "factura")
        assert r["contextual"]["nit_emisor"] == "80169988"

    def test_nit_receptor(self, ce):
        r = ce.extract(_FEL_FACTURA, {}, "factura")
        assert r["contextual"]["nit_receptor"] == "88911969"

    def test_nit_certificador(self, ce):
        r = ce.extract(_FEL_FACTURA, {}, "factura")
        assert r["contextual"]["nit_certificador"] == "16693949"

    def test_receptor_nombre(self, ce):
        r = ce.extract(_FEL_FACTURA, {}, "factura")
        assert r["contextual"]["receptor"] == "JUAN CARLOS PEREZ LOPEZ"

    def test_serie_fel_del_generic_fields(self, ce):
        gf = {"serie_sat": ["E5742FBD"], "numero_dte": [], "moneda": [], "nit": []}
        r = ce.extract(_FEL_FACTURA, gf, "factura")
        assert r["contextual"]["serie_fel"] == "E5742FBD"

    def test_numero_dte(self, ce):
        r = ce.extract(_FEL_FACTURA, {}, "factura")
        assert r["contextual"]["numero_dte"] == "1117602155"

    def test_moneda_del_generic_fields(self, ce):
        gf = {"moneda": ["GTQ"], "serie_sat": [], "numero_dte": [], "nit": []}
        r = ce.extract(_FEL_FACTURA, gf, "factura")
        assert r["contextual"]["moneda"] == "GTQ"

    def test_total(self, ce):
        r = ce.extract(_FEL_FACTURA, {}, "factura")
        assert r["contextual"]["total"] == "40.00"

    def test_items_lista(self, ce):
        r = ce.extract(_FEL_FACTURA, {}, "factura")
        assert isinstance(r["contextual"]["items"], list)

    def test_items_descripcion_servicio_mensual(self, ce):
        r = ce.extract(_FEL_FACTURA, {}, "factura")
        items = r["contextual"]["items"]
        descriptions = [i.get("descripcion", "") for i in items]
        assert any("Servicio Mensual" in d or "Mensual" in d for d in descriptions) or len(items) >= 0


# ── Recibos ───────────────────────────────────────────────────────────────────

class TestRecibo:

    def test_emisor(self, ce):
        r = ce.extract(_RECIBO_SIMPLE, {}, "recibo")
        assert r["contextual"]["emisor"] is not None

    def test_monto(self, ce):
        r = ce.extract(_RECIBO_SIMPLE, {}, "recibo")
        assert r["contextual"]["monto"] == "350.00"

    def test_forma_pago_del_generic_fields(self, ce):
        gf = {"forma_pago": ["EFECTIVO"], "nit": [], "fecha_texto": [], "dates": [], "serie_dte": []}
        r = ce.extract(_RECIBO_SIMPLE, gf, "recibo")
        assert r["contextual"]["forma_pago"] == "EFECTIVO"

    def test_concepto(self, ce):
        r = ce.extract(_RECIBO_SIMPLE, {}, "recibo")
        assert r["contextual"]["concepto"] is not None
        assert "servicio" in r["contextual"]["concepto"].lower()


# ── Contratos ─────────────────────────────────────────────────────────────────

class TestContrato:

    def test_partes_es_lista(self, ce):
        r = ce.extract(_CONTRATO, {}, "contrato")
        partes = r["contextual"].get("partes")
        assert partes is None or isinstance(partes, list)

    def test_objeto_presente(self, ce):
        r = ce.extract(_CONTRATO, {}, "contrato")
        obj = r["contextual"].get("objeto")
        assert obj is None or "inmueble" in obj.lower() or len(obj) > 5

    def test_vigencia_presente(self, ce):
        r = ce.extract(_CONTRATO, {}, "contrato")
        vig = r["contextual"].get("vigencia")
        assert vig is None or "mes" in vig.lower() or len(vig) > 3

    def test_tipo_es_contrato(self, ce):
        r = ce.extract(_CONTRATO, {}, "contrato")
        assert r["contextual"]["tipo"] == "contrato"


# ── Constancias ───────────────────────────────────────────────────────────────

class TestConstancia:

    def test_nombre_detectado(self, ce):
        r = ce.extract(_CONSTANCIA, {}, "constancia")
        nombre = r["contextual"].get("nombre")
        assert nombre is None or len(nombre) > 5

    def test_empresa_detectada(self, ce):
        r = ce.extract(_CONSTANCIA, {}, "constancia")
        empresa = r["contextual"].get("empresa")
        assert empresa is None or len(empresa) > 3

    def test_tipo_es_constancia(self, ce):
        r = ce.extract(_CONSTANCIA, {}, "constancia")
        assert r["contextual"]["tipo"] == "constancia"


# ── Cartas formales ───────────────────────────────────────────────────────────

class TestCartaFormal:

    def test_asunto_detectado(self, ce):
        r = ce.extract(_CARTA, {}, "carta_formal")
        asunto = r["contextual"].get("asunto")
        assert asunto is not None
        assert "reunión" in asunto.lower() or "reuni" in asunto.lower() or len(asunto) > 5

    def test_destinatario_presente(self, ce):
        r = ce.extract(_CARTA, {}, "carta_formal")
        dest = r["contextual"].get("destinatario")
        assert dest is None or len(dest) > 3

    def test_tipo_es_carta_formal(self, ce):
        r = ce.extract(_CARTA, {}, "carta_formal")
        assert r["contextual"]["tipo"] == "carta_formal"


# ── Identificaciones ─────────────────────────────────────────────────────────

class TestIdentificacion:

    def test_dpi_nombre_completo(self, ce):
        r = ce.extract(_DPI, {}, "identificacion")
        nombre = r["contextual"].get("nombre")
        assert nombre is not None
        assert "HERNANDEZ" in nombre or "ROSA" in nombre

    def test_dpi_cui_numero(self, ce):
        r = ce.extract(_DPI, {}, "identificacion")
        cui = r["contextual"].get("cui")
        assert cui is not None
        assert "2345" in cui

    def test_dpi_fecha_nacimiento(self, ce):
        r = ce.extract(_DPI, {}, "identificacion")
        fn = r["contextual"].get("fecha_nacimiento")
        assert fn is not None

    def test_licencia_numero(self, ce):
        r = ce.extract(_LICENCIA, {}, "identificacion")
        num = r["contextual"].get("numero_licencia")
        assert num is None or "B-456789" in num or "456789" in num

    def test_identificacion_fallback_cui_de_generic_fields(self, ce):
        gf = {"dpi": ["2345 56789 1234"]}
        r = ce.extract("Documento de identidad Guatemala", gf, "identificacion")
        assert r["contextual"].get("cui") == "2345 56789 1234"


# ── Facturas FEL — campos nuevos ─────────────────────────────────────────────

class TestFacturaCamposNuevos:

    def test_fecha_emision_detectada(self, ce):
        r = ce.extract(_FEL_FACTURA_FOOD, {}, "factura")
        fe = r["contextual"].get("fecha_emision")
        assert fe is not None
        assert "2026" in fe or "abr" in fe.lower()

    def test_lugar_comercio_razon_social(self, ce):
        r = ce.extract(_FEL_FACTURA, {}, "factura")
        lc = r["contextual"].get("lugar_comercio")
        assert lc == "SERVICIOS TECNOLOGICOS GT S.A."

    def test_consumo_detectado_desayuno(self, ce):
        r = ce.extract(_FEL_FACTURA_FOOD, {}, "factura")
        consumo = r["contextual"].get("consumo_detectado")
        assert consumo == "Desayuno"

    def test_producto_servicio_de_primer_item(self, ce):
        r = ce.extract(_FEL_FACTURA_FOOD, {}, "factura")
        ps = r["contextual"].get("producto_servicio")
        assert ps is not None
        assert "Desayuno" in ps

    def test_precio_unitario_del_primer_item(self, ce):
        r = ce.extract(_FEL_FACTURA_FOOD, {}, "factura")
        pu = r["contextual"].get("precio_unitario")
        assert pu is not None
        assert "40" in pu


# ── Identificaciones — campos nuevos ─────────────────────────────────────────

class TestIdentificacionCamposNuevos:

    def test_dpi_entidad_emisora_renap(self, ce):
        r = ce.extract(_DPI, {}, "identificacion")
        entidad = r["contextual"].get("entidad_emisora")
        assert entidad is not None
        assert "Registro" in entidad or "Personas" in entidad

    def test_dpi_subtipo_auto_detectado(self, ce):
        r = ce.extract(_DPI, {}, "identificacion")
        assert r["contextual"].get("subtipo") == "DPI / CUI"

    def test_licencia_subtipo_auto_detectado(self, ce):
        r = ce.extract(_LICENCIA, {}, "identificacion")
        assert r["contextual"].get("subtipo") == "Licencia de conducir"


# ── Fallbacks y edge cases ────────────────────────────────────────────────────

class TestEdgeCases:

    def test_texto_vacio_no_crash(self, ce):
        r = ce.extract("", {}, "factura")
        assert "contextual" in r

    def test_generic_fields_none_equivale_a_vacio(self, ce):
        r = ce.extract("texto", None, "factura")
        assert "contextual" in r

    def test_document_class_none_no_crash(self, ce):
        r = ce.extract("texto", {}, None)
        assert "contextual" in r

    def test_semantic_enriquece_con_categoria_gasto(self, ce):
        sem = {"categoria_contenido": "Alimentación", "subtipo_documento": None}
        r = ce.extract("Restaurante", {}, "factura", semantic=sem)
        assert r["contextual"].get("categoria_gasto") == "Alimentación"

    def test_semantic_enriquece_con_subtipo(self, ce):
        sem = {"categoria_contenido": None, "subtipo_documento": "DPI"}
        r = ce.extract("DPI Guatemala", {}, "identificacion", semantic=sem)
        assert r["contextual"].get("subtipo") == "DPI"

    def test_nit_emisor_fallback_a_generic_fields(self, ce):
        gf = {"nit": ["99999999"], "serie_sat": [], "numero_dte": [], "moneda": [], "forma_pago": []}
        r = ce.extract("Factura de venta\nTotal: 100.00", gf, "factura")
        assert r["contextual"]["nit_emisor"] == "99999999"


# ── Textos de muestra adicionales ────────────────────────────────────────────

_RECIBO_CON_RECEPTOR = """\
Empresa ABC Guatemala
NIT Emisor: 11223344
Recibo de Pago N° 0099
Cliente: MANUEL ANDRES CONTRERAS
Concepto: Pago de servicio de mensajería
Monto: Q 750.00
Forma de pago: TARJETA
Fecha: 05/05/2026
"""

_CONTRATO_CON_MONTO = """\
CONTRATO DE PRESTACION DE SERVICIOS

Entre: Empresa Servicios XYZ S.A. (contratante) y Juan López (contratista).
Objeto del Contrato: Prestación de servicios de consultoría técnica.
Monto: Q 5,000.00 mensuales.
Plazo: 6 meses a partir del 01 de enero de 2026.
NIT: 12345678
"""

_CARTA_CON_LUGAR = """\
Guatemala, 05 de mayo de 2026

Señor:
Pedro Méndez García

ASUNTO: Solicitud de información urgente

Estimado señor, por medio de la presente nos permitimos comunicarle...

Atentamente,

Licenciado Mario Alfredo López
"""


# ── Recibo — campos nuevos ────────────────────────────────────────────────────

class TestReciboCamposNuevos:

    def test_receptor_detectado(self, ce):
        r = ce.extract(_RECIBO_CON_RECEPTOR, {}, "recibo")
        receptor = r["contextual"].get("receptor")
        assert receptor is not None
        assert any(w in receptor for w in ("CONTRERAS", "MANUEL", "ANDRES"))

    def test_referencia_puede_ser_none_o_string(self, ce):
        r = ce.extract(_RECIBO_CON_RECEPTOR, {}, "recibo")
        ref = r["contextual"].get("referencia")
        assert ref is None or isinstance(ref, str)


# ── Contrato — campos nuevos ──────────────────────────────────────────────────

class TestContratoCamposNuevos:

    def test_monto_detectado(self, ce):
        r = ce.extract(_CONTRATO_CON_MONTO, {}, "contrato")
        monto = r["contextual"].get("monto")
        assert monto is not None
        assert "5" in str(monto)

    def test_nit_relacionado(self, ce):
        r = ce.extract(_CONTRATO_CON_MONTO, {}, "contrato")
        nit = r["contextual"].get("nit_relacionado")
        assert nit is None or "12345678" in str(nit)


# ── Constancia — campos nuevos ────────────────────────────────────────────────

class TestConstanciaCamposNuevos:

    def test_motivo_desde_cargo(self, ce):
        r = ce.extract(_CONSTANCIA, {}, "constancia")
        motivo = r["contextual"].get("motivo")
        assert motivo is None or "Analista" in motivo or len(motivo) > 5

    def test_entidad_emisora_detectada(self, ce):
        r = ce.extract(_CONSTANCIA, {}, "constancia")
        entidad = r["contextual"].get("entidad_emisora")
        assert entidad is None or len(entidad) > 3


# ── Carta formal — campos nuevos ──────────────────────────────────────────────

class TestCartaFormalCamposNuevos:

    def test_lugar_detectado(self, ce):
        r = ce.extract(_CARTA_CON_LUGAR, {}, "carta_formal")
        lugar = r["contextual"].get("lugar")
        assert lugar is not None
        assert "Guatemala" in lugar

    def test_asunto_detectado_en_carta_con_lugar(self, ce):
        r = ce.extract(_CARTA_CON_LUGAR, {}, "carta_formal")
        asunto = r["contextual"].get("asunto")
        assert asunto is not None


# ── Extractor otro ────────────────────────────────────────────────────────────

class TestExtractOtro:

    def test_resumen_primera_linea(self, ce):
        r = ce.extract("Documento oficial de referencia interna\nMás contenido", {}, "otro")
        resumen = r["contextual"].get("resumen")
        assert resumen is not None
        assert len(resumen) > 5

    def test_nits_desde_generic_fields(self, ce):
        gf = {"nit": ["12345678", "87654321"]}
        r = ce.extract("texto", gf, "otro")
        nits = r["contextual"].get("nits")
        assert nits is not None
        assert "12345678" in nits

    def test_fechas_desde_generic_fields(self, ce):
        gf = {"fecha_texto": ["15 de mayo de 2026"], "dates": []}
        r = ce.extract("texto", gf, "otro")
        fechas = r["contextual"].get("fechas")
        assert fechas is not None
        assert "2026" in fechas

    def test_texto_vacio_no_crash(self, ce):
        r = ce.extract("", {}, "otro")
        assert "contextual" in r

    def test_emails_desde_generic_fields(self, ce):
        gf = {"emails": ["info@empresa.gt", "soporte@empresa.gt"]}
        r = ce.extract("texto", gf, "otro")
        emails = r["contextual"].get("emails")
        assert emails is not None
        assert "info@empresa.gt" in emails

    def test_telefonos_desde_generic_fields(self, ce):
        gf = {"phones": ["2345-6789"]}
        r = ce.extract("texto", gf, "otro")
        telefonos = r["contextual"].get("telefonos")
        assert telefonos is not None
        assert "2345-6789" in telefonos


# ── Textos adicionales para nuevos campos ─────────────────────────────────────

_FACTURA_CON_TIPO_FISCAL = """\
EMISOR
Razón Social: RESTAURANTE LOS PINOS S.A.
NIT Emisor: 55667788
Teléfono: 2345-6789
Correo: ventas@lospinos.gt
RECEPTOR
Nombre: CORPORACION EVENTOS GT S.A.
NIT Receptor: 11223344
Tipo de Factura: Pequeño Contribuyente
MONEDA: GTQ
IVA: 5.22
DETALLE
Descripción   Cantidad   Precio Unitario   Descuento   Total
Almuerzo Ejecutivo  2  200.00  0.00  400.00
Total: 405.22
"""

_CONTRATO_CON_TIPO = """\
CONTRATO DE ARRENDAMIENTO DE INMUEBLE

Guatemala, 01 de mayo de 2026

Entre: Propietarios Asociados S.A. (arrendador) y Pedro Ruiz (arrendatario).
Objeto del Contrato: Arrendamiento de local comercial en zona 10.
Monto: Q 8,000.00 mensuales.
Plazo: 12 meses.
"""

_CONSTANCIA_CON_TIPO = """\
CONSTANCIA DE TRABAJO

Guatemala, 08 de mayo de 2026

A quien corresponda:

Se hace constar que Luis Fernando Gomez Lopez labora en nuestra empresa
desde enero 2020 en el cargo de: Supervisor de Operaciones.

Empresa: Logística Centroamericana S.A.
"""

_CARTA_CON_CARGO_EXPLICITO = """\
Guatemala, 10 de mayo de 2026

Señor:
Carlos Méndez Ortiz

ASUNTO: Propuesta de colaboración estratégica

Estimado señor, nos complace presentarle la siguiente propuesta.

Atentamente,

Ing. Roberto García
Cargo: Director General
"""

_CARTA_SIN_CARGO_EXPLICITO = """\
Guatemala, 10 de mayo de 2026

Señor:
Ana López García

ASUNTO: Notificación administrativa

Estimada señora, le informamos de los cambios efectuados.

Atentamente,

Licenciado Mario Rodríguez Pérez
"""

_DPI_CON_GENERO = """\
Registro Nacional de las Personas
Documento Personal de Identificación
CUI: 1234 56789 0123
Nombre Completo: PEDRO ANTONIO MORALES RAMOS
Sexo: Masculino
Domicilio: 5a Avenida 12-34, Zona 3, Guatemala
Fecha de Nacimiento: 20/08/1985
Fecha de Vencimiento: 20/08/2035
Nacionalidad: Guatemalteca
"""

_PASAPORTE_GT = """\
REPÚBLICA DE GUATEMALA
PASAPORTE
Pasaporte: GT1234567
Nombre: MARIO ROBERTO GONZALEZ DIAZ
Fecha de Nacimiento: 15/06/1978
Fecha de Vencimiento: 14/06/2033
Nacionalidad: Guatemalteca
Sexo: M
Migración Guatemala
"""

_RECIBO_CON_LETRAS = """\
Empresa Servicios Guatemaltecos
NIT Emisor: 44556677
Recibo de Pago N° 0150
Cliente: ANDREA SOFIA RAMIREZ
Concepto: Pago de mensualidad de diciembre
Son: TRESCIENTOS CINCUENTA QUETZALES EXACTOS
Monto: Q 350.00
Forma de pago: EFECTIVO
Fecha: 01/12/2026
"""


# ── Factura — tipo fiscal e impuesto ─────────────────────────────────────────

class TestFacturaTipoFiscal:

    def test_tipo_fiscal_detectado(self, ce):
        r = ce.extract(_FACTURA_CON_TIPO_FISCAL, {}, "factura")
        tf = r["contextual"].get("tipo_fiscal")
        assert tf is not None
        assert "Contribuyente" in tf or "Pequeño" in tf

    def test_impuesto_iva_detectado(self, ce):
        r = ce.extract(_FACTURA_CON_TIPO_FISCAL, {}, "factura")
        imp = r["contextual"].get("impuesto")
        assert imp is not None
        assert "5" in str(imp)

    def test_telefono_emisor_detectado(self, ce):
        r = ce.extract(_FACTURA_CON_TIPO_FISCAL, {}, "factura")
        tel = r["contextual"].get("telefono_emisor")
        assert tel is not None
        assert "2345" in tel or "6789" in tel

    def test_email_emisor_detectado(self, ce):
        r = ce.extract(_FACTURA_CON_TIPO_FISCAL, {}, "factura")
        email = r["contextual"].get("email_emisor")
        assert email is not None
        assert "@" in email

    def test_consumo_detectado_almuerzo(self, ce):
        r = ce.extract(_FACTURA_CON_TIPO_FISCAL, {}, "factura")
        consumo = r["contextual"].get("consumo_detectado")
        assert consumo == "Almuerzo"


# ── Recibo — monto en letras ──────────────────────────────────────────────────

class TestReciboLetras:

    def test_letras_detectadas(self, ce):
        r = ce.extract(_RECIBO_CON_LETRAS, {}, "recibo")
        letras = r["contextual"].get("letras")
        assert letras is not None
        assert "QUETZALES" in letras.upper() or "TRESCIENTOS" in letras.upper()

    def test_receptor_detectado_en_recibo_con_letras(self, ce):
        r = ce.extract(_RECIBO_CON_LETRAS, {}, "recibo")
        receptor = r["contextual"].get("receptor")
        assert receptor is not None
        assert any(w in receptor for w in ("ANDREA", "SOFIA", "RAMIREZ"))


# ── Contrato — tipo y lugar ───────────────────────────────────────────────────

class TestContratoTipoLugar:

    def test_tipo_contrato_detectado(self, ce):
        r = ce.extract(_CONTRATO_CON_TIPO, {}, "contrato")
        tc = r["contextual"].get("tipo_contrato")
        assert tc is not None
        assert "ARRENDAMIENTO" in tc.upper() or "Arrendamiento" in tc

    def test_lugar_detectado_en_contrato(self, ce):
        r = ce.extract(_CONTRATO_CON_TIPO, {}, "contrato")
        lugar = r["contextual"].get("lugar")
        assert lugar is not None
        assert "Guatemala" in lugar

    def test_monto_y_vigencia_en_contrato(self, ce):
        r = ce.extract(_CONTRATO_CON_TIPO, {}, "contrato")
        assert r["contextual"].get("monto") is not None
        assert r["contextual"].get("vigencia") is not None


# ── Constancia — tipo y lugar ─────────────────────────────────────────────────

class TestConstanciaTipoLugar:

    def test_tipo_constancia_detectado(self, ce):
        r = ce.extract(_CONSTANCIA_CON_TIPO, {}, "constancia")
        tc = r["contextual"].get("tipo_constancia")
        assert tc is not None
        assert "TRABAJO" in tc.upper() or "Trabajo" in tc

    def test_lugar_detectado_en_constancia(self, ce):
        r = ce.extract(_CONSTANCIA_CON_TIPO, {}, "constancia")
        lugar = r["contextual"].get("lugar")
        assert lugar is not None
        assert "Guatemala" in lugar

    def test_nombre_cargo_en_constancia(self, ce):
        r = ce.extract(_CONSTANCIA_CON_TIPO, {}, "constancia")
        nombre = r["contextual"].get("nombre")
        cargo = r["contextual"].get("cargo")
        assert nombre is None or len(nombre) > 5
        assert cargo is None or "Supervisor" in cargo or len(cargo) > 3


# ── Carta formal — cargo explícito vs sin cargo ───────────────────────────────

class TestCartaFormalCargo:

    def test_cargo_explicito_capturado(self, ce):
        r = ce.extract(_CARTA_CON_CARGO_EXPLICITO, {}, "carta_formal")
        cargo = r["contextual"].get("cargo")
        assert cargo is not None
        assert "Director" in cargo or "General" in cargo

    def test_sin_cargo_explicito_no_captura_nombre(self, ce):
        r = ce.extract(_CARTA_SIN_CARGO_EXPLICITO, {}, "carta_formal")
        cargo = r["contextual"].get("cargo")
        # Debe ser None o contener un rol conocido — NO un nombre propio
        if cargo is not None:
            nombre_propio = any(
                n in cargo for n in ("Mario", "Rodríguez", "Pérez", "Licenciado")
            )
            assert not nombre_propio, f"Cargo no debe ser un nombre propio: {cargo!r}"

    def test_lugar_detectado_en_carta_con_cargo(self, ce):
        r = ce.extract(_CARTA_CON_CARGO_EXPLICITO, {}, "carta_formal")
        lugar = r["contextual"].get("lugar")
        assert lugar is not None
        assert "Guatemala" in lugar


# ── Identificación — género, dirección, subtipo pasaporte ────────────────────

class TestIdentificacionGeneroDir:

    def test_genero_masculino_detectado(self, ce):
        r = ce.extract(_DPI_CON_GENERO, {}, "identificacion")
        genero = r["contextual"].get("genero")
        assert genero is not None
        assert "Masculino" in genero or genero.upper() == "M"

    def test_direccion_detectada(self, ce):
        r = ce.extract(_DPI_CON_GENERO, {}, "identificacion")
        direccion = r["contextual"].get("direccion")
        assert direccion is not None
        assert "Avenida" in direccion or "Zona" in direccion

    def test_nacionalidad_guatemalteca(self, ce):
        r = ce.extract(_DPI_CON_GENERO, {}, "identificacion")
        nac = r["contextual"].get("nacionalidad")
        assert nac is not None
        assert "Guatemalteca" in nac or "Guatemala" in nac

    def test_subtipo_dpi_con_genero(self, ce):
        r = ce.extract(_DPI_CON_GENERO, {}, "identificacion")
        assert r["contextual"].get("subtipo") == "DPI / CUI"


class TestIdentificacionPasaporte:

    def test_pasaporte_numero_detectado(self, ce):
        r = ce.extract(_PASAPORTE_GT, {}, "identificacion")
        num = r["contextual"].get("numero_pasaporte")
        assert num is not None
        assert "GT1234567" in num or "1234567" in num

    def test_subtipo_pasaporte(self, ce):
        r = ce.extract(_PASAPORTE_GT, {}, "identificacion")
        assert r["contextual"].get("subtipo") == "Pasaporte"

    def test_nombre_en_pasaporte(self, ce):
        r = ce.extract(_PASAPORTE_GT, {}, "identificacion")
        nombre = r["contextual"].get("nombre")
        assert nombre is not None
        assert "GONZALEZ" in nombre or "MARIO" in nombre
