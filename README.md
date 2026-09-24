# SmartDoc Engine — Buzón Inteligente RIWI Barranquilla

> **Plataforma de Clasificación Automatizada, Restauración OpenCV de Documentos Borrosos de 20 Páginas, Detección Visual ("Árbol SÍ/NO"), Doble Motor de Caché (0.002s) y Asistente Cognitivo Q&A.**

Diseñada para resolver integralmente el reto de automatización del buzón corporativo `info@riwi.io`, garantizando **$0.00 USD de costos operativos**, máxima velocidad de respuesta y trazabilidad empresarial.

---

## 🏛️ Arquitectura: 75% Determinística / 25% Inteligencia Artificial

```
                      [ CLIENTES / PROVEEDORES ]
                                  │
                                  ▼
               [ info@riwi.io / CARGA MULTIFORMATO ]
         (PDF 20 págs, DOCX, ZIP con XML DIAN, PNG, JPG, TIFF)
                                  │
                                  ▼
            ┌───────────────────────────────────────────┐
            │       CAPA 1: DOBLE MOTOR DE CACHÉ        │
            │  • L1 en RAM (LRU): 0.0001s               │
            │  • L2 SQLite (cache.db) SHA-256: 0.002s   │
            └───────────────────────────────────────────┘
                                  │ (Si es nuevo documento)
                                  ▼
            ┌───────────────────────────────────────────┐
            │        CAPA 2: ROUTER MULTIFORMATO        │
            │  • .ZIP/.XML -> Parser DIAN UBL 2.1 (lxml)│
            │  • .PDF      -> PyMuPDF (fitz) + Triage   │
            │  • .DOCX     -> python-docx (tablas/fotos)│
            │  • Imágenes  -> OpenCV Pipeline           │
            └───────────────────────────────────────────┘
                                  │
                                  ▼
            ┌───────────────────────────────────────────┐
            │   CAPA 3: RESTAURACIÓN OPENCV (ESCANEOS)  │
            │  • Varianza Laplaciana (blur < 120)       │
            │  • Unsharp Masking (enfoque de trazos)    │
            │  • CLAHE (ecualización adaptativa local)  │
            │  • Deskewing (corrección de inclinación)  │
            └───────────────────────────────────────────┘
                                  │
                                  ▼
            ┌───────────────────────────────────────────┐
            │    CAPA 4: VISIÓN Y DETECCIÓN DE OBJETOS  │
            │  • YOLOv8-Nano (15ms en CPU)              │
            │  • Detección "Árbol SÍ/NO" (HSV + Gemini) │
            │  • Detección morfológica de firmas/sellos │
            └───────────────────────────────────────────┘
                                  │
                                  ▼
            ┌───────────────────────────────────────────┐
            │    CAPA 5: CASCADA INTELIGENTE MULTI-TIER │
            │  • Tier 0: Reglas determinísticas & Regex │
            │  • Tier 1: Groq Cloud API (LLaMA 3.3 70B) │
            │  • Tier 2: Google Gemini (2.5 Flash VLM)  │
            │  • Tier 3: Local Offline Fallback         │
            └───────────────────────────────────────────┘
                                  │
                                  ▼
            ┌───────────────────────────────────────────┐
            │     CAPA 6: RENOMBRADO, REPORTE & CHAT    │
            │  • {FECHA}_{TIPO}_{ARBOL}_{ID}.ext        │
            │  • Descarga en lote ZIP + Reporte Excel   │
            │  • Auditoría Conversacional Multimodal    │
            └───────────────────────────────────────────┘
```

---

## 🚀 Capacidades Destacadas

1. **Escaneo y Procesamiento de Documentos de 20 Páginas:**
   - Soporta PDFs extensos y escaneos multipágina gracias al triage digital inteligente de `PyMuPDF`.
   - Si el documento contiene texto digital, lo extrae en milisegundos; si es un escaneo de baja resolución, lo rasteriza y aplica el pipeline OpenCV.

2. **Restauración de Documentos e Imágenes Borrosas:**
   - Calcula la **Varianza Laplaciana** de cada página. Si la nitidez cae por debajo del umbral de calidad, aplica un filtro de realce de bordes de alta frecuencia (**Unsharp Masking**) y **CLAHE** para rescatar tinta desvanecida y fondos manchados.

3. **Detección Visual: "¿Hay un árbol en la imagen? SÍ/NO":**
   - Resuelve preguntas de visión artificial mediante segmentación colorimétrica en espacio HSV, YOLOv8-Nano y confirmación multimodal con **Google Gemini 2.5 Flash**.

4. **Extracción Fiscal DIAN 100% Determinística (ZIP con XML UBL 2.1):**
   - Lee archivos `.zip` comprimidos con facturas electrónicas colombianas.
   - Extrae CUFE, NIT del emisor, Razón Social, valor total e IVA en **0.002 segundos** usando `lxml`, con 0% de alucinación y 0% de costo en tokens.

5. **Doble Motor de Caché Criptográfico (SHA-256):**
   - Si un usuario o proveedor envía 10 veces la misma factura, el sistema detecta la huella SHA-256 en 0.002 segundos y devuelve el resultado precalculado, ahorrando el 100% del cómputo y evitando duplicados en la base de datos de Tesorería.

6. **Estandarización y Renombrado Automático:**
   - Genera nombres uniformes bajo la norma empresarial:
     ```text
     {FECHA}_{CATEGORIA}_{ARBOL_SI/NO}_{ID}.ext
     Ejemplo: 20260921_FACTURA_ARBOL_NO_SETP9921.zip
     ```

7. **Asistente Cognitivo & Chat Documental (Q&A):**
   - Permite seleccionar cualquier archivo analizado y hacerle preguntas libres en lenguaje natural con citas de páginas y respuestas en menos de 1 segundo.

---

## 💻 Instalación y Ejecución Rápida

### Requisitos Previos
- Python 3.11 o 3.12
- Gestor de paquetes `uv` (o `pip`)

### 1. Clonar y Crear Entorno Virtual
```bash
# Crear entorno virtual con Python 3.12 usando uv
uv venv .venv --python 3.12
source .venv/bin/activate
```

### 2. Instalar Dependencias
```bash
uv pip install -r requirements.txt
```

### 3. Configurar Variables de Entorno (Opcional)
Copia el archivo de ejemplo y configura tu clave de Gemini si deseas aceleración de visión:
```bash
cp .env.example .env
```
*(También puedes ingresar tu clave directamente en la interfaz gráfica de Streamlit).*

### 4. Ejecutar la Aplicación Web
```bash
streamlit run main.py
```
Abre tu navegador en `http://localhost:8501`.

---

## 🧪 Pruebas Automatizadas

Para ejecutar la suite completa de pruebas unitarias e integración:
```bash
python3 -m unittest tests/test_pipeline.py -v
```

---

## 👥 Equipo de Desarrollo y Roles
- **Daniel David Martinez Gonzalez:** Arquitectura Open Source, Doble Motor de Caché e Integración del Sistema.
- **Breyner De Jesus Manga Arias:** Ingeniería de Datos, Pipeline OpenCV y Restauración de Documentos Borrosos.
- **Joseph Romero:** Visión Artificial, YOLOv8-Nano y Cascada Multimodal de Lenguaje (Gemini / Groq).

---

## 📄 Licencia
Proyecto desarrollado para RIWI Barranquilla bajo licencia MIT. Libre de costos de licenciamiento o suscripciones pagas ($0.00 USD).
