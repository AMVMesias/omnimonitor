# ==============================================
# ATOM: Icon Components
# ==============================================
# Componentes de iconos atómicos reutilizables

import flet as ft
from ..tokens import BLUE_PRIMARY, BORDER_RADIUS_XL


def create_icon(
    icon: str,
    color: str = BLUE_PRIMARY,
    size: int = 20
) -> ft.Icon:
    """
    Crea un icono simple.
    
    Args:
        icon: Icono de ft.Icons.*
        color: Color del icono
        size: Tamaño del icono
    
    Returns:
        ft.Icon configurado
    """
    return ft.Icon(icon, color=color, size=size)


def create_icon_with_bg(
    icon: str,
    color: str = BLUE_PRIMARY,
    icon_size: int = 28,
    container_size: int = 40
) -> ft.Container:
    """
    Crea un icono con fondo circular.
    
    Args:
        icon: Icono de ft.Icons.*
        color: Color del icono y fondo
        icon_size: Tamaño del icono
        container_size: Tamaño del contenedor
    
    Returns:
        ft.Container con el icono centrado
    """
    return ft.Container(
        content=ft.Icon(icon, color=color, size=icon_size),
        width=container_size,
        height=container_size,
        border_radius=container_size // 2,
        bgcolor=ft.Colors.with_opacity(0.1, color),
        alignment=ft.alignment.center,
    )
