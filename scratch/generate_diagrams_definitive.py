import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

out_dir = "/home/ddamago/Projects/buzoncorporativoRIWI/Propuesta/assets"
os.makedirs(out_dir, exist_ok=True)

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'

# -------------------------------------------------------------
# 1. DIAGRAMA DE ARQUITECTURA DEFINITIVA (DOBLE CACHÉ & CASCADA)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(13, 11), dpi=300)
ax.set_xlim(0, 13)
ax.set_ylim(0, 11)
ax.axis('off')

ax.text(6.5, 10.6, "ARQUITECTURA DE PRODUCCIÓN SMARTINBOX RIWI — MÁXIMO RENDIMIENTO ($0 USD)", 
        fontsize=14.5, fontweight='bold', ha='center', va='center', color='#1B365D')
ax.text(6.5, 10.25, "Doble Motor de Caché • Cascada Multi-Proveedor (Groq/Gemini/Local) • PaddleOCR ONNX & YOLOv8", 
        fontsize=10, fontstyle='italic', ha='center', va='center', color='#4A5568')

def draw_layer_box(ax, x, y, w, h, title, bg_color, border_color):
    rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.15",
                                  facecolor=bg_color, edgecolor=border_color, linewidth=1.8, alpha=0.95)
    ax.add_patch(rect)
    hb = patches.FancyBboxPatch((x, y + h - 0.45), w, 0.45, boxstyle="round,pad=0.08,rounding_size=0.15",
                                facecolor=border_color, edgecolor=border_color, linewidth=1)
    ax.add_patch(hb)
    ax.text(x + w/2, y + h - 0.22, title, fontsize=9.5, fontweight='bold', ha='center', va='center', color='white')

def draw_comp(ax, x, y, w, h, text, subtext="", fill="#FFFFFF", border="#CBD5E0", text_color="#1A202C"):
    c = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.1",
                               facecolor=fill, edgecolor=border, linewidth=1.2)
    ax.add_patch(c)
    if subtext:
        ax.text(x + w/2, y + h*0.62, text, fontsize=8.2, fontweight='bold', ha='center', va='center', color=text_color)
        ax.text(x + w/2, y + h*0.28, subtext, fontsize=7.0, ha='center', va='center', color='#718096')
    else:
        ax.text(x + w/2, y + h/2, text, fontsize=8, fontweight='bold', ha='center', va='center', color=text_color)

# Capa 1: Ingesta & Doble Caché
draw_layer_box(ax, 0.5, 8.7, 12, 1.35, "1. INGESTA ASÍNCRONA & DOBLE MOTOR DE CACHÉ CRIPTOGRÁFICO", "#F8FAFC", "#1B365D")
draw_comp(ax, 0.8, 8.85, 3.6, 0.75, "Buzón info@riwi.io", "API Graph / Webhook Push", "#FFFFFF", "#1B365D")
draw_comp(ax, 4.7, 8.85, 3.6, 0.75, "Caché SHA-256 (0.002s)", "Bypass instantáneo si el PDF ya fue procesado", "#ECFDF5", "#059669", "#064E3B")
draw_comp(ax, 8.6, 8.85, 3.6, 0.75, "Cola Asíncrona en Memoria", "asyncio.Queue / Redis local anti-colapso", "#FFFFFF", "#1B365D")

# Arrow 1 -> 2
ax.annotate('', xy=(6.5, 8.4), xytext=(6.5, 8.7), arrowprops=dict(facecolor='#1B365D', width=2, headwidth=6))

# Capa 2: Preprocesamiento OpenCV
draw_layer_box(ax, 0.5, 6.75, 12, 1.45, "2. PROCESAMIENTO MULTIPÁGINA & RESTAURACIÓN VISUAL (PyMuPDF + OpenCV)", "#F0FDF4", "#16A34A")
draw_comp(ax, 0.8, 6.9, 2.7, 0.8, "Triage de Capa (0.01s)", "Bypass de texto digital nativo", "#FFFFFF", "#16A34A")
draw_comp(ax, 3.8, 6.9, 2.7, 0.8, "Detección Desenfoque", "Varianza Laplaciana (cv2)", "#FFFFFF", "#16A34A")
draw_comp(ax, 6.8, 6.9, 2.7, 0.8, "Filtro Unsharp & CLAHE", "Enfoque de trazos y contraste", "#FFFFFF", "#16A34A")
draw_comp(ax, 9.8, 6.9, 2.4, 0.8, "Binarización Sauvola", "Limpieza de sombras y pliegues", "#FFFFFF", "#16A34A")

# Arrow 2 -> 3
ax.annotate('', xy=(6.5, 6.45), xytext=(6.5, 6.75), arrowprops=dict(facecolor='#16A34A', width=2, headwidth=6))

# Capa 3: Motores de Análisis (DIAN Determinista + OCR ONNX)
draw_layer_box(ax, 0.5, 4.65, 12, 1.6, "3. MOTORES DETERMINISTAS & OCR NEURONAL PARALELO (CERO IA EN FINANZAS)", "#F0F9FF", "#0284C7")
draw_comp(ax, 0.8, 4.8, 3.6, 0.85, "Parser XML DIAN (lxml)", "Apertura de .ZIP y lectura UBL 2.1\nPrecisión matemática 100% (0.001s)", "#F0FDF4", "#15803D", "#15803D")
draw_comp(ax, 4.7, 4.8, 3.6, 0.85, "PaddleOCR (PP-OCRv4 ONNX)", "Multiprocesamiento en 4 núcleos\n3x más rápido que Tesseract en borroso", "#EFF6FF", "#2563EB", "#1D4ED8")
draw_comp(ax, 8.6, 4.8, 3.6, 0.85, "Búsqueda Difusa RapidFuzz", "Tolerancia a errores de lectura OCR\n(Distancia de Levenshtein)", "#FFFFFF", "#0284C7")

# Arrow 3 -> 4
ax.annotate('', xy=(6.5, 4.35), xytext=(6.5, 4.65), arrowprops=dict(facecolor='#0284C7', width=2, headwidth=6))

# Capa 4: Cascada Multi-Proveedor
draw_layer_box(ax, 0.5, 2.15, 12, 2.0, "4. CASCADA MULTI-PROVEEDOR GRATUITA (TIER 1 GROQ -> TIER 2 GEMINI -> TIER 3 LOCAL)", "#FAF5FF", "#7C3AED")
draw_comp(ax, 0.8, 2.9, 3.6, 0.75, "Tier 1: Groq Cloud API (Free)", "LLaMA-3.3-70B (0.2s de respuesta)\nClasificación instantánea de PQRS", "#F3E8FF", "#7C3AED", "#581C87")
draw_comp(ax, 4.7, 2.9, 3.6, 0.75, "Tier 2: Gemini 2.0 Flash (Free)", "Google AI Studio (15 RPM / 1.500 día)\nVisión multimodal nativa de respaldo", "#EFF6FF", "#2563EB", "#1E3A8A")
draw_comp(ax, 8.6, 2.9, 3.6, 0.75, "Tier 3: Local Offline Fallback", "YOLOv8-Nano (15ms árbol sí/no)\n+ Moondream2 / Ollama sin internet", "#FEF3C7", "#D97706", "#78350F")
draw_comp(ax, 2.5, 2.25, 8.0, 0.5, "Consola Human-in-the-Loop (Local): Resolución asistida en 2 clics si C < 90%", "", "#FEF2F2", "#DC2626", "#7F1D1D")

# Arrow 4 -> 5
ax.annotate('', xy=(6.5, 1.85), xytext=(6.5, 2.15), arrowprops=dict(facecolor='#7C3AED', width=2, headwidth=6))

# Capa 5: Enrutamiento y Auditoría
draw_layer_box(ax, 0.5, 0.2, 12, 1.45, "5. RENOMBRADO AUTOMÁTICO, ENRUTAMIENTO Y AUDITORÍA INMUTABLE", "#F8FAFC", "#1E293B")
draw_comp(ax, 0.8, 0.35, 3.6, 0.8, "Renombrado Estandarizado", "{FECHA}_{TIPO}_{ARBOL_SI}_{ID}.pdf", "#FFFFFF", "#475569")
draw_comp(ax, 4.7, 0.35, 3.6, 0.8, "Enrutamiento Departamental", "Cuentas por Pagar, Compras, SAC", "#FFFFFF", "#475569")
draw_comp(ax, 8.6, 0.35, 3.6, 0.8, "Auditoría Trace-ID", "SQLite / PostgreSQL inmutable", "#EFF6FF", "#3B82F6")

plt.tight_layout()
arch_path = os.path.join(out_dir, "diagrama_arquitectura.png")
plt.savefig(arch_path, dpi=300, bbox_inches='tight')
plt.close()
print("Diagrama de arquitectura actualizado con doble caché y cascada.")

# -------------------------------------------------------------
# 2. DIAGRAMA DE FLUJO CON DOBLE CACHÉ Y CASCADA
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 11), dpi=300)
ax.set_xlim(0, 12)
ax.set_ylim(0, 11)
ax.axis('off')

ax.text(6.0, 10.6, "FLUJO TÉCNICO: DOBLE CACHÉ, CASCADA MULTI-PROVEEDOR Y RENOMBRADO", 
        fontsize=14, fontweight='bold', ha='center', va='center', color='#1B365D')
ax.text(6.0, 10.25, "Bypass criptográfico SHA-256 (0.002s) -> OpenCV -> PaddleOCR -> Cascada Groq/Gemini/YOLO", 
        fontsize=9.5, fontstyle='italic', ha='center', va='center', color='#4A5568')

def draw_step(ax, x, y, w, h, step_num, title, detail, fill="#FFFFFF", border="#CBD5E0", title_color="#1B365D"):
    p = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06,rounding_size=0.12",
                               facecolor=fill, edgecolor=border, linewidth=1.5)
    ax.add_patch(p)
    circ = patches.Circle((x + 0.4, y + h/2), 0.25, facecolor=border, edgecolor=border)
    ax.add_patch(circ)
    ax.text(x + 0.4, y + h/2, str(step_num), fontsize=9.5, fontweight='bold', ha='center', va='center', color='white')
    ax.text(x + 0.85, y + h*0.64, title, fontsize=9, fontweight='bold', ha='left', va='center', color=title_color)
    ax.text(x + 0.85, y + h*0.32, detail, fontsize=7.8, ha='left', va='center', color='#4B5563')

# Step 1: Ingesta & SHA-256
draw_step(ax, 2.5, 9.2, 7.0, 0.75, 1, "Ingesta & Chequeo de Caché SHA-256 (0.002s)", 
          "Si el PDF ya fue procesado antes, devuelve el resultado de inmediato sin gastar CPU", "#ECFDF5", "#059669", "#064E3B")

ax.annotate('', xy=(6.0, 8.5), xytext=(6.0, 9.2), arrowprops=dict(facecolor='#059669', width=1.5, headwidth=5))

# Step 2: PyMuPDF Triage
draw_step(ax, 2.5, 7.75, 7.0, 0.75, 2, "Triage de Capa con PyMuPDF (0.01s)", 
          "Extrae texto digital si existe; envía páginas escaneadas/borrosas a OpenCV", "#F8FAFC", "#1B365D")

ax.annotate('', xy=(6.0, 7.05), xytext=(6.0, 7.75), arrowprops=dict(facecolor='#1B365D', width=1.5, headwidth=5))

# Step 3: Decision Gate (DIAN vs OCR)
d_box = patches.FancyBboxPatch((3.0, 6.15), 6.0, 0.8, boxstyle="round,pad=0.06,rounding_size=0.15",
                               facecolor="#FEF3C7", edgecolor="#D97706", linewidth=1.8)
ax.add_patch(d_box)
ax.text(6.0, 6.6, "¿Adjunto .ZIP con XML UBL 2.1?", fontsize=9, fontweight='bold', ha='center', va='center', color="#92400E")
ax.text(6.0, 6.35, "Compuerta de Facturación DIAN", fontsize=7.5, fontstyle='italic', ha='center', va='center', color="#B45309")

# Left (XML)
ax.annotate('', xy=(2.7, 5.05), xytext=(4.0, 6.15), arrowprops=dict(facecolor='#059669', width=1.5, headwidth=5))
ax.text(2.6, 5.6, "SÍ (Factura)", fontsize=8, fontweight='bold', color="#059669")

# Right (PDF/OCR)
ax.annotate('', xy=(9.3, 5.05), xytext=(8.0, 6.15), arrowprops=dict(facecolor='#7C3AED', width=1.5, headwidth=5))
ax.text(8.7, 5.6, "NO (PDF Escaneado/OC/PQRS)", fontsize=8, fontweight='bold', color="#7C3AED")

# Step 4A (Left)
draw_step(ax, 0.4, 4.2, 5.2, 0.8, "4A", "Parser Determinista lxml (0.001s)", 
          "Lectura matemática exacta de CUFE, NIT y montos (0% IA)", "#ECFDF5", "#059669", "#064E3B")

# Step 4B (Right)
draw_step(ax, 6.4, 4.2, 5.2, 0.8, "4B", "OpenCV Sauvola + PaddleOCR ONNX", 
          "Enfoque de letras borrosas y OCR neuronal en paralelo", "#EFF6FF", "#2563EB", "#1D4ED8")

# Converge to Step 5
ax.annotate('', xy=(5.2, 3.45), xytext=(3.0, 4.2), arrowprops=dict(facecolor='#4B5563', width=1.5, headwidth=5))
ax.annotate('', xy=(6.8, 3.45), xytext=(9.0, 4.2), arrowprops=dict(facecolor='#4B5563', width=1.5, headwidth=5))

# Step 5: Cascada Multi-Proveedor
draw_step(ax, 1.5, 2.45, 9.0, 0.9, 5, "Cascada Multi-Proveedor Gratuita ($0 USD)", 
          "Tier 1: Groq Cloud (0.2s) -> Tier 2: Gemini Flash Free (Visión) -> Tier 3: YOLOv8 / Ollama Local", "#FAF5FF", "#7C3AED", "#581C87")

ax.annotate('', xy=(6.0, 1.75), xytext=(6.0, 2.45), arrowprops=dict(facecolor='#7C3AED', width=1.5, headwidth=5))

# Step 6: Renombrado
draw_step(ax, 1.5, 0.85, 9.0, 0.8, 6, "Renombrado Automático & Enrutamiento Departamental", 
          "Formato: {FECHA}_{TIPO}_{ARBOL_SI/NO}_{ID}.pdf y movimiento a carpetas", "#F8FAFC", "#1E293B")

ax.annotate('', xy=(6.0, 0.15), xytext=(6.0, 0.85), arrowprops=dict(facecolor='#1E293B', width=1.5, headwidth=5))

# Step 7: Auditoría
draw_step(ax, 2.5, -0.55, 7.0, 0.65, 7, "Audit Ledger SQLite / PostgreSQL", 
          "Registro inmutable de Trace-ID, marcas de tiempo y métricas diarias", "#F1F5F9", "#64748B")

plt.tight_layout()
flujo_path = os.path.join(out_dir, "diagrama_flujo.png")
plt.savefig(flujo_path, dpi=300, bbox_inches='tight')
plt.close()
print("Diagrama de flujo actualizado con doble caché y cascada.")
