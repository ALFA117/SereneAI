<div align="center">

<img src="logo/SereneIA.png" alt="Logo de SereneAI" width="130" />

# SereneAI 🌿

### "Habla. Te escucho. Respiremos juntos."

Compañero de bienestar emocional por voz: te escucha, responde con empatía, te propone una técnica real de bienestar y, si detecta una crisis, te da líneas de ayuda.

[![Frontend](https://img.shields.io/badge/Frontend-serene--ai--seven.vercel.app-2f9e6e?style=for-the-badge&logo=vercel&logoColor=white)](https://serene-ai-seven.vercel.app/)
[![Backend offline](https://img.shields.io/badge/Backend-offline-b23b3b?style=for-the-badge)](#-estado-del-proyecto)
[![Video demo](https://img.shields.io/badge/Video_demo-YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://youtu.be/CDG0c7wVv3M)
[![OxBuild](https://img.shields.io/badge/Hackathon-OxBuild_·_Oxlo.ai_2026-6d4bd1?style=for-the-badge)](#-hackathon)

![Python](https://img.shields.io/badge/Python_3.11-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?logo=numpy&logoColor=white)
![HTML](https://img.shields.io/badge/HTML_+_JS-E34F26?logo=html5&logoColor=white)
![Oxlo.ai](https://img.shields.io/badge/Oxlo.ai-5_modelos-222)
![Railway](https://img.shields.io/badge/Railway-0B0D0E?logo=railway&logoColor=white)
![Vercel](https://img.shields.io/badge/Vercel-000000?logo=vercel&logoColor=white)

<br/>

<img src="docs/img/hero.jpg" alt="SereneAI en una laptop y en un celular: pantalla de chat con el saludo inicial y el indicador 'Sin conexión'" width="100%" />

**[▶ Abrir el frontend](https://serene-ai-seven.vercel.app/)** · **[Ver el video demo](https://youtu.be/CDG0c7wVv3M)** · **[Cómo funciona](#-cómo-funciona)** · **[Correrlo local](#-correrlo-en-tu-compu)**

</div>

> [!WARNING]
> **El backend ya no está en línea.** El frontend en Vercel carga, pero el servidor de Railway responde 404, así que la app muestra **"Sin conexión"** y no puede transcribir, responder ni generar tarjetas. Las capturas de la galería son de abril de 2026, cuando el backend funcionaba; el [video demo](https://youtu.be/CDG0c7wVv3M) muestra el flujo completo. Para probarlo hoy hay que correr el backend local con una API key de Oxlo.ai.

---

## 🎯 El problema

Cuando alguien se siente mal, el primer momento de necesidad casi nunca coincide con una cita con un profesional. Muchas personas no tienen con quién hablar en ese momento, y escribir o hablar con un chatbot genérico puede dar respuestas vacías o, peor, minimizar lo que sienten.

## 💡 La solución

SereneAI es un espacio para **hablar (o escribir) sobre cómo te sientes** y recibir:

- **Apoyo emocional inmediato**, leído en voz alta con voz sintetizada.
- **Una técnica de bienestar concreta**, recuperada por búsqueda semántica (RAG) de una base de **53 técnicas**; el nombre de la técnica aparece como chip en el chat.
- **Detección de crisis antes del modelo**: si el mensaje contiene una de **35 frases clave**, la respuesta es un texto fijo (no generado) con líneas de ayuda en México.
- **Una tarjeta motivacional** con imagen generada, descargable como imagen o PDF, y un resumen de la sesión al cerrar.

```
 Persona:   "me falta la respiración, tengo mucho miedo"
 SereneAI:  "Tu miedo es válido y merece ser atendido con calma… Imagina un cuadrado:
             inhala contando hasta 4, mantén 4, exhala 4, espera 4…"
            [▶ Escuchar respuesta]   [✦ Técnica: Respiración en caja (Box Breathing)]
```

No reemplaza la terapia profesional: la complementa en el primer momento de necesidad.

## 📸 Capturas (abril 2026, con el backend en línea)

<table>
<tr>
<td width="50%"><img src="docs/img/chat.jpg" alt="Chat: la persona escribe que se siente triste y cansada; SereneAI responde y propone la técnica Carta de autocompasión" /><p align="center"><sub>Respuesta empática con botón de audio y chip de la técnica recuperada.</sub></p></td>
<td width="50%"><img src="docs/img/rag-chip.jpg" alt="Chat: respuesta guiando la respiración en caja, con el chip de la técnica" /><p align="center"><sub>La técnica viene de la base de conocimiento, no se la inventa el modelo.</sub></p></td>
</tr>
<tr>
<td width="50%"><img src="docs/img/download.jpg" alt="Tarjeta motivacional con un paisaje de lago al amanecer y botones Cerrar, PDF e Imagen" /><p align="center"><sub>Tarjeta motivacional generada, descargable como imagen o PDF.</sub></p></td>
<td width="50%"><img src="docs/img/help.jpg" alt="Guía de uso: modo voz, modo texto, voz de SereneAI, tarjeta, finalizar sesión y aviso importante" /><p align="center"><sub>Guía de uso con el aviso de que no es una terapeuta.</sub></p></td>
</tr>
<tr>
<td width="50%"><img src="docs/img/card.jpg" alt="Tarjeta: Cada respiro que tomas es un paso hacia tu calma interior" /><p align="center"><sub>Otra tarjeta generada.</sub></p></td>
<td width="50%"><img src="docs/img/summary.jpg" alt="Resumen de la sesión" /><br/><img src="docs/img/settings.jpg" alt="Panel de ajustes" width="45%" /><p align="center"><sub>Resumen de la sesión y ajustes.</sub></p></td>
</tr>
</table>

## 🧠 Cómo funciona

```mermaid
flowchart LR
    A["Navegador: voz o texto"] -->|audio| B["/transcribe: Whisper Large v3"]
    B --> C["/chat"]
    A -->|texto| C
    C --> K{"Frase de crisis?"}
    K -->|si| L["Mensaje fijo con lineas de ayuda"]
    K -->|no| D["Embedding BGE-Large"]
    D --> E[("knowledge_base.json: 53 tecnicas")]
    E -->|top 3 por coseno| F["DeepSeek R1 8B redacta"]
    F --> G["/synthesize: Kokoro 82M"]
    G --> A
    C --> H["/generate-card: Oxlo Image Pro"]
    H --> A
```

**Pipeline RAG**

1. Al arrancar el servidor, los embeddings de las 53 técnicas se generan en segundo plano (`data/embeddings.json`).
2. Por cada mensaje: embedding → similitud coseno → top 3 técnicas → contexto inyectado al modelo.
3. El modelo solo usa técnicas recuperadas de la base; el nombre de la principal se muestra como chip.

### Modelos de Oxlo utilizados

| Modelo | Función |
|:--|:--|
| `whisper-large-v3` | Voz → texto (WebM / MP4 / OGG) |
| `bge-large` | Embeddings de 1 024 dimensiones para RAG |
| `deepseek-r1-8b` | Respuestas empáticas y resumen de sesión |
| `kokoro-82m` | Síntesis de voz (TTS) |
| `oxlo-image-pro` | Tarjeta motivacional 1 024×1 024 |

### Endpoints de la API (`backend/main.py`)

| Método | Ruta | Descripción |
|:--|:--|:--|
| GET | `/health` | Estado: base cargada + embeddings en caché |
| POST | `/generate-embeddings` | Genera los embeddings de las 53 técnicas (incremental) |
| POST | `/transcribe` | Transcribe audio con Whisper Large v3 |
| POST | `/chat` | Pipeline completo: crisis → embedding → recuperación → LLM |
| POST | `/synthesize` | Texto → audio WAV (base64) con Kokoro 82M |
| POST | `/generate-card` | Imagen motivacional con Image Pro |
| POST | `/session-summary` | Resumen empático de la sesión |

## 🛡️ Seguridad y ética

- **Nunca diagnostica** ni recomienda medicamentos; el system prompt prohíbe minimizar el dolor de la persona.
- **Crisis primero:** la detección corre antes del modelo y la respuesta es fija, con estas líneas:
  - **Línea de la Vida:** 800 911 2000 (24 horas)
  - **SAPTEL:** 55 5259 8121 (24 horas)
  - **IMSS Salud Mental:** 800 890 0024 (lunes a viernes)
- La guía de uso de la app aclara que SereneAI es un compañero de apoyo, no una terapeuta.

## 🛠️ Stack

| Capa | Tecnología |
|:--|:--|
| Backend | Python 3.11 · FastAPI · Uvicorn · httpx · NumPy (similitud coseno) |
| Frontend | Un solo `index.html` (HTML, CSS y JavaScript, MediaRecorder API) |
| IA | Oxlo.ai: Whisper Large v3, BGE-Large, DeepSeek R1 8B, Kokoro 82M, Image Pro |
| Deploy | Frontend en Vercel · backend en Railway (hoy offline) |

## 🚀 Correrlo en tu compu

Necesitas Python 3.11+ y una API key de Oxlo.ai.

```bash
git clone https://github.com/ALFA117/SereneAI
cd SereneAI/backend
pip install -r requirements.txt
cp ../.env.example ../.env      # pon tu OXLO_API_KEY
uvicorn main:app --reload --port 8000
```

Los embeddings se generan solos al arrancar. Para el frontend:

```bash
python -m http.server 5500 --directory frontend   # http://localhost:5500
```

> El frontend apunta al backend de Railway (`API_URL` en `frontend/index.html`); para usarlo con tu backend local cambia esa constante a `http://localhost:8000`.

<details>
<summary><b>Variables de entorno y estructura</b></summary>

| Variable | Descripción |
|:--|:--|
| `OXLO_API_KEY` | API key de Oxlo.ai |
| `OXLO_BASE_URL` | URL base de la API (default: `https://api.oxlo.ai/v1`) |
| `CORS_ORIGINS` | Orígenes permitidos para CORS (separados por coma) |

```
SereneAI/
├── backend/
│   ├── main.py                    # FastAPI: 7 endpoints + pipeline RAG
│   ├── sereneai_system_prompt.py  # System prompt, detección de crisis, limpieza de R1
│   ├── requirements.txt
│   └── test_api.py
├── frontend/
│   ├── index.html                 # SPA: chat + voz + tarjeta + ayuda + ajustes
│   └── logo.png
├── data/
│   ├── knowledge_base.json        # 53 técnicas de bienestar
│   └── embeddings.json            # Generado al arrancar
├── docs/img/                      # Capturas
├── logo/SereneIA.png
├── Procfile · railway.json · .env.example
```

</details>

## 🏆 Hackathon

Desarrollado para el hackathon **OxBuild · Oxlo.ai · 2026**. Video del demo: [youtu.be/CDG0c7wVv3M](https://youtu.be/CDG0c7wVv3M).

---

<div align="center">

<img src="logo/SereneIA.png" alt="" width="60" />

**Un primer momento de calma, no un reemplazo de la terapia.**

Hecho por **ALFA** · [@ALFA117](https://github.com/ALFA117) · Instagram [@alfa_edg.mou](https://www.instagram.com/alfa_edg.mou/)

</div>
