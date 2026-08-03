import flet as ft
import asyncio
import os
from dotenv import load_dotenv
import httpx

load_dotenv()
# Carga de las 4 llaves de raciocinio (Sakana/Custom API)
KEY1 = os.getenv("KEY1") # IA 1
KEY2 = os.getenv("KEY2") # IA 2
KEY3 = os.getenv("KEY3") # IA 3
KEY4 = os.getenv("KEY4") # IA 4

# ==========================================
# ORQUESTADOR SAKANA / OPENAI-COMPATIBLE
# ==========================================
async def call_ai(api_key, role_name, system_prompt, user_msg):
    # URL de API (Cámbiala si Sakana usa otro endpoint, pero usa formato estándar)
    API_URL = "https://api.sakana.ai/v1/chat/completions" 
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "research-deep", # Modelo hipotético de razonamiento
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg}
        ],
        "temperature": 0.7
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(API_URL, headers=headers, json=payload)
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
            else:
                return f"[Error API {role_name}: {res.status_code}]"
    except Exception as e:
        # Fallback simulado si no hay red/configurada la URL
        return f"[{role_name}] (Modo Local): Analizando '{user_msg[:40]}...' desde perspectiva asignada."

async def main(page: ft.Page):
    page.title = "ForChat - Investigación Profunda"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = ft.colors.BLACK
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    topic_input = ft.TextField(label="Tu tema de investigación complejo...", width=350, bgcolor=ft.colors.SURFACE, color=ft.colors.WHITE)
    chat_column = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=5)
    scroll_view = ft.ListView(controls=[chat_column], expand=True, padding=10)

    def bubble(text, is_user=False, bg=ft.colors.SURFACE):
        return ft.Container(
            content=ft.Text(text, color=ft.colors.WHITE, size=13),
            bgcolor=ft.colors.BLUE_900 if is_user else bg,
            border_radius=10, padding=8, margin=4, width=page.width * 0.85
        )

    async def start_debate(e):
        topic = topic_input.value
        if not topic: return
        
        # Usuario participa
        chat_column.controls.append(bubble(f"👤 Tú: {topic}", is_user=True))
        page.update()
        
        # Definición Estricta de Roles (Raciocinio)
        roles = [
            ("IA 1 (Pragmático)", KEY1, "Eres un analista práctico. Debes debatir de tú a tú, enfocándote en viabilidad técnica y datos duros.", ft.colors.GREEN_800),
            ("IA 2 (Crítico)", KEY2, "Eres un crítico de riesgos. Cuestiona los puntos anteriores, busca fallos lógicos y escenarios de fallo.", ft.colors.ORANGE_800),
            ("IA 3 (Ético)", KEY3, "Eres especialista en impacto social y ética. Aporta ángulos humanos que los otros ignoran.", ft.colors.PURPLE_800)
        ]
        
        msg = topic
        transcript = []
        
        # FASE 1: Debate de 3 turnos
        for _ in range(3):
            for name, key, sys_p, color in roles:
                resp = await call_ai(key, name, sys_p, msg)
                transcript.append(f"{name}: {resp}")
                chat_column.controls.append(bubble(f"🤖 {name}: {resp}", bg=color))
                page.update()
                msg = resp # La siguiente IA responde a esta

        # FASE 2: Auditoría IA 4
        audit_prompt = "Eres el Auditor Principal. Sintetiza la transcripción en un informe de investigación exhaustivo, estructurado y profundo."
        audit = await call_ai(KEY4, "IA 4 (Auditor)", audit_prompt, "\n".join(transcript))
        chat_column.controls.append(bubble(f"📋 IA 4 (Auditoría): {audit}", bg=ft.colors.AMBER_800))
        page.update()

    page.add(
        ft.Column([
            ft.Text("ForChat Deep Research", size=22, weight=ft.FontWeight.BOLD, color=ft.colors.CYAN),
            topic_input,
            ft.ElevatedButton("Generar Debate y Auditoría", on_click=start_debate, bgcolor=ft.colors.CYAN, color=ft.colors.BLACK),
            ft.Divider(color=ft.colors.SURFACE),
            ft.Container(content=scroll_view, border=ft.border.all(1, ft.colors.SURFACE), border_radius=8, expand=True, width=400)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)
    )

ft.app(target=main)
