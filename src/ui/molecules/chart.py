# ==============================================
# MOLECULE: Chart Components
# ==============================================
# Componentes de gráficos moleculares

import flet as ft
from ..tokens import BORDER_RADIUS_SM


def create_mini_chart(
    data: list,
    color: str,
    height: int = 50,
    max_points: int = 30
) -> ft.Container:
    """
    Crea un mini gráfico de barras estilizado.
    
    Combina: múltiples contenedores como barras
    
    Args:
        data: Lista de valores numéricos
        color: Color de las barras
        height: Altura del gráfico
        max_points: Máximo de puntos a mostrar
    
    Returns:
        ft.Container con el mini gráfico
    """
    if not data or len(data) < 2:
        data = [0] * 10
    
    max_val = max(data) if max(data) > 0 else 100
    
    bars = []
    for value in data[-max_points:]:
        bar_height = max((value / max_val) * height, 2) if max_val > 0 else 2
        bars.append(
            ft.Container(
                width=4,
                height=bar_height,
                bgcolor=color,
                border_radius=2,
            )
        )
    
    return ft.Container(
        content=ft.Row(
            bars,
            spacing=2,
            alignment=ft.MainAxisAlignment.END,
            vertical_alignment=ft.CrossAxisAlignment.END,
        ),
        height=height,
        bgcolor=ft.Colors.with_opacity(0.1, color),
        border_radius=BORDER_RADIUS_SM + 3,
        padding=5,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
    )


def create_bar_group(
    value1: float,
    value2: float,
    color1: str,
    color2: str,
    height: int = 140,
    max_val: float = 100
) -> ft.Container:
    """
    Crea un grupo de dos barras verticales (ej: download/upload).
    
    Args:
        value1: Valor de la primera barra
        value2: Valor de la segunda barra
        color1: Color de la primera barra
        color2: Color de la segunda barra
        height: Altura total
        max_val: Valor máximo para escala
    
    Returns:
        ft.Container con el grupo de barras
    """
    if max_val <= 0:
        max_val = 100
    
    h1 = max((value1 / max_val) * (height - 40), 2)
    h2 = max((value2 / max_val) * (height - 40), 2)
    
    return ft.Container(
        content=ft.Column([
            ft.Container(
                width=6,
                height=h1,
                bgcolor=color1,
                border_radius=ft.border_radius.only(top_left=3, top_right=3),
            ),
            ft.Container(
                width=6,
                height=h2,
                bgcolor=color2,
                border_radius=ft.border_radius.only(bottom_left=3, bottom_right=3),
            ),
        ], spacing=1, alignment=ft.MainAxisAlignment.END),
        height=height - 40,
    )
