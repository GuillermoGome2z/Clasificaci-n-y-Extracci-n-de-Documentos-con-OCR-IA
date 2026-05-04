"""Genera archivos de entrenamiento: 5 corto identificacion + 5 corto carta_formal + 10 carta_formal nuevos."""
from pathlib import Path

BASE_ID = Path("data/training/identificacion")
BASE_CF = Path("data/training/carta_formal")

# ─── Identificacion: 5 corto distintos ────────────────────────────────────────

ID_FILES = {
    "identificacion_corto_01.txt": (
        "DOCUMENTO PERSONAL DE IDENTIFICACION\n"
        "DPI - RENAP GUATEMALA\n"
        "Numero de documento: 00100101\n\n"
        "DATOS DEL TITULAR\n"
        "Nombre: Sofia Alejandra Martinez Perez\n"
        "DPI: 1234 56789 0101\n"
        "Fecha nacimiento: 12/05/1990\n"
        "Municipio: Guatemala\n"
        "Departamento: Guatemala\n"
        "Nacionalidad: Guatemalteca\n\n"
        "Registro Nacional de las Personas - RENAP\n"
        "Fecha emision: 15/01/2018\n"
        "Fecha vencimiento: 15/01/2028\n"
    ),
    "identificacion_corto_02.txt": (
        "DOCUMENTO PERSONAL DE IDENTIFICACION\n"
        "DPI - RENAP GUATEMALA\n"
        "Numero de documento: 00200202\n\n"
        "DATOS DEL TITULAR\n"
        "Nombre: Roberto Carlos Fuentes Lopez\n"
        "DPI: 9876 54321 9876\n"
        "Fecha nacimiento: 03/11/1978\n"
        "Municipio: Quetzaltenango\n"
        "Departamento: Quetzaltenango\n"
        "Nacionalidad: Guatemalteco\n\n"
        "Registro Nacional de las Personas - RENAP\n"
        "Fecha emision: 20/06/2020\n"
        "Fecha vencimiento: 20/06/2030\n"
    ),
    "identificacion_corto_03.txt": (
        "DOCUMENTO PERSONAL DE IDENTIFICACION\n"
        "CUI - RENAP GUATEMALA\n"
        "Numero de documento: 00300303\n\n"
        "DATOS DEL TITULAR\n"
        "Nombre completo: Maria Isabel Rodriguez Garcia\n"
        "CUI: 5555 12345 6789\n"
        "Fecha nacimiento: 28/02/1995\n"
        "Municipio: Mixco\n"
        "Departamento: Guatemala\n"
        "Estado civil: Casada\n"
        "Nacionalidad: Guatemalteca\n\n"
        "RENAP Guatemala - Documento oficial\n"
        "Emitido: 08/03/2021\n"
        "Vence: 08/03/2031\n"
    ),
    "identificacion_corto_04.txt": (
        "DOCUMENTO PERSONAL DE IDENTIFICACION\n"
        "DPI RENAP REPUBLICA DE GUATEMALA\n"
        "Numero: 00400404\n\n"
        "Nombre: Luis Enrique Morales Castillo\n"
        "DPI: 3322 11445 6677\n"
        "Fecha de nacimiento: 17/07/1985\n"
        "Lugar de nacimiento: Escuintla, Guatemala\n"
        "Municipio: Escuintla\n"
        "Departamento: Escuintla\n"
        "Profesion: Contador Publico\n"
        "Nacionalidad: Guatemalteco\n\n"
        "Registro Nacional de las Personas\n"
        "Fecha emision: 12/09/2019\n"
        "Vigencia: 10 anos\n"
    ),
    "identificacion_corto_05.txt": (
        "DOCUMENTO PERSONAL DE IDENTIFICACION\n"
        "DPI - RENAP GUATEMALA\n"
        "Numero de documento: 00500505\n\n"
        "DATOS DEL TITULAR\n"
        "Nombre: Carmen Lucia Velasquez Torres\n"
        "DPI: 7788 99001 1223\n"
        "Fecha nacimiento: 22/12/2000\n"
        "Municipio: Villa Nueva\n"
        "Departamento: Guatemala\n"
        "Estado civil: Soltera\n"
        "Sexo: Femenino\n"
        "Nacionalidad: Guatemalteca\n\n"
        "RENAP - Registro Nacional de las Personas\n"
        "Centro America - Guatemala\n"
        "Emision: 05/01/2022\n"
        "Vencimiento: 05/01/2032\n"
    ),
}

# ─── Carta formal: 5 corto distintos + 10 nuevos ─────────────────────────────

CF_FILES = {
    "carta_formal_corto_01.txt": (
        "CARTA FORMAL\n"
        "Ref: CF-2026-0101\n"
        "Guatemala, 15/01/2026\n\n"
        "Senor Gerente de Compras\n"
        "Empresa Distribuidora GT S.A.\n\n"
        "Estimado senor:\n\n"
        "Solicitamos formalmente una reunion para presentar nuestra propuesta "
        "de suministro de materiales para el presente ano.\n\n"
        "Atentamente,\n"
        "Lic. Carlos Morales\n"
        "Tel: 2345-6789\n"
        "Correo: c.morales@empresa.gt\n"
    ),
    "carta_formal_corto_02.txt": (
        "CARTA FORMAL\n"
        "Ref: CF-2026-0202\n"
        "Guatemala, 20/02/2026\n\n"
        "Senora Directora de Recursos Humanos\n"
        "Corporacion Nacional S.A.\n\n"
        "Estimada senora:\n\n"
        "Manifiesto mi interes en el puesto de Analista Financiero. "
        "Adjunto hoja de vida. Fecha disponible: 01/03/2026.\n\n"
        "Respetuosamente,\n"
        "Ana Patricia Lopez\n"
        "Tel: 5512-3456\n"
        "Correo: ana.lopez@gmail.com\n"
    ),
    "carta_formal_corto_03.txt": (
        "CARTA FORMAL\n"
        "Num. referencia: CF-MUN-2026-003\n"
        "Guatemala, 10/03/2026\n\n"
        "Senor Alcalde\n"
        "Municipalidad de Guatemala\n\n"
        "Estimado senor Alcalde:\n\n"
        "Solicitamos autorizacion para el evento cultural programado "
        "el 25/04/2026 en el parque central. Presupuesto: Q 15,000.00.\n\n"
        "Atentamente,\n"
        "Comite Organizador\n"
        "Tel: 2200-5678\n"
    ),
    "carta_formal_corto_04.txt": (
        "CARTA FORMAL DE RECOMENDACION\n"
        "Ref: REC-2026-004\n"
        "Guatemala, 05/04/2026\n\n"
        "A quien corresponda:\n\n"
        "Certifico que Juan Pablo Herrera laboro del 01/01/2020 al "
        "31/03/2026 como Jefe de Sistemas con excelente desempeno.\n\n"
        "Atentamente,\n"
        "Dra. Maria Fernandez - Gerente General\n"
        "Tel: 2300-4500\n"
        "Correo: gerencia@corporacion.gt\n"
    ),
    "carta_formal_corto_05.txt": (
        "CARTA FORMAL\n"
        "Ref: CF-2026-005\n"
        "Guatemala, 28/04/2026\n\n"
        "Director General\n"
        "Ministerio de Educacion\n\n"
        "Estimado senor Director:\n\n"
        "Solicitamos intervencion para resolver situacion administrativa "
        "del establecimiento. Fecha limite: 15/05/2026.\n\n"
        "Atentamente,\n"
        "Prof. Rosa Elena Mendez\n"
        "Tel: 2456-7890\n"
        "Correo: direccion@escuela.edu.gt\n"
    ),
    "carta_formal_071.txt": (
        "CARTA FORMAL DE SOLICITUD DE CREDITO\n"
        "Ref: SOL-CRED-2026-071\n"
        "Guatemala, 02/01/2026\n\n"
        "Senor Gerente de Creditos\n"
        "Banco Industrial de Guatemala\n\n"
        "Estimado senor:\n\n"
        "El suscrito Luis Fernando Castellanos, con NIT 4521890-3, solicita "
        "aprobacion de credito empresarial por Q 250,000.00 a 36 meses.\n\n"
        "Se adjuntan estados financieros y garantias.\n\n"
        "Atentamente,\n"
        "Luis Fernando Castellanos\n"
        "Tel: 2400-1234\n"
        "Correo: lcastellanos@empresa.gt\n"
        "Web: https://www.empresa.gt\n"
    ),
    "carta_formal_072.txt": (
        "CARTA FORMAL DE PROPUESTA COMERCIAL\n"
        "Num. ref: CF-PROV-2026-072\n"
        "Guatemala, 08/01/2026\n\n"
        "Licenciado Director de Adquisiciones\n"
        "Hospital Nacional General\n\n"
        "Estimado Licenciado:\n\n"
        "Presentamos propuesta de insumos medicos para el primer semestre 2026:\n"
        "- Equipos de proteccion: Q 45,000.00\n"
        "- Material de curacion: Q 28,500.00\n"
        "Total: Q 73,500.00\n\n"
        "Respuesta requerida antes del 20/01/2026.\n\n"
        "Cordialmente,\n"
        "Ing. Patricia Ruiz\n"
        "Tel: 2300-9876\n"
        "Correo: pruiz@suministros.gt\n"
    ),
    "carta_formal_073.txt": (
        "CARTA FORMAL DE NOTIFICACION LEGAL\n"
        "Ref: NOT-JUR-2026-073\n"
        "Guatemala, 15/01/2026\n\n"
        "Representante Legal\n"
        "Empresa Comercial ABC S.A.\n\n"
        "Estimado senor:\n\n"
        "Notifico formalmente incumplimiento del contrato del 01/06/2025 "
        "por la suma adeudada de Q 85,000.00. Se concede plazo de 15 dias "
        "a partir del 15/01/2026.\n\n"
        "Lic. Jorge Estrada - Abogado y Notario\n"
        "Colegiado No. 12345\n"
        "Tel: 2234-5678\n"
        "Correo: jestrada@bufete.gt\n"
    ),
    "carta_formal_074.txt": (
        "CARTA FORMAL DE RENUNCIA\n"
        "Ref: REN-2026-074\n"
        "Guatemala, 22/01/2026\n\n"
        "Senora Gerente de Recursos Humanos\n"
        "Corporacion Multinacional GT S.A.\n\n"
        "Estimada senora:\n\n"
        "Comunico formalmente mi renuncia al cargo de Coordinador de Proyectos "
        "que he desempenado desde el 15/03/2020. "
        "Mi ultimo dia sera el 22/02/2026, otorgando el mes de aviso.\n\n"
        "Atentamente,\n"
        "Pedro Antonio Vasquez Lopez\n"
        "Tel: 5523-4567\n"
        "Correo: p.vasquez@personal.com\n"
    ),
    "carta_formal_075.txt": (
        "CARTA FORMAL DE APELACION TRIBUTARIA\n"
        "Ref: APE-SAT-2026-075\n"
        "Guatemala, 30/01/2026\n\n"
        "Superintendente de Administracion Tributaria - SAT\n\n"
        "Estimado senor Superintendente:\n\n"
        "La empresa Importaciones Globales S.A. con NIT 7823401-5 presenta "
        "recurso de apelacion contra la resolucion del 15/01/2026 por "
        "Q 42,000.00 en ajustes fiscales.\n\n"
        "Lic. Sandra Morales - Representante Legal\n"
        "Tel: 2456-3210\n"
        "Correo: s.morales@importaciones.gt\n"
    ),
    "carta_formal_076.txt": (
        "CARTA FORMAL DE CONVENIO DE PAGO\n"
        "Ref: CONV-2026-076\n"
        "Guatemala, 05/02/2026\n\n"
        "Jefe del Departamento de Cobros\n"
        "Empresa Servicios Generales S.A.\n\n"
        "Estimado senor:\n\n"
        "Propongo convenio de pago para cancelar deuda de Q 12,500.00:\n"
        "- Cuota inicial: Q 2,500.00 al 15/02/2026\n"
        "- Cuotas mensuales: Q 1,000.00 del 01/03/2026 al 01/12/2026\n\n"
        "Atentamente,\n"
        "Rosa Maria Cifuentes\n"
        "Correo: rmcifuentes@cliente.gt\n"
        "Tel: 2305-8901\n"
        "Fecha: 05 de febrero de 2026\n"
    ),
    "carta_formal_077.txt": (
        "CARTA FORMAL DE INVITACION INSTITUCIONAL\n"
        "Ref: INV-2026-077\n"
        "Guatemala, 12/02/2026\n\n"
        "Doctor Rector\n"
        "Universidad de San Carlos de Guatemala\n\n"
        "Estimado senor Rector:\n\n"
        "Invitamos al Foro Empresarial 2026 el dia 28/02/2026 en el Hotel "
        "Westin Camino Real, de 8:00 a 18:00 horas. "
        "Confirmar asistencia antes del 20/02/2026.\n\n"
        "Cordialmente,\n"
        "Ing. Mario Antonio Recinos - Presidente\n"
        "Tel: 2200-5000\n"
        "Correo: presidencia@aeg.org.gt\n"
        "Web: https://www.aeg.org.gt\n"
    ),
    "carta_formal_078.txt": (
        "CARTA FORMAL DE QUEJA Y RECLAMO\n"
        "Ref: QUE-2026-078\n"
        "Guatemala, 20/02/2026\n\n"
        "Gerente de Servicio al Cliente\n"
        "Empresa de Telecomunicaciones GT S.A.\n\n"
        "Estimado senor:\n\n"
        "Presento queja formal por deficiente servicio de internet desde "
        "el 01/01/2026, a pesar de pagar puntualmente la mensualidad de "
        "Q 350.00. Solicito resolucion antes del 28/02/2026.\n\n"
        "Atentamente,\n"
        "Claudia Beatriz Ajanel Mendez\n"
        "NIT: 3456789-1\n"
        "Tel: 5534-2109\n"
        "Correo: cajanel@correo.gt\n"
    ),
    "carta_formal_079.txt": (
        "CARTA FORMAL DE AGRADECIMIENTO INSTITUCIONAL\n"
        "Ref: AGR-2026-079\n"
        "Guatemala, 28/02/2026\n\n"
        "Excelentisimo senor Embajador de Espana en Guatemala\n\n"
        "Distinguido senor Embajador:\n\n"
        "Expresamos agradecimiento por el apoyo al proyecto de restauracion "
        "del Parque Historico, con inversion de USD 150,000.00. "
        "La inauguracion sera el 15/03/2026.\n\n"
        "Ministra de Cultura y Deportes\n"
        "Tel: 2239-0000\n"
        "Correo: despacho@mcd.gob.gt\n"
    ),
    "carta_formal_080.txt": (
        "CARTA FORMAL DE RESPUESTA A PROPUESTA\n"
        "Ref: RESP-2026-080\n"
        "Guatemala, 07/03/2026\n\n"
        "Licenciada Gerente de Proyectos\n"
        "Consultora Estrategica GUA S.A.\n\n"
        "Estimada Licenciada:\n\n"
        "En respuesta a su propuesta del 28/02/2026, aprobamos presupuesto "
        "de Q 120,000.00 para los servicios del 01/04/2026 al 31/03/2027. "
        "Forma de pago: TRANSFERENCIA BANCARIA mensual.\n\n"
        "Cordialmente,\n"
        "Diego Ernesto Herrera - Director de Operaciones\n"
        "Tel: 2400-7890\n"
        "Correo: contabilidad@empresa.gt\n"
    ),
}

for fname, content in ID_FILES.items():
    (BASE_ID / fname).write_text(content, encoding="utf-8")
    print(f"  ID {fname} ({len(content)} chars)")

for fname, content in CF_FILES.items():
    (BASE_CF / fname).write_text(content, encoding="utf-8")
    print(f"  CF {fname} ({len(content)} chars)")

print(f"\nTotal identificacion: {len(list(BASE_ID.glob('*.txt')))} files")
print(f"Total carta_formal:   {len(list(BASE_CF.glob('*.txt')))} files")
