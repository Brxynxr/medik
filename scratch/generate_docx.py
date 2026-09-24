import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_document():
    doc = Document()

    # Set page margins (1 inch)
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Base Colors
    c_primary = RGBColor(27, 54, 93)     # Navy #1B365D
    c_secondary = RGBColor(43, 108, 176) # Blue #2B6CB0
    c_dark = RGBColor(45, 55, 72)        # Slate #2D3748
    c_gray = RGBColor(113, 128, 150)     # Gray #718096

    # ==================== PORTADA ====================
    p_pre = doc.add_paragraph()
    p_pre.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_pre = p_pre.add_run("PROPUESTA TÉCNICA Y COMERCIAL\n")
    r_pre.font.name = "Arial"
    r_pre.font.size = Pt(14)
    r_pre.font.bold = True
    r_pre.font.color.rgb = c_secondary

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("AUTOMATIZACIÓN INTELIGENTE DEL BUZÓN CORPORATIVO DE RIWI\n")
    r_title.font.name = "Arial"
    r_title.font.size = Pt(22)
    r_title.font.bold = True
    r_title.font.color.rgb = c_primary

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run('“SmartInbox RIWI: Capa de Ingesta Inteligente, Orquestación Asíncrona y Enrutamiento Operativo para info@riwi.io”\n')
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(13)
    r_sub.font.italic = True
    r_sub.font.color.rgb = c_dark

    p_div = doc.add_paragraph()
    p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_div = p_div.add_run("—" * 35 + "\n")
    r_div.font.color.rgb = c_gray

    # Metadata Box
    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Cliente:", "RIWI Barranquilla"),
        ("Canal Objetivo:", "info@riwi.io (Punto Único de Entrada)"),
        ("Fecha de Emisión:", "22 de Septiembre de 2026"),
        ("Versión del Documento:", "1.0 — Propuesta de Arquitectura y Diseño Empresarial")
    ]
    for i, (k, v) in enumerate(meta_data):
        row = meta_table.rows[i]
        c1, c2 = row.cells[0], row.cells[1]
        c1.text = k
        c2.text = v
        c1.paragraphs[0].runs[0].font.bold = True
        c1.paragraphs[0].runs[0].font.color.rgb = c_primary
        c2.paragraphs[0].runs[0].font.color.rgb = c_dark
        c1.width = Inches(2.2)
        c2.width = Inches(4.0)

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(24)

    # Equipo Proponente (Sin "Líder")
    p_team_title = doc.add_paragraph()
    p_team_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_tt = p_team_title.add_run("EQUIPO CONSULTOR PROPONENTE")
    r_tt.font.name = "Arial"
    r_tt.font.size = Pt(12)
    r_tt.font.bold = True
    r_tt.font.color.rgb = c_primary

    team_table = doc.add_table(rows=3, cols=2)
    team_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    team_data = [
        ("Daniel David Martinez Gonzalez", "Especialista en Arquitectura Cloud e Integración de Sistemas"),
        ("Breyner De Jesus Manga Arias", "Especialista en Datos, Estándares DIAN & Pipelines de Extracción"),
        ("Joseph Romero", "Especialista en Inteligencia Artificial, NLP & Human-in-the-Loop Systems")
    ]
    for i, (name, role) in enumerate(team_data):
        row = team_table.rows[i]
        c1, c2 = row.cells[0], row.cells[1]
        c1.text = name
        c2.text = role
        c1.paragraphs[0].runs[0].font.bold = True
        c1.paragraphs[0].runs[0].font.color.rgb = c_dark
        c2.paragraphs[0].runs[0].font.italic = True
        c2.paragraphs[0].runs[0].font.color.rgb = c_secondary
        c1.width = Inches(2.8)
        c2.width = Inches(3.7)

    doc.add_page_break()

    # Helpers for content
    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = "Arial"
        r.font.size = Pt(15)
        r.font.bold = True
        r.font.color.rgb = c_primary
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = "Arial"
        r.font.size = Pt(12.5)
        r.font.bold = True
        r.font.color.rgb = c_secondary
        return p

    def add_h3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = "Arial"
        r.font.size = Pt(11)
        r.font.bold = True
        r.font.color.rgb = c_dark
        return p

    def add_body(text, bold_prefix=None):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.name = "Calibri"
            r_pre.font.size = Pt(10.5)
            r_pre.font.bold = True
            r_pre.font.color.rgb = c_dark
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(10.5)
        r.font.color.rgb = c_dark
        return p

    def add_bullet(text, bold_prefix=None):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.name = "Calibri"
            r_pre.font.size = Pt(10.5)
            r_pre.font.bold = True
            r_pre.font.color.rgb = c_dark
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(10.5)
        r.font.color.rgb = c_dark
        return p

    def add_image_centered(img_path, width_inches=6.2, caption=""):
        if os.path.exists(img_path):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run()
            run.add_picture(img_path, width=Inches(width_inches))
            if caption:
                p_cap = doc.add_paragraph()
                p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_cap.paragraph_format.space_after = Pt(8)
                r_cap = p_cap.add_run(caption)
                r_cap.font.name = "Calibri"
                r_cap.font.size = Pt(9)
                r_cap.font.italic = True
                r_cap.font.color.rgb = c_gray

    # ==================== 1. RESUMEN EJECUTIVO ====================
    add_h1("1. RESUMEN EJECUTIVO")
    add_body("La presente propuesta técnica y comercial establece el diseño arquitectural y operativo de SmartInbox RIWI, una solución integral concebida para transformar el buzón corporativo info@riwi.io de RIWI Barranquilla en un canal transaccional inteligente, automatizado y rigurosamente auditable.")
    add_body("Actualmente, info@riwi.io opera como el punto único de entrada para una comunidad consolidada de más de dos millones (2.000.000) de clientes registrados, además de cientos de proveedores y aliados estratégicos. La naturaleza no estructurada de los mensajes recibidos diariamente —que mezclan facturas electrónicas, órdenes de compra de diversa índole, solicitudes de soporte y quejas urgentes— ha generado un cuello de botella operativo crítico, caracterizado por clasificación manual, lectura individual de archivos adjuntos, dispersión documental y demoras en el direccionamiento a las áreas correspondientes.")
    add_body("Frente a este escenario, SmartInbox RIWI propone la implementación de una Capa de Ingesta Inteligente y Orquestación Asíncrona que desacopla la recepción del correo de su procesamiento operativo. La solución combina automatización determinista basada en reglas (para la validación estricta de documentos normativos como el XML UBL 2.1 de facturación electrónica DIAN), modelos avanzados de extracción de información estructurada y agentes de Procesamiento de Lenguaje Natural (NLP/LLM) para la interpretación de solicitudes libres y análisis de sentimiento en PQRS.")
    
    add_h2("Propuesta de Valor y Retorno de Inversión (ROI) Proyectado")
    add_bullet(" Más del 88% al 92% de los correos clasificados, extraídos y direccionados hacia los sistemas destino (ERP contable, gestión de compras y CRM de SAC) sin requerir intervención humana alguna.", "Procesamiento Directo Desatendido (Straight-Through Processing - STP):")
    add_bullet(" El tiempo transcurrido desde la recepción del correo hasta su registro en el sistema correspondiente disminuye de un promedio de 4 a 12 horas hábiles a menos de 45 segundos.", "Reducción Drástica en Tiempos de Ciclo:")
    add_bullet(" La intervención del personal se reduce a menos del 10% del volumen total, limitándose estrictamente a casos de incertidumbre probabilística, validación de excepciones o aprobaciones de negocio en interfaces especializadas de un solo clic.", "Principio Fundamental 'No Trasladar la Carga':")
    add_bullet(" Se preserva de forma absoluta el buzón info@riwi.io como canal principal. Ningún cliente, proveedor o aliado se ve obligado a cambiar sus hábitos de envío o migrar a nuevos correos electrónicos.", "Cero Fricción Externa:")
    add_bullet(" Cada transacción cuenta con un identificador único de trazabilidad (Trace-ID), registrando el histórico inmutable de decisiones, niveles de confianza y marcas de tiempo, satisfaciendo requerimientos de auditoría y la regulación colombiana de protección de datos (Habeas Data).", "Trazabilidad de Grado Corporativo:")

    # ==================== 2. ANÁLISIS DEL PROBLEMA ====================
    add_h1("2. ANÁLISIS DEL PROBLEMA")
    add_h2("2.1. Diagnóstico del Modelo Actual")
    add_body("El buzón info@riwi.io concentra la totalidad de las comunicaciones entrantes de la operación de RIWI Barranquilla. El modelo actual depende de operadores que realizan un proceso secuencial y manual:")
    add_bullet(" Lectura individual de cada correo entrante para entender el contexto.", "1. Apertura e Inspección Visual:")
    add_bullet(" Extracción de archivos .pdf, .zip, imágenes o documentos de texto para determinar su contenido.", "2. Descarga Manual de Adjuntos:")
    add_bullet(" Comprensión subjetiva de si el correo es una factura, una orden de compra, un reclamo o una notificación informativa.", "3. Interpretación y Triage Cognitivo:")
    add_bullet(" Reenvío del correo o transcripción manual de los datos a bandejas departamentales o planillas de cálculo.", "4. Digitación y Reenvío:")

    add_h2("2.2. Impactos Operativos, Financieros y Reputacionales")
    
    t_diag = doc.add_table(rows=6, cols=3)
    t_diag.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Dimensión", "Situación Actual", "Impacto en RIWI Barranquilla"]
    for j, h in enumerate(headers):
        cell = t_diag.rows[0].cells[j]
        cell.text = h
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_background(cell, "1B365D")
        set_cell_margins(cell, 120, 120, 150, 150)
    
    diag_rows = [
        ("Financiera (Cuentas por Pagar)", "Facturas represadas o no identificadas oportunamente en el buzón.", "Pérdida de descuentos por pronto pago, riesgo de cobros jurídicos por vencimiento de plazos, inconsistencias en el flujo de caja y retrasos en la causación contable."),
        ("Operativa (Compras / Servicios)", "Órdenes de compra mezcladas con cotizaciones o mensajes generales.", "Demoras en la adquisición de insumos críticos para la operación, desabastecimiento de suministros físicos y retrasos en la contratación de servicios."),
        ("Cliente (Servicio al Cliente - SAC)", "PQRS dispersas entre correos comerciales y administrativos.", "Incumplimiento de los tiempos legales de respuesta estipulados por la ley colombiana, deterioro del Net Promoter Score (NPS) y riesgo de sanciones regulatorias."),
        ("Talento Humano", "Tareas repetitivas de clasificación y descarga de archivos.", "Desgaste y fatiga cognitiva en el personal administrativo, alta rotación y costos hundidos en labores de nulo valor agregado."),
        ("Gobernanza y Control", "Ausencia de métricas en tiempo real sobre el estado del buzón.", "Imposibilidad de auditar cuántas facturas ingresaron en el día, cuáles están pendientes y quién asumió la responsabilidad de cada caso.")
    ]
    for i, r_data in enumerate(diag_rows):
        row = t_diag.rows[i+1]
        for j, val in enumerate(r_data):
            cell = row.cells[j]
            cell.text = val
            cell.paragraphs[0].runs[0].font.size = Pt(9.5)
            cell.paragraphs[0].runs[0].font.color.rgb = c_dark
            if j == 0:
                cell.paragraphs[0].runs[0].font.bold = True
            set_cell_margins(cell, 80, 80, 120, 120)
            if i % 2 == 1:
                set_cell_background(cell, "F7FAFC")

    add_h2("2.3. La Restricción No Negociable: info@riwi.io como Canal Único")
    add_body("La organización cuenta con un histórico consolidado de más de dos millones de clientes registrados y una vasta red de proveedores que utilizan info@riwi.io como su punto natural de contacto.")
    add_body("Intentar resolver el problema mediante la fragmentación del buzón en cuentas satélite (por ejemplo: facturas@riwi.io, compras@riwi.io, pqrs@riwi.io) representaría un error estratégico de alto impacto:")
    add_bullet(" Obligaría a campañas masivas de notificación con bajas tasas de apertura y adopción.", "Costo Masivo de Gestión de Cambio:")
    add_bullet(" Los proveedores continuarían enviando facturas al buzón tradicional por inercia, manteniéndose el problema original en paralelo.", "Falsos Positivos y Pérdida de Correos:")
    add_bullet(" Multiplicación de buzones expuestos a spam, phishing y vectores de vulnerabilidad.", "Aumento de la Superficie de Ataque:")
    add_body("Por ende, el diseño propuesto asume como premisa rectora inviolable que info@riwi.io seguirá siendo el único buzón de entrada. La inteligencia y la organización se implementan como una capa digital de software subyacente que opera de manera transparente para el mundo exterior.")

    # ==================== 3. SOLUCIÓN PROPUESTA ====================
    add_h1("3. SOLUCIÓN PROPUESTA")
    add_body("La solución SmartInbox RIWI se estructura como un motor de procesamiento documental e inteligente que atiende de forma especializada los tres procesos neurálgicos definidos para la organización, complementado con una gestión controlada de mensajes administrativos generales.")

    # Insert Diagrama Procesos
    add_image_centered("/home/ddamago/Projects/buzoncorporativoRIWI/Propuesta/assets/diagrama_procesos.png",
                       width_inches=6.2, caption="Figura 1: Especialización Técnica de los Tres Procesos Clave en SmartInbox RIWI.")

    add_h2("3.1. Proceso de Facturación Electrónica (Cuentas por Pagar / Tesorería)")
    add_body("El tratamiento de facturas constituye el proceso de mayor rigor legal y financiero. Siguiendo las directrices normativas de la Dirección de Impuestos y Aduanas Nacionales (DIAN) en Colombia, una factura electrónica legítima se emite y transmite habitualmente dentro de un contenedor comprimido (.zip), el cual resguarda el archivo XML firmado digitalmente bajo el estándar internacional UBL 2.1 (AttachedDocument), frecuentemente acompañado de su representación gráfica en PDF.")
    
    add_h3("Mecanismo de Identificación y Validación Previa (.zip / XML)")
    add_body("Antes de ejecutar cualquier extracción cognitiva o invocar modelos de lenguaje de alto costo, el sistema activa una compuerta determinista de validación:")
    add_bullet(" Identificación de archivos con extensión .zip o .xml en el mensaje entrante.", "1. Inspección de Adjuntos:")
    add_bullet(" Apertura del contenedor .zip en un entorno protegido (sandbox) sin persistir archivos no verificados en disco.", "2. Descompresión en Memoria Segura:")
    add_bullet(" Verificación de esquema contra los esquemas XSD oficiales de la DIAN (AttachedDocument, Invoice, ApplicationResponse). Confirmación de la presencia de la firma digital (ds:Signature) y el Código Único de Facturación Electrónica (CUFE). Comprobación del acuse de recibo o validación previa DIAN mediante el nodo ApplicationResponse embebido.", "3. Parsing y Validación de Estructura XML (UBL 2.1):")
    add_bullet(" Si el correo solo contiene un PDF comercial sin archivo XML, se marca como 'Factura en Formato Gráfico / No Electrónica', canalizándolo a OCR estructurado con bandera de alerta para Tesorería.", "4. Vía Alterna (PDF sin XML):")

    add_h3("Extracción Estructurada de Datos")
    add_body("Una vez confirmada la validez del XML, los datos no se 'estiman' mediante IA probabilística; se leen de manera determinista y con 100% de precisión directamente del árbol XML:")
    add_bullet(" Tag cbc:ID.", "• Número de Factura:")
    add_bullet(" Tag cac:AccountingSupplierParty.", "• Identificación del Proveedor (NIT / DV):")
    add_bullet(" Tag cac:PartyLegalEntity/cbc:RegistrationName.", "• Razón Social del Proveedor:")
    add_bullet(" Tags cbc:IssueDate y cbc:DueDate.", "• Fecha de Emisión y Vencimiento:")
    add_bullet(" Tags cbc:TaxExclusiveAmount (Subtotal), cac:TaxTotal/cbc:TaxAmount (IVA) y cbc:PayableAmount (Total a Pagar).", "• Moneda y Valores Totales:")
    add_bullet(" Tag cac:OrderReference/cbc:ID (si viene reportada por el emisor).", "• Orden de Compra Referenciada:")
    add_bullet(" Tag cbc:UUID.", "• Código CUFE:")

    add_h3("Validación de Negocio y Enrutamiento")
    add_bullet(" Consulta instantánea en la base de datos de trazabilidad por CUFE y combinación NIT + Número de Factura. Si ya existe, se bloquea el reprocesamiento y se archiva como duplicado con notificación automática.", "Detección de Duplicados:")
    add_bullet(" Verificación automática de la existencia de la Orden de Compra citada en el ERP interno de RIWI.", "Conciliación:")
    add_bullet(" Inyección de los datos estructurados en el módulo de Cuentas por Pagar / Tesorería mediante API o cola de integración, notificando al proveedor la recepción exitosa.", "Direccionamiento:")

    add_h2("3.2. Proceso de Órdenes de Compra (Servicios Internos)")
    add_body("Las órdenes de compra (OC) y sus documentos asociados llegan comúnmente en formatos semi-estructurados (PDFs vectoriales, documentos escaneados o tablas en el cuerpo del correo). El sistema clasifica y jerarquiza estos documentos para el área de Servicios Internos.")

    add_h3("Clasificación Contextual Bipersonalizada: Producto vs. Servicio")
    add_bullet(" Identificadas por la presencia de unidades de medida físicas (unidades, cajas, metros, kilogramos), códigos de referencia SKU, descripciones de bienes tangibles, direcciones de despacho/bodega e indicaciones de logística de entrega.", "Órdenes de Compra de Producto:")
    add_bullet(" Identificadas por conceptos de consultoría, horas de desarrollo, honorarios profesionales, soporte técnico, actividades de mantenimiento, licencias de software, cronogramas de hitos o actas de entrega.", "Órdenes de Compra de Servicio:")

    add_h3("Jerarquización y Discriminación Documental")
    add_body("Un correo de orden de compra suele llegar con múltiples archivos adjuntos que confunden a un operador humano. El sistema ejecuta una jerarquización de adjuntos:")
    add_bullet(" Se identifica el documento que formaliza la transacción (generalmente titulado 'Orden de Compra', 'Purchase Order' u 'Orden de Servicio' debidamente numerada y valorizada).", "1. Documento Principal (Core):")
    add_bullet(" Cotizaciones previas, documentos de identidad tributaria (RUT), términos de referencia o pólizas de cumplimiento, los cuales quedan vinculados como metadatos secundarios al expediente de la OC principal.", "2. Documentos de Soporte (Anexos):")

    add_h3("Extracción y Enrutamiento a Servicios Internos")
    add_bullet(" Número de OC, Razón Social del Cliente/Proveedor, NIT, Ítems o conceptos detallados, Fechas pactadas de entrega y Monto total contratado.", "Datos Extraídos:")
    add_bullet(" Los expedientes categorizados se insertan en la plataforma de Servicios Internos con etiquetas claras (OC-PRODUCTO u OC-SERVICIO), permitiendo que los analistas de compras gestionen directamente el aprovisionamiento o la programación del servicio sin triage manual.", "Direccionamiento:")

    add_h2("3.3. Proceso de PQRS (Servicio al Cliente - SAC)")
    add_body("El canal de atención de Peticiones, Quejas, Reclamos y Solicitudes requiere una interpretación profunda del lenguaje natural, dado que los usuarios finales rara vez estructuran sus mensajes bajo taxonomías formales.")

    add_h3("Comprensión Semántica de Lenguaje Coloquial (NLU)")
    add_body("El sistema no se basa en palabras clave rígidas (como buscar únicamente 'PQRS'), sino en el análisis semántico de la intención del remitente. Por ejemplo, ante un mensaje como: 'Buenas tardes, llevo varios días esperando respuesta sobre mi solicitud y nadie me ha informado qué está pasando con mi cuenta...', el modelo de lenguaje identifica de inmediato una Queja / Reclamo por Falta de Oportunidad en la Atención, reconociendo la frustración del usuario aun cuando no se use terminología técnica o jurídica.")

    add_h3("Extracción de Entidades y Priorización Automática")
    add_bullet(" Nombre del cliente, Documento de identidad (cédula o NIT), Datos de contacto, Identificación del programa académico o servicio contratado, y Resumen sintético del motivo del caso.", "Metadatos Extraídos:")
    add_bullet(" Evaluación del tono del mensaje (Neutral, Insatisfecho, Altamente Crítico/Amenaza de escalamiento legal o entes de control).", "Análisis de Sentimiento y Severidad:")
    add_bullet(" Alta Prioridad (SLA < 4h) para reclamos económicos o amenazas jurídicas; Media Prioridad (SLA < 24h) para solicitudes de soporte operativo; Baja Prioridad (SLA < 48h) para consultas informativas o sugerencias generales.", "Matriz de Priorización:")

    add_h3("Enrutamiento a Servicio al Cliente (SAC)")
    add_body("El sistema genera un ticket automático en la plataforma de CRM/Mesa de Ayuda de RIWI, precargando la tipificación, el resumen estructurado, los adjuntos normalizados y el nivel de prioridad sugerido, enviando una confirmación automática con número de radicado al cliente.")

    add_h2("3.4. Tratamiento de Comunicaciones Generales y No Catalogables")
    add_body("Aquellos correos que no correspondan a facturación, órdenes de compra ni PQRS (tales como boletines informativos, comunicaciones interinstitucionales, ofertas comerciales entrantes, notificaciones automáticas o spam) son filtrados en una etapa temprana. Los correos con contenido corporativo legítimo pero no encasillable en los 3 procesos principales son etiquetados como 'Comunicaciones Administrativas Generales' y dirigidos a una bandeja de lectura unificada sin generar interrupciones ni tareas manuales ficticias en las áreas operativas.")

    # ==================== 4. ARQUITECTURA DE LA SOLUCIÓN ====================
    add_h1("4. ARQUITECTURA DE LA SOLUCIÓN")
    add_h2("4.1. Diagrama de Arquitectura de Alto Nivel")
    add_body("A continuación se presenta la arquitectura en capas diseñada bajo el principio de microservicios, eventos asíncronos y desacoplamiento estructural:")

    # Insert Diagrama Arquitectura
    add_image_centered("/home/ddamago/Projects/buzoncorporativoRIWI/Propuesta/assets/diagrama_arquitectura.png",
                       width_inches=6.2, caption="Figura 2: Arquitectura Empresarial por Capas de SmartInbox RIWI.")

    add_h2("4.2. Descripción Detallada de Componentes")
    add_bullet(" Punto único de contacto alojado en el proveedor de mensajería empresarial (Microsoft 365 Exchange Online o Google Workspace). No sufre alteraciones de configuración ni reenvíos masivos visibles.", "1. Buzón Corporativo (info@riwi.io):")
    add_bullet(" Servicio reactivo basado en eventos de subscripción (webhooks). Cada vez que un nuevo mensaje ingresa al buzón, el servidor de correo emite un evento instantáneo hacia la infraestructura de procesamiento, eliminando la necesidad de sondeos periódicos (polling).", "2. Webhook Event Listener (API Graph):")
    add_bullet(" Componente esencial para garantizar la resiliencia del sistema ante picos repentinos de tráfico (ej. cierre de mes contable con cientos de facturas recibidas en minutos). Garantiza entrega at-least-once, reintentos con retraso exponencial y aislamiento de fallos mediante Dead-Letter Queues (DLQ).", "3. Cola de Mensajes Transaccional (Message Broker):")
    add_bullet(" Coordina la ejecución ordenada de las distintas herramientas de extracción y validación, manteniendo el estado de cada transacción.", "4. Orquestador Asíncrono de Procesos:")
    add_bullet(" Microservicio de alto rendimiento especializado en abrir archivos .zip, comprobar firmas digitales y parsear tags XML de la DIAN sin costo de inferencia por IA.", "5. Parser Determinista XML / UBL 2.1:")
    add_bullet(" Extrae pares clave-valor y estructuras tabulares a partir de órdenes de compra en formato PDF o imágenes escaneadas.", "6. Servicio de Document Intelligence / OCR:")
    add_bullet(" Modelo fundacional ajustado mediante Few-Shot Prompting e instrucciones de sistema seguras para clasificar intenciones, resumir quejas y calcular el sentimiento en PQRS.", "7. Modelo de Lenguaje para Clasificación y Semántica (LLM):")
    add_bullet(" Evalúa coherencia numérica (subtotales + impuestos = total), comprueba la existencia de proveedores en la base de datos local y verifica que no falten campos mandatorios.", "8. Motor de Validación de Reglas de Negocio:")
    add_bullet(" Almacena de forma inmutable los correos en formato MIME original (.eml) y sus adjuntos descomprimidos, con cifrado en reposo (AES-256) y políticas de retención temporal.", "9. Almacenamiento de Objetos Cifrado (Object Storage):")
    add_bullet(" Registra cada estado del ciclo de vida del mensaje, scores de confianza, identificadores tributarios, tiempos de atención y bitácora de auditoría.", "10. Base de Datos Operativa Relacional (SQL):")
    add_bullet(" Módulos que traducen el JSON enriquecido final hacia las APIs REST del ERP contable de RIWI, la herramienta de compras de Servicios Internos y el CRM de Atención al Cliente.", "11. Conectores API hacia Sistemas Core:")
    add_bullet(" Interfaz web optimizada donde los analistas atienden exclusivamente correos con baja confianza o alertas de inconsistencia, permitiendo resolver incidencias en segundos.", "12. Consola de Resolución Rápida (Human-in-the-Loop UI):")

    # ==================== 5. AUTOMATIZACIÓN VS. IA ====================
    add_h1("5. AUTOMATIZACIÓN TRADICIONAL VS. INTELIGENCIA ARTIFICIAL")
    add_body("Uno de los principios de diseño fundamentales de la presente propuesta es el uso riguroso, eficiente y justificado de la tecnología. Aplicar Inteligencia Artificial para tareas que pueden resolverse con algoritmos deterministas encarece la solución, introduce latencia innecesaria y añade un riesgo de alucinación inaceptable en operaciones corporativas.")

    add_h2("5.1. Matriz de Asignación y Racional Técnico")
    
    t_mat = doc.add_table(rows=10, cols=3)
    t_mat.alignment = WD_TABLE_ALIGNMENT.CENTER
    m_headers = ["Actividad del Proceso", "Mecanismo Recomendado", "Justificación Técnica de la Decisión"]
    for j, h in enumerate(m_headers):
        cell = t_mat.rows[0].cells[j]
        cell.text = h
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_background(cell, "1B365D")
        set_cell_margins(cell, 100, 100, 120, 120)
        
    mat_rows = [
        ("Captura y filtrado inicial de correo", "Automatización por Reglas (APIs / Webhooks)", "La intercepción de encabezados (remitente, asunto, fecha) es determinista, de costo computacional cercano a cero y 100% predecible."),
        ("Descompresión y validación fiscal (.zip / XML)", "Automatización por Reglas (Parsers XML nativos)", "El estándar UBL 2.1 de la DIAN es estructurado. Utilizar IA generativa para leer un XML bien formado sería ineficiente y riesgoso. Un parser XSD garantiza cero margen de error en cifras contables."),
        ("Validaciones matemáticas de montos", "Automatización por Reglas (Lógica Aritmética)", "La verificación de Subtotal + Impuestos = Total debe ser exacta. Los LLMs no son calculadoras confiables; el código tradicional sí lo es."),
        ("Detección de duplicados", "Automatización por Reglas (Consultas SQL Indexadas)", "Comparar hashes de archivos, códigos CUFE o combinaciones NIT + Número de Factura contra la base de datos es una operación de consulta determinista instantánea."),
        ("Clasificación de OCs (Producto vs. Servicio)", "IA Generativa / Clasificador NLP", "La distinción entre un bien y un servicio en descripciones heterogéneas requiere comprensión de contexto semántico que no puede capturarse eficientemente con listas de palabras clave estáticas."),
        ("Jerarquización de adjuntos en OCs", "Extracción Estructurada + Reglas Heurísticas", "La combinación de metadatos del archivo (nombres, páginas, encabezados OCR) permite identificar el contrato principal vs. cotizaciones anexas."),
        ("Interpretación y tipificación de PQRS", "IA Generativa (Modelos de Lenguaje - LLM)", "El lenguaje coloquial humano es ambiguo, variado y emocional. Solo un modelo de lenguaje puede inferir que 'llevo días sin respuesta' constituye un reclamo prioritario."),
        ("Análisis de sentimiento y severidad en PQRS", "IA Generativa (LLM)", "Requiere interpretar matices emocionales, frustración o urgencia implícita en la redacción del usuario."),
        ("Enrutamiento e inserción en ERP/CRM", "Automatización por Reglas (Conectores API REST)", "La comunicación intersistemas debe ser transaccional, con manejo estricto de esquemas JSON y códigos de respuesta HTTP.")
    ]
    for i, r_data in enumerate(mat_rows):
        row = t_mat.rows[i+1]
        for j, val in enumerate(r_data):
            cell = row.cells[j]
            cell.text = val
            cell.paragraphs[0].runs[0].font.size = Pt(9)
            cell.paragraphs[0].runs[0].font.color.rgb = c_dark
            if j == 0:
                cell.paragraphs[0].runs[0].font.bold = True
            elif j == 1:
                cell.paragraphs[0].runs[0].font.color.rgb = c_secondary
            set_cell_margins(cell, 80, 80, 100, 100)
            if i % 2 == 1:
                set_cell_background(cell, "F7FAFC")

    add_h2("5.2. Definición del Rol de los Agentes de IA")
    add_body("Para evitar la sobre-ingeniería común de desplegar múltiples agentes autónomos conversando entre sí (lo cual añade latencia, costos y descontrol estocástico), proponemos una arquitectura de Agente Especializado Único con Herramientas Deterministas (Tool Calling / Function Calling):")
    add_bullet(" Ejecuta el script determinista si detecta un .zip o .xml.", "Tool 1: parse_dian_xml(file_path):")
    add_bullet(" Invoca el servicio de visión si es un PDF o imagen.", "Tool 2: extract_document_ocr(file_path):")
    add_bullet(" Clasifica la intención y extrae entidades del texto libre.", "Tool 3: classify_business_intent(email_body, attachments_summary):")
    add_bullet(" Verifica existencia previa en la base de datos de RIWI.", "Tool 4: check_database_duplicates(cufe_or_id):")
    add_body("Este enfoque centrado en herramientas garantiza que el agente actúe como un cerebro de orquestación y razonamiento semántico, pero delegue la precisión numérica y las reglas de negocio a funciones de código duro.")

    add_h2("5.3. Límites Infranqueables de la IA (Dónde NO se Permite Decisión Autónoma)")
    add_bullet(" La IA puede extraer y validar los datos de una factura, pero jamás puede autorizar un desembolso o pago financiero. La aprobación sigue residiendo en los directores de Tesorería dentro del ERP.", "1. Aprobación o Dispersión de Pagos:")
    add_bullet(" Si una factura presenta inconsistencias, el sistema no emite un rechazo ante la DIAN de forma unilateral; suspende el trámite y notifica al área contable para su validación formal.", "2. Rechazo Definitivo de Facturas con Efecto Legal:")
    add_bullet(" El sistema nunca redondea, corrige o asume montos si no cuadran matemáticamente; marca la discordancia y la turna a excepción.", "3. Modificación de Cifras Contables:")
    add_bullet(" Ninguna queja o reclamo puede ser marcada como 'descartada' o 'spam' de forma autónoma por la IA si proviene de un remitente con historial de cliente o si expresa insatisfacción.", "4. Descarte o Eliminación de PQRS:")

    # ==================== 6. FLUJO DE PROCESAMIENTO ====================
    add_h1("6. FLUJO DE PROCESAMIENTO END-TO-END")
    add_body("El procesamiento de una comunicación entrante en info@riwi.io sigue un ciclo de vida estrictamente secuencial y auditable, dividido en siete (7) etapas consecutivas:")

    # Insert Diagrama Flujo
    add_image_centered("/home/ddamago/Projects/buzoncorporativoRIWI/Propuesta/assets/diagrama_flujo.png",
                       width_inches=6.2, caption="Figura 3: Flujo de Procesamiento Lógico y Compuertas de Decisión en SmartInbox RIWI.")

    add_h2("6.1. Descripción Paso a Paso del Ciclo de Vida")
    add_bullet(" El correo arriba a info@riwi.io. El listener de la API emite el payload del mensaje hacia el Gateway y se genera un Identificador Único Global (Trace-ID) que acompañará al mensaje durante toda su vida operativa.", "Etapa 1: Recepción e Ingesta:")
    add_bullet(" El mensaje se descompone en metadatos, cuerpo y adjuntos. Los adjuntos se envían a un contenedor de almacenamiento de objetos cifrado (Blob Storage) y se ejecuta un análisis antivirus/antimalware determinista.", "Etapa 2: Sanitización y Almacenamiento Seguro:")
    add_bullet(" El orquestador evalúa si el correo contiene archivos comprimidos .zip o .xml. Si detecta un .zip, abre el archivo en memoria y busca la presencia de XMLs de la DIAN. Si se confirma la estructura DIAN, pasa a la Ruta Factura Inmediata (4A). Si no, pasa a la Ruta Cognitiva General (4B).", "Etapa 3: Compuerta de Decisión Rápida (Validación Factura DIAN):")
    add_bullet(" Si hay documentos PDF/imágenes, el motor de OCR extrae el texto manteniendo la disposición tabular. El Agente LLM procesa conjuntamente el cuerpo y los adjuntos para clasificar en Orden de Compra (Producto vs. Servicio) o PQRS (Tipificación y Severidad).", "Etapa 4B: Clasificación y Extracción Cognitiva:")
    add_bullet(" Se contrastan los datos contra las reglas del negocio (identificación de NIT/Cédula, coherencia de montos, proveedor activo). El sistema calcula un Índice de Confianza Compuesto (C) entre 0.00 y 1.00.", "Etapa 5: Validación de Reglas de Negocio y Cálculo de Confianza:")
    add_bullet(" Si C >= 0.90 y no hay inconsistencias, se ejecuta Straight-Through Processing (STP) hacia el ERP, Compras o CRM. Si C < 0.90 o hay conflicto de reglas, se desvía a la bandeja Human-in-the-Loop.", "Etapa 6: Direccionamiento o Derivación Human-in-the-Loop:")
    add_bullet(" Se consolidan los resultados en la base de datos de auditoría y se emite un evento a la plataforma de monitoreo para actualizar los indicadores del día.", "Etapa 7: Registro Transaccional y Emisión de Métricas:")

    # ==================== 7. MANEJO DE EXCEPCIONES ====================
    add_h1("7. MANEJO DE EXCEPCIONES (HUMAN-IN-THE-LOOP CONCEPTUAL)")
    add_body("En consonancia con las directrices de la arquitectura y el principio fundamental de no trasladar la carga de trabajo, el manejo de excepciones en SmartInbox RIWI no consiste en enviar correos no clasificados a una persona para que empiece de cero, sino en ofrecer una experiencia de resolución asistida y ultra-eficiente.")

    add_h2("7.1. Criterios de Disparo de Incertidumbre y Excepción")
    add_body("Una comunicación ingresa al estado de excepción exclusivamente bajo dos premisas objetivas:")
    add_bullet(" El modelo de IA no alcanza el umbral de confianza mínimo requerido (C < 0.90) para clasificar la categoría del correo o para extraer un campo mandatorio (ej. el mensaje no aclara si es una queja o una solicitud comercial).", "1. Incertidumbre Probabilística:")
    add_bullet(" La información fue extraída, pero contradice una regla dura de validación (ej. la suma de ítems no coincide con el total de la orden de compra, el archivo adjunto está corrupto o protegido con contraseña, o la factura carece de archivo XML de la DIAN).", "2. Inconsistencia Lógica o de Negocio:")

    add_h2("7.2. Protocolo de Enrutamiento y Consola 'Human-in-the-Loop'")
    add_bullet(" El registro se marca automáticamente con el estado 'Requiere Revisión Humana', asociándole el motivo exacto de la alerta, el nivel de confianza, los datos pre-extraídos y el área responsable sugerida (Tesorería, Servicios Internos o SAC).", "1. Marcación con Metadata Explicativa:")
    add_bullet(" El analista del área no debe buscar el correo en Outlook ni descargar adjuntos manualmente. La consola le presenta una vista dividida (Split-Screen): a la izquierda, el documento o correo original; a la derecha, el formulario con los campos pre-llenados por el sistema y el campo en conflicto resaltado en color ámbar. El operador solo debe confirmar, corregir el dato específico o seleccionar la categoría correcta con un solo clic.", "2. Experiencia de Resolución en la Consola Web ('No trasladar la carga'):")
    add_bullet(" Una vez el humano valida o corrige, el sistema retoma el flujo automatizado: envía los datos al ERP/CRM y emite la confirmación. La decisión humana queda firmada con su usuario, fecha y valor corregido en el log de auditoría. Este evento se almacena como dato de entrenamiento supervisado (Ground Truth) para la mejora continua del sistema.", "3. Cierre de Excepción y Aprendizaje:")

    # ==================== 8. TRAZABILIDAD Y AUDITORÍA ====================
    add_h1("8. TRAZABILIDAD Y AUDITORÍA EMPRESARIAL")
    add_body("La trazabilidad integral es el pilar que garantiza que la automatización no se convierta en una 'caja negra' incontrolable. La organización debe estar facultada para auditar cualquier decisión en cualquier momento.")

    add_h2("8.1. Registro Inmutable por Evento (Audit Ledger)")
    add_body("Cada mensaje recibido en info@riwi.io da origen a un registro de auditoría estructurado en una base de datos relacional protegida contra alteraciones. Los datos mínimos registrados por cada transacción incluyen:")
    add_bullet(" Identificador Único Global (UUIDv4) asignado en la ingesta.", "• Trace-ID:")
    add_bullet(" Timestamp exacto con precisión de milisegundos y copia íntegra de cabeceras RFC 822.", "• Fecha, Hora y Metadatos del Mensaje:")
    add_bullet(" Nombres de archivo, tamaños en bytes y hashes criptográficos SHA-256.", "• Adjuntos Detectados:")
    add_bullet(" Factura Electrónica, Orden de Compra (Producto/Servicio), PQRS o Comunicación General.", "• Clasificación Asignada:")
    add_bullet(" Regla determinista DIAN XML, Heurística de negocio o Modelo LLM con número de versión.", "• Mecanismo de Clasificación Utilizado:")
    add_bullet(" Valor numérico entre 0.00 y 1.00.", "• Score de Confianza Compuesto:")
    add_bullet(" JSON estructurado con los valores extraídos (CUFE, NIT, montos, número de OC, radicado PQRS, etc.).", "• Metadatos y Entidades Extraídas:")
    add_bullet(" Endpoint de ERP Cuentas por Pagar, Compras o CRM SAC con código de respuesta HTTP recibido.", "• Destino y Confirmación de Enrutamiento:")
    add_bullet(" Booleano indicador de intervención, usuario corporativo que intervino, timestamp y datos ajustados.", "• Historial de Intervención Humana:")

    add_h2("8.2. Preguntas Clave del Negocio Respaldadas por la Trazabilidad")
    add_bullet(" Timestamp de recepción con precisión de milisegundos y copia del encabezado del correo.", "¿Cuándo llegó exactamente una factura en reclamo?")
    add_bullet(" Registro de la justificación técnica emitida por el modelo de IA o la regla de negocio activada.", "¿Por qué un correo fue clasificado como Orden de Compra y no como PQRS?")
    add_bullet(" Respaldo de los valores exactos enviados vía API versus los contenidos en el documento original.", "¿Qué datos específicos fueron extraídos y transferidos al ERP?")
    add_bullet(" Registro explícito del score de confianza probabilístico.", "¿Cuál fue el nivel de certeza de la decisión?")
    add_bullet(" Identificador del usuario corporativo, fecha de la intervención y comparativa del valor antes y después de la corrección manual.", "¿Quién intervino en un caso de excepción y qué modificó?")
    add_bullet(" Métricas precisas de latencia desde la entrada hasta la radicación final.", "¿Cuánto tiempo tomó todo el ciclo?")

    add_h2("8.3. Criterios de Seguridad, Cifrado y Retención Normativa")
    add_bullet(" Comunicaciones en tránsito cifradas bajo protocolo TLS 1.3. Datos y documentos en reposo cifrados mediante el algoritmo AES-256.", "Cifrado de Extremo a Extremo:")
    add_bullet(" Los datos personales extraídos de PQRS y correos son clasificados como información confidencial, con controles de acceso basados en roles (RBAC). Solo el personal autorizado de SAC y Auditoría puede consultar la identidad y los datos de contacto de los clientes.", "Cumplimiento de Habeas Data (Ley 1581 de 2012):")
    add_bullet(" Los archivos originales y sus logs no pueden ser modificados ni eliminados por los operadores, garantizando validez probatoria ante posibles inspecciones tributarias (DIAN) o demandas civiles.", "Inmutabilidad y Retención Documental:")

    # ==================== 9. REPORTES E INDICADORES ====================
    add_h1("9. REPORTES E INDICADORES DE GESTIÓN")
    add_body("Para garantizar una gobernanza efectiva de la operación sin necesidad de que los coordinadores tengan que ingresar a revisar correos manualmente, la solución incorpora un sistema de reportería y analítica en tiempo real.")

    add_h2("9.1. Cuadro de Mando Diario (Executive & Operational Dashboard)")
    add_body("El sistema genera un resumen consolidado diario estructurado en indicadores cuantitativos y cualitativos:")

    t_rep = doc.add_table(rows=6, cols=6)
    t_rep.alignment = WD_TABLE_ALIGNMENT.CENTER
    rep_headers = ["Categoría de Proceso", "Recibidos", "Procesados (STP)", "Excepciones", "Pendientes", "Tasa Auto (%)"]
    for j, h in enumerate(rep_headers):
        cell = t_rep.rows[0].cells[j]
        cell.text = h
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(8.5)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_background(cell, "1B365D")
        set_cell_margins(cell, 100, 100, 100, 100)

    rep_rows = [
        ("Facturas Electrónicas", "192", "181", "9", "2", "94.3%"),
        ("Órdenes de Compra", "68", "61", "5", "2", "89.7%"),
        ("PQRS (SAC)", "54", "48", "4", "2", "88.9%"),
        ("Comunicaciones Generales", "35", "32", "3", "0", "91.4%"),
        ("TOTAL CONSOLIDADO", "349", "322", "21", "6", "92.3%")
    ]
    for i, r_data in enumerate(rep_rows):
        row = t_rep.rows[i+1]
        for j, val in enumerate(r_data):
            cell = row.cells[j]
            cell.text = val
            cell.paragraphs[0].runs[0].font.size = Pt(8.5)
            cell.paragraphs[0].runs[0].font.color.rgb = c_dark
            if i == len(rep_rows) - 1 or j == 0:
                cell.paragraphs[0].runs[0].font.bold = True
            set_cell_margins(cell, 60, 60, 80, 80)
            if i % 2 == 1:
                set_cell_background(cell, "F7FAFC")
            if i == len(rep_rows) - 1:
                set_cell_background(cell, "EDF2F7")

    add_h3("Indicadores Clave de Desempeño (KPIs) Operativos")
    add_bullet(" 92.3% procesados de punta a punta sin intervención humana (Meta corporativa: > 85%).", "KPI 1: Tasa Global Straight-Through Processing (STP):")
    add_bullet(" 38 segundos desde la llegada a info@riwi.io hasta la inserción en el sistema destino (vs. 6.5 horas en el modelo manual anterior).", "KPI 2: Tiempo Medio de Radicación:")
    add_bullet(" $485.620.000 COP procesados y conciliados con validación DIAN UBL 2.1.", "KPI 3: Monto Total Facturado Gestionado:")
    add_bullet(" 8.5 minutos por caso en la consola Human-in-the-Loop (Meta: < 15 minutos).", "KPI 4: Tiempo Medio de Resolución Humana:")

    add_h2("9.2. Mecanismos de Generación y Distribución Automatizada")
    add_bullet(" A las 07:00 hrs y a las 18:00 hrs, el sistema compila automáticamente el reporte consolidado y lo despacha vía correo electrónico cifrado y canal interno de Microsoft Teams/Slack a la Dirección de Operaciones, Tesorería y SAC.", "1. Notificación Matutina y Vespertina (Executive Digest):")
    add_bullet(" Los líderes de área disponen de un tablero dinámico (construido en Power BI / Metabase) donde pueden filtrar métricas por rango de fechas, proveedor, tipo de documento o estado de excepción, permitiendo auditorías en vivo sin intervenir la operación técnica.", "2. Dashboard Interactivo en Tiempo Real:")

    # ==================== 10. PROPUESTA TECNOLÓGICA ====================
    add_h1("10. PROPUESTA TECNOLÓGICA Y JUSTIFICACIÓN DEL STACK")
    add_body("La selección de tecnologías para SmartInbox RIWI responde a criterios de alta disponibilidad, bajo costo transaccional, seguridad empresarial y prevención del bloqueo de proveedor (vendor lock-in), asegurando que la empresa no dependa exclusivamente de una sola plataforma propietaria.")

    add_h2("10.1. Selección del Stack Tecnológico Recomendado")
    add_bullet(" React con Tailwind CSS para una interfaz ligera, intuitiva y reactiva; Power BI / Metabase para tableros directivos.", "Capa de Presentación & Gestión:")
    add_bullet(" Python 3.11 con FastAPI para ingesta asíncrona de alto rendimiento; Temporal.io (o n8n Enterprise) para la orquestación con ejecución duradera; Microsoft Graph API / Google Workspace REST API para integración de correo.", "Capa de Aplicación y Orquestación:")
    add_bullet(" Parser nativo en Python (lxml / xmltodict) para validación UBL 2.1 DIAN sin costo de inferencia; Azure AI Document Intelligence para OCR y tablas; Azure OpenAI (GPT-4o-mini / GPT-4o) o Google Vertex AI bajo acuerdo empresarial confidencial (los datos de RIWI no se usan para reentrenar modelos).", "Capa de Inteligencia Artificial & Extracción:")
    add_bullet(" Azure Service Bus / AWS SQS para desacoplamiento y reintentos; PostgreSQL gestionado para metadatos y auditoría; Azure Blob Storage / AWS S3 con cifrado AES-256 para archivos adjuntos; contenedores Docker en Azure Container Apps o AWS ECS.", "Capa de Infraestructura, Persistencia & Bus:")

    add_h2("10.2. Justificación Técnica y Económica")
    add_bullet(" Python es el estándar de la industria en procesamiento de datos y lenguaje natural. FastAPI ofrece un rendimiento asíncrono excepcional con soporte nativo de tipado y esquemas Pydantic, ideal para procesar payloads de correo con latencias menores a 50 milisegundos.", "¿Por qué Python + FastAPI para la Ingesta y Parsers?")
    add_bullet(" A diferencia de herramientas puramente iPaaS como Zapier (que presentan costos prohibitivos por ejecución a gran volumen y carecen de control fino de estado), un orquestador como Temporal.io o n8n Enterprise permite flujos de trabajo asíncronos duraderos (Durable Execution). Si un servicio externo o API del ERP se cae temporalmente, el flujo no se pierde; queda pausado y reintenta de forma segura sin intervención técnica.", "¿Por qué Temporal.io / n8n Enterprise para la Orquestación?")
    add_bullet(" La clasificación de intenciones y el análisis de sentimiento no requieren modelos masivos de costo excesivo. Los modelos optimizados ofrecen tiempos de respuesta inferiores a 1 segundo y costos por token mínimos. Crucialmente, la suscripción empresarial garantiza contractualmente que ningún dato corporativo, factura o correo de RIWI es utilizado para entrenar modelos públicos.", "¿Por qué Azure OpenAI / Vertex AI con Modelos Ligeros (GPT-4o-mini / Gemini Flash)?")
    add_bullet(" El uso de librerías nativas (lxml) para el procesamiento de facturas DIAN dentro de archivos .zip reduce el costo de procesamiento por factura a prácticamente cero centavos de dólar y elimina el riesgo de error numérico, reservando el presupuesto de IA para casos no estructurados (PQRS y órdenes de compra complejas).", "¿Por qué Parser XML Local frente a OCR para Facturas?")

    # ==================== 11. ROADMAP POR FASES ====================
    add_h1("11. ROADMAP DE IMPLEMENTACIÓN POR FASES")
    add_body("Para asegurar un despliegue controlado, mitigar riesgos operativos y ajustarse de forma realista a la capacidad operativa de un equipo de consultoría de tres (3) especialistas, se propone un plan de trabajo estructurado en cuatro (4) fases secuenciales durante un período total de catorce (14) semanas.")

    add_h2("11.1. Plan de Trabajo Detallado (14 Semanas)")
    
    t_road = doc.add_table(rows=5, cols=4)
    t_road.alignment = WD_TABLE_ALIGNMENT.CENTER
    r_headers = ["Fase", "Duración", "Foco Principal", "Entregables Clave"]
    for j, h in enumerate(r_headers):
        cell = t_road.rows[0].cells[j]
        cell.text = h
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(8.5)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_background(cell, "1B365D")
        set_cell_margins(cell, 100, 100, 100, 100)

    road_rows = [
        ("Fase 1: Cimientos & Facturación", "Semanas 1-4", "Infraestructura base, ingesta segura y facturación electrónica DIAN.", "Webhook Graph API, bus de mensajería, almacenamiento seguro cifrado, parser .zip/XML UBL 2.1 e integración Cuentas por Pagar."),
        ("Fase 2: OCs, PQRS & Human-in-the-Loop", "Semanas 5-8", "Modelos cognitivos y consola de resolución de excepciones.", "Pipeline OCR y clasificación OCs (Producto vs. Servicio), NLU de PQRS (SAC), consola web Human-in-the-Loop y conectores API."),
        ("Fase 3: Trazabilidad, Dashboards & Piloto", "Semanas 9-11", "Observabilidad integral y validación en modo sombra.", "Base de datos de auditoría relacional con Trace-ID, generador de reportes diarios, tableros Power BI y piloto en modo sombra (Shadow Testing)."),
        ("Fase 4: Despliegue, Monitoreo & Cierre", "Semanas 12-14", "Puesta en producción gradual y transferencia.", "Despliegue escalonado (Canary Rollout 25%-100%), capacitación a operadores de Tesorería, Compras y SAC, y entrega de documentación final.")
    ]
    for i, r_data in enumerate(road_rows):
        row = t_road.rows[i+1]
        for j, val in enumerate(r_data):
            cell = row.cells[j]
            cell.text = val
            cell.paragraphs[0].runs[0].font.size = Pt(8.5)
            cell.paragraphs[0].runs[0].font.color.rgb = c_dark
            if j == 0:
                cell.paragraphs[0].runs[0].font.bold = True
            set_cell_margins(cell, 60, 60, 80, 80)
            if i % 2 == 1:
                set_cell_background(cell, "F7FAFC")

    add_h2("11.2. Asignación de Roles y Responsabilidades del Equipo Consultor")
    
    t_roles = doc.add_table(rows=4, cols=3)
    t_roles.alignment = WD_TABLE_ALIGNMENT.CENTER
    role_headers = ["Consultor", "Rol Principal", "Responsabilidades Específicas"]
    for j, h in enumerate(role_headers):
        cell = t_roles.rows[0].cells[j]
        cell.text = h
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(8.5)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_background(cell, "1B365D")
        set_cell_margins(cell, 100, 100, 100, 100)

    role_rows = [
        ("Daniel David Martinez Gonzalez", "Especialista en Arquitectura Cloud e Integración de Sistemas", "Configuración del Webhook Listener en Microsoft Graph / Google API; diseño y despliegue de infraestructura cloud, bus de mensajería y persistencia segura; construcción de conectores API hacia ERP y CRM; observabilidad y ciberseguridad."),
        ("Breyner De Jesus Manga Arias", "Especialista en Datos, Estándares DIAN & Extracción", "Desarrollo del motor determinista de descompresión de .zip y parsing XML UBL 2.1; diseño de validaciones matemáticas y reglas de negocio para Cuentas por Pagar; estructuración del modelo de datos de trazabilidad y esquema PostgreSQL; tableros en Power BI."),
        ("Joseph Romero", "Especialista en Inteligencia Artificial & Human-in-the-Loop", "Configuración y optimización de prompts y guardrails para LLMs; implementación del pipeline de OCR y clasificación semántica de OCs y PQRS; desarrollo de la interfaz web de la Consola Human-in-the-Loop; calibración de umbrales de confianza y mejora continua.")
    ]
    for i, r_data in enumerate(role_rows):
        row = t_roles.rows[i+1]
        for j, val in enumerate(r_data):
            cell = row.cells[j]
            cell.text = val
            cell.paragraphs[0].runs[0].font.size = Pt(8.5)
            cell.paragraphs[0].runs[0].font.color.rgb = c_dark
            if j == 0:
                cell.paragraphs[0].runs[0].font.bold = True
            elif j == 1:
                cell.paragraphs[0].runs[0].font.color.rgb = c_secondary
            set_cell_margins(cell, 60, 60, 80, 80)
            if i % 2 == 1:
                set_cell_background(cell, "F7FAFC")

    # ==================== 12. CONCLUSIÓN ====================
    add_h1("12. CONCLUSIÓN Y VALOR ESTRATÉGICO")
    add_body("La solución SmartInbox RIWI no es un experimento de automatización superficial ni una reubicación de tareas manuales; es un rediseño estratégico del canal de entrada corporativo de RIWI Barranquilla.")
    add_body("Al combinar la precisión quirúrgica de la automatización basada en reglas para los procesos fiscales (validación de XML UBL 2.1 en facturación electrónica) con la flexibilidad cognitiva de los modelos de lenguaje para la atención de clientes y compras, la organización logra:")
    add_bullet(" Preservar intacto su canal histórico info@riwi.io, protegiendo la relación con más de dos millones de clientes registrados.", "1. Continuidad Absoluta:")
    add_bullet(" Erradicar el cuello de botella operativo, reduciendo los tiempos de atención de horas a segundos.", "2. Eficiencia Operativa Radical:")
    add_bullet(" Liberar a sus colaboradores de la carga mecánica, permitiéndoles concentrarse exclusivamente en decisiones estratégicas de negocio, negociación con proveedores y resolución de casos de alto impacto.", "3. Empoderamiento del Talento Humano:")
    add_bullet(" Alcanzar una trazabilidad y control total, respaldada por auditoría inmutable, cumplimiento legal estricto y reportería ejecutiva automática.", "4. Gobernanza y Seguridad:")
    add_body("El equipo consultor queda a total disposición de la Dirección de RIWI Barranquilla para realizar la presentación ejecutiva de esta propuesta y dar inicio a la Fase 1 del proyecto.")

    # Save document
    output_path = "/home/ddamago/Projects/buzoncorporativoRIWI/Propuesta/Propuesta_Tecnica_Comercial_SmartInbox_RIWI.docx"
    doc.save(output_path)
    print(f"Document successfully created at {output_path}")

if __name__ == "__main__":
    create_document()
