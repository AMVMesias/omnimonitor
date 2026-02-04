# ==============================================
# ORGANISM: Navigation Components
# ==============================================
# Componentes de navegación: sidebar y header

import flet as ft
from ..tokens import (
    SIDEBAR_BG, TEXT_WHITE, TEXT_GRAY, BLUE_PRIMARY,
    BORDER_DARK
)
from ..atoms.icon import create_icon_with_bg


def create_sidebar(on_change_callback=None) -> ft.Container:
    """
    Crea la barra lateral de navegación.
    
    Combina: logo + nav_items + destinations
    
    Args:
        on_change_callback: Callback al cambiar de sección
    
    Returns:
        ft.Container con el sidebar completo
    """
    nav_items = [
        {"icon": ft.Icons.HOME_OUTLINED, "icon_selected": ft.Icons.HOME, "label": "Resumen"},
        {"icon": ft.Icons.MEMORY_OUTLINED, "icon_selected": ft.Icons.MEMORY, "label": "CPU"},
        {"icon": ft.Icons.STORAGE_OUTLINED, "icon_selected": ft.Icons.STORAGE, "label": "RAM"},
        {"icon": ft.Icons.DISC_FULL_OUTLINED, "icon_selected": ft.Icons.DISC_FULL, "label": "Disco"},
        {"icon": ft.Icons.WIFI_OUTLINED, "icon_selected": ft.Icons.WIFI, "label": "Red"},
        {"icon": ft.Icons.SETTINGS_OUTLINED, "icon_selected": ft.Icons.SETTINGS, "label": "Ajustes"},
    ]
    
    # Logo del app
    logo = ft.Container(
        content=ft.Column([
            ft.Row([
                create_icon_with_bg(ft.Icons.RADAR, BLUE_PRIMARY, 28, 40),
                ft.Text("OmniMonitor", size=18, weight=ft.FontWeight.BOLD, color=TEXT_WHITE),
            ], spacing=10, alignment=ft.MainAxisAlignment.START),
        ]),
        padding=ft.Padding(left=15, top=15, bottom=30, right=0),
    )
    
    nav_rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=80,
        min_extended_width=180,
        extended=True,
        leading=logo,
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
        border=ft.border.only(right=ft.BorderSide(1, BORDER_DARK)),
    )


def create_header(title: str) -> ft.Container:
    """
    Crea el encabezado con título e iconos de acción.
    
    Combina: title + action_buttons
    
    Args:
        title: Título de la sección
    
    Returns:
        ft.Container con el header
    """
    return ft.Container(
        content=ft.Row([
            ft.Text(title, size=26, weight=ft.FontWeight.BOLD, color=TEXT_WHITE),
            ft.Container(expand=True),
            ft.Row([
                ft.IconButton(
                    icon=ft.Icons.LIGHT_MODE_OUTLINED,
                    icon_color=TEXT_GRAY,
                    icon_size=20,
                    tooltip="Cambiar tema",
                ),
                ft.IconButton(
                    icon=ft.Icons.DARK_MODE_OUTLINED,
                    icon_color=TEXT_GRAY,
                    icon_size=20,
                    tooltip="Modo oscuro",
                ),
                ft.IconButton(
                    icon=ft.Icons.NOTIFICATIONS_OUTLINED,
                    icon_color=TEXT_GRAY,
                    icon_size=20,
                    tooltip="Notificaciones",
                ),
            ], spacing=0),
        ]),
    )
