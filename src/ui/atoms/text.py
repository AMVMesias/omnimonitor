# ==============================================
# ATOM: Text Components
# ==============================================
# Componentes de texto atómicos reutilizables

import flet as ft
from ..tokens import (
    TEXT_WHITE, TEXT_GRAY, TEXT_DARK_GRAY,
    FONT_SIZE_SM, FONT_SIZE_MD, FONT_SIZE_LG, FONT_SIZE_XL, FONT_SIZE_XXL
)


def create_title(
    text: str,
    size: int = FONT_SIZE_XXL,
    color: str = TEXT_WHITE
) -> ft.Text:
    """
    Crea un título principal.
    
    Args:
        text: Texto del título
        size: Tamaño de fuente
        color: Color del texto
    
    Returns:
        ft.Text configurado como título
    """
    return ft.Text(
        text,
        size=size,
        weight=ft.FontWeight.BOLD,
        color=color,
    )


def create_subtitle(
    text: str,
    size: int = FONT_SIZE_LG,
    color: str = TEXT_WHITE
) -> ft.Text:
    """
    Crea un subtítulo.
    
    Args:
        text: Texto del subtítulo
        size: Tamaño de fuente
        color: Color del texto
    
    Returns:
        ft.Text configurado como subtítulo
    """
    return ft.Text(
        text,
        size=size,
        weight=ft.FontWeight.W_500,
        color=color,
    )


def create_label(
    text: str,
    size: int = FONT_SIZE_MD,
    color: str = TEXT_GRAY,
    width: int = None
) -> ft.Text:
    """
    Crea una etiqueta de texto secundario.
    
    Args:
        text: Texto de la etiqueta
        size: Tamaño de fuente
        color: Color del texto
        width: Ancho fijo opcional
    
    Returns:
        ft.Text configurado como etiqueta
    """
    return ft.Text(
        text,
        size=size,
        color=color,
        width=width,
    )


def create_value(
    text: str,
    size: int = FONT_SIZE_LG,
    color: str = TEXT_WHITE,
    weight: ft.FontWeight = ft.FontWeight.W_500
) -> ft.Text:
    """
    Crea un texto para mostrar valores.
    
    Args:
        text: Valor a mostrar
        size: Tamaño de fuente
        color: Color del texto
        weight: Peso de la fuente
    
    Returns:
        ft.Text configurado para valores
    """
    return ft.Text(
        text,
        size=size,
        color=color,
        weight=weight,
    )


def create_percentage(
    value: float,
    size: int = 28,
    color: str = TEXT_WHITE
) -> ft.Text:
    """
    Crea un texto de porcentaje formateado.
    
    Args:
        value: Valor numérico del porcentaje
        size: Tamaño de fuente
        color: Color del texto
    
    Returns:
        ft.Text con formato de porcentaje
    """
    return ft.Text(
        f"{value:.1f}%",
        size=size,
        weight=ft.FontWeight.BOLD,
        color=color,
    )
