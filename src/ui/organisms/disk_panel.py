# ==============================================
# ORGANISM: Disk Panel
# ==============================================
# Panel completo de Disco combinando múltiples moléculas

import flet as ft
from ..tokens import (
    CARD_BG, BLUE_PRIMARY, BORDER_DARK,
    BORDER_RADIUS_LG, SPACING_LG
)
from ..atoms.icon import create_icon
from ..atoms.button import create_detail_button


def create_disk_card(
    disk_name: ft.Text,
    used_text: ft.Text,
    speed_text: ft.Text,
    progress_bar: ft.ProgressBar,
    on_details_click=None
) -> ft.Container:
    """
    Crea la tarjeta completa de Disco.
    
    Combina: icon + text + progress_bar + speed_info + detail_button
    
    Args:
        disk_name: Texto con nombre del disco
        used_text: Texto con espacio usado
        speed_text: Texto con velocidad de lectura/escritura
        progress_bar: Barra de progreso
        on_details_click: Callback para ver detalles
    
    Returns:
        ft.Container con el panel completo de Disco
    """
    return ft.Container(
        content=ft.Column([
            # Header
            ft.Row([
                create_icon(ft.Icons.STORAGE, BLUE_PRIMARY, 20),
                disk_name,
            ], spacing=10),
            
            ft.Container(height=15),
            
            # Progress bar con info de uso
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
            
            # Info de velocidad
            speed_text,
            
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
