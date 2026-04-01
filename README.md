# SereneAI 🌿

> **"Habla. Te escucho. Respiremos juntos."**

Companion de salud mental con inteligencia artificial, voz natural y búsqueda semántica.  
Desarrollado para el hackathon **OxBuild · Oxlo.ai · 2026**.

---

## Caso de uso

SereneAI permite a cualquier persona hablar libremente sobre cómo se siente y recibir:

- **Apoyo emocional inmediato** por voz sintetizada
- **Técnicas de bienestar validadas** recuperadas mediante búsqueda semántica (RAG)
- **Respuestas empáticas** generadas por un LLM con instrucciones éticas estrictas
- **Detección automática de crisis** con derivación a líneas profesionales
- **Tarjeta motivacional visual** al cerrar la sesión

No reemplaza la terapia profesional: la complementa y facilita el acceso en el primer momento de necesidad.

---

## Modelos de Oxlo utilizados

| Modelo | Función | Por qué |
|--------|---------|---------|
| `whisper-large-v3` | Transcripción de voz → texto | Alta precisión con acentos latinoamericanos y ruido de fondo |
| `bge-large` | Embeddings semánticos (1024 dims) | Búsqueda de técnicas clínicas por similitud de significado |
| `deepseek-r1-8b` | Generación de respuestas empáticas | Calidad de razonamiento + instrucciones éticas controlables |
| `kokoro-82m` | Síntesis de voz (TTS) | Voz natural en español, reduce fricción en momentos de angustia |
| `oxlo-image-pro` | Generación de tarjeta motivacional | Cierre visual personalizado de la sesión |

---

## Arquitectura del sistema

```
Usuario (navegador)
    │
    │  1. Audio WebM (MediaRecorder API)
    ▼
[FastAPI Backend]
    │
    ├─ POST /transcribe  ──► Oxlo Whisper Large v3  ──► texto
    │
    ├─ POST /chat
    │     ├─ Embed texto  ──► Oxlo BGE-Large  ──► vector 1024d
    │     ├─ Cosine sim   ──► knowledge_base.json (50 técnicas)
    │     ├─ Top-3 técnicas → system prompt enriquecido
    │     └─ LLM call     ──► Oxlo DeepSeek R1 8B  ──► respuesta
    │
    ├─ POST /synthesize  ──► Oxlo Kokoro 82M  ──► audio MP3 base64
    │
    └─ POST /generate-card ──► Oxlo Image Pro  ──► imagen 512x512
    │
    ▼
Usuario (audio autoplay + tarjeta descargable)
```

**RAG Pipeline:**
1. Al arrancar el servidor, se generan embeddings para las 50 técnicas (`POST /generate-embeddings`)
2. Por cada mensaje del usuario: embed → similitud coseno → top-3 técnicas → contexto al LLM
3. El LLM nunca inventa técnicas: solo usa las recuperadas del knowledge base

---

## Instalación

### Requisitos
- Python 3.11+
- API Key de Oxlo.ai (código promo: `OXBUILD` para acceso Premium)

### Backend

```bash
cd backend
pip install -r requirements.txt
cp ../.env.example ../.env
# Editar .env con tu OXLO_API_KEY
uvicorn main:app --reload --port 8000
```

### Generar embeddings (primera vez)

```bash
curl -X POST http://localhost:8000/generate-embeddings
```

### Frontend

Abre `frontend/index.html` directamente en el navegador o sirve con:

```bash
# Con Python
python -m http.server 5500 --directory frontend
# Luego abre: http://localhost:5500
```

---

## Variables de entorno

| Variable | Descripción |
|----------|-------------|
| `OXLO_API_KEY` | Tu API key de Oxlo.ai |
| `OXLO_BASE_URL` | URL base de la API (default: `https://api.oxlo.ai/v1`) |
| `CORS_ORIGINS` | Orígenes permitidos para CORS |

---

## Estructura del proyecto

```
SereneAI/
├── backend/
│   ├── main.py              # FastAPI app con todos los endpoints
│   └── requirements.txt
├── frontend/
│   └── index.html           # SPA con MediaRecorder + chat UI
├── data/
│   ├── knowledge_base.json  # 50 técnicas clínicas validadas
│   └── embeddings.json      # Generado en runtime (no en git)
├── docs/
├── .env.example
├── .gitignore
└── README.md
```

---

## Endpoints de la API

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Estado del servidor y conteo de KB/embeddings |
| POST | `/generate-embeddings` | Genera y cachea embeddings de las 50 técnicas |
| POST | `/transcribe` | Transcribe audio (multipart/form-data) |
| POST | `/chat` | Pipeline RAG completo: embed → retrieval → LLM |
| POST | `/synthesize` | Convierte texto a audio MP3 (base64) |
| POST | `/generate-card` | Genera imagen motivacional |

---

## Capturas de pantalla

> _Próximamente_

---

## Demo

> _Link a demo desplegada — próximamente_

---

## Seguridad y ética

- El sistema **nunca hace diagnósticos clínicos** ni recomienda medicamentos
- Detección automática de palabras clave de crisis con derivación a:
  - **SAPTEL México:** 55 5259-8121 (24 horas)
  - **Línea de la Vida:** 800 911-2000 (gratuita, 24 horas)
- El knowledge base contiene **solo técnicas clínicas validadas** con nivel de evidencia documentado

---

## Email registrado en Oxlo.ai

> _[Tu email aquí]_

---

Hackathon OxBuild · Oxlo.ai · 2026
