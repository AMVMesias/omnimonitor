# ==============================================
# MOLECULE: Stat Box Component
# ==============================================
# Caja de estadística compacta con icono, título y valor

import flet as ft
from ..tokens import (
    CARD_BG, TEXT_WHITE, TEXT_GRAY, BLUE_PRIMARY,
    BORDER_RADIUS_MD, SPACING_SM
)
from ..atoms.icon import create_icon


def create_stat_box(
    title: str,
    value: str,
    icon: str,
    color: str = BLUE_PRIMARY
) -> ft.Container:
    """
    Crea una caja de estadística compacta.
    
    Combina: icon (atom) + title (atom) + value (atom)
    
    Args:
        title: Título de la estadística
        value: Valor a mostrar
        icon: Icono de ft.Icons.*
        color: Color del tema
    
    Returns:
        ft.Container con la caja de estadística
    """
    return ft.Container(
        content=ft.Column([
            ft.Row([
                create_icon(icon, color, 18),
                ft.Text(title, size=11, color=TEXT_GRAY),
            ], spacing=SPACING_SM),
            ft.Text(value, size=20, weight=ft.FontWeight.BOLD, color=TEXT_WHITE),
        ], spacing=SPACING_SM),
        bgcolor=ft.Colors.with_opacity(0.5, CARD_BG),
        border_radius=BORDER_RADIUS_MD,
        padding=15,
        border=ft.border.all(1, ft.Colors.with_opacity(0.3, color)),
    )
