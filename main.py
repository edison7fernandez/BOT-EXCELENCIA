import os
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, HTMLResponse
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
app = FastAPI()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')
VERIFY_TOKEN = "eddie_excelencia_2026"

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html><head><title>BOT-EXCELENCIA | PAUTO</title>
    <style>body{font-family:Arial;background:#0f172a;color:white;text-align:center;padding:50px}
   .card{background:white;color:#0f172a;max-width:600px;margin:auto;padding:40px;border-radius:20px}
    h1{color:#2563eb}.status{background:#10b981;color:white;padding:10px 20px;border-radius:30px;display:inline-block}</style>
    </head><body><div class="card"><h1>🚀 BOT-EXCELENCIA</h1>
    <div class="status">● ONLINE 24/7 - PAUTO PAYTON EDITION</div>
    <p><b>Asesor Automotriz Inteligente - Apariencia Profesional</b></p>
    <p>Potenciado por Payton & IA</p></div></body></html>
    """

@app.get("/webhook")
async def verificar(request: Request):
    if request.query_params.get("hub.verify_token") == VERIFY_TOKEN:
        return PlainTextResponse(request.query_params.get("hub.challenge"))
    return PlainTextResponse("Error", status_code=403)

@app.post("/webhook")
async def recibir(request: Request):
    data = await request.json()
    try:
        value = data['entry'][0]['changes'][0]['value']
        if 'messages' not in value: return {"ok": True}
        texto = value['messages'][0]['text']['body']
        prompt = f"Eres Payton, asesor TOP de PAUTO Ecuador, profesional, elegante, vendedor experto. Cliente dijo: {texto}. Responde corto, profesional max 2 lineas, usa emojis premium y cierra para agendar cita."
        respuesta = model.generate_content(prompt).text
        print(respuesta)
        return {"ok": True}
    except: return {"ok": True}
