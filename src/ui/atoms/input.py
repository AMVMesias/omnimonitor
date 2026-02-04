# ==============================================
# ATOM: Input Components
# ==============================================
# Componentes de entrada atómicos reutilizables

import flet as ft
from ..tokens import (
    TEXT_WHITE, TEXT_GRAY, CARD_BG, BORDER_DARK,
    BORDER_RADIUS_MD
)


def create_text_input(
    label: str = None,
    hint: str = None,
    value: str = "",
    on_change=None,
    password: bool = False,
    width: int = None
) -> ft.TextField:
    """
    Crea un campo de texto.
    
    Args:
        label: Etiqueta del campo
        hint: Texto de placeholder
        value: Valor inicial
        on_change: Callback al cambiar
        password: Si es campo de contraseña
        width: Ancho opcional
    
    Returns:
        ft.TextField configurado
    """
    return ft.TextField(
        label=label,
        hint_text=hint,
        value=value,
        on_change=on_change,
        password=password,
        width=width,
        border_radius=BORDER_RADIUS_MD,
        border_color=BORDER_DARK,
        focused_border_color=ft.Colors.BLUE,
        label_style=ft.TextStyle(color=TEXT_GRAY),
        text_style=ft.TextStyle(color=TEXT_WHITE),
    )


def create_dropdown(
    label: str = None,
    options: list = None,
    value: str = None,
    on_change=None,
    width: int = None
) -> ft.Dropdown:
    """
    Crea un menú desplegable.
    
    Args:
        label: Etiqueta del dropdown
        options: Lista de opciones [(value, label), ...]
        value: Valor seleccionado
        on_change: Callback al cambiar
        width: Ancho opcional
    
    Returns:
        ft.Dropdown configurado
    """
    dropdown_options = []
    if options:
        for opt in options:
            if isinstance(opt, tuple):
                dropdown_options.append(ft.dropdown.Option(key=opt[0], text=opt[1]))
            else:
                dropdown_options.append(ft.dropdown.Option(opt))
    
    return ft.Dropdown(
        label=label,
        value=value,
        options=dropdown_options,
        on_change=on_change,
        width=width,
        border_radius=BORDER_RADIUS_MD,
        border_color=BORDER_DARK,
        focused_border_color=ft.Colors.BLUE,
        label_style=ft.TextStyle(color=TEXT_GRAY),
        text_style=ft.TextStyle(color=TEXT_WHITE),
    )


def create_switch(
    label: str = None,
    value: bool = False,
    on_change=None
) -> ft.Row:
    """
    Crea un interruptor con etiqueta.
    
    Args:
        label: Etiqueta del switch
        value: Estado inicial
        on_change: Callback al cambiar
    
    Returns:
        ft.Row con switch y etiqueta
    """
    return ft.Row([
        ft.Switch(value=value, on_change=on_change),
        ft.Text(label, color=TEXT_WHITE) if label else None,
    ], spacing=10)
