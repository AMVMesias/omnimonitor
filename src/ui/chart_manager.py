import flet as ft
from collections import deque


class ChartManager:
    """Maneja la creación y actualización de gráficos para el monitor"""
    
    def __init__(self, max_points: int = 60):
        self.max_points = max_points
        self.cpu_history = deque([0] * max_points, maxlen=max_points)
        self.mem_history = deque([0] * max_points, maxlen=max_points)
        self.net_up_history = deque([0] * max_points, maxlen=max_points)
        self.net_down_history = deque([0] * max_points, maxlen=max_points)
    
    def create_mini_line_chart(self, data: list, color: str, height: int = 50) -> ft.Container:
        """Crea un mini gráfico de barras estilizado como línea para las tarjetas"""
        if not data or len(data) < 2:
            data = [0] * 10
        
        max_val = max(data) if max(data) > 0 else 100
        
        bars = []
        for value in data[-30:]:  # Últimos 30 puntos
            bar_height = max((value / max_val) * height, 2) if max_val > 0 else 2
            bars.append(
                ft.Container(
                    width=4,
                    height=bar_height,
                    bgcolor=color,
                    border_radius=2,
                )
            )
        
        return ft.Container(
            content=ft.Row(
                bars,
                spacing=2,
                alignment=ft.MainAxisAlignment.END,
                vertical_alignment=ft.CrossAxisAlignment.END,
            ),
            height=height,
            bgcolor=ft.Colors.with_opacity(0.1, color),
            border_radius=8,
            padding=5,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )

    def create_network_area_chart(self, download_data: list, upload_data: list, 
                                   time_labels: list, height: int = 180) -> ft.Container:
        """Crea el gráfico grande de red con barras para download/upload"""
        
        # Asegurar datos mínimos
        if not download_data:
            download_data = [0] * 30
        if not upload_data:
            upload_data = [0] * 30
        
        # Normalizar
        min_len = min(len(download_data), len(upload_data))
        download_data = download_data[-min_len:][-40:]
        upload_data = upload_data[-min_len:][-40:]
        
        if len(download_data) < 2:
            download_data = [0, 0]
            upload_data = [0, 0]
        
        # Calcular escala
        all_data = download_data + upload_data
        max_val = max(all_data) if max(all_data) > 0 else 100
        
        # Crear barras combinadas
        bars = []
        for i, (down, up) in enumerate(zip(download_data, upload_data)):
            down_height = max((down / max_val) * (height - 40), 2) if max_val > 0 else 2
            up_height = max((up / max_val) * (height - 40), 2) if max_val > 0 else 2
            
            bars.append(
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            width=6,
                            height=down_height,
                            bgcolor="#4FC3F7",
                            border_radius=ft.border_radius.only(top_left=3, top_right=3),
                        ),
                        ft.Container(
                            width=6,
                            height=up_height,
                            bgcolor="#81C784",
                            border_radius=ft.border_radius.only(bottom_left=3, bottom_right=3),
                        ),
                    ], spacing=1, alignment=ft.MainAxisAlignment.END),
                    height=height - 40,
                )
            )
        
        # Leyenda
        legend = ft.Row([
            ft.Container(
                content=ft.Row([
                    ft.Container(width=12, height=12, bgcolor="#4FC3F7", border_radius=6),
                    ft.Text("Download", size=12, color="#AAAAAA"),
                ], spacing=5),
            ),
            ft.Container(
                content=ft.Row([
                    ft.Container(width=12, height=12, bgcolor="#81C784", border_radius=6),
                    ft.Text("Upload", size=12, color="#AAAAAA"),
                ], spacing=5),
            ),
        ], spacing=20, alignment=ft.MainAxisAlignment.CENTER)
        
        # Contenedor del gráfico
        chart_area = ft.Container(
            content=ft.Row(
                bars,
                spacing=3,
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.END,
            ),
            height=height - 40,
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
            border_radius=8,
            padding=10,
            border=ft.border.all(1, "#2A2D3A"),
        )
        
        return ft.Container(
            content=ft.Column([
                legend,
                ft.Container(height=10),
                chart_area,
            ]),
            padding=10,
        )

    def create_bar_chart(self, data: list, colors: list, labels: list, height: int = 100) -> ft.Container:
        """Crea un gráfico de barras horizontal"""
        bars = []
        max_val = max(data) if max(data) > 0 else 100
        
        for i, (value, color, label) in enumerate(zip(data, colors, labels)):
            bar_width = (value / max_val) * 100 if max_val > 0 else 0
            bars.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(label, size=10, color="#888888"),
                        ft.Container(
                            content=ft.Row([
                                ft.Container(
                                    width=bar_width * 2,
                                    height=15,
                                    bgcolor=color,
                                    border_radius=5,
                                ),
                                ft.Text(f"{value:.1f}%", size=10, color=color),
                            ], spacing=10),
                        ),
                    ], spacing=2),
                )
            )
        
        return ft.Container(
            content=ft.Column(bars, spacing=8),
            height=height,
        )
