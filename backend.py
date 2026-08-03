import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio

# Cargar las variables de entorno del archivo .env
load_dotenv()

# Asignamos las keys a variables de memoria
KEY1 = os.getenv("KEY1")
KEY2 = os.getenv("KEY2")
KEY3 = os.getenv("KEY3")
KEY4 = os.getenv("KEY4")

app = FastAPI()

class Query(BaseModel):
    topic: str

# ==========================================
# ORQUESTADOR DE IAs CON KEYS INYECTADAS
# ==========================================
async def call_llm(role, system_prompt, history, user_msg, api_key):
    await asyncio.sleep(1)  # Latencia simulada
    
    # AQUÍ ES DONDE CONECTARÍAS TU API REAL USANDO 'api_key'
    # Ejemplo conceptual:
    # headers = {"Authorization": f"Bearer {api_key}"}
    # (Lógica de conexión a la API de tu proveedor 'fish_...')
    
    # Por ahora retornamos un echo demostrando que la Key se cargó:
    return f"[{role}] (Auth: {api_key[:15]}...) Analizando: {user_msg[:40]}..."

@app.post("/api/forchat")
async def run_forchat(query: Query):
    topic = query.topic
    debate_log = []
    
    sys1 = "Eres la IA 1 (Perspectiva Práctica). Debatir de tú a tú."
    sys2 = "Eres la IA 2 (Perspectiva Crítica). Cuestiona con lógica."
    sys3 = "Eres la IA 3 (Perspectiva Ética). Aporta ángulos humanos."
    sys4 = "Eres la IA 4 (Auditor). Sintetiza el debate en un informe."
    
    msg_actual = f"Hola, hablemos sobre: {topic}"
    # FASE 1: Debate (usando KEY1, KEY2, KEY3)
    for _ in range(3): 
        r1 = await call_llm("IA 1", sys1, debate_log, msg_actual, KEY1)
        debate_log.append(r1)
        r2 = await call_llm("IA 2", sys2, debate_log, r1, KEY2)
        debate_log.append(r2)
        r3 = await call_llm("IA 3", sys3, debate_log, r2, KEY3)
        debate_log.append(r3)
        msg_actual = r3 
        
    # FASE 2: Auditoría (usando KEY4)
    transcript = "\n".join(debate_log)
    report = await call_llm("IA 4", sys4, [], f"Genera el informe basado en:\n{transcript}", KEY4)
    
    return {"debate": debate_log, "report": report}
