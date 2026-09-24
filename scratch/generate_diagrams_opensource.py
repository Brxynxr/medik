import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

out_dir = "/home/ddamago/Projects/buzoncorporativoRIWI/Propuesta/assets"
os.makedirs(out_dir, exist_ok=True)

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'

# -------------------------------------------------------------
# 1. DIAGRAMA DE ARQUITECTURA OPEN SOURCE (CERO COSTO DE LICENCIAS)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(13, 10.5), dpi=300)
ax.set_xlim(0, 13)
ax.set_ylim(0, 10.5)
ax.axis('off')

ax.text(6.5, 10.1, "ARQUITECTURA SMARTINBOX RIWI — STACK 100% OPEN SOURCE & LOCAL", 
        fontsize=15, fontweight='bold', ha='center', va='center', color='#1B365D')
ax.text(6.5, 9.75, "Cero Costos de Licencia • Procesamiento de PDFs Complejos/Borrosos • Tesseract + Qwen2-VL/LLaVA", 
        fontsize=10.5, fontstyle='italic', ha='center', va='center', color='#4A5568')

def draw_layer_box(ax, x, y, w, h, title, bg_color, border_color):
    rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.15",
                                  facecolor=bg_color, edgecolor=border_color, linewidth=1.8, alpha=0.95)
    ax.add_patch(rect)
    hb = patches.FancyBboxPatch((x, y + h - 0.45), w, 0.45, boxstyle="round,pad=0.08,rounding_size=0.15",
                                facecolor=border_color, edgecolor=border_color, linewidth=1)
    ax.add_patch(hb)
    ax.text(x + w/2, y + h - 0.22, title, fontsize=10, fontweight='bold', ha='center', va='center', color='white')

def draw_comp(ax, x, y, w, h, text, subtext="", fill="#FFFFFF", border="#CBD5E0", text_color="#1A202C"):
    c = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.1",
                               facecolor=fill, edgecolor=border, linewidth=1.2)
    ax.add_patch(c)
    if subtext:
        ax.text(x + w/2, y + h*0.62, text, fontsize=8.5, fontweight='bold', ha='center', va='center', color=text_color)
        ax.text(x + w/2, y + h*0.28, subtext, fontsize=7.2, ha='center', va='center', color='#718096')
    else:
        ax.text(x + w/2, y + h/2, text, fontsize=8, fontweight='bold', ha='center', va='center', color=text_color)

# Capa 1: Ingesta
draw_layer_box(ax, 0.5, 8.3, 12, 1.25, "1. INGESTA & LECTURA DE DOCUMENTOS MULTIPÁGINA (PyMuPDF / Poppler)", "#F8FAFC", "#1B365D")
draw_comp(ax, 0.8, 8.45, 3.6, 0.65, "Buzón info@riwi.io", "Recepción de correos y adjuntos", "#FFFFFF", "#1B365D")
draw_comp(ax, 4.7, 8.45, 3.6, 0.65, "PyMuPDF (fitz) + Poppler", "Lectura de PDFs de 20+ páginas", "#EFF6FF", "#2563EB")
draw_comp(ax, 8.6, 8.45, 3.6, 0.65, "Extractor de Capas", "Separación de texto vectorial e imágenes", "#FFFFFF", "#1B365D")

# Arrow 1 -> 2
ax.annotate('', xy=(6.5, 8.0), xytext=(6.5, 8.3), arrowprops=dict(facecolor='#1B365D', width=2, headwidth=6))

# Capa 2: Preprocesamiento de Imágenes Borrosas
draw_layer_box(ax, 0.5, 6.4, 12, 1.45, "2. PIPELINE DE PREPROCESAMIENTO PARA CASOS REALES Y BORROSOS (OpenCV)", "#F0FDF4", "#16A34A")
draw_comp(ax, 0.8, 6.55, 2.7, 0.8, "Detección de Desenfoque", "Varianza Laplaciana (cv2)", "#FFFFFF", "#16A34A")
draw_comp(ax, 3.8, 6.55, 2.7, 0.8, "Filtro Unsharp & CLAHE", "Enfoque y contraste adaptativo", "#FFFFFF", "#16A34A")
draw_comp(ax, 6.8, 6.55, 2.7, 0.8, "Binarización Sauvola/Otsu", "Limpieza de manchas y sombras", "#FFFFFF", "#16A34A")
draw_comp(ax, 9.8, 6.55, 2.4, 0.8, "Deskewing Automático", "Corrección de inclinación", "#FFFFFF", "#16A34A")

# Arrow 2 -> 3
ax.annotate('', xy=(6.5, 6.1), xytext=(6.5, 6.4), arrowprops=dict(facecolor='#16A34A', width=2, headwidth=6))

# Capa 3: Motores de Análisis 100% Gratuitos (OCR + VLM)
draw_layer_box(ax, 0.5, 4.0, 12, 1.95, "3. MOTORES COGNITIVOS OPEN SOURCE (CERO COSTO DE API)", "#F0F9FF", "#0284C7")
draw_comp(ax, 0.8, 4.95, 3.6, 0.65, "Parser XML UBL 2.1 (lxml)", "Facturas DIAN dentro de .ZIP", "#F0FDF4", "#15803D", "#15803D")
draw_comp(ax, 4.7, 4.95, 3.6, 0.65, "Tesseract OCR 5.x (LSTM)", "Extracción de texto en 20 páginas", "#EFF6FF", "#2563EB", "#1D4ED8")
draw_comp(ax, 8.6, 4.95, 3.6, 0.65, "VLM: Qwen2-VL / LLaVA (Ollama)", "Análisis visual: ¿Árbol sí/no? / Sellos", "#FAF5FF", "#7C3AED", "#6D28D9")
draw_comp(ax, 2.5, 4.15, 8.0, 0.6, "Motor de Palabras Clave Difusas (RapidFuzz / Regex)", "Búsqueda tolerante a fallos de OCR sobre texto borroso", "#FFFFFF", "#0284C7")

# Arrow 3 -> 4
ax.annotate('', xy=(6.5, 3.7), xytext=(6.5, 4.0), arrowprops=dict(facecolor='#0284C7', width=2, headwidth=6))

# Capa 4: Decisión y Human-in-the-Loop
draw_layer_box(ax, 0.5, 2.2, 12, 1.35, "4. GOBIERNO, VALIDACIÓN Y HUMAN-IN-THE-LOOP", "#FFFBEB", "#D97706")
draw_comp(ax, 1.0, 2.35, 5.2, 0.65, "Procesamiento Directo (STP >= 90%)", "Clasificación segura y datos validados", "#ECFDF5", "#059669", "#064E3B")
draw_comp(ax, 6.8, 2.35, 5.2, 0.65, "Consola Human-in-the-Loop (Local)", "Revisión asistida en 1 clic para casos dudosos", "#FEF2F2", "#DC2626", "#7F1D1D")

# Arrow 4 -> 5
ax.annotate('', xy=(6.5, 1.9), xytext=(6.5, 2.2), arrowprops=dict(facecolor='#D97706', width=2, headwidth=6))

# Capa 5: Enrutamiento y Renombrado
draw_layer_box(ax, 0.5, 0.2, 12, 1.55, "5. RENOMBRADO AUTOMÁTICO, ENRUTAMIENTO Y AUDITORÍA INMUTABLE", "#F8FAFC", "#1E293B")
draw_comp(ax, 0.8, 0.35, 3.6, 0.85, "Pipeline de Renombrado\nAutomático de PDFs", "{FECHA}_{TIPO}_{TAG_ARBOL}.pdf", "#FFFFFF", "#475569")
draw_comp(ax, 4.7, 0.35, 3.6, 0.85, "Enrutamiento Operativo\n(ERP, Compras, SAC)", "Cuentas por Pagar, OCs y PQRS", "#FFFFFF", "#475569")
draw_comp(ax, 8.6, 0.35, 3.6, 0.85, "Auditoría Local Inmutable\n(PostgreSQL / SQLite)", "Trace-ID y logs de ejecución", "#EFF6FF", "#3B82F6")

plt.tight_layout()
arch_path = os.path.join(out_dir, "diagrama_arquitectura.png")
plt.savefig(arch_path, dpi=300, bbox_inches='tight')
plt.close()

# -------------------------------------------------------------
# 2. DIAGRAMA DE FLUJO END-TO-END ADAPTADO (OPENCV + TESSERACT + VLM)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 11), dpi=300)
ax.set_xlim(0, 12)
ax.set_ylim(0, 11)
ax.axis('off')

ax.text(6.0, 10.6, "FLUJO TÉCNICO: PROCESAMIENTO DE PDFs COMPLEJOS Y BORROSOS", 
        fontsize=14.5, fontweight='bold', ha='center', va='center', color='#1B365D')
ax.text(6.0, 10.25, "Lectura de 20 páginas, mejora con OpenCV, Tesseract OCR, análisis visual Qwen2-VL y renombrado", 
        fontsize=10, fontstyle='italic', ha='center', va='center', color='#4A5568')

def draw_step(ax, x, y, w, h, step_num, title, detail, fill="#FFFFFF", border="#CBD5E0", title_color="#1B365D"):
    p = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06,rounding_size=0.12",
                               facecolor=fill, edgecolor=border, linewidth=1.5)
    ax.add_patch(p)
    circ = patches.Circle((x + 0.4, y + h/2), 0.25, facecolor=border, edgecolor=border)
    ax.add_patch(circ)
    ax.text(x + 0.4, y + h/2, str(step_num), fontsize=9.5, fontweight='bold', ha='center', va='center', color='white')
    ax.text(x + 0.85, y + h*0.64, title, fontsize=9, fontweight='bold', ha='left', va='center', color=title_color)
    ax.text(x + 0.85, y + h*0.32, detail, fontsize=7.8, ha='left', va='center', color='#4B5563')

# Step 1
draw_step(ax, 2.5, 9.2, 7.0, 0.75, 1, "Ingesta del PDF Multipágina (PyMuPDF / fitz)", 
          "Apertura del archivo de 20+ páginas, extracción de texto directo e imágenes embebidas", "#F8FAFC", "#1B365D")

ax.annotate('', xy=(6.0, 8.5), xytext=(6.0, 9.2), arrowprops=dict(facecolor='#1B365D', width=1.5, headwidth=5))

# Step 2
draw_step(ax, 2.5, 7.7, 7.0, 0.75, 2, "Pipeline de Restauración de Imagen (OpenCV)", 
          "Denoising, corrección de inclinación (Deskew), realce de bordes (Unsharp) y CLAHE", "#F0FDF4", "#16A34A", "#15803D")

ax.annotate('', xy=(6.0, 7.0), xytext=(6.0, 7.7), arrowprops=dict(facecolor='#16A34A', width=1.5, headwidth=5))

# Step 3: Decision Gate
d_box = patches.FancyBboxPatch((3.0, 6.1), 6.0, 0.8, boxstyle="round,pad=0.06,rounding_size=0.15",
                               facecolor="#FEF3C7", edgecolor="#D97706", linewidth=1.8)
ax.add_patch(d_box)
ax.text(6.0, 6.55, "¿Contiene Contenedor .ZIP con XML DIAN?", fontsize=9, fontweight='bold', ha='center', va='center', color="#92400E")
ax.text(6.0, 6.30, "Compuerta de Facturación Electrónica Legal", fontsize=7.5, fontstyle='italic', ha='center', va='center', color="#B45309")

# Left branch (XML)
ax.annotate('', xy=(2.7, 5.0), xytext=(4.0, 6.1), arrowprops=dict(facecolor='#059669', width=1.5, headwidth=5))
ax.text(2.6, 5.55, "SÍ (Factura)", fontsize=8, fontweight='bold', color="#059669")

# Right branch (OCR + VLM)
ax.annotate('', xy=(9.3, 5.0), xytext=(8.0, 6.1), arrowprops=dict(facecolor='#7C3AED', width=1.5, headwidth=5))
ax.text(8.7, 5.55, "NO (PDF Escaneado/OC/PQRS)", fontsize=8, fontweight='bold', color="#7C3AED")

# Step 4A (Left)
draw_step(ax, 0.4, 4.15, 5.2, 0.8, "4A", "Parser XML Nativo (lxml / UBL 2.1)", 
          "Lectura 100% exacta de CUFE, NIT, montos, impuestos y duplicados", "#ECFDF5", "#059669", "#064E3B")

# Step 4B (Right)
draw_step(ax, 6.4, 4.15, 5.2, 0.8, "4B", "Tesseract OCR 5 + Qwen2-VL / LLaVA", 
          "OCR en 20 págs + VLM para 'árbol sí/no' y búsqueda difusa de keywords", "#F5F3FF", "#7C3AED", "#4C1D95")

# Converge to Step 5
ax.annotate('', xy=(5.2, 3.4), xytext=(3.0, 4.15), arrowprops=dict(facecolor='#4B5563', width=1.5, headwidth=5))
ax.annotate('', xy=(6.8, 3.4), xytext=(9.0, 4.15), arrowprops=dict(facecolor='#4B5563', width=1.5, headwidth=5))

# Step 5
draw_step(ax, 2.5, 2.55, 7.0, 0.8, 5, "Fusión de Datos, Validación de Reglas & Confianza", 
          "Extracción de palabras clave, resultado visual y cálculo de Score C", "#EFF6FF", "#2563EB")

ax.annotate('', xy=(6.0, 1.85), xytext=(6.0, 2.55), arrowprops=dict(facecolor='#2563EB', width=1.5, headwidth=5))

# Step 6
draw_step(ax, 1.0, 0.95, 10.0, 0.8, 6, "Renombrado Inteligente & Enrutamiento Departamental", 
          "Nuevo nombre: {FECHA}_{TIPO}_{ARBOL_SI/NO}_{ID}.pdf y movimiento a carpetas operativas", "#F8FAFC", "#1E293B")

ax.annotate('', xy=(6.0, 0.25), xytext=(6.0, 0.95), arrowprops=dict(facecolor='#1E293B', width=1.5, headwidth=5))

# Step 7
draw_step(ax, 2.5, -0.45, 7.0, 0.65, 7, "Audit Ledger Inmutable & Dashboard", 
          "Registro del Trace-ID, confianza y metadatos en base de datos local", "#F1F5F9", "#64748B")

plt.tight_layout()
flujo_path = os.path.join(out_dir, "diagrama_flujo.png")
plt.savefig(flujo_path, dpi=300, bbox_inches='tight')
plt.close()

# -------------------------------------------------------------
# 3. DIAGRAMA DE LOS TRES PROCESOS + PROCESAMIENTO VISUAL
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 6.5), dpi=300)
ax.set_xlim(0, 12)
ax.set_ylim(0, 6.5)
ax.axis('off')

ax.text(6.0, 6.1, "ESPECIALIZACIÓN TÉCNICA Y ANÁLISIS MULTIMODAL OPEN SOURCE", 
        fontsize=13.5, fontweight='bold', ha='center', va='center', color='#1B365D')
ax.text(6.0, 5.75, "Tratamiento especializado con herramientas 100% gratuitas, locales y preparadas para escaneos degradados", 
        fontsize=9, fontstyle='italic', ha='center', va='center', color='#4A5568')

def draw_proc_card(ax, x, y, w, h, title, subtitle, points, bg, border, header_bg):
    card = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.15",
                                 facecolor=bg, edgecolor=border, linewidth=1.8)
    ax.add_patch(card)
    hb = patches.FancyBboxPatch((x, y + h - 0.7), w, 0.7, boxstyle="round,pad=0.08,rounding_size=0.15",
                                facecolor=header_bg, edgecolor=header_bg, linewidth=1)
    ax.add_patch(hb)
    ax.text(x + w/2, y + h - 0.28, title, fontsize=10, fontweight='bold', ha='center', va='center', color='white')
    ax.text(x + w/2, y + h - 0.52, subtitle, fontsize=7.8, ha='center', va='center', color='#E2E8F0')
    
    start_y = y + h - 0.95
    for p in points:
        ax.text(x + 0.2, start_y, "•", fontsize=9, fontweight='bold', color=header_bg)
        ax.text(x + 0.4, start_y, p, fontsize=7.8, color='#1F2937', va='top', wrap=True)
        start_y -= 0.65

p1_pts = [
    "Detección de .ZIP con XML UBL 2.1.\nSin costo de inferencia.",
    "Parser determinista lxml con\nesquemas oficiales DIAN.",
    "Extracción exacta de CUFE,\nNIT, subtotal, IVA y fechas.",
    "Conciliación automática con OC y\ndetección de facturas repetidas.",
    "Destino: ERP Cuentas por Pagar."
]
draw_proc_card(ax, 0.4, 0.4, 3.6, 5.0, "1. FACTURAS DIAN", "Parser Determinista lxml", 
               p1_pts, "#F0FDF4", "#16A34A", "#15803D")

p2_pts = [
    "PDFs de 20 páginas con imágenes\nborrosas y texto degradado.",
    "Filtros OpenCV (Unsharp, Sauvola)\ny OCR Tesseract 5.x por página.",
    "Qwen2-VL / LLaVA para detectar\n'árbol sí/no', sellos y logos.",
    "Clasificación Producto vs Servicio\ny renombrado del archivo PDF.",
    "Destino: Servicios Internos."
]
draw_proc_card(ax, 4.2, 0.4, 3.6, 5.0, "2. ÓRDENES & PDFs COMPLEJOS", "Tesseract + Qwen2-VL / OpenCV", 
               p2_pts, "#EFF6FF", "#2563EB", "#1D4ED8")

p3_pts = [
    "Comprensión de lenguaje natural\nlocal con Qwen / LLaMA vía Ollama.",
    "No exige la palabra 'PQRS':\nidentifica quejas implícitas.",
    "Análisis de sentimiento, severidad\ny cálculo de SLA prioritario.",
    "Extracción de datos del cliente y\nradicación de ticket en SAC.",
    "Destino: CRM / SAC."
]
draw_proc_card(ax, 8.0, 0.4, 3.6, 5.0, "3. PQRS (SAC)", "NLU Local & Análisis de Sentimiento", 
               p3_pts, "#FAF5FF", "#9333EA", "#7E22CE")

plt.tight_layout()
proc_path = os.path.join(out_dir, "diagrama_procesos.png")
plt.savefig(proc_path, dpi=300, bbox_inches='tight')
plt.close()
print("Diagramas open source actualizados exitosamente.")
