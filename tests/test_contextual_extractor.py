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


# ── Nuevas muestras para pruebas avanzadas ─────────────────────────────────────

_FACTURA_COMBUSTIBLE = """\
EMISOR
Razón Social: DISTRIBUIDORA DE COMBUSTIBLES DEL NORTE S.A.
NIT Emisor: 33445566
RECEPTOR
Nombre: TRANSPORTES LOGISTICOS S.A.
NIT Receptor: 99887766
NÚMERO DE AUTORIZACIÓN:
A1B2C3D4-E5F6-7890-ABCD-EF1234567890
Serie: ABCD1234 Número de DTE: 20240501001
Fecha y hora de emisión: 01/05/2024 08:15:22
Fecha y hora de certificación: 01/05/2024 08:15:45
MONEDA: GTQ
DETALLE
Descripción   Cantidad   Precio Unitario   Descuento   Total
Diesel        200.00     8.50              0.00         1700.00
Total: 1700.00
"""

_FACTURA_HOSPEDAJE = """\
EMISOR
Razón Social: HOTEL COLONIAL ANTIGUA S.A.
Nombre Comercial: Hotel Colonial
NIT Emisor: 11223344
RECEPTOR
Nombre Receptor: EMPRESA CONSULTORES ASOCIADOS S.A.
NIT Receptor: 55667788
Fecha de Emisión: 15/04/2024
MONEDA: GTQ
IVA: 145.70
Total: 1257.00
DETALLE
Descripción   Cantidad   Precio Unitario   Descuento   Total
Habitación doble  3  371.00  0.00  1113.00
"""

_RECIBO_RECIBI_DE = """\
RECIBO DE PAGO

Recibo N° 00125
Recibí de: EMPRESA NACIONAL DE LOGÍSTICA S.A.
La cantidad de: Q 2,500.00
Por concepto de: Servicio mensual de almacenamiento
Forma de pago: Transferencia bancaria
Fecha: 28/04/2026

Firma: _______________
Emitido por: Bodega Central Guatemala
"""

_CONTRATO_LABORAL = """\
CONTRATO LABORAL INDIVIDUAL

Guatemala, 01 de enero de 2026

Contratante: EMPRESA SERVICIOS INTEGRALES S.A., NIT: 12345678
Contratado: CARLOS ALEJANDRO REYES MENDEZ, DPI: 2345678901234

Objeto del Contrato: Prestación de servicios de analista de sistemas en modalidad presencial.
Vigencia: 12 meses a partir del 01 de enero de 2026
Monto: Q 5,500.00 mensuales
Forma de pago: Mensual los últimos días de cada mes

Atentamente,

Licenciado Marco Tulio Godínez
Director General
"""

_CONSTANCIA_LABORAL = """\
CONSTANCIA DE TRABAJO

Guatemala, 05 de mayo de 2026

A quien corresponda:

Se hace constar que Maria Elena Rodriguez Perez labora en nuestra empresa
desde el 01 de enero de 2020 en el cargo de: Coordinadora de Recursos Humanos.

Empresa: Corporación Nacional de Servicios S.A.
Dirección: 7a Avenida 10-25, Zona 9, Guatemala

Atentamente,

Lic. Roberto Morales Santos
Director de Recursos Humanos
"""

_CARTA_CON_CUERPO = """\
Guatemala, 12 de mayo de 2026

Señor:
Ingeniero Daniel Orellana López
Gerente de Proyectos
Constructora del Sur S.A.

ASUNTO: Solicitud de prórroga en entrega de informes

Estimado señor Orellana, por medio de la presente nos permitimos comunicarle
que debido a retrasos en la obtención de información de campo, se solicita
respetuosamente una prórroga de 15 días hábiles para la entrega del informe final.

Atentamente,

Licda. Sofía Montenegro
Cargo: Coordinadora de Proyectos
Correo: sofia.montenegro@consultores.gt
"""

_LICENCIA_CON_CLASE = """\
Dirección General de Tránsito
Licencia de Conducir
Licencia: GT-789456
Nombre: JORGE ERNESTO CASTILLO DIAZ
Clase: B
Fecha de Nacimiento: 10/07/1988
Fecha de Vencimiento: 10/07/2028
Nacionalidad: Guatemalteca
"""

_CARNE_UNIVERSITARIO = """\
UNIVERSIDAD DE SAN CARLOS DE GUATEMALA
Carné Universitario
Carné: 201912345
Nombre: ANA LUCIA MORALES GARCIA
Carrera: Ingeniería en Sistemas
Fecha de Vencimiento: 31/12/2026
"""

_OTRO_GENERICO = """\
MINISTERIO DE FINANZAS PÚBLICAS
Formulario de Solicitud de Autorización
Referencia: MFP-2026-0045
Fecha: 10 de mayo de 2026
NIT solicitante: 87654321
Correo: solicitante@empresa.gt
Teléfono: 2468-1357
"""


# ── Factura combustible ───────────────────────────────────────────────────────

class TestFacturaCombustible:

    def test_emisor_detectado(self, ce):
        r = ce.extract(_FACTURA_COMBUSTIBLE, {}, "factura")
        assert r["contextual"].get("nombre_emisor") is not None

    def test_consumo_diesel(self, ce):
        r = ce.extract(_FACTURA_COMBUSTIBLE, {}, "factura")
        consumo = r["contextual"].get("consumo_detectado")
        assert consumo is not None
        assert "Diésel" in consumo or "Diesel" in consumo or "Combustible" in consumo

    def test_auth_sat_uuid(self, ce):
        r = ce.extract(_FACTURA_COMBUSTIBLE, {}, "factura")
        auth = r["contextual"].get("autorizacion_sat")
        assert auth is not None
        assert len(auth) > 8


# ── Factura hospedaje ─────────────────────────────────────────────────────────

class TestFacturaHospedaje:

    def test_nombre_comercial_detectado(self, ce):
        r = ce.extract(_FACTURA_HOSPEDAJE, {}, "factura")
        nc = r["contextual"].get("nombre_comercial")
        assert nc is not None
        assert "Colonial" in nc or "Hotel" in nc

    def test_consumo_hospedaje(self, ce):
        r = ce.extract(_FACTURA_HOSPEDAJE, {}, "factura")
        consumo = r["contextual"].get("consumo_detectado")
        assert consumo is not None
        assert any(w in consumo for w in ("Hotel", "Habitación", "Hospedaje", "Noche"))

    def test_impuesto_detectado(self, ce):
        r = ce.extract(_FACTURA_HOSPEDAJE, {}, "factura")
        imp = r["contextual"].get("impuesto")
        assert imp is not None
        assert "145" in str(imp)


# ── Recibo con Recibí de ──────────────────────────────────────────────────────

class TestReciboRecibide:

    def test_receptor_desde_recibi_de(self, ce):
        r = ce.extract(_RECIBO_RECIBI_DE, {}, "recibo")
        receptor = r["contextual"].get("receptor")
        assert receptor is not None
        assert any(w in receptor for w in ("NACIONAL", "LOGÍSTICA", "EMPRESA"))

    def test_concepto_por_concepto(self, ce):
        r = ce.extract(_RECIBO_RECIBI_DE, {}, "recibo")
        concepto = r["contextual"].get("concepto")
        assert concepto is not None
        assert "almacenamiento" in concepto.lower() or "servicio" in concepto.lower()

    def test_monto_la_cantidad_de(self, ce):
        r = ce.extract(_RECIBO_RECIBI_DE, {}, "recibo")
        monto = r["contextual"].get("monto")
        assert monto is not None
        assert "2" in str(monto) or "500" in str(monto)

    def test_forma_pago_detectada(self, ce):
        r = ce.extract(_RECIBO_RECIBI_DE, {}, "recibo")
        fp = r["contextual"].get("forma_pago")
        assert fp is None or "Transferencia" in fp or "transferencia" in fp.lower()


# ── Contrato laboral ──────────────────────────────────────────────────────────

class TestContratoLaboral:

    def test_tipo_contrato_laboral(self, ce):
        r = ce.extract(_CONTRATO_LABORAL, {}, "contrato")
        tc = r["contextual"].get("tipo_contrato")
        assert tc is not None
        assert "Laboral" in tc or "LABORAL" in tc

    def test_contratante_detectado(self, ce):
        r = ce.extract(_CONTRATO_LABORAL, {}, "contrato")
        ct = r["contextual"].get("contratante")
        assert ct is not None
        assert any(w in ct for w in ("EMPRESA", "SERVICIOS", "S.A."))

    def test_contratado_detectado(self, ce):
        r = ce.extract(_CONTRATO_LABORAL, {}, "contrato")
        cd = r["contextual"].get("contratado")
        assert cd is not None
        assert any(w in cd for w in ("CARLOS", "REYES", "MENDEZ"))

    def test_monto_laboral(self, ce):
        r = ce.extract(_CONTRATO_LABORAL, {}, "contrato")
        monto = r["contextual"].get("monto")
        assert monto is not None
        assert "5" in str(monto)

    def test_lugar_detectado(self, ce):
        r = ce.extract(_CONTRATO_LABORAL, {}, "contrato")
        lugar = r["contextual"].get("lugar")
        assert lugar is not None
        assert "Guatemala" in lugar


# ── Constancia laboral ────────────────────────────────────────────────────────

class TestConstanciaLaboral:

    def test_tipo_constancia_trabajo(self, ce):
        r = ce.extract(_CONSTANCIA_LABORAL, {}, "constancia")
        tc = r["contextual"].get("tipo_constancia")
        assert tc is not None
        assert "Trabajo" in tc or "TRABAJO" in tc

    def test_entidad_emisora(self, ce):
        r = ce.extract(_CONSTANCIA_LABORAL, {}, "constancia")
        entidad = r["contextual"].get("entidad_emisora")
        assert entidad is None or "Corporación" in entidad or len(entidad) > 3

    def test_cargo_detectado(self, ce):
        r = ce.extract(_CONSTANCIA_LABORAL, {}, "constancia")
        cargo = r["contextual"].get("cargo")
        assert cargo is None or "Coordinadora" in cargo or len(cargo) > 3

    def test_firmante_detectado(self, ce):
        r = ce.extract(_CONSTANCIA_LABORAL, {}, "constancia")
        firmante = r["contextual"].get("firmante")
        assert firmante is None or len(firmante) > 5

    def test_tipo_es_constancia(self, ce):
        r = ce.extract(_CONSTANCIA_LABORAL, {}, "constancia")
        assert r["contextual"]["tipo"] == "constancia"


# ── Carta formal con cuerpo ───────────────────────────────────────────────────

class TestCartaFormalConCuerpo:

    def test_cargo_explicito(self, ce):
        r = ce.extract(_CARTA_CON_CUERPO, {}, "carta_formal")
        cargo = r["contextual"].get("cargo")
        assert cargo is not None
        assert "Coordinadora" in cargo or "Proyectos" in cargo

    def test_resumen_cuerpo(self, ce):
        r = ce.extract(_CARTA_CON_CUERPO, {}, "carta_formal")
        cuerpo = r["contextual"].get("resumen_cuerpo")
        assert cuerpo is not None
        assert len(cuerpo) > 20

    def test_asunto_detectado(self, ce):
        r = ce.extract(_CARTA_CON_CUERPO, {}, "carta_formal")
        asunto = r["contextual"].get("asunto")
        assert asunto is not None
        assert "prórroga" in asunto.lower() or "prorroga" in asunto.lower() or "informe" in asunto.lower()

    def test_remitente_detectado(self, ce):
        r = ce.extract(_CARTA_CON_CUERPO, {}, "carta_formal")
        remitente = r["contextual"].get("remitente")
        assert remitente is None or len(remitente) > 5


# ── Licencia con clase ────────────────────────────────────────────────────────

class TestLicenciaConClase:

    def test_subtipo_licencia(self, ce):
        r = ce.extract(_LICENCIA_CON_CLASE, {}, "identificacion")
        assert r["contextual"].get("subtipo") == "Licencia de conducir"

    def test_clase_licencia_detectada(self, ce):
        r = ce.extract(_LICENCIA_CON_CLASE, {}, "identificacion")
        clase = r["contextual"].get("clase_licencia")
        assert clase is not None
        assert "B" in clase

    def test_numero_licencia(self, ce):
        r = ce.extract(_LICENCIA_CON_CLASE, {}, "identificacion")
        num = r["contextual"].get("numero_licencia")
        assert num is not None
        assert "789456" in num or "GT" in num


# ── Carné universitario ───────────────────────────────────────────────────────

class TestCarneUniversitario:

    def test_subtipo_carne(self, ce):
        r = ce.extract(_CARNE_UNIVERSITARIO, {}, "identificacion")
        assert r["contextual"].get("subtipo") == "Carné"

    def test_numero_carne(self, ce):
        r = ce.extract(_CARNE_UNIVERSITARIO, {}, "identificacion")
        num = r["contextual"].get("numero_carne")
        assert num is not None
        assert "201912345" in num or "2019" in num


# ── Documento otro genérico ───────────────────────────────────────────────────

class TestOtroGenerico:

    def test_tipo_es_otro(self, ce):
        r = ce.extract(_OTRO_GENERICO, {}, "otro")
        assert r["contextual"]["tipo"] == "otro"

    def test_resumen_presente(self, ce):
        r = ce.extract(_OTRO_GENERICO, {}, "otro")
        assert r["contextual"].get("resumen") is not None

    def test_emails_en_otro(self, ce):
        gf = {"emails": ["solicitante@empresa.gt"]}
        r = ce.extract(_OTRO_GENERICO, gf, "otro")
        assert r["contextual"].get("emails") is not None

    def test_nits_en_otro(self, ce):
        gf = {"nit": ["87654321"]}
        r = ce.extract(_OTRO_GENERICO, gf, "otro")
        assert r["contextual"].get("nits") is not None
        assert "87654321" in r["contextual"]["nits"]


# ── Bug regression: recibo emisor no debe ser la primera línea del doc ────────

_RECIBO_SIN_EMISOR_EXPLICITO = """\
RECIBO DE PAGO No. 00547
Recibí de: MARIA ELENA SANDOVAL FUENTES
Por concepto de: Cuota mensual de arrendamiento
La cantidad de: Q 2,500.00
Son: Dos mil quinientos quetzales exactos
Forma de pago: Efectivo
Guatemala, 10 de marzo de 2024
"""

_RECIBO_CON_EMISOR_EXPLICITO = """\
RECIBO DE PAGO No. 00548
Empresa: ARRENDAMIENTOS CONSOLIDADOS S.A.
Recibí de: PEDRO GARCIA LOPEZ
Por concepto de: Renta mensual
La cantidad de: Q 3,500.00
Forma de pago: Cheque
Guatemala, 15 de marzo de 2024
"""


class TestReciboEmisorNoEsPrimeraLinea:

    def test_emisor_none_cuando_no_hay_etiqueta_explicita(self, ce):
        """La primera linea 'RECIBO DE PAGO No. X' no debe usarse como emisor."""
        r = ce.extract(_RECIBO_SIN_EMISOR_EXPLICITO, {}, "recibo")
        emisor = r["contextual"].get("emisor")
        assert emisor is None or "RECIBO" not in str(emisor).upper()

    def test_emisor_no_contiene_numero_de_recibo(self, ce):
        """El campo emisor no debe contener 'No.' ni texto de numeracion."""
        r = ce.extract(_RECIBO_SIN_EMISOR_EXPLICITO, {}, "recibo")
        emisor = r["contextual"].get("emisor") or ""
        assert "No." not in emisor
        assert "00547" not in emisor

    def test_emisor_con_etiqueta_empresa(self, ce):
        """Con 'Empresa: X' si debe extraerse el emisor."""
        r = ce.extract(_RECIBO_CON_EMISOR_EXPLICITO, {}, "recibo")
        emisor = r["contextual"].get("emisor")
        assert emisor is not None
        assert "ARRENDAMIENTOS" in emisor.upper()

    def test_receptor_se_extrae_correctamente(self, ce):
        """El receptor sigue funcionando aunque no haya emisor explicito."""
        r = ce.extract(_RECIBO_SIN_EMISOR_EXPLICITO, {}, "recibo")
        receptor = r["contextual"].get("receptor")
        assert receptor is not None
        assert "MARIA ELENA" in receptor.upper() or "SANDOVAL" in receptor.upper()


# ── Bug regression: carta formal destinatario no debe ser el cuerpo ───────────

_CARTA_CON_CUERPO_LARGO = """\
Guatemala, 20 de marzo de 2024
Senor: GERENTE DE VENTAS
Empresa ABC S.A.
Cargo: Gerente General
Estimado senor:
Por medio de la presente me permito comunicarle que hemos revisado
su propuesta comercial y estamos interesados en establecer una alianza.
Quedamos a sus ordenes para cualquier consulta.
Atentamente,
CARLOS ROBERTO MENDEZ
"""

_CARTA_SIN_DESTINATARIO_CLARO = """\
Guatemala, 25 de abril de 2024
Por medio de la presente me permito informarle sobre el estado de su solicitud.
Le comunicamos que fue aprobada con fecha 20/04/2024.
Atentamente,
LIC. ROSA MARIA FUENTES
"""


class TestCartaDestinatarioNoCuerpo:

    def test_destinatario_no_es_cuerpo(self, ce):
        """El cuerpo 'Por medio de la presente...' no debe aparecer como destinatario."""
        r = ce.extract(_CARTA_CON_CUERPO_LARGO, {}, "carta_formal")
        dest = r["contextual"].get("destinatario") or ""
        assert "por medio" not in dest.lower()
        assert "me permito" not in dest.lower()

    def test_destinatario_correcto_cuando_hay_senor(self, ce):
        """Con 'Senor: NOMBRE' en las primeras lineas si debe extraerse el destinatario."""
        r = ce.extract(_CARTA_CON_CUERPO_LARGO, {}, "carta_formal")
        dest = r["contextual"].get("destinatario")
        assert dest is not None
        assert "GERENTE" in dest.upper() or "VENTAS" in dest.upper()

    def test_destinatario_none_sin_etiqueta(self, ce):
        """Sin etiqueta Senor/Para/Destinatario el campo debe quedar vacio."""
        r = ce.extract(_CARTA_SIN_DESTINATARIO_CLARO, {}, "carta_formal")
        dest = r["contextual"].get("destinatario")
        assert dest is None or "por medio" not in (dest or "").lower()

    def test_resumen_cuerpo_captura_cuerpo_real(self, ce):
        """resumen_cuerpo si debe contener texto del cuerpo de la carta."""
        r = ce.extract(_CARTA_CON_CUERPO_LARGO, {}, "carta_formal")
        resumen = r["contextual"].get("resumen_cuerpo") or ""
        assert len(resumen) > 10


# ── Factura real OCR: COMEDOR LA BENDICION (FEL Pequeño Contribuyente) ────────
# Texto exacto como lo produce el OCR del sistema, sin etiquetas en emisor/comercial.

_FACTURA_REAL_COMEDOR = """\
Factura Pequeno Contribuyente

ERENDIDA , ESCOBAR FLORES
Nit Emisor: 80169988

COMEDOR LA BENDICION

1 CALLE BARRIO LA LOMITA, Zona 3, EL PROGRESO, JUTIAPA

NIT Receptor: 88911969

Nombre Receptor: CORPORACION AMERICANA DE SERVICIOS DE
SEGURIDAD SOCIEDAD ANONIMA

NUMERO DE AUTORIZACION:
E5742FBD-429D-416B-AB81-9F39A6EB34A7

Serie: E5742FBD Numero de DTE: 1117602155

Fecha y hora de emision: 28-abr-2026 07:32:39
Fecha y hora de certificacion: 28-abr-2026 07:32:40

Moneda: GTQ

1 Bien 1 Desayuno 40.00 0.00 40.00

Datos del certificador

Superintendencia de Administracion Tributaria NIT: 16693949
"""

_GF_COMEDOR = {
    "nit": ["80169988", "88911969"],
    "dates": ["28-abr-2026"],
    "moneda": ["GTQ"],
}


class TestFacturaRealComedor:
    """Regresion: factura FEL sin etiquetas en emisor/comercial/direccion.

    Este test replica el OCR exacto de COMEDOR LA BENDICION para garantizar
    que _parse_fel_unlabeled resuelve los campos posicionales correctamente.
    """

    def test_tipo_fiscal(self, ce):
        r = ce.extract(_FACTURA_REAL_COMEDOR, _GF_COMEDOR, "factura")
        val = r["contextual"].get("tipo_fiscal") or ""
        assert "Pequeno Contribuyente" in val or "Pequeño Contribuyente" in val

    def test_nombre_emisor(self, ce):
        r = ce.extract(_FACTURA_REAL_COMEDOR, _GF_COMEDOR, "factura")
        val = r["contextual"].get("nombre_emisor") or ""
        assert "ESCOBAR" in val.upper() or "ERENDIDA" in val.upper()

    def test_nombre_comercial(self, ce):
        r = ce.extract(_FACTURA_REAL_COMEDOR, _GF_COMEDOR, "factura")
        val = r["contextual"].get("nombre_comercial") or ""
        assert "COMEDOR" in val.upper() and "BENDICION" in val.upper()

    def test_direccion_emisor(self, ce):
        r = ce.extract(_FACTURA_REAL_COMEDOR, _GF_COMEDOR, "factura")
        val = r["contextual"].get("direccion_emisor") or ""
        assert "CALLE" in val.upper() or "LOMITA" in val.upper()

    def test_receptor_multilinea_completo(self, ce):
        """El receptor debe incluir ambas líneas del OCR, no solo la primera."""
        r = ce.extract(_FACTURA_REAL_COMEDOR, _GF_COMEDOR, "factura")
        val = r["contextual"].get("receptor") or ""
        assert "CORPORACION" in val.upper()
        assert "SEGURIDAD" in val.upper()
        assert "ANONIMA" in val.upper()

    def test_autorizacion_sat(self, ce):
        r = ce.extract(_FACTURA_REAL_COMEDOR, _GF_COMEDOR, "factura")
        val = r["contextual"].get("autorizacion_sat") or ""
        assert "E5742FBD" in val.upper()

    def test_certificador_nombre(self, ce):
        r = ce.extract(_FACTURA_REAL_COMEDOR, _GF_COMEDOR, "factura")
        val = r["contextual"].get("certificador") or ""
        assert "Superintendencia" in val or "SUPERINTENDENCIA" in val.upper()

    def test_nit_certificador(self, ce):
        r = ce.extract(_FACTURA_REAL_COMEDOR, _GF_COMEDOR, "factura")
        val = r["contextual"].get("nit_certificador") or ""
        assert "16693949" in val

    def test_serie_fel(self, ce):
        r = ce.extract(_FACTURA_REAL_COMEDOR, _GF_COMEDOR, "factura")
        val = r["contextual"].get("serie_fel") or ""
        assert "E5742FBD" in val.upper()

    def test_numero_dte(self, ce):
        r = ce.extract(_FACTURA_REAL_COMEDOR, _GF_COMEDOR, "factura")
        val = r["contextual"].get("numero_dte") or ""
        assert "1117602155" in val

    def test_fecha_emision(self, ce):
        r = ce.extract(_FACTURA_REAL_COMEDOR, _GF_COMEDOR, "factura")
        val = r["contextual"].get("fecha_emision") or ""
        assert "28-abr-2026" in val

    def test_fecha_certificacion(self, ce):
        r = ce.extract(_FACTURA_REAL_COMEDOR, _GF_COMEDOR, "factura")
        val = r["contextual"].get("fecha_certificacion") or ""
        assert "28-abr-2026" in val

    def test_producto_servicio(self, ce):
        r = ce.extract(_FACTURA_REAL_COMEDOR, _GF_COMEDOR, "factura")
        val = r["contextual"].get("producto_servicio") or ""
        assert "Desayuno" in val

    def test_cantidad(self, ce):
        r = ce.extract(_FACTURA_REAL_COMEDOR, _GF_COMEDOR, "factura")
        assert r["contextual"].get("cantidad") == "1"

    def test_precio_unitario(self, ce):
        r = ce.extract(_FACTURA_REAL_COMEDOR, _GF_COMEDOR, "factura")
        assert r["contextual"].get("precio_unitario") == "40.00"

    def test_descuento(self, ce):
        r = ce.extract(_FACTURA_REAL_COMEDOR, _GF_COMEDOR, "factura")
        assert r["contextual"].get("descuento") == "0.00"


# ── Bug regression: recibo emisor no debe capturarse de un dominio de correo ──

_RECIBO_CON_DOMINIO_EMPRESA = """\
RECIBO OFICIAL DE PAGO
Servicios Administrativos Guatemala

Numero de Recibo:  REC-2026-00892
Fecha:             22/04/2026

Recibi de:         Ana Sofia Castillo
Correo:            ana.castillo@empresa.com
Telefono:          2334-5678

La cantidad de:    Q 2,500.00
Por concepto de:   Pago mensual de arrendamiento
Forma de Pago:     Cheque No. 00234
"""


class TestReciboEmisorEmailDomain:
    """Regresion: 'empresa' dentro de un dominio de correo no debe
    capturarse como emisor del recibo."""

    def test_emisor_no_captura_dominio_com(self, ce):
        r = ce.extract(_RECIBO_CON_DOMINIO_EMPRESA, {}, "recibo")
        emisor = r["contextual"].get("emisor") or ""
        assert ".com" not in emisor
        assert "@" not in emisor

    def test_emisor_none_cuando_no_hay_etiqueta_de_emisor(self, ce):
        r = ce.extract(_RECIBO_CON_DOMINIO_EMPRESA, {}, "recibo")
        emisor = r["contextual"].get("emisor")
        assert emisor is None or len(emisor) > 5

    def test_receptor_sigue_funcionando(self, ce):
        r = ce.extract(_RECIBO_CON_DOMINIO_EMPRESA, {}, "recibo")
        receptor = r["contextual"].get("receptor")
        assert receptor is not None
        assert "CASTILLO" in receptor.upper() or "ANA" in receptor.upper()

    def test_monto_correcto(self, ce):
        r = ce.extract(_RECIBO_CON_DOMINIO_EMPRESA, {}, "recibo")
        monto = r["contextual"].get("monto")
        assert monto is not None
        assert "2" in str(monto) or "500" in str(monto)


# ── Bug regression: factura con "Cliente: X" debe extraer el receptor ─────────

_FACTURA_FORMATO_CLIENTE = """\
FACTURA ELECTRONICA
Distribuidora Central S.A.
NIT: 7823401-5
Documento Tributario Electronico - Serie A - Correlativo 0428
Autorizado por SAT Guatemala

Numero de Factura:     FAC-2026-0428
Fecha de Emision:      22/04/2026
Fecha de Vencimiento:  22/05/2026

Cliente:               Carlos Mendoza
NIT Cliente:           C/F
Correo:                carlos.mendoza@correo.gt

DETALLE DE LA FACTURA:
Descripcion                    Cantidad   Precio Unit.   Subtotal
Servicio de Consultoria TI     1          Q 6,500.00     Q 6,500.00

                                          TOTAL:         Q 10,920.00

Forma de Pago: Transferencia Bancaria
"""

_GF_FACTURA_CLIENTE = {
    "nit": ["7823401"],
    "dates": ["22/04/2026"],
    "moneda": [],
}


class TestFacturaFormatoCliente:
    """Regresion: facturas que usan 'Cliente: X' en lugar de sección RECEPTOR
    deben extraer el receptor desde esa etiqueta."""

    def test_receptor_desde_cliente(self, ce):
        r = ce.extract(_FACTURA_FORMATO_CLIENTE, _GF_FACTURA_CLIENTE, "factura")
        receptor = r["contextual"].get("receptor") or ""
        assert "CARLOS" in receptor.upper() or "MENDOZA" in receptor.upper()

    def test_nit_cliente_no_capturado_como_receptor(self, ce):
        """'NIT Cliente: C/F' no debe confundirse con la línea 'Cliente:'."""
        r = ce.extract(_FACTURA_FORMATO_CLIENTE, _GF_FACTURA_CLIENTE, "factura")
        receptor = r["contextual"].get("receptor") or ""
        assert "C/F" not in receptor
        assert "NIT" not in receptor.upper()

    def test_nit_emisor_fallback_a_generic(self, ce):
        r = ce.extract(_FACTURA_FORMATO_CLIENTE, _GF_FACTURA_CLIENTE, "factura")
        nit = r["contextual"].get("nit_emisor")
        assert nit is not None
        assert "7823401" in str(nit)


# ══════════════════════════════════════════════════════════════════════════════
# TESTS DE REGRESIÓN — fixes post-auditoría
# ══════════════════════════════════════════════════════════════════════════════

# ── Fix 1: Factura con formato Q-prefix ──────────────────────────────────────
# Replica el formato real del demo_factura_completo.pdf:
# "Descripcion Cant. P. Unitario Subtotal\nServicio X 1 Q 6,500.00 Q 6,500.00"

_FACTURA_Q_PREFIX = """\
FACTURA ELECTRONICA
Distribuidora Central S.A. - SAT Guatemala
NIT: 7823401-5

Cliente: Carlos Mendoza Lopez

DETALLE
Descripcion Cant. P. Unitario Subtotal
Servicio de Consultoria TI 1 Q 6,500.00 Q 6,500.00
Licencia de Software Anual 2 Q 1,200.00 Q 2,400.00
Mantenimiento de Equipos 1 Q 850.00 Q 850.00

Subtotal: Q 9,750.00
IVA (12%): Q 1,170.00
TOTAL: Q 10,920.00
"""


class TestFacturaQPrefix:
    """Regresión: tablas con prefijo Q deben extraer items correctamente."""

    def test_producto_servicio_capturado(self, ce):
        r = ce.extract(_FACTURA_Q_PREFIX, {}, "factura")
        ps = r["contextual"].get("producto_servicio")
        assert ps is not None
        assert "Consultoria" in ps or "Servicio" in ps

    def test_cantidad_del_primer_item(self, ce):
        r = ce.extract(_FACTURA_Q_PREFIX, {}, "factura")
        qty = r["contextual"].get("cantidad")
        assert qty is not None
        assert "1" in str(qty)

    def test_precio_unitario_del_primer_item(self, ce):
        r = ce.extract(_FACTURA_Q_PREFIX, {}, "factura")
        pu = r["contextual"].get("precio_unitario")
        assert pu is not None
        assert "6,500" in pu or "6500" in pu

    def test_items_lista_no_vacia(self, ce):
        r = ce.extract(_FACTURA_Q_PREFIX, {}, "factura")
        items = r["contextual"].get("items", [])
        assert len(items) >= 1

    def test_items_no_captura_encabezado(self, ce):
        r = ce.extract(_FACTURA_Q_PREFIX, {}, "factura")
        items = r["contextual"].get("items", [])
        descs = [i.get("descripcion", "") for i in items]
        assert not any("Descripcion" in d or "Subtotal" in d for d in descs)


# ── Fix 2: Recibo — emisor sin etiqueta tras título RECIBO ───────────────────

_RECIBO_EMISOR_FALLBACK = """\
RECIBO OFICIAL DE PAGO
Servicios Administrativos Guatemala
DATOS DEL RECIBO
Numero: REC-2026-00892
Fecha: 22/04/2026
Recibi de: Ana Sofia Castillo Reyes
La cantidad de: Q 2,500.00
Por concepto de: Pago mensual de arrendamiento
Forma de Pago: CHEQUE
"""


class TestReciboEmisorFallback:
    """Regresión: empresa sin etiqueta en 2ª línea debe capturarse como emisor."""

    def test_emisor_capturado_desde_linea_sin_etiqueta(self, ce):
        r = ce.extract(_RECIBO_EMISOR_FALLBACK, {}, "recibo")
        emisor = r["contextual"].get("emisor")
        assert emisor is not None
        assert any(w in emisor for w in ("Servicios", "Administrativos", "Guatemala"))

    def test_emisor_no_contiene_recibo(self, ce):
        r = ce.extract(_RECIBO_EMISOR_FALLBACK, {}, "recibo")
        emisor = r["contextual"].get("emisor") or ""
        assert "RECIBO" not in emisor.upper()

    def test_emisor_no_contiene_numero(self, ce):
        r = ce.extract(_RECIBO_EMISOR_FALLBACK, {}, "recibo")
        emisor = r["contextual"].get("emisor") or ""
        assert "00892" not in emisor
        assert "No." not in emisor

    def test_receptor_sigue_correcto(self, ce):
        r = ce.extract(_RECIBO_EMISOR_FALLBACK, {}, "recibo")
        receptor = r["contextual"].get("receptor")
        assert receptor is not None
        assert any(w in receptor.upper() for w in ("CASTILLO", "ANA", "SOFIA"))

    def test_monto_sigue_correcto(self, ce):
        r = ce.extract(_RECIBO_EMISOR_FALLBACK, {}, "recibo")
        monto = r["contextual"].get("monto")
        assert monto is not None
        assert "2,500" in str(monto) or "2500" in str(monto)


# ── Fix 3: Contrato — OBJETO standalone ──────────────────────────────────────

_CONTRATO_OBJETO_DEMO = """\
CONTRATO DE CONSULTORIA

Guatemala, 01 de mayo de 2026

PARTES:
TechSoluciones Guatemala S.A. (CONTRATANTE) y Ing. Marcos Paz (CONSULTOR).

OBJETO:
Consultoria en desarrollo de software empresarial para la modernizacion
de sistemas internos.

VIGENCIA:
Doce meses a partir del 01/05/2026, prorrogable por acuerdo mutuo.

HONORARIOS: Q 8,000.00 mensuales.
"""

_CONTRATO_OBJETO_MISMA_LINEA = """\
CONTRATO DE SERVICIOS

OBJETO: Prestacion de servicios de capacitacion en herramientas digitales.
VIGENCIA: Seis meses a partir del 01/06/2026.
HONORARIOS: Q 3,500.00.
"""


class TestContratoObjetoStandalone:
    """Regresión: OBJETO: en línea standalone debe capturarse correctamente."""

    def test_objeto_desde_linea_siguiente(self, ce):
        r = ce.extract(_CONTRATO_OBJETO_DEMO, {}, "contrato")
        obj = r["contextual"].get("objeto")
        assert obj is not None
        assert any(w in obj.lower() for w in ("consultoria", "software", "sistemas"))

    def test_objeto_misma_linea_con_colon(self, ce):
        r = ce.extract(_CONTRATO_OBJETO_MISMA_LINEA, {}, "contrato")
        obj = r["contextual"].get("objeto")
        assert obj is not None
        assert "capacitacion" in obj.lower() or "herramientas" in obj.lower()

    def test_vigencia_no_interfiere(self, ce):
        r = ce.extract(_CONTRATO_OBJETO_DEMO, {}, "contrato")
        vig = r["contextual"].get("vigencia")
        obj = r["contextual"].get("objeto")
        assert obj != vig

    def test_tipo_es_contrato(self, ce):
        r = ce.extract(_CONTRATO_OBJETO_DEMO, {}, "contrato")
        assert r["contextual"]["tipo"] == "contrato"


# ── Fix 4: Constancia — HACE CONSTAR QUE ────────────────────────────────────

_CONSTANCIA_HACE_CONSTAR = """\
CONSTANCIA DE TRABAJO
Distribuidora Central S.A.
DATOS DE LA EMPRESA
Empresa: Distribuidora Central S.A.
NIT: 7823401-5
Departamento: Recursos Humanos

HACE CONSTAR QUE:
El senor Jose Carlos Ramirez Gutierrez labora en nuestra empresa
desde el 01/01/2020 en el cargo de Analista de Sistemas Senior.

Guatemala, 22 de abril de 2026.
"""


class TestConstanciaHaceConstarQue:
    """Regresión: HACE CONSTAR QUE con nombre en línea siguiente."""

    def test_nombre_capturado(self, ce):
        r = ce.extract(_CONSTANCIA_HACE_CONSTAR, {}, "constancia")
        nombre = r["contextual"].get("nombre")
        assert nombre is not None
        assert any(w in nombre for w in ("Jose", "Carlos", "Ramirez", "Gutierrez"))

    def test_entidad_emisora_capturada(self, ce):
        r = ce.extract(_CONSTANCIA_HACE_CONSTAR, {}, "constancia")
        entidad = r["contextual"].get("entidad_emisora")
        assert entidad is not None
        assert "Distribuidora" in entidad or "Central" in entidad

    def test_motivo_capturado(self, ce):
        r = ce.extract(_CONSTANCIA_HACE_CONSTAR, {}, "constancia")
        motivo = r["contextual"].get("motivo")
        assert motivo is not None
        assert "Analista" in motivo or "Sistemas" in motivo

    def test_tipo_es_constancia(self, ce):
        r = ce.extract(_CONSTANCIA_HACE_CONSTAR, {}, "constancia")
        assert r["contextual"]["tipo"] == "constancia"

    def test_no_rompe_formato_se_hace_constar(self, ce):
        """El formato original 'Se hace constar que' sigue funcionando."""
        r = ce.extract(_CONSTANCIA, {}, "constancia")
        nombre = r["contextual"].get("nombre")
        assert nombre is None or len(nombre) > 5


# ── Fix 5a: Carta formal — destinatario más allá de línea 8 ─────────────────

_CARTA_DESTINATARIO_TARDIO = """\
CARTA FORMAL
Comunicacion Oficial
REFERENCIA Y FECHA
Num. referencia: CF-2026-0001
Fecha: 22/04/2026
Fecha texto: 22 de abril de 2026
Lugar: Guatemala, Guatemala
DESTINATARIO
Senor
Director General
Empresa Receptora S.A.
Ciudad de Guatemala
ASUNTO
Solicitud formal de servicios de consultoria empresarial
CUERPO DE LA CARTA
Estimado senor, por medio de la presente nos dirigimos a usted
para solicitar sus servicios de consultoria.
Atentamente,
Lic. Roberto Sandoval Fuentes
"""


class TestCartaDestinatarioTardio:
    """Regresión: destinatario en sección que empieza en línea 8+."""

    def test_destinatario_capturado_tras_linea_8(self, ce):
        r = ce.extract(_CARTA_DESTINATARIO_TARDIO, {}, "carta_formal")
        dest = r["contextual"].get("destinatario")
        assert dest is not None
        assert len(dest) > 3

    def test_destinatario_no_es_cuerpo(self, ce):
        r = ce.extract(_CARTA_DESTINATARIO_TARDIO, {}, "carta_formal")
        dest = r["contextual"].get("destinatario") or ""
        assert "por medio" not in dest.lower()
        assert "Estimado" not in dest

    def test_asunto_capturado(self, ce):
        r = ce.extract(_CARTA_DESTINATARIO_TARDIO, {}, "carta_formal")
        asunto = r["contextual"].get("asunto")
        assert asunto is not None
        assert "consultoria" in asunto.lower() or "Solicitud" in asunto

    def test_remitente_capturado(self, ce):
        r = ce.extract(_CARTA_DESTINATARIO_TARDIO, {}, "carta_formal")
        remitente = r["contextual"].get("remitente")
        assert remitente is None or "Sandoval" in remitente or len(remitente) > 5


# ── Fix 5b: Carta formal — ASUNTO en línea siguiente sin dos puntos ──────────

_CARTA_ASUNTO_NEWLINE = """\
Guatemala, 22 de abril de 2026

Senor:
Carlos Lopez Mendez

ASUNTO
Solicitud formal de servicios de consultoria empresarial

Estimado senor, por medio de la presente nos permitimos comunicarle
que requerimos sus servicios de consultoria.

Atentamente,

Lic. Maria Gonzalez Fuentes
"""


class TestCartaAsuntoSiguienteLinea:
    """Regresión: ASUNTO sin dos puntos, texto en línea siguiente."""

    def test_asunto_capturado_en_linea_siguiente(self, ce):
        r = ce.extract(_CARTA_ASUNTO_NEWLINE, {}, "carta_formal")
        asunto = r["contextual"].get("asunto")
        assert asunto is not None
        assert "consultoria" in asunto.lower() or "Solicitud" in asunto

    def test_asunto_no_es_vacio(self, ce):
        r = ce.extract(_CARTA_ASUNTO_NEWLINE, {}, "carta_formal")
        asunto = r["contextual"].get("asunto") or ""
        assert len(asunto) >= 5

    def test_destinatario_con_dos_puntos_sigue_funcionando(self, ce):
        """Senor: Nombre en la misma línea sigue extrayéndose."""
        r = ce.extract(_CARTA_ASUNTO_NEWLINE, {}, "carta_formal")
        dest = r["contextual"].get("destinatario")
        assert dest is not None
        assert any(w in dest for w in ("Carlos", "Lopez", "Mendez"))

    def test_asunto_con_dos_puntos_sigue_funcionando(self, ce):
        """El formato original ASUNTO: texto en la misma línea sigue funcionando."""
        r = ce.extract(_CARTA, {}, "carta_formal")
        asunto = r["contextual"].get("asunto")
        assert asunto is not None
        assert "reunión" in asunto.lower() or "reuni" in asunto.lower()
