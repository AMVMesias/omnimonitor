# ==============================================
# ATOM: Button Components
# ==============================================
# Botones atómicos reutilizables en toda la aplicación

import flet as ft
from ..tokens import (
    TEXT_WHITE, TEXT_GRAY, BLUE_PRIMARY, GREEN_PRIMARY,
    RED_PRIMARY, BORDER_RADIUS_SM, BORDER_RADIUS_MD
)


def create_button(
    text: str,
    on_click=None,
    icon=None,
    variant: str = "primary",
    disabled: bool = False
) -> ft.ElevatedButton:
    """
    Crea un botón estilizado.
    
    Args:
        text: Texto del botón
        on_click: Callback al hacer clic
        icon: Icono opcional (ft.Icons.*)
        variant: "primary", "secondary", "danger"
        disabled: Si está deshabilitado
    
    Returns:
        ft.ElevatedButton configurado
    """
    colors = {
        "primary": BLUE_PRIMARY,
        "secondary": TEXT_GRAY,
        "danger": RED_PRIMARY,
        "success": GREEN_PRIMARY,
    }
    
    return ft.ElevatedButton(
        text=text,
        icon=icon,
        on_click=on_click,
        disabled=disabled,
        bgcolor=colors.get(variant, BLUE_PRIMARY),
        color=TEXT_WHITE,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS_MD),
        ),
    )


def create_icon_button(
    icon: str,
    on_click=None,
    tooltip: str = None,
    color: str = TEXT_GRAY,
    size: int = 20
) -> ft.IconButton:
    """
    Crea un botón de solo icono.
    
    Args:
        icon: Icono de ft.Icons.*
        on_click: Callback al hacer clic
        tooltip: Texto de ayuda al hover
        color: Color del icono
        size: Tamaño del icono
    
    Returns:
        ft.IconButton configurado
    """
    return ft.IconButton(
        icon=icon,
        on_click=on_click,
        tooltip=tooltip,
        icon_color=color,
        icon_size=size,
    )


def create_detail_button(on_click=None) -> ft.Container:
    """
    Crea un botón 'Ver Detalles' estilizado.
    
    Args:
        on_click: Callback al hacer clic
    
    Returns:
        ft.Container con el botón
    """
    return ft.Container(
        content=ft.Row([
            ft.Text("Ver Detalles", size=12, color=TEXT_GRAY),
            ft.Icon(ft.Icons.CHEVRON_RIGHT, color=TEXT_GRAY, size=16),
        ], spacing=2),
        on_click=on_click,
        ink=True,
        padding=ft.Padding(left=10, right=10, top=5, bottom=5),
        border_radius=BORDER_RADIUS_SM,
    )
