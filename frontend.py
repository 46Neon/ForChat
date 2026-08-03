import flet as ft
import httpx
import asyncio

async def main(page: ft.Page):
    page.title = "ForChat - Motor de Debate IA"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    topic_input = ft.TextField(label="Tema de investigación complejo", width=400)
    chat_view = ft.ListView(expand=True, spacing=10, auto_scroll=True)
    report_view = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    report_text = ft.Text("", selectable=True)
    report_view.controls.append(report_text)
    
    def export_report(e):
        if report_text.value:
            with open("informe_forchat.txt", "w") as f:
                f.write(report_text.value)
            page.snack_bar = ft.SnackBar(ft.Text("Informe exportado a informe_forchat.txt"))
            page.snack_bar.open = True
            page.update()

    export_btn = ft.ElevatedButton("Exportar Informe", on_click=export_report, disabled=True)

    async def start_debate(e):
        chat_view.controls.clear()
        report_text.value = ""
        export_btn.disabled = True
        page.update()
        
        topic = topic_input.value
        if not topic: return
        
        chat_view.controls.append(ft.Text(f"👤 Usuario: {topic}", weight=ft.FontWeight.BOLD, color=ft.colors.BLUE))
        page.update()
        
        async with httpx.AsyncClient() as client:
            try:
                # Conexión al backend FastAPI local
                res = await client.post("http://127.0.0.1:8000/api/forchat", json={"topic": topic}, timeout=60.0)
                if res.status_code == 200:
                    data = res.json()
                    for msg in data["debate"]:
                        color = ft.colors.GREEN if "IA 1" in msg else (ft.colors.ORANGE if "IA 2" in msg else ft.colors.PURPLE)
                        chat_view.controls.append(ft.Text(msg, color=color))
                        page.update()
                        await asyncio.sleep(0.1) # Efecto de tipeo/tiempo real
                    
                    report_text.value = data["report"]
                    export_btn.disabled = False
                    page.update()
            except Exception as ex:
                chat_view.controls.append(ft.Text(f"Error de conexión: {ex}", color=ft.colors.RED))
                page.update()

    page.add(
        ft.Column([
            ft.Text("ForChat AI", size=30, weight=ft.FontWeight.BOLD),
            topic_input,
            ft.ElevatedButton("Iniciar Debate (3 IAs)", on_click=start_debate),
            ft.Divider(),
            ft.Container(content=chat_view, border=ft.border.all(1), padding=10, height=300, width=500),
            ft.Divider(),
            ft.Text("📄 INFORME DE AUDITORÍA (IA 4):", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(content=report_view, border=ft.border.all(1), padding=10, height=200, width=500),
            export_btn
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )
