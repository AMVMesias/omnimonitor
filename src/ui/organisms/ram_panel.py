# ==============================================
# ORGANISM: RAM Panel
# ==============================================
# Panel completo de RAM combinando múltiples moléculas

import flet as ft
from ..tokens import (
    CARD_BG, TEXT_WHITE, GREEN_PRIMARY, BORDER_DARK,
    BORDER_RADIUS_LG, SPACING_LG
)
from ..atoms.icon import create_icon
from ..atoms.button import create_detail_button


def create_ram_card(
    used_text: ft.Text,
    available_text: ft.Text,
    progress_bar: ft.ProgressBar,
    history_chart: ft.Container,
    on_details_click=None
) -> ft.Container:
    """
    Crea la tarjeta completa de RAM.
    
    Combina: icon + text + progress_bar + chart (molecules) + detail_button
    
    Args:
        used_text: Texto con RAM usada
        available_text: Texto con RAM disponible
        progress_bar: Barra de progreso
        history_chart: Gráfico de historial
        on_details_click: Callback para ver detalles
    
    Returns:
        ft.Container con el panel completo de RAM
    """
    return ft.Container(
        content=ft.Column([
            # Header
            ft.Row([
                create_icon(ft.Icons.MEMORY_OUTLINED, GREEN_PRIMARY, 20),
                ft.Text("RAM: DDR4", size=14, weight=ft.FontWeight.W_500, color=TEXT_WHITE),
                ft.Container(expand=True),
                used_text,
            ], spacing=10),
            
            ft.Container(height=20),
            
            # Progress bar con info
            ft.Column([
                available_text,
                ft.Container(height=8),
                progress_bar,
            ]),
            
            ft.Container(height=15),
            
            # Gráfico de historial
            history_chart,
            
            ft.Container(expand=True),
            
            # Footer con botón detalles
            ft.Row([
                ft.Container(expand=True),
                create_detail_button(on_details_click),
            ]),
        ]),
        bgcolor=CARD_BG,
        border_radius=BORDER_RADIUS_LG,
        padding=SPACING_LG + 5,
        border=ft.border.all(1, BORDER_DARK),
    )
