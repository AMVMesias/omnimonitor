# ==============================================
# ORGANISM: GPU Panel
# ==============================================
# Panel completo de GPU combinando múltiples moléculas

import flet as ft
from ..tokens import (
    CARD_BG, TEXT_GRAY, ORANGE_PRIMARY, YELLOW_PRIMARY,
    BORDER_DARK, BORDER_RADIUS_LG, SPACING_LG
)
from ..atoms.icon import create_icon
from ..atoms.button import create_detail_button


def create_gpu_card(
    gpu_name: ft.Text,
    progress_ring: ft.Container,
    percent_text: ft.Text,
    temp_text: ft.Text,
    on_details_click=None
) -> ft.Container:
    """
    Crea la tarjeta completa de GPU.
    
    Combina: icon + text + progress_ring + temp_info + detail_button
    
    Args:
        gpu_name: Texto con nombre de la GPU
        progress_ring: Anillo de progreso
        percent_text: Texto con porcentaje de uso
        temp_text: Texto con temperatura
        on_details_click: Callback para ver detalles
    
    Returns:
        ft.Container con el panel completo de GPU
    """
    return ft.Container(
        content=ft.Column([
            # Header
            ft.Row([
                create_icon(ft.Icons.VIDEOGAME_ASSET, ORANGE_PRIMARY, 20),
                gpu_name,
            ], spacing=10),
            
            ft.Container(height=10),
            
            # Progress ring con porcentaje
            ft.Row([
                ft.Stack([
                    progress_ring,
                    ft.Container(
                        content=ft.Column([
                            percent_text,
                            ft.Text("Usage", size=11, color=TEXT_GRAY),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                        alignment=ft.alignment.center,
                        width=100,
                        height=100,
                    ),
                ]),
            ], alignment=ft.MainAxisAlignment.CENTER),
            
            ft.Container(height=10),
            
            # Temperatura con warning icon
            ft.Row([
                create_icon(ft.Icons.WARNING_AMBER, YELLOW_PRIMARY, 16),
                temp_text,
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
            
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
