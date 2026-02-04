# ==============================================
# ATOM: Divider Components
# ==============================================
# Componentes de división y espaciado atómicos reutilizables

import flet as ft
from ..tokens import BORDER_DARK


def create_divider(
    color: str = BORDER_DARK,
    thickness: int = 1,
    vertical: bool = False
) -> ft.Container:
    """
    Crea una línea divisora.
    
    Args:
        color: Color de la línea
        thickness: Grosor de la línea
        vertical: Si es vertical (default horizontal)
    
    Returns:
        ft.Container con la línea divisora
    """
    if vertical:
        return ft.Container(
            width=thickness,
            bgcolor=color,
            expand=True,
        )
    return ft.Container(
        height=thickness,
        bgcolor=color,
        expand=True,
    )


def create_spacer(
    height: int = None,
    width: int = None,
    expand: bool = False
) -> ft.Container:
    """
    Crea un espaciador.
    
    Args:
        height: Altura del espaciador
        width: Ancho del espaciador
        expand: Si debe expandirse
    
    Returns:
        ft.Container vacío con las dimensiones especificadas
    """
    return ft.Container(
        height=height,
        width=width,
        expand=expand,
    )
