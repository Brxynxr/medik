// SmartDoc Engine — Buzón Corporativo RIWI Application Logic

let activeParams = ["total", "fecha", "nit"];
let selectedFiles = []; // Array of { id, file, status, result, error }
let chatHistory = [];
let jobStartTime = null;
let timerInterval = null;

document.addEventListener("DOMContentLoaded", () => {
    initDropzone();
    initParamInputs();
    renderActiveParams();
});

// Dropzone Initialization (Multiple Files & Incremental Upload)
function initDropzone() {
    const dropzone = document.getElementById("dropzone-area");
    const fileInput = document.getElementById("pdf-file-input");

    if (!dropzone || !fileInput) return;

    ["dragenter", "dragover"].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.add("dragover");
        });
    });

    ["dragleave", "drop"].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove("dragover");
        });
    });

    dropzone.addEventListener("drop", (e) => {
        const files = e.dataTransfer.files;
        if (files && files.length > 0) {
            addFilesToQueue(files);
        }
    });

    fileInput.addEventListener("change", (e) => {
        if (fileInput.files && fileInput.files.length > 0) {
            addFilesToQueue(fileInput.files);
            fileInput.value = ""; // Reset to allow re-selection
        }
    });
}

function addFilesToQueue(fileList) {
    const validExts = [".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".webp", ".docx", ".xml", ".zip"];
    let addedCount = 0;

    Array.from(fileList).forEach(file => {
        const fileName = file.name.toLowerCase();
        const isValid = validExts.some(ext => fileName.endsWith(ext)) || file.type.includes("pdf") || file.type.includes("image");
        if (!isValid) {
            showToast(`Archivo '${file.name}' no compatible. Admite PDF, XML, ZIP, DOCX e imágenes.`, "warning");
            return;
        }

        const exists = selectedFiles.some(f => f.file.name === file.name && f.file.size === file.size && f.file.lastModified === file.lastModified);
        if (exists) {
            showToast(`'${file.name}' ya está en la cola de procesamiento.`, "info");
            return;
        }

        selectedFiles.push({
            id: 'file_' + Math.random().toString(36).substring(2, 9),
            file: file,
            status: 'ready',
            result: null,
            error: null
        });
        addedCount++;
    });

    if (addedCount > 0) {
        renderFileQueue();
    }
}

function removeFileFromQueue(fileId) {
    selectedFiles = selectedFiles.filter(item => item.id !== fileId);
    renderFileQueue();
}

function clearFileQueue() {
    selectedFiles = [];
    const fileInput = document.getElementById("pdf-file-input");
    if (fileInput) fileInput.value = "";
    renderFileQueue();
    const batchSummary = document.getElementById("batch-summary-container");
    if (batchSummary) {
        batchSummary.classList.add("hidden");
        batchSummary.innerHTML = "";
    }
}

function renderFileQueue() {
    const queueCard = document.getElementById("file-queue-card");
    const queueList = document.getElementById("file-queue-list");
    const countBadge = document.getElementById("queue-count-badge");
    const submitBtnText = document.getElementById("submit-btn-text");

    if (!queueCard || !queueList) return;

    if (selectedFiles.length === 0) {
        queueCard.classList.add("hidden");
        queueList.innerHTML = "";
        if (submitBtnText) submitBtnText.textContent = "Procesar Documento en Buzón";
        return;
    }

    queueCard.classList.remove("hidden");
    if (countBadge) countBadge.textContent = selectedFiles.length;

    if (submitBtnText) {
        if (selectedFiles.length === 1) {
            submitBtnText.textContent = "Procesar 1 Documento en Buzón";
        } else {
            submitBtnText.textContent = `Procesar Lote de ${selectedFiles.length} Documentos`;
        }
    }

    queueList.innerHTML = "";
    selectedFiles.forEach((item) => {
        const ext = item.file.name.split('.').pop().toLowerCase();
        let iconText = "PDF";
        let iconBg = "#e0e7ff";
        let iconColor = "#4338ca";

        if (["zip", "xml"].includes(ext)) {
            iconText = "DIAN";
            iconBg = "#fef3c7";
            iconColor = "#b45309";
        } else if (["png", "jpg", "jpeg", "webp", "tiff"].includes(ext)) {
            iconText = "IMG";
            iconBg = "#dcfce7";
            iconColor = "#15803d";
        } else if (["docx", "doc"].includes(ext)) {
            iconText = "DOC";
            iconBg = "#e0f2fe";
            iconColor = "#0369a1";
        }

        let statusClass = "status-ready";
        let statusLabel = "Listo";
        if (item.status === "processing") {
            statusClass = "status-processing";
            statusLabel = "Procesando...";
        } else if (item.status === "completed") {
            statusClass = "status-completed";
            statusLabel = "✓ Completado";
        } else if (item.status === "error") {
            statusClass = "status-error";
            statusLabel = "Error";
        }

        const row = document.createElement("div");
        row.className = "file-queue-item";
        row.id = `queue-row-${item.id}`;
        row.innerHTML = `
            <div class="file-queue-item-left">
                <div class="file-queue-icon" style="background: ${iconBg}; color: ${iconColor};">
                    ${iconText}
                </div>
                <div class="file-queue-meta">
                    <span class="file-queue-name" title="${escapeHtml(item.file.name)}">${escapeHtml(item.file.name)}</span>
                    <span class="file-queue-size">${formatBytes(item.file.size)}</span>
                </div>
            </div>
            <div class="file-queue-item-right">
                <span class="file-status-badge ${statusClass}" id="status-badge-${item.id}">${statusLabel}</span>
                <button type="button" class="btn-remove-queue-item" onclick="removeFileFromQueue('${item.id}')" title="Eliminar de la cola">
                    &times;
                </button>
            </div>
        `;
        queueList.appendChild(row);
    });
}

function formatBytes(bytes) {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}

// Parameter Tag Inputs
function initParamInputs() {
    const input = document.getElementById("param-input");
    const addBtn = document.getElementById("btn-add-param");

    if (!input) return;

    input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            addParamFromInput();
        }
    });

    if (addBtn) {
        addBtn.addEventListener("click", () => {
            addParamFromInput();
        });
    }
}

function addParamFromInput() {
    const input = document.getElementById("param-input");
    if (!input) return;
    const val = input.value.trim().toLowerCase();
    if (val) {
        addParamTag(val);
        input.value = "";
    }
}

function addParamTag(param) {
    const cleaned = param.trim().toLowerCase();
    if (!cleaned) return;
    if (!activeParams.includes(cleaned)) {
        activeParams.push(cleaned);
        renderActiveParams();
    }
}

function removeParamTag(index) {
    activeParams.splice(index, 1);
    renderActiveParams();
}

function renderActiveParams() {
    const container = document.getElementById("active-params-container");
    if (!container) return;

    container.innerHTML = "";
    if (activeParams.length === 0) {
        container.innerHTML = `<span class="text-dim" style="font-size: 0.85rem; padding: 0.25rem 0.5rem;">Ningún parámetro ingresado. Agrega al menos uno.</span>`;
        return;
    }

    activeParams.forEach((param, idx) => {
        const tag = document.createElement("div");
        tag.className = "param-tag";
        tag.innerHTML = `
            <span>${param}</span>
            <span class="param-tag-remove" onclick="removeParamTag(${idx})">&times;</span>
        `;
        container.appendChild(tag);
    });
}

// Job Submission & SSE Streaming (Supports Single File & Multi-File Batch)
async function submitJob() {
    if (selectedFiles.length === 0) {
        showToast("Selecciona o arrastra al menos un archivo para continuar.", "warning");
        return;
    }

    if (activeParams.length === 0) {
        showToast("Debes ingresar al menos un parámetro de búsqueda.", "warning");
        return;
    }

    const submitBtn = document.getElementById("btn-submit-job");
    const spinner = document.getElementById("submit-spinner");
    const btnText = document.getElementById("submit-btn-text");
    const progressPanel = document.getElementById("live-progress-panel");

    if (submitBtn) submitBtn.disabled = true;
    if (spinner) spinner.classList.remove("hidden");
    if (progressPanel) progressPanel.classList.remove("hidden");

    startTimer();

    // CASE 1: Archivo único -> Streaming en tiempo real con SSE
    if (selectedFiles.length === 1) {
        if (btnText) btnText.textContent = "Analizando Documento...";
        appendTerminal("> Enviando archivo y parámetros al orquestador...");

        const item = selectedFiles[0];
        item.status = "processing";
        renderFileQueue();

        const formData = new FormData();
        formData.append("file", item.file);
        formData.append("parametros", JSON.stringify(activeParams));
        
        const catalogarCheck = document.getElementById("catalogar-imagenes-checkbox");
        if (catalogarCheck) {
            formData.append("catalogar_imagenes", catalogarCheck.checked);
        }

        try {
            const response = await fetch("/procesar/stream", {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.message || `Error del servidor: ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split("\n\n");
                buffer = lines.pop(); // Keep partial line in buffer

                for (const chunk of lines) {
                    if (!chunk.trim()) continue;
                    const eventLines = chunk.split("\n");
                    let eventData = "";

                    for (const line of eventLines) {
                        if (line.startsWith("data: ")) {
                            eventData = line.substring(6);
                        }
                    }

                    if (eventData) {
                        try {
                            const parsed = JSON.parse(eventData);
                            handleStreamEvent(parsed);
                        } catch (e) {
                            console.error("Error parsing SSE event data:", e);
                        }
                    }
                }
            }
        } catch (err) {
            stopTimer();
            item.status = "error";
            renderFileQueue();
            showToast(err.message, "danger");
            appendTerminal(`[ERROR] ${err.message}`);
            if (submitBtn) submitBtn.disabled = false;
            if (spinner) spinner.classList.add("hidden");
            if (btnText) btnText.textContent = "Reintentar Análisis";
        }
        return;
    }

    // CASE 2: Procesamiento por Lote de Múltiples Archivos
    if (btnText) btnText.textContent = `Procesando Lote (0 / ${selectedFiles.length})...`;
    appendTerminal(`> Iniciando procesamiento en lote de ${selectedFiles.length} documentos...`);

    const batchResults = [];
    const progressBar = document.getElementById("progress-bar-fill");
    const statusText = document.getElementById("progress-status-text");

    for (let i = 0; i < selectedFiles.length; i++) {
        const item = selectedFiles[i];
        item.status = "processing";
        renderFileQueue();

        if (statusText) statusText.textContent = `Procesando archivo ${i + 1} de ${selectedFiles.length}: ${item.file.name}...`;
        appendTerminal(`> [${i + 1}/${selectedFiles.length}] Subiendo y analizando '${item.file.name}'...`);

        const formData = new FormData();
        formData.append("file", item.file);
        formData.append("parametros", JSON.stringify(activeParams));
        const catalogarCheck = document.getElementById("catalogar-imagenes-checkbox");
        if (catalogarCheck) formData.append("catalogar_imagenes", catalogarCheck.checked);

        try {
            const resp = await fetch("/procesar", {
                method: "POST",
                body: formData
            });

            if (!resp.ok) {
                const errData = await resp.json().catch(() => ({}));
                throw new Error(errData.message || `Error del servidor: ${resp.status}`);
            }

            const data = await resp.json();
            item.status = "completed";
            item.result = data;
            batchResults.push(data);
            appendTerminal(`> [${i + 1}/${selectedFiles.length}] ✓ Completado '${item.file.name}' (${data.duracion_total_ms.toFixed(1)} ms, ${data.paginas_totales} págs)`);
        } catch (err) {
            item.status = "error";
            item.error = err.message;
            appendTerminal(`> [${i + 1}/${selectedFiles.length}] ✕ Error en '${item.file.name}': ${err.message}`);
        }

        renderFileQueue();
        const pct = Math.round(((i + 1) / selectedFiles.length) * 100);
        if (progressBar) progressBar.style.width = `${pct}%`;
        if (btnText) btnText.textContent = `Procesando Lote (${i + 1} / ${selectedFiles.length})...`;
    }

    stopTimer();
    if (submitBtn) submitBtn.disabled = false;
    if (spinner) spinner.classList.add("hidden");
    if (btnText) btnText.textContent = "Procesar Nuevos Documentos";
    if (statusText) statusText.textContent = `Lote finalizado: ${batchResults.length} de ${selectedFiles.length} documentos procesados con éxito.`;

    renderBatchSummary(batchResults);
}

function renderBatchSummary(results) {
    const container = document.getElementById("batch-summary-container");
    if (!container || !results || results.length === 0) return;

    container.classList.remove("hidden");
    container.innerHTML = `
        <div class="batch-summary-header">
            <div class="batch-summary-title">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                <span>Resumen del Lote: ${results.length} Documentos Analizados</span>
            </div>
            <a href="/resultados/${results[0].pdf_hash}" class="btn btn-primary" style="padding: 0.35rem 0.85rem; font-size: 0.82rem;">
                Abrir Primer Documento &rarr;
            </a>
        </div>
        <table class="batch-summary-table">
            <thead>
                <tr>
                    <th>Archivo / Hash</th>
                    <th>Páginas</th>
                    <th>Área / Clasificación</th>
                    <th>Hallazgos Clave</th>
                    <th>Acción</th>
                </tr>
            </thead>
            <tbody>
                ${results.map(r => {
                    const topHallazgos = (r.hallazgos || []).slice(0, 2).map(h => `${h.parametro}: ${h.valor}`).join(" • ") || "—";
                    return `
                    <tr>
                        <td>
                            <strong style="color:#0f172a;">${escapeHtml(r.nombre_archivo_sugerido || r.pdf_hash.substring(0, 14))}</strong>
                            <div style="font-family:var(--font-mono); font-size:0.72rem; color:#64748b;">${r.pdf_hash.substring(0, 16)}...</div>
                        </td>
                        <td><strong>${r.paginas_totales}</strong></td>
                        <td><span class="param-badge">${escapeHtml(r.departamento_sugerido || 'General')}</span></td>
                        <td style="font-size:0.8rem; color:#334155;">${escapeHtml(topHallazgos)}</td>
                        <td>
                            <a href="/resultados/${r.pdf_hash}" class="btn btn-secondary" style="padding:0.25rem 0.65rem; font-size:0.78rem;">
                                🔍 Abrir Visor
                            </a>
                        </td>
                    </tr>
                    `;
                }).join("")}
            </tbody>
        </table>
    `;

    container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function handleStreamEvent(event) {
    const statusText = document.getElementById("progress-status-text");
    const progressBar = document.getElementById("progress-bar-fill");
    const pagesLabel = document.getElementById("pages-processed-label");

    if (event.tipo === "inicio") {
        if (statusText) statusText.textContent = `Calculado SHA-256 (${event.pdf_hash.substring(0, 10)}...). Total: ${event.total_paginas} páginas.`;
        if (progressBar) progressBar.style.width = "15%";
        initPageGrid(event.total_paginas);
        appendTerminal(`> Hash SHA-256: ${event.pdf_hash}`);
        appendTerminal(`> Total páginas detectadas: ${event.total_paginas}`);
    } else if (event.tipo === "pagina") {
        updatePageBlock(event.numero_pagina, event.carril);
        if (statusText) statusText.textContent = `Página ${event.numero_pagina} clasificada como '${event.carril}' (${event.duracion_ms.toFixed(1)} ms)`;
        if (pagesLabel) pagesLabel.textContent = `${event.paginas_completadas} / ${event.total_paginas}`;
        
        const pct = Math.min(85, Math.floor((event.paginas_completadas / event.total_paginas) * 80) + 15);
        if (progressBar) progressBar.style.width = `${pct}%`;
        appendTerminal(`> Pág ${event.numero_pagina}: ${event.carril} (${event.duracion_ms.toFixed(1)} ms)`);
    } else if (event.tipo === "completado") {
        stopTimer();
        if (progressBar) progressBar.style.width = "100%";
        if (statusText) statusText.textContent = "Procesamiento completado con éxito. Redirigiendo...";
        appendTerminal(`> Dictamen consolidado en ${event.duracion_total_ms.toFixed(1)} ms. Caché: ${event.nivel_cache}`);
        setTimeout(() => {
            window.location.href = `/resultados/${event.pdf_hash}`;
        }, 600);
    }
}

function initPageGrid(totalPages) {
    const grid = document.getElementById("pages-live-grid");
    if (!grid) return;
    grid.innerHTML = "";
    for (let i = 1; i <= totalPages; i++) {
        const block = document.createElement("div");
        block.id = `page-block-${i}`;
        block.className = "page-block";
        block.textContent = `Pág ${i}`;
        grid.appendChild(block);
    }
}

function updatePageBlock(pageNum, carril) {
    const block = document.getElementById(`page-block-${pageNum}`);
    if (block) {
        block.className = `page-block page-${carril}`;
    }
}

function appendTerminal(msg) {
    const terminal = document.getElementById("stream-terminal");
    if (!terminal) return;
    const line = document.createElement("div");
    line.className = "terminal-line";
    line.textContent = msg;
    terminal.appendChild(line);
    terminal.scrollTop = terminal.scrollHeight;
}

function startTimer() {
    jobStartTime = performance.now();
    const badge = document.getElementById("elapsed-badge");
    if (timerInterval) clearInterval(timerInterval);
    timerInterval = setInterval(() => {
        const elapsed = (performance.now() - jobStartTime) / 1000;
        if (badge) badge.textContent = `${elapsed.toFixed(2)}s`;
    }, 50);
}

function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}

function escapeHtml(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function formatMarkdownResponse(text) {
    if (!text) return "";
    let html = escapeHtml(text);

    // Formatear encabezados de nivel 3 (### Título)
    html = html.replace(/^###\s+(.*?)$/gm, '<h4 class="chat-heading">$1</h4>');

    // Negritas y cursivas
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // Bloques de código inline
    html = html.replace(/`([^`]+)`/g, '<code style="background:#f1f5f9; padding:2px 6px; border-radius:4px; font-size:0.86em; color:#0f172a; font-family:var(--font-mono); border:1px solid #e2e8f0;">$1</code>');

    // Citas a páginas inline convertidas en badges clicables interactivos
    html = html.replace(/\[P[áa]gina\s*(\d+)\]/gi, (match, p) => {
        return `<button type="button" class="inline-citation-badge" onclick="if(window.activePdfViewer) window.activePdfViewer.goToPage(${p})" title="Saltar a Página ${p} en el visor"><svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path></svg> Pág ${p}</button>`;
    });

    // Listas ordenadas y desordenadas
    const lines = html.split('\n');
    let inUl = false;
    let inOl = false;
    let result = [];

    for (let line of lines) {
        const trimmed = line.trim();

        // Lista no ordenada (* o -)
        if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
            if (inOl) { result.push('</ol>'); inOl = false; }
            if (!inUl) {
                result.push('<ul class="chat-list">');
                inUl = true;
            }
            result.push(`<li>${trimmed.substring(2)}</li>`);
        }
        // Lista ordenada (1. , 2. )
        else if (/^\d+\.\s+/.test(trimmed)) {
            if (inUl) { result.push('</ul>'); inUl = false; }
            if (!inOl) {
                result.push('<ol class="chat-list-ol">');
                inOl = true;
            }
            const itemText = trimmed.replace(/^\d+\.\s+/, '');
            result.push(`<li>${itemText}</li>`);
        } else {
            if (inUl) { result.push('</ul>'); inUl = false; }
            if (inOl) { result.push('</ol>'); inOl = false; }

            if (trimmed) {
                if (trimmed.startsWith('<h4')) {
                    result.push(trimmed);
                } else {
                    result.push(`<p class="chat-p">${trimmed}</p>`);
                }
            }
        }
    }
    if (inUl) result.push('</ul>');
    if (inOl) result.push('</ol>');

    return result.join('');
}

// SmartDoc Chat Integration
function askQuickPrompt(text) {
    const input = document.getElementById("chat-input-field");
    if (input) {
        input.value = text;
        sendChatMessage();
    }
}

async function sendChatMessage() {
    const input = document.getElementById("chat-input-field");
    const container = document.getElementById("chat-messages-container");
    const hashEl = document.getElementById("doc-pdf-hash");

    if (!input || !container || !hashEl) return;
    const pregunta = input.value.trim();
    if (!pregunta) return;

    const pdfHash = hashEl.textContent.trim();

    // Fila del Usuario (estilo moderno con avatar alineado a la derecha)
    const userRow = document.createElement("div");
    userRow.className = "chat-message-row user-row";
    userRow.innerHTML = `
        <div class="user-bubble">${escapeHtml(pregunta)}</div>
        <div class="user-avatar" title="Usuario">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
        </div>
    `;
    container.appendChild(userRow);
    input.value = "";
    container.scrollTop = container.scrollHeight;

    // Fila del Asistente en estado de consulta (Loading)
    const assistantRow = document.createElement("div");
    assistantRow.className = "chat-message-row assistant-row";
    assistantRow.innerHTML = `
        <div class="assistant-avatar" title="SmartDoc AI">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"></path></svg>
        </div>
        <div class="assistant-card-bubble">
            <div class="assistant-card-header">
                <span class="loading-spinner" style="width: 10px; height: 10px; border-width: 2px;"></span>
                <span>Analizando expediente documental...</span>
            </div>
            <p style="color: #64748b; font-size: 0.88rem; margin: 0;">Consultando texto, firmas y sellos en alta resolución...</p>
        </div>
    `;
    container.appendChild(assistantRow);
    container.scrollTop = container.scrollHeight;

    try {
        const response = await fetch(`/chat/${pdfHash}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                pregunta: pregunta,
                historial: chatHistory
            })
        });

        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.message || "Error al consultar el Asistente Cognitivo SmartDoc");
        }

        const data = await response.json();
        chatHistory.push({ role: "user", content: pregunta });
        chatHistory.push({ role: "assistant", content: data.respuesta });

        let citasHtml = "";
        if (data.evidencias_relacionadas && data.evidencias_relacionadas.length > 0) {
            citasHtml = `<div class="citations-list-wrapper">
                <span class="citations-label">📍 Evidencias Verificadas en Documento:</span>
                <div class="citations-list" style="display: flex; flex-wrap: wrap; gap: 0.4rem;">` +
                data.evidencias_relacionadas.map(ev => {
                    const bboxStr = JSON.stringify(ev.bbox || []);
                    const label = (ev.text || "Evidencia").substring(0, 25).replace(/'/g, "\\'");
                    return `<button type="button" class="citation-pill citation-pill-interactive" onclick="window.highlightSourceInPdf(${ev.page}, ${bboxStr}, '${label}')" title="Localizar en visor: Pág ${ev.page}">
                        <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                        <span>Pág ${ev.page}</span>
                    </button>`;
                }).join("") +
                `</div></div>`;
        } else if (data.citas && data.citas.length > 0) {
            citasHtml = `<div class="citations-list-wrapper">
                <span class="citations-label">📍 Páginas Referenciadas:</span>
                <div class="citations-list" style="display: flex; flex-wrap: wrap; gap: 0.4rem;">` +
                data.citas.map(c => {
                    const match = c.match(/\d+/);
                    const pageNum = match ? parseInt(match[0], 10) : 1;
                    return `<button type="button" class="citation-pill citation-pill-interactive" onclick="if(window.activePdfViewer) window.activePdfViewer.goToPage(${pageNum})" title="Ir a Pág ${pageNum}">
                        <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                        <span>${escapeHtml(c)}</span>
                    </button>`;
                }).join("") +
                `</div></div>`;
        }

        const bubbleEl = assistantRow.querySelector(".assistant-card-bubble");
        if (bubbleEl) {
            bubbleEl.innerHTML = `
                <div class="assistant-card-header">
                    <span class="status-indicator-dot"></span>
                    <span>Respuesta Verificada • SmartDoc</span>
                </div>
                <div class="assistant-content">
                    ${formatMarkdownResponse(data.respuesta)}
                </div>
                ${citasHtml}
            `;
        }
        container.scrollTop = container.scrollHeight;
    } catch (err) {
        const bubbleEl = assistantRow.querySelector(".assistant-card-bubble");
        if (bubbleEl) {
            bubbleEl.innerHTML = `
                <div class="assistant-card-header" style="background:#fef2f2; border-color:#fecaca; color:#b91c1c;">✕ Error en consulta</div>
                <p style="color: #ef4444; font-size: 0.88rem; margin: 0;">${escapeHtml(err.message)}</p>
            `;
        }
    }
}

// Toast Notifications
function showToast(message, type = "info") {
    let container = document.getElementById("toast-container");
    if (!container) {
        container = document.createElement("div");
        container.id = "toast-container";
        container.style.cssText = "position: fixed; bottom: 1.5rem; right: 1.5rem; z-index: 9999; display: flex; flex-direction: column; gap: 0.5rem; pointer-events: none;";
        document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    
    let borderCol = "#e2e8f0";
    let icon = "ℹ️";
    if (type === "warning") { borderCol = "#f59e0b"; icon = "⚠️"; }
    else if (type === "danger" || type === "error") { borderCol = "#ef4444"; icon = "❌"; }
    else if (type === "success") { borderCol = "#10b981"; icon = "✅"; }

    toast.style.cssText = `
        background: #ffffff;
        color: #0f172a;
        padding: 0.75rem 1.15rem;
        border-radius: 8px;
        border: 1px solid ${borderCol};
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.1);
        font-size: 0.88rem;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        pointer-events: auto;
        transition: opacity 0.25s ease, transform 0.25s ease;
    `;
    toast.innerHTML = `<span>${icon}</span><span>${escapeHtml(message)}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateY(6px)";
        setTimeout(() => toast.remove(), 250);
    }, 4000);
}
