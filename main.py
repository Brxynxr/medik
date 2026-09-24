"""Main Entry Point for Buzón Corporativo RIWI — High-Speed Document Engine.

Runs the asynchronous FastAPI application with Jinja2 templates, PDF.js client-side
hardware-accelerated viewer, visual grounding, and multi-tier caching.
"""

import uvicorn
from app.main import app
from app.settings import settings

if __name__ == "__main__":
    print(f"[RIWI Engine] Iniciando servidor en http://{settings.HOST}:{settings.PORT}")
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
