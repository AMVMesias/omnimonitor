# ==============================================
# MOLECULE: Stat Row Components
# ==============================================
# Filas de estadísticas que combinan label + valor + icono

import flet as ft
from ..tokens import TEXT_WHITE, TEXT_GRAY, TEXT_DARK_GRAY, SPACING_SM


def create_stat_row(
    label: str,
    value: str,
    color: str = TEXT_WHITE
) -> ft.Row:
    """
    Crea una fila simple de estadística.
    
    Combina: label (atom) + value (atom)
    
    Args:
        label: Etiqueta descriptiva
        value: Valor a mostrar
        color: Color del valor
    
    Returns:
        ft.Row con label y valor
    """
    return ft.Row([
        ft.Text(label, size=13, color=TEXT_GRAY),
        ft.Text(" | ", color=TEXT_DARK_GRAY),
        ft.Text(value, size=13, color=color, weight=ft.FontWeight.W_500),
    ], spacing=5)


def create_info_row(
    label: str,
    value: str,
    icon: str = None,
    value_color: str = TEXT_WHITE
) -> ft.Container:
    """
    Crea una fila de información estilizada con icono opcional.
    
    Combina: icon (atom) + label (atom) + value (atom)
    
    Args:
        label: Etiqueta descriptiva
        value: Valor a mostrar
        icon: Icono opcional de ft.Icons.*
        value_color: Color del valor
    
    Returns:
        ft.Container con la fila de información
    """
    row_content = [
        ft.Text(label, size=13, color=TEXT_GRAY, width=120),
        ft.Text(value, size=13, color=value_color, weight=ft.FontWeight.W_500),
    ]
    
    if icon:
        row_content.insert(0, ft.Icon(icon, color=value_color, size=16))
    
    return ft.Container(
        content=ft.Row(row_content, spacing=10),
        padding=ft.Padding(left=0, right=0, top=5, bottom=5),
    )


def create_labeled_value(
    label: str,
    value: str,
    value_color: str = TEXT_WHITE,
    vertical: bool = False
) -> ft.Container:
    """
    Crea un par label-valor.
    
    Args:
        label: Etiqueta descriptiva
        value: Valor a mostrar
        value_color: Color del valor
        vertical: Si debe ser vertical (label arriba, valor abajo)
    
    Returns:
        ft.Container con label y valor
    """
    if vertical:
        return ft.Column([
            ft.Text(label, size=11, color=TEXT_GRAY),
            ft.Text(value, size=16, weight=ft.FontWeight.BOLD, color=value_color),
        ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    return ft.Row([
        ft.Text(label, size=12, color=TEXT_GRAY),
        ft.Text(value, size=12, weight=ft.FontWeight.W_500, color=value_color),
    ], spacing=SPACING_SM)
