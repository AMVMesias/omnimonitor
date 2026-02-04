# ==============================================
# OmniMonitor - Theme Manager
# ==============================================
# Sistema de temas dinámico para soportar modo claro y oscuro

import flet as ft
from typing import Callable

# ============ TEMA OSCURO (DEFAULT) ============
DARK_THEME = {
    "name": "dark",
    "bg_primary": "#0D1117",
    "bg_secondary": "#161B22",
    "bg_sidebar": "#0D1117",
    "bg_card": "#161B22",
    "bg_hover": "#1A1F26",
    
    "text_primary": "#FFFFFF",
    "text_secondary": "#9CA3AF",
    "text_muted": "#6B7280",
    
    "border_primary": "#1E2130",
    "border_secondary": "#2A2D3A",
    
    "accent_green": "#4ADE80",
    "accent_blue": "#60A5FA",
    "accent_orange": "#FB923C",
    "accent_red": "#F87171",
    "accent_yellow": "#FBBF24",
    "accent_purple": "#A78BFA",
    
    "net_download": "#4FC3F7",
    "net_upload": "#81C784",
}

# ============ TEMA CLARO ============
LIGHT_THEME = {
    "name": "light",
    "bg_primary": "#F8FAFC",
    "bg_secondary": "#FFFFFF",
    "bg_sidebar": "#F1F5F9",
    "bg_card": "#FFFFFF",
    "bg_hover": "#E2E8F0",
    
    "text_primary": "#1E293B",
    "text_secondary": "#64748B",
    "text_muted": "#94A3B8",
    
    "border_primary": "#E2E8F0",
    "border_secondary": "#CBD5E1",
    
    "accent_green": "#22C55E",
    "accent_blue": "#3B82F6",
    "accent_orange": "#F97316",
    "accent_red": "#EF4444",
    "accent_yellow": "#EAB308",
    "accent_purple": "#8B5CF6",
    
    "net_download": "#0EA5E9",
    "net_upload": "#22C55E",
}


class ThemeManager:
    """Gestor de temas para OmniMonitor"""
    
    _instance = None
    _current_theme = DARK_THEME
    _listeners: list[Callable] = []
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def get_theme(cls) -> dict:
        """Obtener el tema actual"""
        return cls._current_theme
    
    @classmethod
    def is_dark(cls) -> bool:
        """¿Está en modo oscuro?"""
        return cls._current_theme["name"] == "dark"
    
    @classmethod
    def set_dark(cls):
        """Cambiar a tema oscuro"""
        cls._current_theme = DARK_THEME
        cls._notify_listeners()
    
    @classmethod
    def set_light(cls):
        """Cambiar a tema claro"""
        cls._current_theme = LIGHT_THEME
        cls._notify_listeners()
    
    @classmethod
    def toggle(cls):
        """Alternar entre temas"""
        if cls.is_dark():
            cls.set_light()
        else:
            cls.set_dark()
    
    @classmethod
    def add_listener(cls, callback: Callable):
        """Agregar listener de cambio de tema"""
        cls._listeners.append(callback)
    
    @classmethod
    def _notify_listeners(cls):
        """Notificar a todos los listeners"""
        for callback in cls._listeners:
            try:
                callback(cls._current_theme)
            except:
                pass
    
    # ============ GETTERS DE COLORES ============
    @classmethod
    def bg_primary(cls) -> str:
        return cls._current_theme["bg_primary"]
    
    @classmethod
    def bg_secondary(cls) -> str:
        return cls._current_theme["bg_secondary"]
    
    @classmethod
    def bg_sidebar(cls) -> str:
        return cls._current_theme["bg_sidebar"]
    
    @classmethod
    def bg_card(cls) -> str:
        return cls._current_theme["bg_card"]
    
    @classmethod
    def text_primary(cls) -> str:
        return cls._current_theme["text_primary"]
    
    @classmethod
    def text_secondary(cls) -> str:
        return cls._current_theme["text_secondary"]
    
    @classmethod
    def text_muted(cls) -> str:
        return cls._current_theme["text_muted"]
    
    @classmethod
    def border_primary(cls) -> str:
        return cls._current_theme["border_primary"]
    
    @classmethod
    def accent_green(cls) -> str:
        return cls._current_theme["accent_green"]
    
    @classmethod
    def accent_blue(cls) -> str:
        return cls._current_theme["accent_blue"]
    
    @classmethod
    def accent_orange(cls) -> str:
        return cls._current_theme["accent_orange"]
    
    @classmethod
    def accent_red(cls) -> str:
        return cls._current_theme["accent_red"]
    
    @classmethod
    def accent_yellow(cls) -> str:
        return cls._current_theme["accent_yellow"]


# ============ FUNCIÓN HELPER PARA APLICAR TEMA A PAGE ============
def apply_theme_to_page(page: ft.Page, theme: dict):
    """Aplica el tema a la página de Flet"""
    is_dark = theme["name"] == "dark"
    
    page.theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT
    page.bgcolor = theme["bg_primary"]
    
    # Configurar tema de Flet con parámetros compatibles
    page.theme = ft.Theme(
        color_scheme_seed=theme["accent_blue"],
    )
    
    page.update()


# Instancia global
theme_manager = ThemeManager.get_instance()
