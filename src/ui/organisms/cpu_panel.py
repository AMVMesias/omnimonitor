# ==============================================
# ORGANISM: CPU Panel
# ==============================================
# Panel completo de CPU combinando múltiples moléculas

import flet as ft
from ..tokens import (
    CARD_BG, TEXT_WHITE, TEXT_GRAY, TEXT_DARK_GRAY,
    GREEN_PRIMARY, BORDER_DARK, BORDER_RADIUS_LG, SPACING_LG
)
from ..atoms.icon import create_icon
from ..atoms.progress import create_progress_ring
from ..atoms.button import create_detail_button


def create_cpu_card(
    cpu_name: ft.Text,
    progress_ring: ft.Container,
    percent_text: ft.Text,
    temp_text: ft.Text,
    speed_text: ft.Text,
    on_details_click=None
) -> ft.Container:
    """
    Crea la tarjeta completa de CPU.
    
    Combina: icon (atom) + text (atom) + progress_ring (atom) + 
             stat_rows (molecules) + detail_button (atom)
    
    Args:
        cpu_name: ft.Text con el nombre del CPU
        progress_ring: Anillo de progreso del CPU
        percent_text: Texto con el porcentaje
        temp_text: Texto con la temperatura
        speed_text: Texto con la velocidad
        on_details_click: Callback para ver detalles
    
    Returns:
        ft.Container con el panel completo de CPU
    """
    return ft.Container(
        content=ft.Column([
            # Header
            ft.Row([
                create_icon(ft.Icons.MEMORY, GREEN_PRIMARY, 20),
                cpu_name,
            ], spacing=10),
            
            ft.Container(height=15),
            
            # Progress ring con porcentaje centrado
            ft.Row([
                ft.Stack([
                    progress_ring,
                    ft.Container(
                        content=ft.Column([
                            percent_text,
                            ft.Text("Usage", size=12, color=TEXT_GRAY),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                        alignment=ft.alignment.center,
                        width=130,
                        height=130,
                    ),
                ]),
            ], alignment=ft.MainAxisAlignment.CENTER),
            
            ft.Container(height=15),
            
            # Info de temperatura y velocidad
            ft.Row([
                temp_text,
                ft.Container(width=10),
                ft.Text("|", color=TEXT_DARK_GRAY),
                ft.Container(width=10),
                speed_text,
            ], alignment=ft.MainAxisAlignment.CENTER),
            
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
