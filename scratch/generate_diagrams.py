import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Ensure output directory exists
out_dir = "/home/ddamago/Projects/buzoncorporativoRIWI/Propuesta/assets"
os.makedirs(out_dir, exist_ok=True)

# Set high DPI and aesthetic styling
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'

# -------------------------------------------------------------
# 1. DIAGRAMA DE ARQUITECTURA (6 CAPAS)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(13, 10), dpi=300)
ax.set_xlim(0, 13)
ax.set_ylim(0, 10)
ax.axis('off')

# Title
ax.text(6.5, 9.6, "ARQUITECTURA EMPRESARIAL — SMARTINBOX RIWI", 
        fontsize=16, fontweight='bold', ha='center', va='center', color='#1B365D')
ax.text(6.5, 9.25, "Capa de Ingesta Inteligente, Orquestación Asíncrona y Gobierno Human-in-the-Loop", 
        fontsize=11, fontstyle='italic', ha='center', va='center', color='#4A5568')

def draw_layer_box(ax, x, y, w, h, title, subtitle, bg_color, border_color):
    # Main box
    rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.15",
                                  facecolor=bg_color, edgecolor=border_color, linewidth=1.8, alpha=0.95)
    ax.add_patch(rect)
    # Header banner
    hb = patches.FancyBboxPatch((x, y + h - 0.45), w, 0.45, boxstyle="round,pad=0.08,rounding_size=0.15",
                                facecolor=border_color, edgecolor=border_color, linewidth=1)
    ax.add_patch(hb)
    ax.text(x + w/2, y + h - 0.22, title, fontsize=10.5, fontweight='bold', ha='center', va='center', color='white')

def draw_component(ax, x, y, w, h, text, subtext="", fill="#FFFFFF", border="#CBD5E0", text_color="#1A202C"):
    c = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.1",
                               facecolor=fill, edgecolor=border, linewidth=1.2)
    ax.add_patch(c)
    if subtext:
        ax.text(x + w/2, y + h*0.62, text, fontsize=9, fontweight='bold', ha='center', va='center', color=text_color)
        ax.text(x + w/2, y + h*0.28, subtext, fontsize=7.5, ha='center', va='center', color='#718096')
    else:
        ax.text(x + w/2, y + h/2, text, fontsize=8.5, fontweight='bold', ha='center', va='center', color=text_color)

# Capa 1: Ingesta
draw_layer_box(ax, 0.5, 7.8, 12, 1.2, "1. CAPA DE INGESTA Y RECEPCIÓN", "", "#F8FAFC", "#1B365D")
draw_component(ax, 0.8, 7.95, 3.2, 0.65, "Clientes / Proveedores", "2M+ usuarios (info@riwi.io)", "#FFFFFF", "#1B365D")
draw_component(ax, 4.8, 7.95, 3.4, 0.65, "Buzón info@riwi.io", "Microsoft 365 / Google Workspace", "#FFFFFF", "#1B365D")
draw_component(ax, 8.9, 7.95, 3.3, 0.65, "Webhook Event Listener", "API Graph (Event-Driven Push)", "#EBF8FF", "#2B6CB0")

# Arrow 1 -> 2
ax.annotate('', xy=(6.5, 7.5), xytext=(6.5, 7.8),
            arrowprops=dict(facecolor='#2B6CB0', edgecolor='#2B6CB0', width=2, headwidth=7))

# Capa 2: Desacoplamiento
draw_layer_box(ax, 0.5, 6.2, 12, 1.25, "2. CAPA DE DESACOPLAMIENTO Y MENSAJERÍA", "", "#F8FAFC", "#4A5568")
draw_component(ax, 1.2, 6.35, 5.0, 0.65, "Cola Transaccional de Mensajes", "Azure Service Bus / AWS SQS (At-least-once)", "#FFFFFF", "#4A5568")
draw_component(ax, 6.8, 6.35, 5.0, 0.65, "Dead-Letter Queue (DLQ) & Alertas", "Aislamiento de fallos y reintentos exponenciales", "#FFF5F5", "#E53E3E")

# Arrow 2 -> 3
ax.annotate('', xy=(6.5, 5.9), xytext=(6.5, 6.2),
            arrowprops=dict(facecolor='#2B6CB0', edgecolor='#2B6CB0', width=2, headwidth=7))

# Capa 3: Procesamiento Híbrido
draw_layer_box(ax, 0.5, 3.9, 12, 1.95, "3. MOTOR DE PROCESAMIENTO HÍBRIDO (ORQUESTADOR ASÍNCRONO)", "", "#F0F9FF", "#0284C7")
draw_component(ax, 0.8, 4.85, 3.5, 0.6, "Parser XML UBL 2.1 (DIAN)", "Regla pura: Contenedor .ZIP / CUFE", "#F0FDF4", "#16A34A", "#14532D")
draw_component(ax, 4.75, 4.85, 3.5, 0.6, "OCR & Document Intelligence", "Extracción tabular OCs y PDFs", "#EFF6FF", "#2563EB", "#1E3A8A")
draw_component(ax, 8.7, 4.85, 3.5, 0.6, "Agente Clasificador Semántico", "LLM: NLU de PQRS y OCs servicio", "#FAF5FF", "#9333EA", "#581C87")
draw_component(ax, 2.5, 4.05, 8.0, 0.55, "Motor de Reglas de Negocio & Validación Aritmética", "Cálculo de Score de Confianza Compuesto (C)", "#FFFFFF", "#0284C7")

# Arrow 3 -> 4
ax.annotate('', xy=(6.5, 3.6), xytext=(6.5, 3.9),
            arrowprops=dict(facecolor='#2B6CB0', edgecolor='#2B6CB0', width=2, headwidth=7))

# Capa 4: Gobierno y Excepciones
draw_layer_box(ax, 0.5, 2.1, 12, 1.45, "4. GOBIERNO, EVALUACIÓN Y HUMAN-IN-THE-LOOP", "", "#FFFBEB", "#D97706")
draw_component(ax, 1.0, 2.3, 5.2, 0.7, "Ruta Straight-Through (STP)", "Confianza >= 90% y consistencia total (Desatendido)", "#ECFDF5", "#059669", "#064E3B")
draw_component(ax, 6.8, 2.3, 5.2, 0.7, "Consola Human-in-the-Loop", "Confianza < 90% (Resolución asistida en 1 clic)", "#FEF2F2", "#DC2626", "#7F1D1D")

# Arrow 4 -> 5
ax.annotate('', xy=(6.5, 1.8), xytext=(6.5, 2.1),
            arrowprops=dict(facecolor='#2B6CB0', edgecolor='#2B6CB0', width=2, headwidth=7))

# Capa 5: Integración y Persistencia
draw_layer_box(ax, 0.5, 0.2, 12, 1.55, "5. INTEGRACIÓN EMPRESARIAL, AUDITORÍA Y OBSERVABILIDAD", "", "#F8FAFC", "#1E293B")
draw_component(ax, 0.8, 0.35, 2.6, 0.85, "Cuentas por Pagar\n(ERP Contable)", "Facturas radicadas", "#FFFFFF", "#64748B")
draw_component(ax, 3.7, 0.35, 2.6, 0.85, "Servicios Internos\n(Compras)", "OCs Producto/Servicio", "#FFFFFF", "#64748B")
draw_component(ax, 6.6, 0.35, 2.6, 0.85, "Servicio al Cliente\n(CRM / SAC)", "Tickets con prioridad", "#FFFFFF", "#64748B")
draw_component(ax, 9.5, 0.35, 2.7, 0.85, "Audit Ledger & BI\n(PostgreSQL + Storage)", "Trace-ID inmutable", "#EFF6FF", "#3B82F6")

plt.tight_layout()
arch_path = os.path.join(out_dir, "diagrama_arquitectura.png")
plt.savefig(arch_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Arquitectura guardada en: {arch_path}")

# -------------------------------------------------------------
# 2. DIAGRAMA DE FLUJO END-TO-END
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 11), dpi=300)
ax.set_xlim(0, 12)
ax.set_ylim(0, 11)
ax.axis('off')

# Title
ax.text(6.0, 10.6, "FLUJO DE PROCESAMIENTO END-TO-END — SMARTINBOX RIWI", 
        fontsize=15, fontweight='bold', ha='center', va='center', color='#1B365D')
ax.text(6.0, 10.25, "Desde la llegada del correo hasta la radicación transaccional y auditoría", 
        fontsize=10.5, fontstyle='italic', ha='center', va='center', color='#4A5568')

def draw_step(ax, x, y, w, h, step_num, title, detail, fill="#FFFFFF", border="#CBD5E0", title_color="#1B365D"):
    p = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06,rounding_size=0.12",
                               facecolor=fill, edgecolor=border, linewidth=1.5)
    ax.add_patch(p)
    # Circle step number
    circ = patches.Circle((x + 0.4, y + h/2), 0.26, facecolor=border, edgecolor=border)
    ax.add_patch(circ)
    ax.text(x + 0.4, y + h/2, str(step_num), fontsize=10, fontweight='bold', ha='center', va='center', color='white')
    # Text
    ax.text(x + 0.85, y + h*0.64, title, fontsize=9.5, fontweight='bold', ha='left', va='center', color=title_color)
    ax.text(x + 0.85, y + h*0.32, detail, fontsize=8, ha='left', va='center', color='#4B5563')

# Step 1
draw_step(ax, 2.5, 9.1, 7.0, 0.8, 1, "Recepción en info@riwi.io & Webhook Push", 
          "Captura inmediata por API Graph y generación de Trace-ID único", "#F8FAFC", "#1B365D")

# Arrow 1 -> 2
ax.annotate('', xy=(6.0, 8.4), xytext=(6.0, 9.1),
            arrowprops=dict(facecolor='#1B365D', edgecolor='#1B365D', width=1.5, headwidth=6))

# Step 2
draw_step(ax, 2.5, 7.6, 7.0, 0.8, 2, "Sanitización & Almacenamiento Cifrado", 
          "Extracción segura de adjuntos a Blob Storage (AES-256) y antivirus", "#F8FAFC", "#2B6CB0")

# Arrow 2 -> 3
ax.annotate('', xy=(6.0, 6.9), xytext=(6.0, 7.6),
            arrowprops=dict(facecolor='#2B6CB0', edgecolor='#2B6CB0', width=1.5, headwidth=6))

# Step 3: Decision Gate (Compuerta XML)
d_box = patches.FancyBboxPatch((3.0, 6.0), 6.0, 0.9, boxstyle="round,pad=0.06,rounding_size=0.15",
                               facecolor="#FEF3C7", edgecolor="#D97706", linewidth=1.8)
ax.add_patch(d_box)
ax.text(6.0, 6.55, "¿Contiene archivo .ZIP con XML UBL 2.1?", fontsize=9.5, fontweight='bold', ha='center', va='center', color="#92400E")
ax.text(6.0, 6.25, "Compuerta determinista de Facturación DIAN", fontsize=8, fontstyle='italic', ha='center', va='center', color="#B45309")

# Branch 3 -> 4A (Left)
ax.annotate('', xy=(2.7, 4.9), xytext=(4.0, 6.0),
            arrowprops=dict(facecolor='#059669', edgecolor='#059669', width=1.5, headwidth=6))
ax.text(2.6, 5.5, "SÍ (Factura DIAN)", fontsize=8.5, fontweight='bold', color="#059669")

# Branch 3 -> 4B (Right)
ax.annotate('', xy=(9.3, 4.9), xytext=(8.0, 6.0),
            arrowprops=dict(facecolor='#7C3AED', edgecolor='#7C3AED', width=1.5, headwidth=6))
ax.text(8.7, 5.5, "NO (Otros procesos)", fontsize=8.5, fontweight='bold', color="#7C3AED")

# Step 4A (Left)
draw_step(ax, 0.5, 4.1, 5.0, 0.8, "4A", "Parser Determinista XML (UBL 2.1)", 
          "Extracción exacta de CUFE, NIT, valores e impuestos", "#ECFDF5", "#059669", "#064E3B")

# Step 4B (Right)
draw_step(ax, 6.5, 4.1, 5.0, 0.8, "4B", "Clasificación Cognitiva (LLM + OCR)", 
          "Triage de OCs (Producto/Servicio) y NLU de PQRS", "#F5F3FF", "#7C3AED", "#4C1D95")

# Converge to Step 5
ax.annotate('', xy=(5.2, 3.4), xytext=(3.0, 4.1),
            arrowprops=dict(facecolor='#4B5563', edgecolor='#4B5563', width=1.5, headwidth=6))
ax.annotate('', xy=(6.8, 3.4), xytext=(9.0, 4.1),
            arrowprops=dict(facecolor='#4B5563', edgecolor='#4B5563', width=1.5, headwidth=6))

# Step 5: Validación de Negocio
draw_step(ax, 2.5, 2.6, 7.0, 0.8, 5, "Validación de Negocio & Score de Confianza", 
          "Verificación de montos, duplicados y cálculo de confianza (C)", "#EFF6FF", "#2563EB")

# Arrow 5 -> Decision 6
ax.annotate('', xy=(6.0, 1.9), xytext=(6.0, 2.6),
            arrowprops=dict(facecolor='#2563EB', edgecolor='#2563EB', width=1.5, headwidth=6))

# Step 6: Decision Gate Confidence
d6 = patches.FancyBboxPatch((3.5, 1.1), 5.0, 0.8, boxstyle="round,pad=0.06,rounding_size=0.15",
                            facecolor="#ECFDF5", edgecolor="#059669", linewidth=1.8)
ax.add_patch(d6)
ax.text(6.0, 1.58, "¿Confianza C >= 90% sin conflictos?", fontsize=9.5, fontweight='bold', ha='center', va='center', color="#064E3B")
ax.text(6.0, 1.30, "Evaluación de certidumbre para direccionamiento", fontsize=8, fontstyle='italic', ha='center', va='center', color="#047857")

# Out 6A (Left: STP)
ax.annotate('', xy=(1.5, 0.2), xytext=(4.0, 1.1),
            arrowprops=dict(facecolor='#059669', edgecolor='#059669', width=1.5, headwidth=6))
draw_step(ax, 0.3, 0.0, 4.5, 0.75, "6A", "Straight-Through Processing", 
          "Enrutamiento 100% automático al ERP/CRM", "#ECFDF5", "#059669", "#064E3B")

# Out 6B (Right: HITL)
ax.annotate('', xy=(10.5, 0.2), xytext=(8.0, 1.1),
            arrowprops=dict(facecolor='#DC2626', edgecolor='#DC2626', width=1.5, headwidth=6))
draw_step(ax, 7.2, 0.0, 4.5, 0.75, "6B", "Human-in-the-Loop (1 Clic)", 
          "Resolución ágil en consola especializada", "#FEF2F2", "#DC2626", "#7F1D1D")

plt.tight_layout()
flujo_path = os.path.join(out_dir, "diagrama_flujo.png")
plt.savefig(flujo_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Flujo guardado en: {flujo_path}")

# -------------------------------------------------------------
# 3. DIAGRAMA DE LOS 3 PROCESOS CLAVE
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 6.5), dpi=300)
ax.set_xlim(0, 12)
ax.set_ylim(0, 6.5)
ax.axis('off')

ax.text(6.0, 6.1, "ESPECIALIZACIÓN DE LOS TRES PROCESOS CLAVE", 
        fontsize=14, fontweight='bold', ha='center', va='center', color='#1B365D')
ax.text(6.0, 5.75, "Tratamiento técnico diferenciado según la naturaleza jurídica y operativa del documento", 
        fontsize=9.5, fontstyle='italic', ha='center', va='center', color='#4A5568')

def draw_process_card(ax, x, y, w, h, title, subtitle, points, bg, border, header_bg):
    card = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.15",
                                 facecolor=bg, edgecolor=border, linewidth=1.8)
    ax.add_patch(card)
    hb = patches.FancyBboxPatch((x, y + h - 0.7), w, 0.7, boxstyle="round,pad=0.08,rounding_size=0.15",
                                facecolor=header_bg, edgecolor=header_bg, linewidth=1)
    ax.add_patch(hb)
    ax.text(x + w/2, y + h - 0.28, title, fontsize=10.5, fontweight='bold', ha='center', va='center', color='white')
    ax.text(x + w/2, y + h - 0.52, subtitle, fontsize=8, ha='center', va='center', color='#E2E8F0')
    
    start_y = y + h - 0.95
    for p in points:
        ax.text(x + 0.2, start_y, "•", fontsize=10, fontweight='bold', color=header_bg)
        ax.text(x + 0.4, start_y, p, fontsize=8, color='#1F2937', va='top', wrap=True)
        start_y -= 0.65

p1_points = [
    "Detección de contenedor .ZIP con\nXML firmado digitalmente.",
    "Validación de estándar UBL 2.1\ncon esquemas oficiales DIAN.",
    "Extracción 100% determinista:\nCUFE, NIT, número, total, IVA.",
    "Conciliación con Orden de Compra\ny bloqueo de facturas duplicadas.",
    "Destino: ERP Cuentas por Pagar."
]
draw_process_card(ax, 0.4, 0.4, 3.6, 5.0, "1. FACTURAS DIAN", "Cuentas por Pagar / Tesorería", 
                  p1_points, "#F0FDF4", "#16A34A", "#15803D")

p2_points = [
    "Clasificación Contextual Dual:\nProducto (físico) vs Servicio.",
    "Discriminación de adjuntos:\nDoc principal vs cotizaciones.",
    "Extracción mediante OCR:\nÍtems, cantidades, valores y fechas.",
    "Normalización de expedientes\npara compras y contratos.",
    "Destino: Servicios Internos."
]
draw_process_card(ax, 4.2, 0.4, 3.6, 5.0, "2. ÓRDENES DE COMPRA", "Servicios Internos (Compras)", 
                  p2_points, "#EFF6FF", "#2563EB", "#1D4ED8")

p3_points = [
    "Procesamiento de Lenguaje Natural:\nInterpreta lenguaje libre/coloquial.",
    "No requiere la palabra 'PQRS':\nDetecta intención de queja/reclamo.",
    "Extracción de metadatos:\nCédula, nombre, caso y producto.",
    "Análisis de sentimiento y SLA:\nPriorización Alta, Media o Baja.",
    "Destino: CRM / SAC."
]
draw_process_card(ax, 8.0, 0.4, 3.6, 5.0, "3. PQRS (SAC)", "Servicio al Cliente", 
                  p3_points, "#FAF5FF", "#9333EA", "#7E22CE")

plt.tight_layout()
proc_path = os.path.join(out_dir, "diagrama_procesos.png")
plt.savefig(proc_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Procesos guardados en: {proc_path}")
