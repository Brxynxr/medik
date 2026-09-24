import os
import subprocess
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

def set_cell_background(cell, fill_hex):
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_proposal_docx(output_docx):
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(1)
        s.bottom_margin = Inches(1)
        s.left_margin = Inches(1)
        s.right_margin = Inches(1)

    c_primary = RGBColor(27, 54, 93)     # Navy #1B365D
    c_secondary = RGBColor(43, 108, 176) # Blue #2B6CB0
    c_dark = RGBColor(45, 55, 72)        # Slate #2D3748
    c_gray = RGBColor(113, 128, 150)     # Gray #718096

    # PORTADA
    p_pre = doc.add_paragraph()
    p_pre.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_pre = p_pre.add_run("PROPUESTA TÉCNICA Y COMERCIAL DEFINITIVA — LISTA PARA PRODUCCIÓN\n")
    r_pre.font.name = "Arial"
    r_pre.font.size = Pt(13)
    r_pre.font.bold = True
    r_pre.font.color.rgb = c_secondary

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("AUTOMATIZACIÓN INTELIGENTE DEL BUZÓN CORPORATIVO DE RIWI\n")
    r_title.font.name = "Arial"
    r_title.font.size = Pt(21)
    r_title.font.bold = True
    r_title.font.color.rgb = c_primary

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run('“SmartInbox RIWI: Arquitectura de Ultra-Rendimiento ($0 USD), Doble Motor de Caché, Cascada Multi-Proveedor y Procesamiento de Documentos Degradados”\n')
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(11.5)
    r_sub.font.italic = True
    r_sub.font.color.rgb = c_dark

    p_div = doc.add_paragraph()
    p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_div = p_div.add_run("—" * 35 + "\n")
    r_div.font.color.rgb = c_gray

    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Cliente:", "RIWI Barranquilla"),
        ("Canal Objetivo:", "info@riwi.io (Punto Único de Entrada Inviolable)"),
        ("Presupuesto de Licenciamiento:", "100% Gratuito y Open Source ($0.00 USD)"),
        ("Fecha de Emisión:", "Versión Definitiva para Producción — Septiembre 2026")
    ]
    for i, (k, v) in enumerate(meta_data):
        row = meta_table.rows[i]
        row.cells[0].text = k
        row.cells[1].text = v
        row.cells[0].paragraphs[0].runs[0].font.bold = True
        row.cells[0].paragraphs[0].runs[0].font.color.rgb = c_primary
        row.cells[1].paragraphs[0].runs[0].font.color.rgb = c_dark
        row.cells[0].width = Inches(2.3)
        row.cells[1].width = Inches(4.2)

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(24)

    p_team = doc.add_paragraph()
    p_team.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_tt = p_team.add_run("EQUIPO CONSULTOR PROPONENTE")
    r_tt.font.name = "Arial"
    r_tt.font.size = Pt(12)
    r_tt.font.bold = True
    r_tt.font.color.rgb = c_primary

    team_table = doc.add_table(rows=3, cols=2)
    team_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    team_data = [
        ("Daniel David Martinez Gonzalez", "Especialista en Arquitectura Open Source, Concurrencia e Integración"),
        ("Breyner De Jesus Manga Arias", "Especialista en Datos, Preprocesamiento OpenCV & Estándares DIAN"),
        ("Joseph Romero", "Especialista en Visión Computacional, Inferencia VLM & Modelos de Lenguaje")
    ]
    for i, (name, role) in enumerate(team_data):
        row = team_table.rows[i]
        row.cells[0].text = name
        row.cells[1].text = role
        row.cells[0].paragraphs[0].runs[0].font.bold = True
        row.cells[0].paragraphs[0].runs[0].font.color.rgb = c_dark
        row.cells[1].paragraphs[0].runs[0].font.italic = True
        row.cells[1].paragraphs[0].runs[0].font.color.rgb = c_secondary
        row.cells[0].width = Inches(2.8)
        row.cells[1].width = Inches(3.7)

    doc.add_page_break()

    def h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(15)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = "Arial"
        r.font.size = Pt(13.5)
        r.font.bold = True
        r.font.color.rgb = c_primary
        return p

    def h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = "Arial"
        r.font.size = Pt(11.5)
        r.font.bold = True
        r.font.color.rgb = c_secondary
        return p

    def body(text, bold_pre=None):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        if bold_pre:
            r_pre = p.add_run(bold_pre)
            r_pre.font.name = "Calibri"
            r_pre.font.size = Pt(10)
            r_pre.font.bold = True
            r_pre.font.color.rgb = c_dark
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(10)
        r.font.color.rgb = c_dark
        return p

    def bullet(text, bold_pre=None):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        if bold_pre:
            r_pre = p.add_run(bold_pre)
            r_pre.font.name = "Calibri"
            r_pre.font.size = Pt(10)
            r_pre.font.bold = True
            r_pre.font.color.rgb = c_dark
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(10)
        r.font.color.rgb = c_dark
        return p

    def img(path, width=6.0, cap=""):
        if os.path.exists(path):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(4)
            p.add_run().add_picture(path, width=Inches(width))
            if cap:
                p_c = doc.add_paragraph()
                p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_c.paragraph_format.space_after = Pt(6)
                r_c = p_c.add_run(cap)
                r_c.font.name = "Calibri"
                r_c.font.size = Pt(8.5)
                r_c.font.italic = True
                r_c.font.color.rgb = c_gray

    # 1. RESUMEN EJECUTIVO
    h1("1. RESUMEN EJECUTIVO")
    body("La presente propuesta técnica y comercial establece el diseño arquitectural definitivo de SmartInbox RIWI, una solución concebida para operar en un entorno de producción real, resolviendo de forma integral el flujo de comunicaciones del buzón info@riwi.io con máxima velocidad, costo cero de licenciamiento y una estricta minimización del uso de Inteligencia Artificial.")
    body("Entendiendo que en el mundo productivo la Inteligencia Artificial debe usarse como una herramienta quirúrgica y no como un fin en sí misma, la arquitectura asigna el 75% de la carga de trabajo a algoritmos deterministas de alta velocidad (C++, álgebra lineal y reglas de negocio), reservando la IA únicamente para el 25% donde se requiere percepción humana (OCR neuronal sobre texto borroso, detección visual de objetos y comprensión de lenguaje libre).")
    
    h2("Pilares de la Solución de Producción")
    bullet(" Antes de invocar cualquier modelo u OCR, el sistema calcula el hash SHA-256 del documento. Si el archivo ya fue procesado antes, retorna los metadatos en 0.002 segundos, ahorrando el 100% del procesamiento.", "Doble Motor de Caché Criptográfico:")
    bullet(" Para el texto semántico (PQRS), el sistema consulta Tier 1: Groq Cloud API (LPU a 600 tok/s en 0.2s); si la cuota se agota, conmuta a Tier 2: Google AI Studio (Gemini 2.0 Flash Free); y si no hay internet, conmuta a Tier 3: Ollama local (Llama 3.2 3B). Cero caídas y cero costos.", "Cascada Multi-Proveedor Gratuita:")
    bullet(" Pipeline de visión matemática con OpenCV (filtro Unsharp Masking vectorizado y binarización Sauvola) para rescatar texto de escaneos borrosos, arrugados o de baja calidad.", "Restauración de Documentos Degradados (Caso Real):")
    bullet(" Motor neuronal en C++ (PP-OCRv4 con ONNX Runtime) que supera en 3x la velocidad de Tesseract y lee trazos deformados en paralelo.", "OCR de Alto Rendimiento en 20 Páginas:")
    bullet(" Detección en 15 milisegundos mediante YOLOv8-Nano para responder si en una foto hay un árbol, firma o sello, complementado con RapidFuzz para palabras clave y renombrado automático de archivos.", "Visión Ligera y Renombrado Estandarizado:")

    # 2. ANÁLISIS DEL PROBLEMA
    h1("2. ANÁLISIS DEL PROBLEMA Y CASOS EXTREMOS REALES")
    body("En la operación cotidiana de RIWI Barranquilla, el buzón info@riwi.io recibe cientos de correos heterogéneos. En el mundo real, los documentos no llegan en condiciones ideales:")
    bullet(" Expedientes escaneados a 600 DPI que generan archivos de 80 MB. Un OCR secuencial tradicional tardaría más de 90 segundos; la arquitectura multiproceso lo resuelve en 3 a 5 segundos.", "1. Documentos Multipágina Pesados (20+ Páginas):")
    bullet(" Escaneos torcidos, fotos tomadas con celular con iluminación deficiente o documentos arrugados que hacen fallar a los OCRs estándar.", "2. Imágenes Borrosas y Desenfoque:")
    bullet(" Mezcla de hojas de texto contractual con fotos adjuntas (inspecciones de compras, fotos de bienes o certificados) donde se requiere verificar si hay un árbol, una firma o un sello.", "3. Contenido Visual No Estructurado:")
    bullet(" Proveedores que envían facturas en contenedores .zip con XML legítimo de la DIAN, pero también proveedores que adjuntan facturas físicas escaneadas.", "4. Heterogeneidad Fiscal:")

    h2("La Restricción Inviolable: info@riwi.io como Canal Único")
    body("Con más de dos millones de clientes y cientos de proveedores registrados, info@riwi.io es un canal permanente. La solución opera como una capa de servicio invisible sin obligar a los clientes a migrar a nuevos correos ni trasladar la carga de trabajo al personal interno.")

    # 3. SOLUCIÓN PROPUESTA
    h1("3. SOLUCIÓN PROPUESTA Y ESPECIALIZACIÓN DE PROCESOS")
    img("/home/ddamago/Projects/buzoncorporativoRIWI/Propuesta/assets/diagrama_procesos.png",
        width=6.0, cap="Figura 1: Especialización técnica y análisis multimodal open source en SmartInbox RIWI.")

    h2("3.1. Facturación Electrónica DIAN (Cuentas por Pagar)")
    body("Tratamiento determinista con validez jurídica y cero error contable:")
    bullet(" Apenas llega un adjunto .zip, se descomprime en memoria protegida y se parsea el XML UBL 2.1 (AttachedDocument / Invoice) con lxml nativo. Se extraen matemáticamente CUFE, NIT, fechas, subtotal, IVA y total a pagar.", "• Validación UBL 2.1:")
    bullet(" Verificación instantánea en PostgreSQL/SQLite para impedir el pago de facturas repetidas y conciliación con la Orden de Compra citada.", "• Bloqueo de Duplicados:")
    bullet(" Radicación directa en el ERP de Cuentas por Pagar sin requerir inferencia de modelos pesados.", "• Enrutamiento:")

    h2("3.2. Órdenes de Compra y PDFs Complejos (Servicios Internos)")
    body("Pipeline especializado en documentos con imágenes borrosas y texto degradado de 20 páginas:")
    bullet(" PyMuPDF (fitz) escanea las 20 páginas. Si la página tiene texto vectorial nativo, lo extrae en 0.005 segundos. Si es escaneo puro, la envía al pipeline visual.", "• Triage de Capa Inteligente:")
    bullet(" La imagen pasa por OpenCV: eliminación de ruido, corrección de inclinación (Deskewing) y filtro Unsharp Masking para devolver nitidez a las letras.", "• Restauración OpenCV:")
    bullet(" PaddleOCR con motor ONNX procesa los bloques de texto en paralelo aprovechando los núcleos del CPU.", "• OCR Neuronal Ultrarrápido:")
    bullet(" YOLOv8-Nano analiza las fotos extraídas en 15 milisegundos para confirmar la presencia de elementos visuales (ej. árbol sí/no, sellos o firmas). Si se requiere una pregunta semántica compleja, interviene Moondream2 (1.6B) vía Ollama en menos de 1 segundo.", "• Detección Visual Dual:")
    bullet(" RapidFuzz localiza palabras clave incluso si el texto borroso provocó lecturas imperfectas (ej. arbo1 -> árbol).", "• Búsqueda Difusa:")
    bullet(" El archivo se renombra automáticamente como {FECHA}_{TIPO}_{ARBOL_SI/NO}_{ID}.pdf y se mueve a la carpeta de Servicios Internos.", "• Renombrado y Archivo:")

    h2("3.3. Proceso de PQRS (Servicio al Cliente - SAC)")
    bullet(" Se envía el texto limpio a Groq Cloud API (Llama 3.3 70B) que interpreta el tono y la intención en 0.2 segundos, con fallback a Gemini Flash y Ollama local.", "• NLU Semántico en Cascada:")
    bullet(" Asignación de nivel de severidad (Alta/Media/Baja) y creación de ticket automático en SAC con acuse de recibo al usuario.", "• Priorización y Ticket:")

    # 4. ARQUITECTURA
    h1("4. ARQUITECTURA DE LA SOLUCIÓN")
    img("/home/ddamago/Projects/buzoncorporativoRIWI/Propuesta/assets/diagrama_arquitectura.png",
        width=6.0, cap="Figura 2: Arquitectura Empresarial de Producción con Doble Caché y Cascada Multi-Proveedor.")

    h2("Componentes de la Arquitectura de Producción")
    bullet(" Conector reactivo por webhook de correo mediante API abierta.", "1. Capa de Ingesta:")
    bullet(" Hash SHA-256 del archivo para bypass instantáneo de documentos ya procesados + cola en memoria (asyncio.Queue / Redis local).", "2. Doble Motor de Caché y Cola:")
    bullet(" OpenCV (cv2) con kernels optimizados de nitidez, contraste CLAHE y binarización adaptativa Sauvola.", "3. Pipeline de Restauración Visual:")
    bullet(" PaddleOCR (PP-OCRv4 ONNX) en 4 núcleos + YOLOv8-Nano local en 15 ms para detección de objetos.", "4. Motores de Inferencia Local:")
    bullet(" Tier 1: Groq Cloud API (0.2s) -> Tier 2: Google Gemini Flash Free (Visión) -> Tier 3: Ollama Local (Offline).", "5. Cascada Multi-Proveedor:")
    bullet(" Consola web local en FastAPI/React para que un analista apruebe o corrija casos dudosos en 2 clics.", "6. Capa Human-in-the-Loop:")
    bullet(" Almacenamiento local con renombrado estandarizado y base de datos relacional para auditoría.", "7. Archivo y Persistencia:")

    # 5. AUTOMATIZACIÓN VS. IA
    h1("5. AUTOMATIZACIÓN TRADICIONAL VS. INTELIGENCIA ARTIFICIAL")
    body("La solución aplica la tecnología justa para cada necesidad, evitando el desperdicio computacional y garantizando precisión:")

    t_mat = doc.add_table(rows=6, cols=3)
    t_mat.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdrs = ["Actividad", "Mecanismo Seleccionado", "Justificación Técnica de Rendimiento"]
    for j, h in enumerate(hdrs):
        cell = t_mat.rows[0].cells[j]
        cell.text = h
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(8.5)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_background(cell, "1B365D")
        set_cell_margins(cell, 80, 80, 100, 100)

    rows_data = [
        ("Validación fiscal .ZIP/XML", "Parser lxml nativo (0% IA)", "100% determinista. Los LLMs no son calculadoras; lxml garantiza cero errores de cálculo y cero costo."),
        ("Enfoque de escaneos borrosos", "Filtros OpenCV (C++)", "Convolución matemática instantánea para restaurar bordes y limpiar sombras en milisegundos."),
        ("OCR de 20 páginas", "PaddleOCR PP-OCRv4 (ONNX)", "Red neuronal profunda DBNet. Supera en 3x a Tesseract en velocidad y rescata texto severamente borroso."),
        ("Detección de objetos ('árbol')", "YOLOv8-Nano (Ultralytics)", "15 milisegundos en CPU. Usar un LLM gigante para buscar un árbol es ineficiente; YOLO lo resuelve al instante."),
        ("Comprensión de quejas PQRS", "Cascada: Groq -> Gemini -> Ollama", "Velocidad de 0.2s en la nube gratuita con salvavidas offline local por si falla internet.")
    ]
    for i, rd in enumerate(rows_data):
        row = t_mat.rows[i+1]
        for j, val in enumerate(rd):
            cell = row.cells[j]
            cell.text = val
            cell.paragraphs[0].runs[0].font.size = Pt(8)
            cell.paragraphs[0].runs[0].font.color.rgb = c_dark
            if j == 0:
                cell.paragraphs[0].runs[0].font.bold = True
            set_cell_margins(cell, 60, 60, 80, 80)
            if i % 2 == 1:
                set_cell_background(cell, "F7FAFC")

    # 6. FLUJO DE PROCESAMIENTO
    h1("6. FLUJO DE PROCESAMIENTO END-TO-END")
    img("/home/ddamago/Projects/buzoncorporativoRIWI/Propuesta/assets/diagrama_flujo.png",
        width=6.0, cap="Figura 3: Flujo de procesamiento end-to-end con doble caché, cascada y renombrado.")

    body("El ciclo de vida del documento consta de 7 etapas consecutivas:")
    bullet(" Captura de correo, descarga de adjuntos y verificación del hash SHA-256. Si ya existe en base de datos, retorna en 0.002s.", "1. Ingesta & Doble Caché:")
    bullet(" Triage de capas en PyMuPDF: las páginas digitales se extraen al instante; las páginas borrosas pasan a restauración OpenCV.", "2. Triage y Restauración:")
    bullet(" Si hay contenedor .zip con XML DIAN, pasa a validación inmediata lxml.", "3. Compuerta Rápida DIAN:")
    bullet(" PaddleOCR extrae el texto en paralelo. YOLOv8-Nano inspecciona imágenes para confirmar presencia de objetos (árbol sí/no).", "4. Extracción Híbrida:")
    bullet(" Validación cruzada con RapidFuzz y cálculo de Score de Confianza Compuesto (C).", "5. Validación de Negocio:")
    bullet(" Si C >= 0.90, el archivo se renombra como {FECHA}_{TIPO}_{ARBOL_SI/NO}_{ID}.pdf y se mueve a la carpeta departamental. Si C < 0.90, pasa a Human-in-the-Loop.", "6. Renombrado y Enrutamiento:")
    bullet(" Registro inmutable en base de datos local y emisión de métricas diarias.", "7. Auditoría:")

    # 7. MANEJO DE EXCEPCIONES
    h1("7. MANEJO DE EXCEPCIONES (HUMAN-IN-THE-LOOP)")
    body("La intervención humana solo ocurre ante verdadera incertidumbre:")
    bullet(" Se dispara cuando el índice de confianza es inferior al 90% (C < 0.90) o cuando una imagen está tan dañada que no es posible extraer los campos obligatorios.", "Criterio de Disparo:")
    bullet(" El analista visualiza una pantalla dividida con el PDF a la izquierda y el formulario pre-llenado a la derecha, con el campo dudoso resaltado.", "Resolución en 2 Clics:")
    bullet(" La corrección queda guardada como dato de entrenamiento para retroalimentación continua del sistema.", "Trazabilidad:")

    # 8. TRAZABILIDAD
    h1("8. TRAZABILIDAD Y AUDITORÍA EMPRESARIAL")
    body("El sistema garantiza el registro inmutable de cada transacción:")
    bullet(" Trace-ID único, fecha y hora con precisión de milisegundos, remitente y hash SHA-256.", "• Identificación Inmutable:")
    bullet(" Resultado del OCR, score de certeza, etiquetas visuales detectadas (ej. árbol: SÍ) y nuevo nombre del archivo.", "• Metadatos Almacenados:")
    bullet(" Cifrado local AES-256, políticas de acceso RBAC y estricto apego a la Ley 1581 de Habeas Data.", "• Seguridad:")

    # 9. REPORTES E INDICADORES
    h1("9. REPORTES E INDICADORES DE GESTIÓN")
    body("Generación diaria automática a las 07:00 y 18:00 hrs:")
    bullet(" > 90% de expedientes y correos resueltos sin intervención de personal.", "• Tasa de Procesamiento Directo (STP):")
    bullet(" De 3 a 5 segundos totales para procesar un PDF escaneado de 20 páginas (vs. más de 60 segundos con motores tradicionales).", "• Latencia de Procesamiento:")
    bullet(" Monto total de facturas DIAN UBL procesadas y duplicados bloqueados.", "• Resumen Financiero:")

    # 10. PROPUESTA TECNOLÓGICA
    h1("10. PROPUESTA TECNOLÓGICA Y JUSTIFICACIÓN DEL STACK")
    bullet(" PyMuPDF (fitz) para extracción de texto vectorial y capas; pdf2image para renderizado a 300 DPI.", "• Manipulación de PDFs de 20 Páginas:")
    bullet(" OpenCV (cv2) con kernels optimizados de nitidez, contraste CLAHE y binarización adaptativa Sauvola.", "• Restauración de Imágenes Borrosas:")
    bullet(" PaddleOCR (PP-OCRv4 ONNX) ejecutado localmente con aceleración multi-núcleo.", "• Motor de OCR:")
    bullet(" YOLOv8-Nano (15 ms) para detección instantánea de objetos + Moondream2 (1.6B) vía Ollama para preguntas abiertas.", "• Visión Multimodal:")
    bullet(" Cascada: Groq Cloud API (Tier 1) -> Google Gemini Flash (Tier 2) -> Ollama local (Tier 3).", "• NLU Semántico:")
    bullet(" RapidFuzz para búsqueda difusa con tolerancia a errores de escaneo.", "• Búsqueda de Palabras Clave:")
    bullet(" Python 3.11 + FastAPI + PostgreSQL / SQLite local con caché SHA-256.", "• Backend y Persistencia:")

    # 11. ROADMAP
    h1("11. ROADMAP DE IMPLEMENTACIÓN POR FASES")
    body("Cronograma de 14 semanas para el equipo de 3 especialistas:")
    bullet(" Despliegue de ingesta, parser .zip/XML DIAN y estructura de base de datos local con caché SHA-256.", "Fase 1 (Semanas 1-4): Cimientos, Doble Caché & Facturación DIAN:")
    bullet(" Pipeline de OpenCV para escaneos borrosos, PaddleOCR ONNX, YOLOv8-Nano en Ollama y lógica de renombrado.", "Fase 2 (Semanas 5-8): PDFs Complejos, OCR & Análisis Visual:")
    bullet(" Auditoría con Trace-ID, tableros de métricas y pruebas con PDFs reales de 20 páginas suministrados por el TL.", "Fase 3 (Semanas 9-11): Trazabilidad, Métricas & Pruebas Reales:")
    bullet(" Despliegue gradual (Canary Rollout), capacitación y entrega formal.", "Fase 4 (Semanas 12-14): Despliegue Productivo & Cierre:")

    h2("Asignación de Roles del Equipo")
    bullet(" Arquitectura de servicios locales, concurrencia multiproceso e integración con sistemas destino.", "Daniel David Martinez Gonzalez (Arquitectura Open Source, Concurrencia e Integración):")
    bullet(" Pipeline de OpenCV para escaneos borrosos, parser XML DIAN y diseño de base de datos de auditoría.", "Breyner De Jesus Manga Arias (Datos, Preprocesamiento OpenCV & DIAN):")
    bullet(" Configuración de PaddleOCR ONNX, integración de YOLOv8/Moondream2 y consola Human-in-the-Loop.", "Joseph Romero (Visión Computacional, Inferencia VLM & Modelos de Lenguaje):")

    # 12. CONCLUSIÓN
    h1("12. CONCLUSIÓN Y VALOR ESTRATÉGICO")
    body("SmartInbox RIWI demuestra que no se requieren suscripciones costosas en la nube para construir la solución documental más rápida del mercado. Al integrar la velocidad de PaddleOCR con la potencia de OpenCV y la agilidad de YOLOv8-Nano, el aplicativo procesa expedientes complejos de 20 páginas en segundos, identifica objetos visuales con precisión milimétrica y garantiza el orden y la trazabilidad operativa bajo un costo de licenciamiento de cero dólares.")

    doc.save(output_docx)
    print(f"Propuesta docx guardada en: {output_docx}")

def create_guide_docx(output_docx):
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(1)
        s.bottom_margin = Inches(1)
        s.left_margin = Inches(1)
        s.right_margin = Inches(1)

    c_primary = RGBColor(27, 54, 93)
    c_secondary = RGBColor(43, 108, 176)
    c_dark = RGBColor(45, 55, 72)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t = p_title.add_run("GUÍA DE COMPRENSIÓN PARA EL EQUIPO\n")
    r_t.font.name = "Arial"
    r_t.font.size = Pt(17)
    r_t.font.bold = True
    r_t.font.color.rgb = c_primary

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_s = p_sub.add_run("“Entendiendo SmartInbox RIWI: Doble Caché, Cascada Gratuita y Máxima Velocidad Explicada con Plastilina”\n")
    r_s.font.name = "Arial"
    r_s.font.size = Pt(11.5)
    r_s.font.italic = True
    r_s.font.color.rgb = c_secondary

    def h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(13)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(text)
        r.font.name = "Arial"
        r.font.size = Pt(12.5)
        r.font.bold = True
        r.font.color.rgb = c_primary
        return p

    def body(text, bold_pre=None):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        if bold_pre:
            r_pre = p.add_run(bold_pre)
            r_pre.font.name = "Calibri"
            r_pre.font.size = Pt(10)
            r_pre.font.bold = True
            r_pre.font.color.rgb = c_dark
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(10)
        r.font.color.rgb = c_dark
        return p

    def bullet(text, bold_pre=None):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        if bold_pre:
            r_pre = p.add_run(bold_pre)
            r_pre.font.name = "Calibri"
            r_pre.font.size = Pt(10)
            r_pre.font.bold = True
            r_pre.font.color.rgb = c_dark
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(10)
        r.font.color.rgb = c_dark
        return p

    h1("1. ¿QUÉ ES EL DOBLE MOTOR DE CACHÉ?")
    body("Imagina que un cliente envía el mismo PDF de 20 páginas dos veces por error. En un sistema novato, la máquina vuelve a hacer OCR y gastar 10 segundos inútilmente. En SmartInbox RIWI:")
    bullet(" Calcula la huella digital única (SHA-256) del archivo en 0.001 segundos.", "• Motor 1 (Huella Digital Criptográfica):")
    bullet(" Si la huella ya existe en la base de datos, el sistema devuelve el resultado guardado en 0.002 segundos, sin gastar ni un ciclo de procesador.", "• Motor 2 (Caché en Memoria):")

    h1("2. ¿CÓMO FUNCIONA LA CASCADA MULTI-PROVEEDOR?")
    body("Para entender quejas de clientes sin gastar dinero y sin que el sistema se caiga jamás, usamos una cascada de 3 niveles:")
    bullet(" Le pregunta a Groq Cloud (gratis), que responde en solo 0.2 segundos gracias a sus chips ultrarrápidos.", "• Nivel 1 (Groq Cloud API):")
    bullet(" Si Groq agota su cuota por minuto o se satura, pasa automáticamente a Google AI Studio (Gemini Flash gratis).", "• Nivel 2 (Google Gemini Flash):")
    bullet(" Si no hay internet o se cortan las conexiones externas, un modelo local pequeño (Llama 3.2 3B en Ollama) resuelve la tarea en la máquina.", "• Nivel 3 (Salvavidas Local Offline):")

    h1("3. GLOSARIO DE TÉRMINOS PARA ENTENDER LA TECNOLOGÍA")
    bullet(" Motor de OCR de última generación basado en redes neuronales profundas (DBNet). Es hasta 3 veces más rápido que Tesseract y lee texto borroso donde otros fallan.", "PaddleOCR (PP-OCRv4):")
    bullet(" Modelo de visión ultraligero (pesa 6 MB) que detecta objetos como árboles, personas o vehículos en 15 milisegundos en cualquier CPU humilde.", "YOLOv8-Nano:")
    bullet(" Modelo de visión y lenguaje diminuto (1.6B parámetros) que corre en computadores locales sin tarjeta gráfica y responde preguntas visuales en menos de 1 segundo.", "Moondream2:")
    bullet(" Técnica de Python para usar todos los núcleos del procesador al mismo tiempo, dividiendo el trabajo de las 20 páginas en paralelo.", "Multiprocessing (ProcessPoolExecutor):")
    bullet(" Algoritmo que encuentra palabras clave aunque el escaneo borroso haya cambiado una letra (ej. encuentra 'árbol' aunque diga 'arbo1').", "RapidFuzz:")

    h1("4. EL ROL DE CADA UNO EN EL EQUIPO")
    bullet(" Arquitectura del sistema, concurrencia multiproceso para procesar en paralelo y seguridad de datos.", "Daniel David Martinez Gonzalez:")
    bullet(" Pipeline de filtros OpenCV para escaneos borrosos, parser XML DIAN y diseño de la base de datos de auditoría.", "Breyner De Jesus Manga Arias:")
    bullet(" Configuración de PaddleOCR ONNX, integración de YOLOv8/Moondream2 y consola web para excepciones.", "Joseph Romero:")

    doc.save(output_docx)
    print(f"Guia docx guardada en: {output_docx}")

def create_pitch_docx(output_docx):
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(1)
        s.bottom_margin = Inches(1)
        s.left_margin = Inches(1)
        s.right_margin = Inches(1)

    c_primary = RGBColor(27, 54, 93)
    c_secondary = RGBColor(43, 108, 176)
    c_dark = RGBColor(45, 55, 72)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t = p_title.add_run("GUIÓN DE SUSTENTACIÓN COMERCIAL Y TÉCNICA\n")
    r_t.font.name = "Arial"
    r_t.font.size = Pt(17)
    r_t.font.bold = True
    r_t.font.color.rgb = c_primary

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_s = p_sub.add_run("“Pitch Empresarial: SmartInbox RIWI — La Solución Ultra-Rápida con Doble Caché y Cascada Multi-Proveedor”\n")
    r_s.font.name = "Arial"
    r_s.font.size = Pt(11.5)
    r_s.font.italic = True
    r_s.font.color.rgb = c_secondary

    def h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(13)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(text)
        r.font.name = "Arial"
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = c_primary
        return p

    def body(text, bold_pre=None):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        if bold_pre:
            r_pre = p.add_run(bold_pre)
            r_pre.font.name = "Calibri"
            r_pre.font.size = Pt(10)
            r_pre.font.bold = True
            r_pre.font.color.rgb = c_dark
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(10)
        r.font.color.rgb = c_dark
        return p

    h1("DINÁMICA DE LA PRESENTACIÓN (14 MINUTOS + Q&A)")
    body("Modalidad: 1 Orador Principal + 2 Miembros de Apoyo Estratégico.")

    h1("ACTO 1: EL GANCHO Y LA PROMESA DE RENDIMIENTO (00:00 - 02:30)")
    body("[ORADOR PRINCIPAL]: 'Buenos días a la mesa directiva y al jurado evaluador. Mientras la mayoría de proyectos caen en la trampa de usar herramientas en la nube que cobran por cada página y tardan minutos en procesar escaneos pesados, nosotros venimos a presentarles SmartInbox RIWI: una arquitectura 100% Open Source y local, con costo de licenciamiento de cero dólares, diseñada para procesar expedientes reales de 20 páginas con imágenes borrosas en menos de 5 segundos gracias a un doble motor de caché y concurrencia multiproceso.'")

    h1("ACTO 2: EL CASO REAL Y LA VENTAJA TÉCNICA (02:30 - 07:00)")
    body("[ORADOR PRINCIPAL]: 'En la operación real, los documentos llegan borrosos, torcidos y manchados. Por eso integramos un pipeline de OpenCV que enfoca bordes y limpia sombras con binarización Sauvola. Y en lugar de motores lentos, utilizamos PaddleOCR sobre ONNX Runtime, que procesa el texto en paralelo a una velocidad 3 veces superior.'")
    body("Intervención de Joseph Romero: 'Y cuando se trata de responder preguntas visuales —como verificar si en una foto de 20 páginas hay un árbol, un sello o una firma— no quemamos recursos con modelos gigantes: usamos YOLOv8-Nano que responde en 15 milisegundos en CPU, y Moondream2 para razonamiento abierto en menos de un segundo.'")
    body("Intervención de Breyner Manga: 'Y para las facturas electrónicas de la DIAN, leemos directamente el XML legal con lxml en 2 milisegundos, garantizando cero error contable y cero costo de inteligencia artificial.'")

    h1("ACTO 3: GOBERNANZA, RENOMBRADO Y ROADMAP (07:00 - 11:00)")
    body("[ORADOR PRINCIPAL]: 'El sistema renombra automáticamente cada archivo como {FECHA}_{TIPO}_{ARBOL_SI}_{ID}.pdf y lo archiva en su carpeta. Si la confianza es baja, la consola Human-in-the-Loop permite resolver excepciones en 2 clics. Además, implementamos una cascada multi-proveedor gratuita: Groq como Tier 1 en 0.2s, Gemini Flash como Tier 2 y Ollama local como Tier 3 de emergencia.'")

    h1("ACTO 4: CIERRE Y LLAMADO A LA ACCIÓN (11:00 - 13:00)")
    body("[ORADOR PRINCIPAL]: 'SmartInbox RIWI combina máxima velocidad, cero costo operativo y total resiliencia ante los peores escaneos. Estamos listos para comenzar la Fase 1.'")

    h1("BANCO DE PREGUNTAS DIFÍCILES DEL TL (Q&A)")
    body("Pregunta del TL: '¿Cómo garantizan que el sistema no colapse si se satura la API de Groq o si se corta el internet?'")
    body("Respuesta (Joseph / Daniel): 'Ese riesgo está blindado por diseño mediante nuestra Cascada Multi-Proveedor: si Groq devuelve error 429 por límite de cuota, el sistema conmuta automáticamente a Google Gemini Flash Free; y si se cae el internet por completo, el sistema activa el Tier 3 de salvavidas local con Ollama en la propia máquina, garantizando que el aplicativo nunca se detenga.'")

    doc.save(output_docx)
    print(f"Guion docx guardada en: {output_docx}")

if __name__ == "__main__":
    out_dir = "/home/ddamago/Projects/buzoncorporativoRIWI/Propuesta"
    p_docx = os.path.join(out_dir, "Propuesta_Tecnica_Comercial_SmartInbox_RIWI.docx")
    g_docx = os.path.join(out_dir, "Guia_Explicativa_No_Tecnica_SmartInbox.docx")
    s_docx = os.path.join(out_dir, "Guion_Sustentacion_RIWI.docx")

    create_proposal_docx(p_docx)
    create_guide_docx(g_docx)
    create_pitch_docx(s_docx)
