from fastapi import FastAPI, Request, Response
import os

app = FastAPI()

# CONFIG - Pon estos en tu Render > Environment
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "abra_excelencia_123")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN") # El token de Meta
PHONE_ID = os.getenv("PHONE_ID") # El ID de tu número +593-96-321-2112

@app.get("/")
def home():
    return {"status": "ABRA Bebé vivo", "mensaje": "Creo conforme hablo"}

# PASO 1 - VERIFICACIÓN DE META (Para que Meta te apruebe el webhook)
@app.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("WEBHOOK VERIFICADO!")
        return Response(content=challenge, media_type="text/plain")
    else:
        return Response(status_code=403)

# PASO 2 - RECIBIR MENSAJES REALES
@app.post("/webhook")
async def receive_message(request: Request):
    data = await request.json()
    print("Mensaje recibido:", data)

    # Aquí es donde el bebé respira
    try:
        # Extraer mensaje
        entry = data['entry'][0]['changes'][0]['value']
        if 'messages' in entry:
            mensaje = entry['messages'][0]['text']['body']
            numero = entry['messages'][0]['from']
            print(f"De {numero}: {mensaje}")

            # Aquí luego conectamos el ALMA (Paso 2)
            # Por ahora responde eco con excelencia
            await responder_whatsapp(numero, f"¡Recibido con excelencia! Dijiste: {mensaje} - ABRA Bebé está naciendo 👶")

    except Exception as e:
        print(f"Error: {e}")

    return {"status": "ok"}

async def responder_whatsapp(to, text):
    import httpx
    url = f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": text}
    }
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload, headers=headers)
