import flet as ft

# ============ COLORES DEL TEMA OSCURO (DEFAULT/FALLBACK) ============
DARK_BG = "#0D1117"           # Fondo principal oscuro
CARD_BG = "#161B22"           # Fondo de tarjetas
SIDEBAR_BG = "#0D1117"        # Fondo del sidebar
SIDEBAR_HOVER = "#1A1F26"     # Hover en sidebar

# Colores de acento
GREEN_PRIMARY = "#4ADE80"     # Verde principal (CPU normal, éxito)
BLUE_PRIMARY = "#60A5FA"      # Azul principal (enlaces, info)
ORANGE_PRIMARY = "#FB923C"    # Naranja (GPU, advertencias)
RED_PRIMARY = "#F87171"       # Rojo (errores, temperatura alta)
YELLOW_PRIMARY = "#FBBF24"    # Amarillo (advertencias medias)
PURPLE_PRIMARY = "#A78BFA"    # Púrpura (acentos)

# Colores de texto
TEXT_WHITE = "#FFFFFF"
TEXT_GRAY = "#9CA3AF"
TEXT_DARK_GRAY = "#6B7280"


def get_theme_colors():
    """Obtener colores del tema actual dinámicamente"""
    try:
        from .theme_manager import ThemeManager
        theme = ThemeManager.get_theme()
        return {
            "bg": theme["bg_primary"],
            "card": theme["bg_card"],
            "sidebar": theme["bg_sidebar"],
            "text": theme["text_primary"],
            "text_secondary": theme["text_secondary"],
            "text_muted": theme["text_muted"],
            "border": theme["border_primary"],
            "green": theme["accent_green"],
            "blue": theme["accent_blue"],
            "orange": theme["accent_orange"],
            "red": theme["accent_red"],
            "yellow": theme["accent_yellow"],
        }
    except:
        # Fallback a colores oscuros por defecto
        return {
            "bg": DARK_BG,
            "card": CARD_BG,
            "sidebar": SIDEBAR_BG,
            "text": TEXT_WHITE,
            "text_secondary": TEXT_GRAY,
            "text_muted": TEXT_DARK_GRAY,
            "border": "#1E2130",
            "green": GREEN_PRIMARY,
            "blue": BLUE_PRIMARY,
            "orange": ORANGE_PRIMARY,
            "red": RED_PRIMARY,
            "yellow": YELLOW_PRIMARY,
        }


def create_circular_progress(value: float, color: str, size: int = 130) -> ft.Container:
    """Crea un indicador de progreso circular con porcentaje en el centro"""
    return ft.Container(
        content=ft.Stack([
            ft.ProgressRing(
                value=value,
                width=size,
                height=size,
                stroke_width=10,
                color=color,
                bgcolor="#2A2D3A",
            ),
        ]),
        width=size,
        height=size,
        alignment=ft.alignment.Alignment(0, 0),
    )


def create_sidebar(on_change_callback) -> ft.Container:
    """Crea la barra lateral de navegación estilo OmniMonitor"""
    
    nav_items = [
        {"icon": ft.Icons.HOME_OUTLINED, "icon_selected": ft.Icons.HOME, "label": "Resumen"},
        {"icon": ft.Icons.MEMORY_OUTLINED, "icon_selected": ft.Icons.MEMORY, "label": "CPU"},
        {"icon": ft.Icons.STORAGE_OUTLINED, "icon_selected": ft.Icons.STORAGE, "label": "RAM"},
        {"icon": ft.Icons.DISC_FULL_OUTLINED, "icon_selected": ft.Icons.DISC_FULL, "label": "Disco"},
        {"icon": ft.Icons.WIFI_OUTLINED, "icon_selected": ft.Icons.WIFI, "label": "Red"},
        {"icon": ft.Icons.SETTINGS_OUTLINED, "icon_selected": ft.Icons.SETTINGS, "label": "Ajustes"},
    ]
    
    nav_rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=80,
        min_extended_width=180,
        extended=True,
        leading=ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.RADAR, color=BLUE_PRIMARY, size=28),
                        width=40,
                        height=40,
                        border_radius=20,
                        bgcolor=ft.Colors.with_opacity(0.1, BLUE_PRIMARY),
                        alignment=ft.alignment.Alignment(0, 0),
                    ),
                    ft.Text("OmniMonitor", size=18, weight=ft.FontWeight.BOLD, color=TEXT_WHITE),
                ], spacing=10, alignment=ft.MainAxisAlignment.START),
            ]),
            padding=ft.Padding(left=15, top=15, bottom=30, right=0),
        ),
        destinations=[
            ft.NavigationRailDestination(
                icon=item["icon"],
                selected_icon=item["icon_selected"],
                label=item["label"],
            ) for item in nav_items
        ],
        on_change=on_change_callback,
        bgcolor=SIDEBAR_BG,
        indicator_color=ft.Colors.with_opacity(0.1, BLUE_PRIMARY),
    )
    
    return ft.Container(
        content=nav_rail,
        width=180,
        bgcolor=SIDEBAR_BG,
        border=ft.border.only(right=ft.BorderSide(1, "#1E2130")),
    )


def create_header(title: str, on_theme_toggle=None, on_dark_mode=None, on_notifications=None) -> ft.Container:
    """Crea el encabezado con título e iconos de acción
    
    Args:
        title: Título del encabezado
        on_theme_toggle: Callback para cambiar tema (modo claro/oscuro)
        on_dark_mode: Callback para activar modo oscuro
        on_notifications: Callback para ver/gestionar notificaciones
    """
    colors = get_theme_colors()
    return ft.Container(
        content=ft.Row([
            ft.Text(title, size=26, weight=ft.FontWeight.BOLD, color=colors["text"]),
            ft.Container(expand=True),
            ft.Row([
                ft.IconButton(
                    icon=ft.Icons.LIGHT_MODE_OUTLINED,
                    icon_color=colors["text_secondary"],
                    icon_size=20,
                    tooltip="Modo claro",
                    on_click=on_theme_toggle,
                ),
                ft.IconButton(
                    icon=ft.Icons.DARK_MODE_OUTLINED,
                    icon_color=colors["text_secondary"],
                    icon_size=20,
                    tooltip="Modo oscuro",
                    on_click=on_dark_mode,
                ),
                ft.IconButton(
                    icon=ft.Icons.NOTIFICATIONS_OUTLINED,
                    icon_color=colors["text_secondary"],
                    icon_size=20,
                    tooltip="Ver alertas",
                    on_click=on_notifications,
                ),
            ], spacing=0),
        ]),
    )


def create_detail_button(on_click) -> ft.Container:
    """Crea un botón 'Ver Detalles' estilizado"""
    colors = get_theme_colors()
    return ft.Container(
        content=ft.Row([
            ft.Text("Ver Detalles", size=12, color=colors["text_secondary"]),
            ft.Icon(ft.Icons.CHEVRON_RIGHT, color=colors["text_secondary"], size=16),
        ], spacing=2),
        on_click=on_click,
        ink=True,
        padding=ft.Padding(left=10, right=10, top=5, bottom=5),
        border_radius=5,
    )



def create_cpu_card(cpu_name: ft.Text, progress_ring: ft.Container, 
                    percent_text: ft.Text, temp_text: ft.Text, 
                    speed_text: ft.Text, on_details_click, 
                    expanded_content: ft.Control = None) -> ft.Container:
    """Crea la tarjeta de CPU con diseño circular y detalles expandibles"""
    colors = get_theme_colors()
    
    details_container = ft.Container(
        content=expanded_content,
        visible=False,
        animate_opacity=300,
    ) if expanded_content else None

    def toggle_details(e):
        print(f"DEBUG: Toggle details clicked. details_container={details_container}")
        if details_container:
            details_container.visible = not details_container.visible
            try:
                # Actualizar icono y texto
                row = e.control.content
                text = row.controls[0]
                icon = row.controls[1]
                
                text.value = "Ocultar Detalles" if details_container.visible else "Ver Detalles"
                icon.name = ft.Icons.KEYBOARD_ARROW_UP if details_container.visible else ft.Icons.CHEVRON_RIGHT
                
                e.control.update()
            except Exception as ex:
                print(f"DEBUG: Error updating icon/text: {ex}")
            
            details_container.update()
            if e.page: e.page.update()
            
    action = toggle_details if expanded_content else on_details_click

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.MEMORY, color=colors["green"], size=20),
                cpu_name,
            ], spacing=10),
            ft.Container(height=15),
            ft.Row([
                ft.Stack([
                    progress_ring,
                    ft.Container(
                        content=ft.Column([
                            percent_text,
                            ft.Text("Usage", size=12, color=colors["text_secondary"]),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                        alignment=ft.alignment.Alignment(0, 0),
                        width=130,
                        height=130,
                    ),
                ]),
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=15),
            ft.Row([
                temp_text,
                ft.Container(width=10),
                ft.Text("|", color=colors["text_muted"]),
                ft.Container(width=10),
                speed_text,
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=10),
            details_container if details_container else ft.Container(),
            ft.Container(expand=True),
            ft.Row([
                ft.Container(expand=True),
                create_detail_button(action),
            ]),
        ]),
        bgcolor=colors["card"],
        border_radius=15,
        padding=20,
        border=ft.border.all(1, colors["border"]),
        animate_size=300,
    )


def create_ram_card(used_text: ft.Text, available_text: ft.Text,
                    progress_bar: ft.ProgressBar, history_chart: ft.Container,
                    on_details_click, expanded_content: ft.Control = None) -> ft.Container:
    """Crea la tarjeta de RAM con barra de progreso y detalles expandibles"""
    colors = get_theme_colors()
    
    details_container = ft.Container(
        content=expanded_content,
        visible=False,
        animate_opacity=300,
    ) if expanded_content else None

    def toggle_details(e):
        print(f"DEBUG: RAM Toggle clicked. details_container={details_container}")
        if details_container:
            details_container.visible = not details_container.visible
            try:
                # Actualizar icono y texto
                row = e.control.content
                text = row.controls[0]
                icon = row.controls[1]
                
                text.value = "Ocultar Detalles" if details_container.visible else "Ver Detalles"
                icon.name = ft.Icons.KEYBOARD_ARROW_UP if details_container.visible else ft.Icons.CHEVRON_RIGHT
                
                e.control.update()
            except Exception as ex:
                print(f"DEBUG: Error updating icon/text: {ex}")
            
            details_container.update()
            e.control.update()
            if e.page: e.page.update()
            
    action = toggle_details if expanded_content else on_details_click

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.MEMORY_OUTLINED, color=colors["green"], size=20),
                ft.Text("RAM: DDR4", size=14, weight=ft.FontWeight.W_500, color=colors["text"]),
                ft.Container(expand=True),
                used_text,
            ], spacing=10),
            ft.Container(height=20),
            ft.Column([
                available_text,
                ft.Container(height=8),
                progress_bar,
            ]),
            ft.Container(height=15),
            history_chart,
            ft.Container(height=10),
            details_container if details_container else ft.Container(),
            ft.Container(expand=True),
            ft.Row([
                ft.Container(expand=True),
                create_detail_button(action),
            ]),
        ]),
        bgcolor=colors["card"],
        border_radius=15,
        padding=20,
        border=ft.border.all(1, colors["border"]),
        animate_size=300,
    )


def create_gpu_card(gpu_name: ft.Text, progress_ring: ft.Container,
                    percent_text: ft.Text, temp_text: ft.Text,
                    on_details_click) -> ft.Container:
    """Crea la tarjeta de GPU/Temperatura"""
    colors = get_theme_colors()
    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.VIDEOGAME_ASSET, color=colors["orange"], size=20),
                gpu_name,
            ], spacing=10),
            ft.Container(height=10),
            ft.Row([
                ft.Stack([
                    progress_ring,
                    ft.Container(
                        content=ft.Column([
                            percent_text,
                            ft.Text("Usage", size=11, color=colors["text_secondary"]),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                        alignment=ft.alignment.Alignment(0, 0),
                        width=100,
                        height=100,
                    ),
                ]),
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=10),
            ft.Row([
                ft.Icon(ft.Icons.WARNING_AMBER, color=colors["yellow"], size=16),
                temp_text,
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
            ft.Container(expand=True),
            ft.Row([
                ft.Container(expand=True),
                create_detail_button(on_details_click),
            ]),
        ]),
        bgcolor=colors["card"],
        border_radius=15,
        padding=20,
        border=ft.border.all(1, colors["border"]),
    )


def create_disk_card(disk_name: ft.Text, used_text: ft.Text,
                     speed_text: ft.Text, progress_bar: ft.ProgressBar,
                     on_details_click, expanded_content: ft.Control = None) -> ft.Container:
    """Crea la tarjeta de disco con barra de progreso y detalles expandibles"""
    colors = get_theme_colors()
    
    details_container = ft.Container(
        content=expanded_content,
        visible=False,
        animate_opacity=300,
    ) if expanded_content else None

    def toggle_details(e):
        print(f"DEBUG: Disk Toggle clicked. details_container={details_container}")
        if details_container:
            details_container.visible = not details_container.visible
            try:
                # Actualizar icono y texto
                row = e.control.content
                text = row.controls[0]
                icon = row.controls[1]
                
                text.value = "Ocultar Detalles" if details_container.visible else "Ver Detalles"
                icon.name = ft.Icons.KEYBOARD_ARROW_UP if details_container.visible else ft.Icons.CHEVRON_RIGHT
                
                e.control.update()
            except Exception as ex:
                print(f"DEBUG: Error updating icon/text: {ex}")
            
            details_container.update()
            e.control.update()
            if e.page: e.page.update()
            
    action = toggle_details if expanded_content else on_details_click

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.STORAGE, color=colors["blue"], size=20),
                disk_name,
            ], spacing=10),
            ft.Container(height=15),
            ft.Row([
                ft.Column([
                    ft.Container(
                        content=progress_bar,
                        width=280,
                    ),
                    ft.Container(height=8),
                    used_text,
                ], spacing=0),
            ]),
            ft.Container(height=10),
            speed_text,
            ft.Container(height=10),
            details_container if details_container else ft.Container(),
            ft.Container(expand=True),
            ft.Row([
                ft.Container(expand=True),
                create_detail_button(action),
            ]),
        ]),
        bgcolor=colors["card"],
        border_radius=15,
        padding=20,
        border=ft.border.all(1, colors["border"]),
        animate_size=300,
    )


def create_network_chart_card(chart_container: ft.Container, 
                               on_details_click) -> ft.Container:
    """Crea la tarjeta grande del historial de red"""
    colors = get_theme_colors()
    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.WIFI, color=colors["blue"], size=20),
                ft.Text("Historial de Red (Última Hora)", size=14, 
                       weight=ft.FontWeight.W_500, color=colors["text"]),
            ], spacing=10),
            ft.Container(height=10),
            chart_container,
        ]),
        bgcolor=colors["card"],
        border_radius=15,
        padding=20,
        border=ft.border.all(1, colors["border"]),
    )


def create_info_row(label: str, value: str, icon: str = None, 
                    value_color: str = TEXT_WHITE) -> ft.Container:
    """Crea una fila de información estilizada"""
    row_content = [
        ft.Text(label, size=13, color=TEXT_GRAY, width=120),
        ft.Text(value, size=13, color=value_color, weight=ft.FontWeight.W_500),
    ]
    
    if icon:
        row_content.insert(0, ft.Icon(icon, color=value_color, size=16))
    
    return ft.Container(
        content=ft.Row(row_content, spacing=10),
        padding=ft.Padding(left=0, right=0, top=5, bottom=5),
    )


def create_stat_box(title: str, value: str, icon: str, 
                    color: str = BLUE_PRIMARY) -> ft.Container:
    """Crea una caja de estadística compacta"""
    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(icon, color=color, size=18),
                ft.Text(title, size=11, color=TEXT_GRAY),
            ], spacing=5),
            ft.Text(value, size=20, weight=ft.FontWeight.BOLD, color=TEXT_WHITE),
        ], spacing=5),
        bgcolor=ft.Colors.with_opacity(0.5, CARD_BG),
        border_radius=10,
        padding=15,
        border=ft.border.all(1, ft.Colors.with_opacity(0.3, color)),
    )
