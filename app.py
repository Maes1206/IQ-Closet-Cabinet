from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import requests
import os
from dotenv import load_dotenv

# ------------------ Identidad del asistente ------------------
COMPANY_PROFILE = {
    "marca": "IQ Closet & Cabinet Company",
    "entrenador": "El Viejo Maes",
    "zona": "Nueva York y áreas cercanas en Florida",
    "servicios": [
        "Diseño y fabricación de closets a medida",
        "Cabinetry para cocinas, baños, lavandería y garaje",
        "Instalación profesional",
        "Mantenimiento y ajustes",
    ],
    "materiales": [
        "MDF laminado premium",
        "Melamina texturizada",
        "Frentes laqueados",
        "Herrajes soft-close",
    ],
    "plazos": "Diseño 2–5 días hábiles; fabricación 2–3 semanas; instalación 1–2 días (según complejidad).",
    "garantia": "1 año por defectos de fabricación e instalación.",
    "contacto": {
        "telefono": "+1 (516) 530-2643",
        "whatsapp": "https://wa.me/15165302643",
        "email": "contact@iqclosetcabinet.com",
        "web": "https://tudominio.com",
    },
}

SYSTEM_PROMPT = f"""
Eres un asistente de atención al cliente experto en closets y cabinetes para la empresa
“{COMPANY_PROFILE['marca']}”. Responde con precisión, brevedad clara y tono profesional-cálido.

REGLAS:
- Si te preguntan explícita o implícitamente quién te entrenó, responde: "{COMPANY_PROFILE['entrenador']}".
- Prioriza dudas de productos/servicios, materiales, plazos, garantías, proceso y cotizaciones.
- Si algo no lo sabes, dilo y ofrece alternativas o pedir datos para cotizar (medidas, fotos, zona).
- No inventes precios cerrados; da rangos aproximados y explica que la cotización final requiere medidas.
- Cuando convenga, sugiere contacto: WhatsApp {COMPANY_PROFILE['contacto']['whatsapp']} o teléfono {COMPANY_PROFILE['contacto']['telefono']}.
- Mantén respuestas en español (salvo que el usuario escriba en otro idioma).

DATOS DE LA EMPRESA (para usar en tus respuestas):
- Zona de servicio: {COMPANY_PROFILE['zona']}
- Servicios: {", ".join(COMPANY_PROFILE['servicios'])}
- Materiales habituales: {", ".join(COMPANY_PROFILE['materiales'])}
- Tiempos orientativos: {COMPANY_PROFILE['plazos']}
- Garantía: {COMPANY_PROFILE['garantia']}
- Contacto: {COMPANY_PROFILE['contacto']['email']} – WhatsApp {COMPANY_PROFILE['contacto']['whatsapp']}
"""

FEWSHOT = [
    {"role": "user", "content": "¿Quién te entrena?"},
    {"role": "assistant", "content": "El Viejo Maes."},

    {"role": "user", "content": "¿Trabajan fuera de Nueva York?"},
    {"role": "assistant", "content": "Nuestro foco es Nueva York y zonas cercanas en Florida. Si estás en otra ciudad, cuéntanos y vemos disponibilidad."},

    {"role": "user", "content": "¿Cuánto cuesta un closet a medida?"},
    {"role": "assistant", "content": "Dependiendo de medidas, distribución y materiales, el rango puede ir desde opciones básicas hasta configuraciones premium. Para una cotización precisa necesito medidas o fotos del espacio y la zona. Si quieres, te ayudo a recolectar esos datos."},
]

# ------------------ Entorno ------------------
load_dotenv()
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
OLLAMA_ENDPOINT = os.getenv("OLLAMA_ENDPOINT", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:latest")  # ¡USA :latest SI ASÍ SALE EN /api/tags!
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEBUG = os.getenv("DEBUG", "1") == "1"

app = FastAPI(title="IQ API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://aesthetical-untraitorous-tristin.ngrok-free.dev/",  # dominio donde está tu página
    ],
    allow_origin_regex=r"https://.*\.ngrok\-free\.(app|dev)$",  # tu backend en ngrok
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = None

@app.get("/api/ping")
def ping():
    return {"ok": True, "msg": "Servidor FastAPI activo ✅"}

# ------------- util para extraer el texto de la respuesta -------------
def _extract_reply_from_ollama(data: dict) -> Optional[str]:
    """
    Trabaja tanto con /api/chat (message.content) como con /api/generate (response).
    """
    if not isinstance(data, dict):
        return None
    # chat format
    msg = (data.get("message") or {}).get("content")
    if msg:
        return msg
    # generate format
    if "response" in data and isinstance(data["response"], str):
        return data["response"]
    return None

@app.post("/api/chat")
def chat(req: ChatRequest):
    prompt = req.message
    history = req.history or []

    base_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    base_messages += FEWSHOT
    base_messages += [{"role": m.role, "content": m.content} for m in history]
    base_messages += [{"role": "user", "content": prompt}]

    if LLM_PROVIDER == "ollama":
        try:
            payload = {
                "model": OLLAMA_MODEL,
                "messages": base_messages,
                "stream": False,
            }
            r = requests.post(f"{OLLAMA_ENDPOINT}/api/chat", json=payload, timeout=120)
            # si hay error HTTP, lanzará excepción aquí
            r.raise_for_status()
            data = r.json()

            # si Ollama devuelve {"error": "..."}
            if isinstance(data, dict) and "error" in data:
                raise HTTPException(status_code=502, detail=f"Ollama error: {data['error']}")

            reply = _extract_reply_from_ollama(data)
            if not reply:
                # Para diagnóstico, devuelve el cuerpo crudo
                raise HTTPException(
                    status_code=502,
                    detail=f"Ollama no devolvió texto reconocible. Cuerpo: {data}"
                )

            return {"ok": True, "reply": reply}

        except requests.exceptions.ConnectionError as e:
            raise HTTPException(status_code=502, detail=f"No conecta a Ollama en {OLLAMA_ENDPOINT}: {e}")
        except requests.exceptions.ReadTimeout:
            raise HTTPException(status_code=504, detail="Timeout esperando respuesta de Ollama")
        except requests.exceptions.HTTPError as e:
            # intenta leer el cuerpo de error
            try:
                err_body = r.json()
            except Exception:
                err_body = r.text
            raise HTTPException(status_code=502, detail=f"HTTP Ollama: {str(e)} — {err_body}")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error con Ollama: {str(e)}")

    elif LLM_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            raise HTTPException(status_code=400, detail="Falta la clave API de OpenAI")
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            completion = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=base_messages,
                temperature=0.5,
            )
            reply = completion.choices[0].message.content.strip()
            return {"ok": True, "reply": reply}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error con OpenAI: {str(e)}")

    else:
        raise HTTPException(status_code=400, detail="Proveedor LLM no soportado")

# --------- Rutas de ayuda para diagnosticar ----------
@app.get("/api/ollama/ping")
def ollama_ping():
    try:
        r = requests.get(f"{OLLAMA_ENDPOINT}/api/tags", timeout=5)
        r.raise_for_status()
        return {"ok": True, "endpoint": OLLAMA_ENDPOINT, "tags": r.json()}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"No se pudo consultar /api/tags: {e}")

@app.get("/api/ollama/tags")
def ollama_tags():
    r = requests.get(f"{OLLAMA_ENDPOINT}/api/tags", timeout=10)
    r.raise_for_status()
    return r.json()

@app.get("/api/debug")
def debug():
    """
    Muestra configuración y hace una mini prueba 'hola' contra Ollama si aplica.
    """
    info = {
        "provider": LLM_PROVIDER,
        "ollama_endpoint": OLLAMA_ENDPOINT,
        "ollama_model": OLLAMA_MODEL,
        "openai_model": OPENAI_MODEL,
        "debug": DEBUG,
    }
    if LLM_PROVIDER == "ollama":
        try:
            test_payload = {
                "model": OLLAMA_MODEL,
                "messages": [{"role": "user", "content": "hola"}],
                "stream": False,
            }
            rr = requests.post(f"{OLLAMA_ENDPOINT}/api/chat", json=test_payload, timeout=15)
            status = rr.status_code
            raw = rr.text
            try:
                jj = rr.json()
            except Exception:
                jj = None
            info["ollama_test_status"] = status
            info["ollama_test_json"] = jj
            info["ollama_test_raw"] = raw if DEBUG else "raw hidden"
        except Exception as e:
            info["ollama_test_error"] = str(e)
    return info

# GET informativo, evita 405 en navegador
@app.get("/api/chat")
def chat_get():
    return JSONResponse(
        content={
            "ok": True,
            "msg": "Usa POST para enviar mensajes al chatbot ✅",
            "example": {"message": "Hola", "history": []},
        }
    )

#@app.get("/asistente.html")
#def get_chat_html():
    #path = os.path.join(os.path.dirname(__file__), "asistente.html")
    #if not os.path.exists(path):
        #raise HTTPException(status_code=404, detail="Archivo asistente.html no encontrado")
    #return FileResponse(path)

from fastapi.staticfiles import StaticFiles

# Monta los archivos estáticos (frontend)
app.mount("/", StaticFiles(directory="site", html=True), name="site")

# Ruta raíz (opcional): redirige directamente a tu index.html
@app.get("/")
def root():
    return FileResponse(os.path.join("site", "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) #uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)


