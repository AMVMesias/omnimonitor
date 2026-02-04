"""
Vistas CRUD para OmniMonitor
Interfaz gráfica para Alertas, Procesos, Historial y Configuración
"""
import flet as ft
from typing import Callable, Optional
from datetime import datetime

# Importar sistema de temas
try:
    from .theme_manager import ThemeManager
except ImportError:
    from src.ui.theme_manager import ThemeManager

# Colores por defecto (fallback)
DARK_BG = "#1A1B26"
CARD_BG = "#24283B"
SIDEBAR_BG = "#1F2335"
GREEN_PRIMARY = "#9ECE6A"
BLUE_PRIMARY = "#7AA2F7"
ORANGE_PRIMARY = "#FF9E64"
RED_PRIMARY = "#F7768E"
YELLOW_PRIMARY = "#E0AF68"
PURPLE_PRIMARY = "#BB9AF7"
TEXT_WHITE = "#C0CAF5"
TEXT_GRAY = "#565F89"


def get_crud_theme():
    """Obtener colores del tema actual para vistas CRUD"""
    theme = ThemeManager.get_theme()
    return {
        "bg": theme["bg_primary"],
        "card": theme["bg_card"],
        "text": theme["text_primary"],
        "text_secondary": theme["text_secondary"],
        "border": theme["border_primary"],
        "green": theme["accent_green"],
        "blue": theme["accent_blue"],
        "orange": theme["accent_orange"],
        "red": theme["accent_red"],
        "yellow": theme["accent_yellow"],
    }


def create_crud_header(title: str, subtitle: str = "", icon: str = None, 
                       on_theme_light=None, on_theme_dark=None, on_notifications=None) -> ft.Container:
    """Crear encabezado para vistas CRUD con botones de tema"""
    colors = get_crud_theme()
    return ft.Container(
        content=ft.Row([
            ft.Icon(icon, color=colors["blue"], size=28) if icon else ft.Container(),
            ft.Column([
                ft.Text(title, size=24, weight=ft.FontWeight.BOLD, color=colors["text"]),
                ft.Text(subtitle, size=13, color=colors["text_secondary"]) if subtitle else ft.Container(),
            ], spacing=2),
            ft.Container(expand=True),
            ft.Row([
                ft.IconButton(
                    icon=ft.Icons.LIGHT_MODE_OUTLINED,
                    icon_color=colors["text_secondary"],
                    icon_size=20,
                    tooltip="Modo claro",
                    on_click=on_theme_light,
                ),
                ft.IconButton(
                    icon=ft.Icons.DARK_MODE_OUTLINED,
                    icon_color=colors["text_secondary"],
                    icon_size=20,
                    tooltip="Modo oscuro",
                    on_click=on_theme_dark,
                ),
                ft.IconButton(
                    icon=ft.Icons.NOTIFICATIONS_OUTLINED,
                    icon_color=colors["text_secondary"],
                    icon_size=20,
                    tooltip="Ver alertas",
                    on_click=on_notifications,
                ),
            ], spacing=0),
        ], spacing=15),
        padding=ft.Padding(0, 0, 0, 15),
    )


# ==================== VISTA DE ALERTAS ====================

def build_alerts_view(alert_manager, page: ft.Page, on_refresh: Callable = None,
                      on_theme_light=None, on_theme_dark=None, on_notifications=None) -> ft.Container:
    """Construir vista de gestión de alertas"""
    colors = get_crud_theme()
    
    alerts_list = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
    
    # Campos del formulario
    name_field = ft.TextField(
        label="Nombre de la alerta",
        hint_text="Ej: CPU Alto",
        bgcolor=colors["card"],
        border_color=colors["border"],
        color=colors["text"],
        width=300,
    )
    
    metric_dropdown = ft.Dropdown(
        label="Métrica",
        options=[
            ft.dropdown.Option("cpu_usage", "Uso de CPU (%)"),
            ft.dropdown.Option("cpu_temp", "Temperatura CPU (°C)"),
            ft.dropdown.Option("ram_usage", "Uso de RAM (%)"),
            ft.dropdown.Option("disk_usage", "Uso de Disco (%)"),
            ft.dropdown.Option("gpu_usage", "Uso de GPU (%)"),
            ft.dropdown.Option("gpu_temp", "Temperatura GPU (°C)"),
        ],
        width=200,
        bgcolor=colors["card"],
        border_color=colors["border"],
        color=colors["text"],
    )
    
    operator_dropdown = ft.Dropdown(
        label="Condición",
        options=[
            ft.dropdown.Option(">", "Mayor que (>)"),
            ft.dropdown.Option("<", "Menor que (<)"),
            ft.dropdown.Option(">=", "Mayor o igual (>=)"),
            ft.dropdown.Option("<=", "Menor o igual (<=)"),
        ],
        value=">",
        width=150,
        bgcolor=colors["card"],
        border_color=colors["border"],
        color=colors["text"],
    )
    
    threshold_field = ft.TextField(
        label="Umbral",
        hint_text="Ej: 80",
        bgcolor=colors["card"],
        border_color=colors["border"],
        color=colors["text"],
        width=100,
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    
    status_text = ft.Text("", color=colors["green"], size=12)
    
    def refresh_alerts_list():
        """Actualizar lista de alertas"""
        c = get_crud_theme()
        alerts_list.controls.clear()
        alerts = alert_manager.get_all()
        
        if not alerts:
            alerts_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.NOTIFICATIONS_OFF, color=c["text_secondary"], size=48),
                        ft.Text("No hay alertas configuradas", color=c["text_secondary"], size=14),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=40,
                    alignment=ft.alignment.Alignment(0, 0),
                )
            )
        else:
            for alert in alerts:
                metric_label = alert_manager.METRICS_LABELS.get(alert.metric, alert.metric)
                
                alert_card = ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Icon(
                                ft.Icons.NOTIFICATIONS_ACTIVE if alert.enabled else ft.Icons.NOTIFICATIONS_OFF,
                                color=c["green"] if alert.enabled else c["text_secondary"],
                                size=24
                            ),
                            padding=10,
                        ),
                        ft.Column([
                            ft.Text(alert.name, size=15, weight=ft.FontWeight.W_500, color=c["text"]),
                            ft.Text(
                                f"{metric_label} {alert.operator} {alert.threshold}",
                                size=12, color=c["text_secondary"]
                            ),
                            ft.Text(
                                f"Disparada {alert.triggered_count} veces",
                                size=11, color=c["yellow"] if alert.triggered_count > 0 else c["text_secondary"]
                            ),
                        ], spacing=2, expand=True),
                        ft.Switch(
                            value=alert.enabled,
                            active_color=c["green"],
                            on_change=lambda e, aid=alert.id: toggle_alert(aid),
                        ),
                        ft.IconButton(
                            ft.Icons.DELETE_OUTLINE,
                            icon_color=c["red"],
                            tooltip="Eliminar",
                            on_click=lambda e, aid=alert.id: delete_alert(aid),
                        ),
                    ], spacing=10),
                    bgcolor=c["card"],
                    border_radius=10,
                    padding=15,
                )
                alerts_list.controls.append(alert_card)
        
        page.update()
    
    def create_alert(e):
        """Crear nueva alerta"""
        c = get_crud_theme()
        if not name_field.value or not metric_dropdown.value or not threshold_field.value:
            status_text.value = "❌ Completa todos los campos"
            status_text.color = c["red"]
            page.update()
            return
        
        try:
            threshold = float(threshold_field.value)
            alert_manager.create(
                name=name_field.value,
                metric=metric_dropdown.value,
                operator=operator_dropdown.value,
                threshold=threshold
            )
            
            # Limpiar campos
            name_field.value = ""
            metric_dropdown.value = None
            threshold_field.value = ""
            
            status_text.value = "✅ Alerta creada exitosamente"
            status_text.color = c["green"]
            refresh_alerts_list()
        except ValueError:
            status_text.value = "❌ Umbral debe ser un número"
            status_text.color = c["red"]
            page.update()
    
    def toggle_alert(alert_id: int):
        """Alternar estado de alerta"""
        alert_manager.toggle(alert_id)
        refresh_alerts_list()
    
    def delete_alert(alert_id: int):
        """Eliminar alerta"""
        c = get_crud_theme()
        alert_manager.delete(alert_id)
        status_text.value = "🗑️ Alerta eliminada"
        status_text.color = c["yellow"]
        refresh_alerts_list()
    
    # Formulario de creación
    form = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.ADD_ALERT, color=colors["green"], size=20),
                ft.Text("Nueva Alerta", size=16, weight=ft.FontWeight.W_500, color=colors["text"]),
            ]),
            ft.Container(height=10),
            ft.Row([name_field, metric_dropdown], spacing=15, wrap=True),
            ft.Container(height=10),
            ft.Row([operator_dropdown, threshold_field], spacing=15),
            ft.Container(height=15),
            ft.Row([
                ft.ElevatedButton(
                    "Crear Alerta",
                    icon=ft.Icons.ADD,
                    bgcolor=colors["green"],
                    color=colors["bg"],
                    on_click=create_alert,
                ),
                status_text,
            ], spacing=15),
        ]),
        bgcolor=colors["card"],
        border_radius=15,
        padding=20,
    )
    
    # Inicializar lista
    refresh_alerts_list()
    
    return ft.Container(
        content=ft.Column([
            create_crud_header("Alertas", "Configura notificaciones automáticas", ft.Icons.NOTIFICATIONS,
                               on_theme_light, on_theme_dark, on_notifications),
            form,
            ft.Container(height=20),
            ft.Row([
                ft.Icon(ft.Icons.LIST, color=colors["blue"], size=20),
                ft.Text("Alertas Activas", size=16, weight=ft.FontWeight.W_500, color=colors["text"]),
                ft.Container(expand=True),
                ft.IconButton(ft.Icons.REFRESH, icon_color=colors["blue"], on_click=lambda e: refresh_alerts_list()),
            ]),
            ft.Container(height=10),
            ft.Container(
                content=alerts_list,
                bgcolor=colors["card"],
                border_radius=15,
                padding=15,
                expand=True,
            ),
        ], scroll=ft.ScrollMode.AUTO),
        padding=25,
        expand=True,
        bgcolor=colors["bg"],
    )


# ==================== VISTA DE PROCESOS ====================

def build_processes_view(process_manager, page: ft.Page,
                         on_theme_light=None, on_theme_dark=None, on_notifications=None) -> ft.Container:
    """Construir vista de gestión de procesos con carga asíncrona"""
    colors = get_crud_theme()
    
    # Crear tabla vacía (se llena después)
    processes_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("PID", color=colors["text"], size=12)),
            ft.DataColumn(ft.Text("Nombre", color=colors["text"], size=12)),
            ft.DataColumn(ft.Text("CPU %", color=colors["text"], size=12)),
            ft.DataColumn(ft.Text("RAM (MB)", color=colors["text"], size=12)),
            ft.DataColumn(ft.Text("Estado", color=colors["text"], size=12)),
            ft.DataColumn(ft.Text("Acción", color=colors["text"], size=12)),
        ],
        rows=[],
        border=ft.border.all(1, colors["border"]),
        border_radius=10,
        heading_row_color=colors["card"],
        data_row_color={"": colors["card"], "hovered": colors["border"]},
        column_spacing=20,
    )
    
    # Loader para mostrar mientras carga
    loading_indicator = ft.Container(
        content=ft.Column([
            ft.ProgressRing(width=40, height=40, stroke_width=3, color=colors["blue"]),
            ft.Text("Cargando procesos...", size=14, color=colors["text_secondary"]),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
           alignment=ft.MainAxisAlignment.CENTER, spacing=15),
        height=200,
    )
    
    # Contenedor que alterna entre loader y tabla
    table_container = ft.Container(
        content=loading_indicator,  # Inicia con loader
        bgcolor=colors["card"],
        border_radius=15,
        padding=15,
        expand=True,
    )
    
    search_field = ft.TextField(
        hint_text="🔍 Buscar proceso...",
        bgcolor=colors["card"],
        border_color=colors["border"],
        color=colors["text"],
        width=300,
        height=40,
        content_padding=ft.Padding(10, 0, 10, 0),
    )
    
    sort_dropdown = ft.Dropdown(
        value="cpu_percent",
        options=[
            ft.dropdown.Option("cpu_percent", "Mayor CPU"),
            ft.dropdown.Option("memory_percent", "Mayor RAM"),
            ft.dropdown.Option("pid", "PID"),
            ft.dropdown.Option("name", "Nombre"),
        ],
        width=150,
        bgcolor=colors["card"],
        border_color=colors["border"],
        color=colors["text"],
        height=40,
    )
    
    stats_text = ft.Text("Cargando estadísticas...", size=12, color=colors["text_secondary"])
    status_text = ft.Text("", size=12, color=colors["green"])
    is_loading = [False]  # Usar lista para poder modificar en closure

    def load_processes_data():
        """Carga los procesos (operación pesada - una sola iteración)"""
        c = get_crud_theme()
        process_manager.set_filter(search_field.value or "")
        process_manager.set_sort(sort_dropdown.value, reverse=(sort_dropdown.value != "name"))
        
        # Usar método optimizado que obtiene procesos y stats en una sola iteración
        processes, stats = process_manager.get_all_with_stats(limit=30)
        
        return processes, stats, c
    
    def update_table_with_data(processes, stats, c):
        """Actualiza la UI con los datos cargados"""
        stats_text.value = f"Total: {stats['total']} | Running: {stats['running']} | Threads: {stats['threads']}"
        
        processes_table.rows.clear()
        
        for proc in processes:
            cpu_color = c["red"] if proc.cpu_percent > 50 else (c["yellow"] if proc.cpu_percent > 20 else c["text"])
            mem_color = c["red"] if proc.memory_mb > 500 else (c["yellow"] if proc.memory_mb > 200 else c["text"])
            
            status_colors = {
                "running": c["green"],
                "sleeping": c["text_secondary"],
                "stopped": c["yellow"],
                "zombie": c["red"],
            }
            
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(proc.pid), color=c["text_secondary"], size=11)),
                    ft.DataCell(ft.Text(proc.name[:25], color=c["text"], size=11)),
                    ft.DataCell(ft.Text(f"{proc.cpu_percent:.1f}", color=cpu_color, size=11)),
                    ft.DataCell(ft.Text(f"{proc.memory_mb:.0f}", color=mem_color, size=11)),
                    ft.DataCell(ft.Text(proc.status[:8], color=status_colors.get(proc.status, c["text_secondary"]), size=11)),
                    ft.DataCell(
                        ft.IconButton(
                            ft.Icons.STOP_CIRCLE_OUTLINED,
                            icon_color=c["red"],
                            icon_size=18,
                            tooltip="Terminar proceso",
                            on_click=lambda e, pid=proc.pid, name=proc.name: kill_process(pid, name),
                        )
                    ),
                ],
            )
            processes_table.rows.append(row)
        
        # Cambiar de loader a tabla
        table_container.content = ft.Column([processes_table], scroll=ft.ScrollMode.AUTO)
        is_loading[0] = False
        page.update()

    def refresh_processes(show_loader=True):
        """Actualizar lista de procesos con loader"""
        if is_loading[0]:
            return  # Evitar múltiples cargas simultáneas
        
        is_loading[0] = True
        c = get_crud_theme()
        
        if show_loader:
            # Mostrar loader
            table_container.content = ft.Container(
                content=ft.Column([
                    ft.ProgressRing(width=40, height=40, stroke_width=3, color=c["blue"]),
                    ft.Text("Cargando procesos...", size=14, color=c["text_secondary"]),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                   alignment=ft.MainAxisAlignment.CENTER, spacing=15),
                height=200,
            )
            stats_text.value = "Cargando..."
            page.update()
        
        # Cargar datos y actualizar tabla
        try:
            processes, stats, c = load_processes_data()
            update_table_with_data(processes, stats, c)
        except Exception as e:
            status_text.value = f"❌ Error: {str(e)}"
            status_text.color = c["red"]
            table_container.content = ft.Text(f"Error al cargar procesos: {e}", color=c["red"])
            is_loading[0] = False
            page.update()
    
    def kill_process(pid: int, name: str):
        """Terminar proceso"""
        c = get_crud_theme()
        def confirm_kill(e):
            if process_manager.terminate(pid):
                status_text.value = f"✅ Proceso {name} (PID: {pid}) terminado"
                status_text.color = c["green"]
            else:
                status_text.value = f"❌ No se pudo terminar {name} (permisos insuficientes)"
                status_text.color = c["red"]
            dialog.open = False
            refresh_processes(show_loader=False)
        
        def cancel(e):
            dialog.open = False
            page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"¿Terminar proceso?", color=c["text"]),
            content=ft.Text(f"¿Estás seguro de terminar '{name}' (PID: {pid})?", color=c["text_secondary"]),
            actions=[
                ft.TextButton("Cancelar", on_click=cancel),
                ft.TextButton("Terminar", on_click=confirm_kill, style=ft.ButtonStyle(color=c["red"])),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=c["card"],
        )
        
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    def on_search_change(e):
        refresh_processes(show_loader=False)  # No mostrar loader en búsqueda
    
    def on_sort_change(e):
        refresh_processes(show_loader=False)  # No mostrar loader en ordenamiento
    
    search_field.on_change = on_search_change
    sort_dropdown.on_change = on_sort_change
    
    # Construir UI inmediatamente (sin esperar a que carguen los procesos)
    view = ft.Container(
        content=ft.Column([
            create_crud_header("Procesos", "Monitorea y gestiona procesos del sistema", ft.Icons.MEMORY,
                               on_theme_light, on_theme_dark, on_notifications),
            ft.Container(
                content=ft.Row([
                    search_field,
                    sort_dropdown,
                    ft.Container(expand=True),
                    ft.IconButton(
                        ft.Icons.REFRESH,
                        icon_color=colors["blue"],
                        tooltip="Actualizar",
                        on_click=lambda e: refresh_processes(),
                    ),
                ], spacing=15),
                padding=ft.Padding(0, 0, 0, 10),
            ),
            ft.Row([stats_text, ft.Container(expand=True), status_text]),
            ft.Container(height=10),
            table_container,
        ]),
        padding=25,
        expand=True,
        bgcolor=colors["bg"],
    )
    
    # Iniciar carga de procesos después de que la UI se haya renderizado
    def on_view_mounted(e=None):
        refresh_processes()
    
    # Usar page.run_task para cargar en background si está disponible
    try:
        page.run_task(lambda: on_view_mounted())
    except:
        # Fallback: cargar síncronamente
        on_view_mounted()
    
    return view


# ==================== VISTA DE HISTORIAL ====================

def build_history_view(history_manager, page: ft.Page,
                       on_theme_light=None, on_theme_dark=None, on_notifications=None) -> ft.Container:
    """Construir vista de historial de métricas"""
    colors = get_crud_theme()
    
    summary_cards = ft.Row(spacing=15, wrap=True)
    history_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Fecha/Hora", color=colors["text"], size=12)),
            ft.DataColumn(ft.Text("CPU %", color=colors["text"], size=12)),
            ft.DataColumn(ft.Text("Temp °C", color=colors["text"], size=12)),
            ft.DataColumn(ft.Text("RAM %", color=colors["text"], size=12)),
            ft.DataColumn(ft.Text("Disco %", color=colors["text"], size=12)),
        ],
        rows=[],
        border=ft.border.all(1, colors["border"]),
        border_radius=10,
        heading_row_color=colors["card"],
        data_row_color={"": colors["card"]},
        column_spacing=30,
    )
    
    hours_dropdown = ft.Dropdown(
        value="1",
        options=[
            ft.dropdown.Option("1", "Última hora"),
            ft.dropdown.Option("6", "Últimas 6 horas"),
            ft.dropdown.Option("24", "Últimas 24 horas"),
            ft.dropdown.Option("168", "Última semana"),
        ],
        width=180,
        bgcolor=colors["card"],
        border_color=colors["border"],
        color=colors["text"],
    )
    
    count_text = ft.Text("", size=12, color=colors["text_secondary"])
    status_text = ft.Text("", size=12, color=colors["green"])
    
    def create_summary_card(title: str, value: str, icon: str, color: str) -> ft.Container:
        c = get_crud_theme()
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, color=color, size=20),
                    ft.Text(title, size=12, color=c["text_secondary"]),
                ], spacing=5),
                ft.Text(value, size=24, weight=ft.FontWeight.BOLD, color=color),
            ], spacing=5),
            bgcolor=c["card"],
            border_radius=10,
            padding=15,
            width=140,
        )
    
    def refresh_history():
        """Actualizar historial"""
        c = get_crud_theme()
        hours = int(hours_dropdown.value)
        history = history_manager.get_history(hours=hours, limit=100)
        summary = history_manager.get_summary(hours=hours)
        count = history_manager.get_count()
        
        count_text.value = f"Total registros: {count}"
        
        # Actualizar resumen
        summary_cards.controls.clear()
        summary_cards.controls.extend([
            create_summary_card(
                "CPU Promedio", 
                f"{summary.get('avg_cpu', 0) or 0:.1f}%",
                ft.Icons.MEMORY, c["green"]
            ),
            create_summary_card(
                "CPU Máximo", 
                f"{summary.get('max_cpu', 0) or 0:.1f}%",
                ft.Icons.TRENDING_UP, c["red"]
            ),
            create_summary_card(
                "RAM Promedio", 
                f"{summary.get('avg_ram', 0) or 0:.1f}%",
                ft.Icons.STORAGE, c["blue"]
            ),
            create_summary_card(
                "Temp. Máxima", 
                f"{summary.get('max_cpu_temp', 0) or 0:.0f}°C",
                ft.Icons.THERMOSTAT, c["orange"]
            ),
        ])
        
        # Actualizar tabla
        history_table.rows.clear()
        for record in history[:50]:  # Mostrar últimos 50
            row = ft.DataRow(cells=[
                ft.DataCell(ft.Text(record.timestamp[:19], color=c["text_secondary"], size=11)),
                ft.DataCell(ft.Text(f"{record.cpu_usage or 0:.1f}", color=c["text"], size=11)),
                ft.DataCell(ft.Text(f"{record.cpu_temp or 0:.0f}", color=c["text"], size=11)),
                ft.DataCell(ft.Text(f"{record.ram_usage or 0:.1f}", color=c["text"], size=11)),
                ft.DataCell(ft.Text(f"{record.disk_usage or 0:.1f}", color=c["text"], size=11)),
            ])
            history_table.rows.append(row)
        
        page.update()
    
    def cleanup_history(e):
        """Limpiar historial antiguo"""
        c = get_crud_theme()
        deleted = history_manager.cleanup(days=7)
        status_text.value = f"🗑️ {deleted} registros antiguos eliminados"
        status_text.color = c["yellow"]
        refresh_history()
    
    def on_hours_change(e):
        refresh_history()
    
    hours_dropdown.on_change = on_hours_change
    
    # Inicializar
    refresh_history()
    
    return ft.Container(
        content=ft.Column([
            create_crud_header("Historial", "Registros históricos de métricas del sistema", ft.Icons.HISTORY,
                               on_theme_light, on_theme_dark, on_notifications),
            summary_cards,
            ft.Container(height=20),
            ft.Row([
                hours_dropdown,
                ft.Container(expand=True),
                count_text,
                ft.IconButton(ft.Icons.REFRESH, icon_color=colors["blue"], on_click=lambda e: refresh_history()),
                ft.IconButton(ft.Icons.DELETE_SWEEP, icon_color=colors["red"], tooltip="Limpiar antiguos", on_click=cleanup_history),
            ], spacing=15),
            status_text,
            ft.Container(height=10),
            ft.Container(
                content=ft.Column([history_table], scroll=ft.ScrollMode.AUTO),
                bgcolor=colors["card"],
                border_radius=15,
                padding=15,
                expand=True,
            ),
        ], scroll=ft.ScrollMode.AUTO),
        padding=25,
        expand=True,
        bgcolor=colors["bg"],
    )


# ==================== VISTA DE CONFIGURACIÓN ====================

def build_config_view(db, page: ft.Page,
                      on_theme_light=None, on_theme_dark=None, on_notifications=None) -> ft.Container:
    """Construir vista de configuración"""
    colors = get_crud_theme()
    
    config = db.get_all_config()
    status_text = ft.Text("", size=12, color=colors["green"])
    
    # Obtener tema actual del ThemeManager (sincronizado con botones del header)
    current_theme = ThemeManager.get_theme()
    current_theme_name = current_theme.get("name", "dark")
    
    # Campos de configuración
    theme_dropdown = ft.Dropdown(
        value=current_theme_name,  # Usar tema actual del ThemeManager
        options=[
            ft.dropdown.Option("dark", "Oscuro"),
            ft.dropdown.Option("light", "Claro"),
        ],
        label="Tema",
        width=200,
        bgcolor=colors["card"],
        border_color=colors["border"],
        color=colors["text"],
    )
    
    interval_dropdown = ft.Dropdown(
        value=config.get('update_interval', '1000'),
        options=[
            ft.dropdown.Option("500", "0.5 segundos"),
            ft.dropdown.Option("1000", "1 segundo"),
            ft.dropdown.Option("2000", "2 segundos"),
            ft.dropdown.Option("5000", "5 segundos"),
        ],
        label="Intervalo de actualización",
        width=200,
        bgcolor=colors["card"],
        border_color=colors["border"],
        color=colors["text"],
    )
    
    retention_dropdown = ft.Dropdown(
        value=config.get('history_retention_days', '7'),
        options=[
            ft.dropdown.Option("1", "1 día"),
            ft.dropdown.Option("7", "7 días"),
            ft.dropdown.Option("30", "30 días"),
            ft.dropdown.Option("90", "90 días"),
        ],
        label="Retención de historial",
        width=200,
        bgcolor=colors["card"],
        border_color=colors["border"],
        color=colors["text"],
    )
    
    notifications_switch = ft.Switch(
        value=config.get('enable_notifications', 'true') == 'true',
        label="Notificaciones",
        active_color=colors["green"],
    )
    
    sounds_switch = ft.Switch(
        value=config.get('enable_sounds', 'true') == 'true',
        label="Sonidos",
        active_color=colors["green"],
    )
    
    def save_config(e):
        """Guardar configuración"""
        c = get_crud_theme()
        db.set_config('theme', theme_dropdown.value)
        db.set_config('update_interval', interval_dropdown.value)
        db.set_config('history_retention_days', retention_dropdown.value)
        db.set_config('enable_notifications', 'true' if notifications_switch.value else 'false')
        db.set_config('enable_sounds', 'true' if sounds_switch.value else 'false')
        
        # Aplicar tema inmediatamente si cambió
        if theme_dropdown.value == 'light' and on_theme_light:
            on_theme_light(None)
        elif theme_dropdown.value == 'dark' and on_theme_dark:
            on_theme_dark(None)
        
        status_text.value = "✅ Configuración guardada"
        status_text.color = c["green"]
        page.update()
    
    def reset_config(e):
        """Resetear configuración"""
        c = get_crud_theme()
        db.reset_config()
        config = db.get_all_config()
        
        theme_dropdown.value = config.get('theme', 'dark')
        interval_dropdown.value = config.get('update_interval', '1000')
        retention_dropdown.value = config.get('history_retention_days', '7')
        notifications_switch.value = config.get('enable_notifications', 'true') == 'true'
        sounds_switch.value = config.get('enable_sounds', 'true') == 'true'
        
        # Aplicar tema por defecto (dark)
        if on_theme_dark:
            on_theme_dark(None)
        
        status_text.value = "🔄 Configuración reseteada a valores por defecto"
        status_text.color = c["yellow"]
        page.update()
    
    return ft.Container(
        content=ft.Column([
            create_crud_header("Configuración", "Personaliza tu experiencia", ft.Icons.SETTINGS,
                               on_theme_light, on_theme_dark, on_notifications),
            
            # Sección Apariencia
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.PALETTE, color=colors["blue"], size=20),
                        ft.Text("Apariencia", size=16, weight=ft.FontWeight.W_500, color=colors["text"]),
                    ]),
                    ft.Container(height=15),
                    theme_dropdown,
                ]),
                bgcolor=colors["card"],
                border_radius=15,
                padding=20,
            ),
            
            ft.Container(height=15),
            
            # Sección Rendimiento
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.SPEED, color=colors["green"], size=20),
                        ft.Text("Rendimiento", size=16, weight=ft.FontWeight.W_500, color=colors["text"]),
                    ]),
                    ft.Container(height=15),
                    ft.Row([interval_dropdown, retention_dropdown], spacing=20, wrap=True),
                ]),
                bgcolor=colors["card"],
                border_radius=15,
                padding=20,
            ),
            
            ft.Container(height=15),
            
            # Sección Notificaciones
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.NOTIFICATIONS, color=colors["orange"], size=20),
                        ft.Text("Notificaciones", size=16, weight=ft.FontWeight.W_500, color=colors["text"]),
                    ]),
                    ft.Container(height=15),
                    ft.Row([notifications_switch, sounds_switch], spacing=30),
                ]),
                bgcolor=colors["card"],
                border_radius=15,
                padding=20,
            ),
            
            ft.Container(height=25),
            
            # Botones
            ft.Row([
                ft.ElevatedButton(
                    "Guardar Cambios",
                    icon=ft.Icons.SAVE,
                    bgcolor=colors["green"],
                    color=colors["bg"],
                    on_click=save_config,
                ),
                ft.OutlinedButton(
                    "Resetear",
                    icon=ft.Icons.RESTART_ALT,
                    style=ft.ButtonStyle(color=colors["yellow"]),
                    on_click=reset_config,
                ),
                status_text,
            ], spacing=15),
        ], scroll=ft.ScrollMode.AUTO),
        padding=25,
        expand=True,
        bgcolor=colors["bg"],
    )
