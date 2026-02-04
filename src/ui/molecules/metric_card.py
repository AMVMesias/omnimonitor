# ==============================================
# MOLECULE: Metric Card Component
# ==============================================
# Tarjeta de métrica que combina icono + título + valor + progreso

import flet as ft
from ..tokens import (
    CARD_BG, TEXT_WHITE, TEXT_GRAY, BORDER_DARK,
    BORDER_RADIUS_LG, SPACING_LG
)
from ..atoms.icon import create_icon
from ..atoms.text import create_subtitle, create_label
from ..atoms.progress import create_progress_ring
from ..atoms.button import create_detail_button


def create_metric_card(
    title: str,
    icon: str,
    color: str,
    progress_value: float = 0.0,
    percent_text: ft.Text = None,
    sub_info: list = None,
    on_details_click=None,
    extra_content: ft.Control = None
) -> ft.Container:
    """
    Crea una tarjeta de métrica con diseño circular.
    
    Combina: icon (atom) + text (atom) + progress_ring (atom) + button (atom)
    
    Args:
        title: Título de la tarjeta (ej: "Intel Core i7")
        icon: Icono de ft.Icons.*
        color: Color del tema de la tarjeta
        progress_value: Valor de 0.0 a 1.0 para el anillo
        percent_text: ft.Text con el porcentaje (para actualización dinámica)
        sub_info: Lista de ft.Row/ft.Text para info adicional
        on_details_click: Callback para el botón de detalles
        extra_content: Contenido adicional opcional
    
    Returns:
        ft.Container con la tarjeta completa
    """
    # Header con icono y título
    header = ft.Row([
        create_icon(icon, color, 20),
        create_subtitle(title) if isinstance(title, str) else title,
    ], spacing=10)
    
    # Contenido del anillo de progreso
    ring_content = ft.Stack([
        create_progress_ring(progress_value, color, 130, 10),
        ft.Container(
            content=ft.Column([
                percent_text if percent_text else ft.Text("0%", size=28, weight=ft.FontWeight.BOLD, color=TEXT_WHITE),
                create_label("Usage"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
            alignment=ft.alignment.center,
            width=130,
            height=130,
        ),
    ])
    
    ring_row = ft.Row([ring_content], alignment=ft.MainAxisAlignment.CENTER)
    
    # Construir columna de contenido
    content_items = [
        header,
        ft.Container(height=15),
        ring_row,
    ]
    
    # Agregar información adicional si existe
    if sub_info:
        content_items.append(ft.Container(height=15))
        content_items.append(ft.Row(sub_info, alignment=ft.MainAxisAlignment.CENTER))
    
    # Agregar contenido extra si existe
    if extra_content:
        content_items.append(ft.Container(height=10))
        content_items.append(extra_content)
    
    # Footer con botón de detalles
    content_items.append(ft.Container(expand=True))
    content_items.append(ft.Row([
        ft.Container(expand=True),
        create_detail_button(on_details_click),
    ]))
    
    return ft.Container(
        content=ft.Column(content_items),
        bgcolor=CARD_BG,
        border_radius=BORDER_RADIUS_LG,
        padding=SPACING_LG + 5,
        border=ft.border.all(1, BORDER_DARK),
    )
