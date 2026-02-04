# ==============================================
# ATOM: Progress Components
# ==============================================
# Componentes de progreso atómicos reutilizables

import flet as ft
from ..tokens import GREEN_PRIMARY, BORDER_LIGHT


def create_progress_ring(
    value: float = 0.0,
    color: str = GREEN_PRIMARY,
    size: int = 130,
    stroke_width: int = 10
) -> ft.Container:
    """
    Crea un anillo de progreso circular.
    
    Args:
        value: Valor de 0.0 a 1.0
        color: Color del anillo
        size: Tamaño del anillo
        stroke_width: Grosor del trazo
    
    Returns:
        ft.Container con el ProgressRing
    """
    return ft.Container(
        content=ft.Stack([
            ft.ProgressRing(
                value=value,
                width=size,
                height=size,
                stroke_width=stroke_width,
                color=color,
                bgcolor=BORDER_LIGHT,
            ),
        ]),
        width=size,
        height=size,
        alignment=ft.alignment.center,
    )


def create_progress_bar(
    value: float = 0.0,
    color: str = GREEN_PRIMARY,
    height: int = 8,
    width: int = None
) -> ft.ProgressBar:
    """
    Crea una barra de progreso horizontal.
    
    Args:
        value: Valor de 0.0 a 1.0
        color: Color de la barra
        height: Altura de la barra
        width: Ancho opcional
    
    Returns:
        ft.ProgressBar configurado
    """
    return ft.ProgressBar(
        value=value,
        color=color,
        bgcolor=BORDER_LIGHT,
        bar_height=height,
        width=width,
        border_radius=height // 2,
    )
