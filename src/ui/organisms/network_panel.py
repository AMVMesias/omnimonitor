# ==============================================
# ORGANISM: Network Panel
# ==============================================
# Panel completo de Red con gráfico grande

import flet as ft
from ..tokens import (
    CARD_BG, TEXT_WHITE, BLUE_PRIMARY, BORDER_DARK,
    BORDER_RADIUS_LG, SPACING_LG
)
from ..atoms.icon import create_icon


def create_network_chart_card(
    chart_container: ft.Container,
    on_details_click=None
) -> ft.Container:
    """
    Crea la tarjeta grande del historial de red.
    
    Combina: icon + title + chart_area
    
    Args:
        chart_container: Contenedor con el gráfico de red
        on_details_click: Callback para ver detalles (opcional)
    
    Returns:
        ft.Container con el panel completo de red
    """
    return ft.Container(
        content=ft.Column([
            # Header
            ft.Row([
                create_icon(ft.Icons.WIFI, BLUE_PRIMARY, 20),
                ft.Text(
                    "Historial de Red (Última Hora)",
                    size=14,
                    weight=ft.FontWeight.W_500,
                    color=TEXT_WHITE
                ),
            ], spacing=10),
            
            ft.Container(height=10),
            
            # Gráfico
            chart_container,
        ]),
        bgcolor=CARD_BG,
        border_radius=BORDER_RADIUS_LG,
        padding=SPACING_LG + 5,
        border=ft.border.all(1, BORDER_DARK),
    )
