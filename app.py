"""
OmniMonitor - Monitor de Sistema Multiplataforma
Soporta modo Escritorio y Web con datos REALES
Incluye CRUD: Alertas, Procesos, Historial, Configuración
"""
import flet as ft
import asyncio
import os
import sys
import urllib.request
import json
from datetime import datetime

# Agregar directorio raíz al path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

from src.core.monitor import SystemMonitor
from src.ui.chart_manager import ChartManager
from src.ui.components import (
    DARK_BG, CARD_BG, SIDEBAR_BG, GREEN_PRIMARY, BLUE_PRIMARY, 
    ORANGE_PRIMARY, RED_PRIMARY, YELLOW_PRIMARY, TEXT_WHITE, TEXT_GRAY,
    create_circular_progress, create_cpu_card, create_ram_card,
    create_gpu_card, create_disk_card, create_network_chart_card, create_header
)

# Importar Theme Manager
from src.ui.theme_manager import ThemeManager, apply_theme_to_page, DARK_THEME, LIGHT_THEME

# Importar CRUD
from src.database.db import get_db
from src.crud.alerts import AlertManager
from src.crud.processes import ProcessManager
from src.crud.history import HistoryManager
from src.ui.crud_views import (
    build_alerts_view, build_processes_view,
    build_history_view, build_config_view
)
from src.ui.toast_manager import ToastManager, ToastType

# Detectar modo de ejecución
IS_WEB = "--web" in sys.argv or "-w" in sys.argv
API_PORT = 8765
API_URL = f"http://localhost:{API_PORT}"


class WebMonitor:
    """Monitor que obtiene datos REALES desde el servidor API"""
    
    def __init__(self, api_url: str = API_URL):
        self.api_url = api_url
        self._cache = {}
    
    def _fetch(self, endpoint: str) -> dict:
        """Hace petición HTTP al servidor API"""
        try:
            with urllib.request.urlopen(f"{self.api_url}{endpoint}", timeout=2) as response:
                return json.loads(response.read().decode())
        except Exception as e:
            print(f"Error fetching {endpoint}: {e}")
            return {}
    
    def refresh(self):
        """Actualiza todos los datos desde el API"""
        try:
            self._cache = self._fetch("/api/all")
        except:
            pass
    
    def get_cpu_usage(self) -> float:
        return self._cache.get("cpu", {}).get("usage", 0)
    
    def get_cpu_per_core(self) -> list:
        return self._cache.get("cpu", {}).get("per_core", [0, 0, 0, 0])
    
    def get_cpu_count(self) -> tuple:
        count = self._cache.get("cpu", {}).get("count", [1, 1])
        return tuple(count) if isinstance(count, list) else count
    
    def get_cpu_freq(self) -> float:
        return self._cache.get("cpu", {}).get("freq")
    
    def get_cpu_temp(self) -> float:
        return self._cache.get("cpu", {}).get("temp")
    
    def get_memory_usage(self) -> dict:
        return self._cache.get("memory", {"percent": 0, "used": 0, "total": 1, "free": 1})
    
    def get_disk_usage(self, path: str = '/') -> dict:
        return self._cache.get("disk", {}).get("usage", {"percent": 0, "used": 0, "total": 1, "free": 1})
    
    def get_disk_info(self) -> dict:
        return self._cache.get("disk", {}).get("info", {"device": "Unknown", "partition": "/", "fstype": "unknown", "mountpoint": "/"})
    
    def get_disk_io(self) -> dict:
        return self._cache.get("disk", {}).get("io", {"read_speed": 0, "write_speed": 0})
    
    def get_network_speed(self) -> dict:
        return self._cache.get("network", {}).get("speed", {"upload": 0, "download": 0})
    
    def get_network_info(self) -> dict:
        return self._cache.get("network", {}).get("info", {"interfaces": []})
    
    def get_gpu_info(self) -> dict:
        return self._cache.get("gpu")
    
    def get_system_info(self) -> dict:
        return self._cache.get("system", {}).get("info", {"os": "Unknown", "os_version": "", "architecture": "", "processor": "Unknown", "hostname": ""})
    
    def get_uptime(self):
        return self._cache.get("system", {}).get("uptime", "0:00:00")
    
    def get_battery_info(self) -> dict:
        return self._cache.get("system", {}).get("battery")


def main(page: ft.Page):
    page.title = "OmniMonitor"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.bgcolor = DARK_BG
    
    # Configurar ventana solo en modo escritorio
    if not IS_WEB:
        page.window.width = 1280
        page.window.height = 800

    # Seleccionar monitor según el modo
    if IS_WEB:
        monitor = WebMonitor(API_URL)
    else:
        monitor = SystemMonitor()
    
    # Inicializar CRUD managers
    db = get_db()
    alert_manager = AlertManager()
    process_manager = ProcessManager()
    history_manager = HistoryManager()
    
    # ============ CARGAR TEMA GUARDADO ============
    saved_theme = db.get_config('theme')
    if saved_theme == 'light':
        ThemeManager.set_light()
    else:
        ThemeManager.set_dark()
    
    # Aplicar tema al iniciar
    apply_theme_to_page(page, ThemeManager.get_theme())
    
    # ============ INICIALIZAR SISTEMA DE NOTIFICACIONES ============
    def get_toast_theme():
        """Obtener colores del tema actual para toasts"""
        theme = ThemeManager.get_theme()
        return {
            "bg": theme["bg_primary"],
            "card": theme["bg_card"],
            "text": theme["text_primary"],
            "text_secondary": theme["text_secondary"],
            "green": theme["accent_green"],
            "blue": theme["accent_blue"],
            "orange": theme["accent_orange"],
            "red": theme["accent_red"],
            "yellow": theme["accent_yellow"],
        }
    
    ToastManager.initialize(page, theme_getter=get_toast_theme)
    
    chart_mgr = ChartManager(max_points=60)
    update_interval = 1.0
    current_view = "resumen"
    history_save_counter = 0  # Para guardar historial cada N actualizaciones

    # ============ VALORES DE CPU ============
    cpu_percent_text = ft.Text("0%", size=42, weight=ft.FontWeight.BOLD, color=TEXT_WHITE)
    cpu_temp_text = ft.Text("Temp: --°C", size=13, color=GREEN_PRIMARY)
    cpu_speed_text = ft.Text("Speed: -- GHz", size=13, color=TEXT_GRAY)
    cpu_progress = create_circular_progress(0, GREEN_PRIMARY, 130)
    cpu_name_text = ft.Text("CPU: Detectando...", size=14, weight=ft.FontWeight.W_500, color=TEXT_WHITE)

    # ============ VALORES DE RAM ============
    ram_used_text = ft.Text("0GB / 0GB (0%)", size=13, color=TEXT_GRAY)
    ram_available_text = ft.Text("Available: 0GB", size=13, color=TEXT_GRAY)
    ram_bar = ft.ProgressBar(value=0, color=GREEN_PRIMARY, bgcolor="#2A2D3A", width=200, height=8)
    ram_history_chart = ft.Container(height=50)

    # ============ VALORES DE GPU ============
    gpu_percent_text = ft.Text("0%", size=36, weight=ft.FontWeight.BOLD, color=TEXT_WHITE)
    gpu_temp_text = ft.Text("Temp: --°C", size=13, color=GREEN_PRIMARY)
    gpu_progress = create_circular_progress(0, ORANGE_PRIMARY, 100)
    gpu_name_text = ft.Text("GPU/Temp: Detectando...", size=14, weight=ft.FontWeight.W_500, color=TEXT_WHITE)

    # ============ VALORES DE DISCO ============
    disk_name_text = ft.Text("Disco: Detectando...", size=14, weight=ft.FontWeight.W_500, color=TEXT_WHITE)
    disk_used_text = ft.Text("0GB Used (0%)", size=13, color=TEXT_GRAY)
    disk_speed_text = ft.Text("Read/Write: 0MB/s", size=13, color=TEXT_GRAY)
    disk_bar = ft.ProgressBar(value=0, color=BLUE_PRIMARY, bgcolor="#2A2D3A", width=280, height=10)

    # ============ VALORES DE RED ============
    net_download_history = []
    net_upload_history = []
    net_time_labels = []
    network_chart_container = ft.Container(height=180)

    # ============ STATUS BAR ============
    mode_indicator = "🌐 WEB (Datos Reales)" if IS_WEB else "🖥️ Escritorio"
    status_text = ft.Text(f"Status: Conectado | {mode_indicator}", size=12, color=BLUE_PRIMARY)
    version_text = ft.Text("Versión 2.2.0", size=12, color=TEXT_GRAY)

    # ============ CONTENEDORES DE DETALLES (EXPANDIBLES) ============
    cpu_details_container = ft.Column(spacing=10)
    ram_details_container = ft.Column(spacing=10)
    disk_details_container = ft.Column(spacing=10)

    def update_details_content():
        """Actualizar el contenido de los desplegables (Top procesos, etc.)"""
        theme = ThemeManager.get_theme()
        
        # --- CPU DETALLES ---
        # Uso por núcleo
        cores = monitor.get_cpu_per_core()
        core_bars = []
        for i, usage in enumerate(cores):
            color = theme["accent_red"] if usage > 80 else (theme["accent_yellow"] if usage > 50 else theme["accent_green"])
            core_bars.append(
                ft.Column([
                    ft.Row([
                        ft.Text(f"Core {i}", size=10, color=theme["text_secondary"]),
                        ft.Text(f"{usage}%", size=10, weight=ft.FontWeight.BOLD, color=theme["text_primary"]),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.ProgressBar(value=usage/100, color=color, bgcolor=theme["bg_hover"], height=4),
                ], spacing=2)
            )
        
        # Top Procesos CPU
        top_cpu = process_manager.get_top_cpu(3)
        top_cpu_items = [ft.Text("Top Procesos:", size=12, weight=ft.FontWeight.BOLD, color=theme["text_secondary"])]
        for p in top_cpu:
            top_cpu_items.append(
                ft.Row([
                    ft.Text(p.name[:15], size=11, color=theme["text_primary"]),
                    ft.Text(f"{p.cpu_percent:.1f}%", size=11, color=theme["accent_red"]),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            )

        cpu_details_container.controls = [
            ft.Divider(color=theme["border_primary"]),
            ft.GridView(runs_count=2, max_extent=150, child_aspect_ratio=4, controls=core_bars),
            ft.Container(height=5),
            ft.Column(top_cpu_items, spacing=2)
        ]

        # --- RAM DETALLES ---
        # Top Procesos RAM
        top_mem = process_manager.get_top_memory(3)
        top_mem_items = [ft.Text("Top Memoria:", size=12, weight=ft.FontWeight.BOLD, color=theme["text_secondary"])]
        for p in top_mem:
            top_mem_items.append(
                ft.Row([
                    ft.Text(p.name[:15], size=11, color=theme["text_primary"]),
                    ft.Text(f"{p.memory_mb:.0f} MB", size=11, color=theme["accent_blue"]),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            )
            
        ram_details_container.controls = [
             ft.Divider(color=theme["border_primary"]),
             ft.Column(top_mem_items, spacing=2)
        ]

        # --- DISK DETALLES ---
        # Particiones (simplificado)
        partitions = monitor.get_disk_info()
        part_items = [ft.Text("Particiones:", size=12, weight=ft.FontWeight.BOLD, color=theme["text_secondary"])]
        for p in partitions:
            usage = p['usage']
            part_items.append(
                ft.Column([
                    ft.Row([
                        ft.Text(f"{p['device']}", size=11, color=theme["text_primary"]),
                        ft.Text(f"{usage['percent']}%", size=11, color=theme["text_primary"]),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.ProgressBar(value=usage['percent']/100, color=theme["accent_blue"], height=3),
                ], spacing=2)
            )

        disk_details_container.controls = [
            ft.Divider(color=theme["border_primary"]),
            ft.Column(part_items, spacing=5)
        ]
        
        # No llamamos update() aquí porque están dentro de las cards que quizas no estén en view
        # O si, deberíamos si queremos refresco en tiempo real
        if cpu_details_container.visible: cpu_details_container.update()
        if ram_details_container.visible: ram_details_container.update()
        if disk_details_container.visible: disk_details_container.update()

    # ============ CREAR CARDS ============
    def build_cpu_card():
        return create_cpu_card(
            cpu_name_text, cpu_progress, cpu_percent_text, 
            cpu_temp_text, cpu_speed_text, on_details_click,
            expanded_content=cpu_details_container
        )

    def build_ram_card():
        return create_ram_card(
            ram_used_text, ram_available_text, ram_bar, 
            ram_history_chart, on_details_click,
            expanded_content=ram_details_container
        )

    def build_gpu_card():
        return create_gpu_card(
            gpu_name_text, gpu_progress, gpu_percent_text,
            gpu_temp_text, on_details_click
        )

    def build_disk_card():
        return create_disk_card(
            disk_name_text, disk_used_text, disk_speed_text,
            disk_bar, on_details_click,
            expanded_content=disk_details_container
        )

    def build_network_card():
        return create_network_chart_card(network_chart_container, on_details_click)

    def on_details_click(e):
        """Handler para botones Ver Detalles"""
        pass

    # ============ HEADER BUTTON HANDLERS ============
    def on_theme_light(e):
        """Cambiar a tema claro"""
        ThemeManager.set_light()
        apply_theme_to_page(page, LIGHT_THEME)
        
        # Guardar preferencia en base de datos
        db.set_config('theme', 'light')
        
        # Reconstruir la vista actual con nuevos colores
        rebuild_current_view()
        
        # Notificación toast
        ToastManager.show_success("☀️ Tema claro activado")
        page.update()
    
    def on_theme_dark(e):
        """Cambiar a tema oscuro"""
        ThemeManager.set_dark()
        apply_theme_to_page(page, DARK_THEME)
        
        # Guardar preferencia en base de datos
        db.set_config('theme', 'dark')
        
        # Reconstruir la vista actual con nuevos colores
        rebuild_current_view()
        
        # Notificación toast
        ToastManager.show_success("🌙 Tema oscuro activado")
        page.update()
    
    def on_show_notifications(e):
        """Ir a la vista de alertas/notificaciones"""
        nonlocal current_view
        current_view = "alertas"
        sidebar.selected_index = 5  # Índice de Alertas en el sidebar
        main_content.content = build_alerts_view(alert_manager, page)
        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"🔔 Tienes {alert_manager.count()} alertas configuradas"),
            bgcolor=YELLOW_PRIMARY,
        )
        page.snack_bar.open = True
        page.update()
    
    def rebuild_current_view():
        """Reconstruir la vista actual con los colores del tema"""
        nonlocal current_view
        theme = ThemeManager.get_theme()
        
        # Actualizar colores de fondo de los contenedores principales
        main_content.bgcolor = theme["bg_primary"]
        
        # Actualizar sidebar
        sidebar.bgcolor = theme["bg_sidebar"]
        
        # Actualizar status bar
        status_bar.bgcolor = theme["bg_sidebar"]
        
        # Actualizar colores de textos dinámicos
        cpu_percent_text.color = theme["text_primary"]
        cpu_name_text.color = theme["text_primary"]
        cpu_speed_text.color = theme["text_secondary"]
        
        gpu_percent_text.color = theme["text_primary"]
        gpu_name_text.color = theme["text_primary"]
        
        disk_name_text.color = theme["text_primary"]
        disk_used_text.color = theme["text_secondary"]
        disk_speed_text.color = theme["text_secondary"]
        
        ram_used_text.color = theme["text_secondary"]
        ram_available_text.color = theme["text_secondary"]
        
        # Actualizar colores de barras de progreso
        ram_bar.bgcolor = theme["border_secondary"]
        disk_bar.bgcolor = theme["border_secondary"]
        
        if current_view == "resumen":
            main_content.content = build_resumen_view()
        elif current_view == "cpu":
            main_content.content = build_cpu_detail_view()
        elif current_view == "ram":
            main_content.content = build_ram_detail_view()
        elif current_view == "disco":
            main_content.content = build_disk_detail_view()
        elif current_view == "red":
            main_content.content = build_network_detail_view()
        elif current_view == "alertas":
            main_content.content = build_alerts_view(
                alert_manager, page,
                on_theme_light=on_theme_light,
                on_theme_dark=on_theme_dark,
                on_notifications=on_show_notifications
            )
        elif current_view == "procesos":
            main_content.content = build_processes_view(
                process_manager, page,
                on_theme_light=on_theme_light,
                on_theme_dark=on_theme_dark,
                on_notifications=on_show_notifications
            )
        elif current_view == "historial":
            main_content.content = build_history_view(
                history_manager, page,
                on_theme_light=on_theme_light,
                on_theme_dark=on_theme_dark,
                on_notifications=on_show_notifications
            )
        elif current_view == "ajustes":
            main_content.content = build_config_view(
                db, page,
                on_theme_light=on_theme_light,
                on_theme_dark=on_theme_dark,
                on_notifications=on_show_notifications
            )

    # ============ VISTAS ============
    def build_resumen_view():
        return ft.Container(
            content=ft.Column([
                create_header(
                    "Estado del Sistema - Tiempo Real",
                    on_theme_toggle=on_theme_light,
                    on_dark_mode=on_theme_dark,
                    on_notifications=on_show_notifications
                ),
                ft.Container(height=15),
                ft.Row([
                    ft.Container(content=build_cpu_card(), expand=1),
                    ft.Container(width=15),
                    ft.Container(content=build_ram_card(), expand=1),
                ], expand=False),
                ft.Container(height=15),
                ft.Row([
                    ft.Container(content=build_disk_card(), expand=2),
                    ft.Container(width=15),
                    ft.Container(content=build_gpu_card(), expand=1),
                ], expand=False),
                ft.Container(height=15),
                build_network_card(),
            ], scroll=ft.ScrollMode.AUTO, spacing=0),
            padding=25,
            expand=True,
            bgcolor=ThemeManager.get_theme()["bg_primary"],
        )


    def build_cpu_detail_view():
        theme = ThemeManager.get_theme()
        
        # Info básica
        user_info = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.INFO_OUTLINE, color=theme["accent_blue"], size=20),
                    ft.Text("Información del Procesador", size=16, weight=ft.FontWeight.W_500, color=theme["text_primary"]),
                ]),
                ft.Container(height=15),
                ft.Text(f"Núcleos físicos: {monitor.get_cpu_count()[0]}", color=theme["text_secondary"]),
                ft.Text(f"Núcleos lógicos: {monitor.get_cpu_count()[1]}", color=theme["text_secondary"]),
                ft.Text(f"Arquitectura: {monitor.get_system_info()['architecture']}", color=theme["text_secondary"]),
                ft.Text(f"Frecuencia actual: {monitor.get_cpu_freq() or 'N/A'} GHz", color=theme["text_secondary"]),
            ]),
            bgcolor=theme["bg_card"],
            border_radius=15,
            padding=20,
            expand=True,
        )

        # Uso por núcleo (construido dinámicamente)
        cores_usage = monitor.get_cpu_per_core()
        core_controls = []
        for i, usage in enumerate(cores_usage):
            color = theme["accent_red"] if usage > 80 else (theme["accent_yellow"] if usage > 50 else theme["accent_green"])
            core_controls.append(
                ft.Column([
                    ft.Row([
                        ft.Text(f"Núcleo {i}", size=12, color=theme["text_secondary"]),
                        ft.Text(f"{usage}%", size=12, weight=ft.FontWeight.BOLD, color=theme["text_primary"]),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.ProgressBar(value=usage/100, color=color, bgcolor=theme["bg_hover"], height=6),
                ], spacing=3)
            )
            
        cores_expansion = ft.Container(
            content=ft.ExpansionTile(
                title=ft.Row([
                    ft.Icon(ft.Icons.GRID_VIEW, color=theme["accent_purple"], size=20),
                    ft.Text("Uso por Núcleo", size=16, weight=ft.FontWeight.W_500, color=theme["text_primary"]),
                ]),
                controls=[
                    ft.Container(height=15),
                    ft.GridView(
                        runs_count=2,
                        max_extent=250,
                        child_aspect_ratio=3,
                        spacing=15,
                        run_spacing=15,
                        controls=core_controls,
                    ),
                    ft.Container(height=10),
                ],

                collapsed_text_color=theme["text_primary"],
                text_color=theme["text_primary"],
                icon_color=theme["text_secondary"],
                bgcolor=ft.Colors.TRANSPARENT,
            ),
            bgcolor=theme["bg_card"],
            border_radius=15,
            padding=5,
        )

        # Top Procesos CPU
        top_cpu = process_manager.get_top_cpu(5)
        top_cpu_rows = []
        for p in top_cpu:
            top_cpu_rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(p.pid), color=theme["text_secondary"], size=12)),
                    ft.DataCell(ft.Text(p.name[:20], color=theme["text_primary"], size=12, weight=ft.FontWeight.BOLD)),
                    ft.DataCell(ft.Text(f"{p.cpu_percent:.1f}%", color=theme["accent_red"] if p.cpu_percent > 10 else theme["text_primary"], size=12)),
                ])
            )
            
        top_processes_expansion = ft.Container(
            content=ft.ExpansionTile(
                title=ft.Row([
                    ft.Icon(ft.Icons.SPEED, color=theme["accent_red"], size=20),
                    ft.Text("Top 5 Procesos (CPU)", size=16, weight=ft.FontWeight.W_500, color=theme["text_primary"]),
                ]),
                controls=[
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("PID", size=12, color=theme["text_secondary"])),
                            ft.DataColumn(ft.Text("Nombre", size=12, color=theme["text_secondary"])),
                            ft.DataColumn(ft.Text("Uso", size=12, color=theme["text_secondary"])),
                        ],
                        rows=top_cpu_rows,
                        heading_row_height=30,
                        data_row_min_height=40,
                    )
                ],

                collapsed_text_color=theme["text_primary"],
                text_color=theme["text_primary"],
                icon_color=theme["text_secondary"],
                bgcolor=ft.Colors.TRANSPARENT,
            ),
            bgcolor=theme["bg_card"],
            border_radius=15,
            padding=5,
        )

        return ft.Container(
            content=ft.Column([
                create_header("CPU - Detalles", on_theme_toggle=on_theme_light, on_dark_mode=on_theme_dark, on_notifications=on_show_notifications),
                ft.Container(height=10),
                build_cpu_card(),
                ft.Container(height=20),
                user_info,
                ft.Container(height=10),
                top_processes_expansion,
                ft.Container(height=10),
                cores_expansion,
            ], scroll=ft.ScrollMode.AUTO),
            padding=25,
            expand=True,
            bgcolor=theme["bg_primary"],
        )

    def build_ram_detail_view():
        theme = ThemeManager.get_theme()
        
        # Info Swap
        swap = monitor.get_swap_memory()
        swap_used_gb = swap['used'] / (1024**3)
        swap_total_gb = swap['total'] / (1024**3)
        swap_percent = swap['percent']
        
        swap_expansion = ft.Container(
            content=ft.ExpansionTile(
                title=ft.Row([
                    ft.Icon(ft.Icons.MEMORY, color=theme["accent_orange"], size=20),
                    ft.Text("Memoria Virtual (Swap)", size=16, weight=ft.FontWeight.W_500, color=theme["text_primary"]),
                ]),
                controls=[
                    ft.Container(height=10),
                    ft.Row([
                        ft.Text("Usado / Total:", color=theme["text_secondary"]),
                        ft.Text(f"{swap_used_gb:.1f} GB / {swap_total_gb:.1f} GB", color=theme["text_primary"], weight=ft.FontWeight.BOLD),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.ProgressBar(value=swap_percent/100, color=theme["accent_orange"], bgcolor=theme["bg_hover"], height=8),
                    ft.Text(f"{swap_percent}% Utilizado", size=12, color=theme["text_secondary"], text_align=ft.TextAlign.RIGHT),
                    ft.Container(height=10),
                ],

                collapsed_text_color=theme["text_primary"],
                text_color=theme["text_primary"],
                icon_color=theme["text_secondary"],
                bgcolor=ft.Colors.TRANSPARENT,
            ),
            bgcolor=theme["bg_card"],
            border_radius=15,
            padding=5,
        )

        # Top Procesos RAM
        top_mem = process_manager.get_top_memory(5)
        top_mem_rows = []
        for p in top_mem:
            top_mem_rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(p.pid), color=theme["text_secondary"], size=12)),
                    ft.DataCell(ft.Text(p.name[:20], color=theme["text_primary"], size=12, weight=ft.FontWeight.BOLD)),
                    ft.DataCell(ft.Text(f"{p.memory_mb:.0f} MB", color=theme["accent_blue"], size=12)),
                ])
            )

        top_processes_expansion = ft.Container(
            content=ft.ExpansionTile(
                title=ft.Row([
                    ft.Icon(ft.Icons.TABLE_CHART, color=theme["accent_blue"], size=20),
                    ft.Text("Top 5 Procesos (RAM)", size=16, weight=ft.FontWeight.W_500, color=theme["text_primary"]),
                ]),
                controls=[
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("PID", size=12, color=theme["text_secondary"])),
                            ft.DataColumn(ft.Text("Nombre", size=12, color=theme["text_secondary"])),
                            ft.DataColumn(ft.Text("Uso", size=12, color=theme["text_secondary"])),
                        ],
                        rows=top_mem_rows,
                        heading_row_height=30,
                        data_row_min_height=40,
                    )
                ],

                collapsed_text_color=theme["text_primary"],
                text_color=theme["text_primary"],
                icon_color=theme["text_secondary"],
                bgcolor=ft.Colors.TRANSPARENT,
            ),
            bgcolor=theme["bg_card"],
            border_radius=15,
            padding=5,
        )

        return ft.Container(
            content=ft.Column([
                create_header("RAM - Detalles", on_theme_toggle=on_theme_light, on_dark_mode=on_theme_dark, on_notifications=on_show_notifications),
                ft.Container(height=10),
                build_ram_card(),
                ft.Container(height=20),
                swap_expansion,
                ft.Container(height=10),
                top_processes_expansion,
            ], scroll=ft.ScrollMode.AUTO),
            padding=25,
            expand=True,
            bgcolor=theme["bg_primary"],
        )

    def build_disk_detail_view():
        theme = ThemeManager.get_theme()
        
        # IO Estadísticas
        io_stats = monitor.get_disk_io()
        read_speed = io_stats['read_speed'] if io_stats else 0
        write_speed = io_stats['write_speed'] if io_stats else 0
        
        io_expansion = ft.Container(
            content=ft.ExpansionTile(
                title=ft.Row([
                    ft.Icon(ft.Icons.SPEED, color=theme["accent_purple"], size=20),
                    ft.Text("Velocidad de Disco (I/O)", size=16, weight=ft.FontWeight.W_500, color=theme["text_primary"]),
                ]),
                controls=[
                    ft.Container(height=10),
                    ft.Row([
                        ft.Column([
                            ft.Text("Lectura", color=theme["text_secondary"], size=12),
                            ft.Text(f"{read_speed:.1f} MB/s", color=theme["accent_green"], size=20, weight=ft.FontWeight.BOLD),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Column([
                            ft.Text("Escritura", color=theme["text_secondary"], size=12),
                            ft.Text(f"{write_speed:.1f} MB/s", color=theme["accent_red"], size=20, weight=ft.FontWeight.BOLD),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    ], alignment=ft.MainAxisAlignment.SPACE_EVENLY, expand=True),
                    ft.Container(height=10),
                ],

                collapsed_text_color=theme["text_primary"],
                text_color=theme["text_primary"],
                icon_color=theme["text_secondary"],
                bgcolor=ft.Colors.TRANSPARENT,
            ),
            bgcolor=theme["bg_card"],
            border_radius=15,
            padding=5,
        )
        
        # Lista de Particiones
        partitions = monitor.get_disk_info()
        partition_controls = []
        
        for p in partitions:
            usage = p['usage']
            used_gb = usage['used'] / (1024**3)
            total_gb = usage['total'] / (1024**3)
            percent = usage['percent']
            
            p_color = theme["accent_red"] if percent > 90 else (theme["accent_yellow"] if percent > 70 else theme["accent_blue"])
            
            partition_controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Row([
                                ft.Icon(ft.Icons.STORAGE, color=theme["text_secondary"]),
                                ft.Text(f"{p['device']} ({p['mountpoint']})", weight=ft.FontWeight.BOLD, color=theme["text_primary"]),
                            ]),
                            ft.Container(
                                content=ft.Text(p['fstype'].upper(), size=10, color=theme["bg_card"]),
                                bgcolor=theme["text_secondary"],
                                padding=ft.Padding(left=8, right=8, top=2, bottom=2),
                                border_radius=10,
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Container(height=10),
                        ft.ProgressBar(value=percent/100, color=p_color, bgcolor=theme["bg_hover"], height=10, border_radius=5),
                        ft.Row([
                            ft.Text(f"{used_gb:.1f} GB usados", size=12, color=theme["text_secondary"]),
                            ft.Text(f"{total_gb:.1f} GB total", size=12, color=theme["text_secondary"]),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ]),
                    bgcolor=theme["bg_hover"], # Ligeramente más claro
                    border_radius=10,
                    padding=15,
                    margin=ft.Margin(left=0, top=0, right=0, bottom=10)
                )
            )

        partitions_expansion = ft.Container(
            content=ft.ExpansionTile(
                title=ft.Row([
                    ft.Icon(ft.Icons.STORAGE, color=theme["accent_blue"], size=20),
                    ft.Text("Particiones y Dispositivos", size=16, weight=ft.FontWeight.W_500, color=theme["text_primary"]),
                ]),
                controls=[
                    ft.Container(height=10),
                    ft.Column(partition_controls),
                    ft.Container(height=10),
                ],

                collapsed_text_color=theme["text_primary"],
                text_color=theme["text_primary"],
                icon_color=theme["text_secondary"],
                bgcolor=ft.Colors.TRANSPARENT,
            ),
            bgcolor=theme["bg_card"],
            border_radius=15,
            padding=5,
        )

        return ft.Container(
            content=ft.Column([
                create_header("Disco - Detalles", on_theme_toggle=on_theme_light, on_dark_mode=on_theme_dark, on_notifications=on_show_notifications),
                ft.Container(height=10),
                build_disk_card(),
                ft.Container(height=20),
                io_expansion,
                ft.Container(height=10),
                partitions_expansion,
            ], scroll=ft.ScrollMode.AUTO),
            padding=25,
            expand=True,
            bgcolor=theme["bg_primary"],
        )

    def build_network_detail_view():
        theme = ThemeManager.get_theme()
        return ft.Container(
            content=ft.Column([
                create_header("Red - Detalles", on_theme_toggle=on_theme_light, on_dark_mode=on_theme_dark, on_notifications=on_show_notifications),
                ft.Container(height=20),
                build_network_card(),
            ], scroll=ft.ScrollMode.AUTO),
            padding=25,
            expand=True,
            bgcolor=theme["bg_primary"],
        )

    # ============ CONTENEDOR PRINCIPAL ============
    main_content = ft.Container(
        content=build_resumen_view(),
        expand=True,
        bgcolor=DARK_BG,
    )

    # ============ NAVEGACIÓN ============
    def on_nav_change(e):
        nonlocal current_view
        index = e.control.selected_index
        views = ["resumen", "cpu", "ram", "disco", "red", "alertas", "procesos", "historial", "ajustes"]
        current_view = views[index]
        
        if current_view == "resumen":
            main_content.content = build_resumen_view()
        elif current_view == "cpu":
            main_content.content = build_cpu_detail_view()
        elif current_view == "ram":
            main_content.content = build_ram_detail_view()
        elif current_view == "disco":
            main_content.content = build_disk_detail_view()
        elif current_view == "red":
            main_content.content = build_network_detail_view()
        elif current_view == "alertas":
            main_content.content = build_alerts_view(
                alert_manager, page,
                on_theme_light=on_theme_light,
                on_theme_dark=on_theme_dark,
                on_notifications=on_show_notifications
            )
        elif current_view == "procesos":
            main_content.content = build_processes_view(
                process_manager, page,
                on_theme_light=on_theme_light,
                on_theme_dark=on_theme_dark,
                on_notifications=on_show_notifications
            )
        elif current_view == "historial":
            main_content.content = build_history_view(
                history_manager, page,
                on_theme_light=on_theme_light,
                on_theme_dark=on_theme_dark,
                on_notifications=on_show_notifications
            )
        elif current_view == "ajustes":
            main_content.content = build_config_view(
                db, page,
                on_theme_light=on_theme_light,
                on_theme_dark=on_theme_dark,
                on_notifications=on_show_notifications
            )
        
        page.update()

    # Crear sidebar con nuevos items CRUD
    sidebar = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=80,
        min_extended_width=200,
        bgcolor=SIDEBAR_BG,
        indicator_color=GREEN_PRIMARY + "30",
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.DASHBOARD_OUTLINED,
                selected_icon=ft.Icons.DASHBOARD,
                label="Resumen",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.MEMORY_OUTLINED,
                selected_icon=ft.Icons.MEMORY,
                label="CPU",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.STORAGE_OUTLINED,
                selected_icon=ft.Icons.STORAGE,
                label="RAM",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.DISC_FULL_OUTLINED,
                selected_icon=ft.Icons.DISC_FULL,
                label="Disco",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.WIFI_OUTLINED,
                selected_icon=ft.Icons.WIFI,
                label="Red",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.NOTIFICATIONS_OUTLINED,
                selected_icon=ft.Icons.NOTIFICATIONS,
                label="Alertas",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.LIST_ALT_OUTLINED,
                selected_icon=ft.Icons.LIST_ALT,
                label="Procesos",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.HISTORY_OUTLINED,
                selected_icon=ft.Icons.HISTORY,
                label="Historial",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
                label="Ajustes",
            ),
        ],
        on_change=on_nav_change,
    )

    # ============ STATUS BAR ============
    status_bar = ft.Container(
        content=ft.Row([
            status_text,
            ft.Container(expand=True),
            version_text,
        ]),
        bgcolor=SIDEBAR_BG,
        padding=ft.Padding(left=20, right=20, top=8, bottom=8),
        height=35,
    )

    # ============ LAYOUT PRINCIPAL ============
    page.add(
        ft.Column([
            ft.Row([
                sidebar,
                ft.VerticalDivider(width=1, color="#2A2D3A"),
                main_content,
            ], expand=True, spacing=0),
            status_bar,
        ], expand=True, spacing=0)
    )

    # ============ LOOP DE ACTUALIZACIÓN ============
    async def update_metrics():
        nonlocal net_download_history, net_upload_history, net_time_labels, history_save_counter
        
        while True:
            try:
                # En modo web, primero refrescar datos desde API
                if IS_WEB and isinstance(monitor, WebMonitor):
                    monitor.refresh()
                
                # CPU
                cpu = monitor.get_cpu_usage()
                chart_mgr.cpu_history.append(cpu)
                cpu_percent_text.value = f"{cpu:.0f}%"
                cpu_progress.content.controls[0].value = cpu / 100
                
                temp = monitor.get_cpu_temp()
                if temp:
                    cpu_temp_text.value = f"Temp: {temp:.0f}°C"
                    if temp > 80:
                        cpu_temp_text.color = RED_PRIMARY
                    elif temp > 60:
                        cpu_temp_text.color = YELLOW_PRIMARY
                    else:
                        cpu_temp_text.color = GREEN_PRIMARY
                else:
                    cpu_temp_text.value = "Temp: N/A"
                    cpu_temp_text.color = TEXT_GRAY

                cpu_freq = monitor.get_cpu_freq()
                if cpu_freq:
                    cpu_speed_text.value = f"Speed: {cpu_freq:.1f} GHz"
                
                sys_info = monitor.get_system_info()
                processor_name = sys_info['processor'] if sys_info['processor'] else 'Unknown'
                cpu_name_text.value = f"CPU: {processor_name[:30]}"

                # Memoria
                mem = monitor.get_memory_usage()
                chart_mgr.mem_history.append(mem['percent'])
                used_gb = mem['used'] / (1024**3)
                total_gb = mem['total'] / (1024**3)
                available_gb = mem['free'] / (1024**3)
                
                ram_used_text.value = f"{used_gb:.0f}GB / {total_gb:.0f}GB ({mem['percent']:.0f}%)"
                ram_available_text.value = f"Available: {available_gb:.0f}GB"
                ram_bar.value = mem['percent'] / 100
                
                # Actualizar mini chart de RAM
                ram_history_chart.content = chart_mgr.create_mini_line_chart(
                    list(chart_mgr.mem_history)[-30:], GREEN_PRIMARY, 50
                )

                # Disco
                disk = monitor.get_disk_usage()
                disk_info_list = monitor.get_disk_info()
                main_disk = disk_info_list[0] if disk_info_list else {}
                
                used_disk_gb = disk['used'] / (1024**3)
                total_disk_gb = disk['total'] / (1024**3)
                
                disk_device = main_disk.get('device', 'SSD')
                disk_name_text.value = f"Disco: {disk_device} {total_disk_gb:.0f}GB"
                disk_used_text.value = f"{used_disk_gb:.0f}GB Used ({disk['percent']:.0f}%)"
                disk_bar.value = disk['percent'] / 100
                
                disk_io = monitor.get_disk_io()
                if disk_io:
                    disk_speed_text.value = f"Read/Write: {disk_io['read_speed']:.0f}MB/s"

                # GPU
                gpu_info = monitor.get_gpu_info()
                if gpu_info:
                    gpu_percent_text.value = f"{gpu_info['usage']:.0f}%"
                    gpu_progress.content.controls[0].value = gpu_info['usage'] / 100
                    gpu_temp_text.value = f"Temp: {gpu_info['temp']:.0f}°C"
                    gpu_name_text.value = f"GPU/Temp: {gpu_info['name'][:20]}"
                    
                    if gpu_info['temp'] > 80:
                        gpu_temp_text.color = RED_PRIMARY
                    elif gpu_info['temp'] > 60:
                        gpu_temp_text.color = YELLOW_PRIMARY
                    else:
                        gpu_temp_text.color = GREEN_PRIMARY
                else:
                    gpu_percent_text.value = f"{cpu * 0.3:.0f}%"
                    gpu_progress.content.controls[0].value = (cpu * 0.3) / 100
                    gpu_temp_text.value = "Temp: N/A"
                    gpu_name_text.value = "GPU/Temp: No detectada"

                # Red
                net = monitor.get_network_speed()
                down_mb = net['download'] / (1024 * 1024)
                up_mb = net['upload'] / (1024 * 1024)
                
                chart_mgr.net_down_history.append(down_mb * 10)
                chart_mgr.net_up_history.append(up_mb * 10)
                
                now = datetime.now()
                time_label = now.strftime("%H:%M")
                
                net_download_history.append(down_mb * 100)
                net_upload_history.append(up_mb * 100)
                net_time_labels.append(time_label)
                
                if len(net_download_history) > 60:
                    net_download_history = net_download_history[-60:]
                    net_upload_history = net_upload_history[-60:]
                    net_time_labels = net_time_labels[-60:]
                
                network_chart_container.content = chart_mgr.create_network_area_chart(
                    net_download_history, net_upload_history, net_time_labels
                )

                # ============ CRUD: Guardar historial cada 10 actualizaciones ============
                history_save_counter += 1
                if history_save_counter >= 10:
                    history_save_counter = 0
                    try:
                        history_manager.save(
                            cpu_usage=cpu,
                            cpu_temp=temp,
                            ram_usage=mem['percent'],
                            ram_used_gb=used_gb,
                            disk_usage=disk['percent'],
                            disk_read_speed=disk_io.get('read_speed') if disk_io else None,
                            disk_write_speed=disk_io.get('write_speed') if disk_io else None,
                            net_upload=up_mb,
                            net_download=down_mb,
                            gpu_usage=gpu_info['usage'] if gpu_info else None,
                            gpu_temp=gpu_info['temp'] if gpu_info else None,
                        )
                    except Exception as he:
                        print(f"Error guardando historial: {he}")
                
                # ============ ACTUALIZAR DETALLES EXPANDIBLES ============
                try:
                    # Actualizar solo si hay contenedores visibles para mejorar performance
                    # O actualizar siempre si queremos que esté listo al abrir
                    update_details_content()
                except Exception as dex:
                     print(f"Error actualizando detalles: {dex}")

                # ============ CRUD: Evaluar alertas ============
                try:
                    current_metrics = {
                        'cpu_usage': cpu,
                        'cpu_temp': temp,
                        'ram_usage': mem['percent'],
                        'disk_usage': disk['percent'],
                        'gpu_usage': gpu_info['usage'] if gpu_info else None,
                        'gpu_temp': gpu_info['temp'] if gpu_info else None,
                    }
                    
                    # Verificar cada alerta habilitada
                    for alert in alert_manager.get_all(only_enabled=True):
                        metric_value = current_metrics.get(alert.metric)
                        if metric_value is not None:
                            # Determinar condición para ToastManager
                            condition = "greater" if alert.operator in [">", ">="] else "less" if alert.operator in ["<", "<="] else "equal"
                            
                            # Mostrar alerta solo si cruza el umbral (no si se mantiene)
                            # ToastManager internamente maneja rate limiting (1 por minuto por métrica)
                            ToastManager.show_alert(
                                alert_name=alert.name,
                                metric=alert.metric,
                                value=metric_value,
                                threshold=alert.threshold,
                                condition=condition
                            )
                except Exception as ae:
                    print(f"Error evaluando alertas: {ae}")

                # Actualizar status
                if IS_WEB:
                    status_text.value = f"Status: Conectado | 🌐 WEB (Datos Reales via API)"
                else:
                    alert_count = alert_manager.count()
                    status_text.value = f"Status: Conectado | 🖥️ Escritorio | 🔔 {alert_count} alertas"
                status_text.color = BLUE_PRIMARY

                page.update()

            except Exception as e:
                print(f"Error en actualización: {e}")
                import traceback
                traceback.print_exc()
                status_text.value = f"Status: Error - {str(e)[:30]}"
                status_text.color = RED_PRIMARY

            await asyncio.sleep(update_interval)

    page.run_task(update_metrics)


if __name__ == "__main__":
    print("=" * 50)
    print("  OmniMonitor v2.3.0 - Sistema de Monitoreo")
    print("  Con CRUD: Alertas, Procesos, Historial, Config")
    print("=" * 50)
    
    if IS_WEB:
        # Modo web - iniciar servidor API primero, luego UI
        print("\n🌐 Iniciando OmniMonitor en modo WEB...")
        print(f"📡 Iniciando servidor API en puerto {API_PORT}...")
        
        # Iniciar servidor API en background
        from src.server.api import run_server_background
        run_server_background(API_PORT)
        
        import time
        time.sleep(1)  # Esperar que arranque el servidor
        
        print(f"📍 API: http://localhost:{API_PORT}/api/all")
        print(f"📍 UI:  Se abrirá en tu navegador")
        print("   Presiona Ctrl+C para detener")
        print()
        
        ft.run(main, view=ft.AppView.WEB_BROWSER, port=8550)
    else:
        # Modo escritorio nativo
        print("\n🖥️  Iniciando OmniMonitor en modo ESCRITORIO...")
        ft.run(main)
