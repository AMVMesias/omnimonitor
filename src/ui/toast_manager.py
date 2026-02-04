"""
Sistema de Notificaciones Toast para OmniMonitor
Notificaciones flotantes en la esquina inferior derecha
Con rate limiting y detección de cruce de umbrales
"""
import flet as ft
from datetime import datetime, timedelta
from typing import Dict, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class ToastType(Enum):
    """Tipos de notificación"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    ALERT = "alert"


@dataclass
class Toast:
    """Modelo de notificación toast"""
    id: str
    message: str
    toast_type: ToastType
    icon: str
    created_at: datetime = field(default_factory=datetime.now)
    duration_ms: int = 5000  # Duración por defecto: 5 segundos


class ToastManager:
    """
    Gestor de notificaciones toast flotantes
    - Muestra notificaciones en esquina inferior derecha
    - Rate limiting: máximo 1 notificación del mismo tipo por minuto
    - Detección de cruce de umbrales (no notifica mientras se mantiene)
    """
    
    # Rate limiting: última notificación por tipo
    _last_notifications: Dict[str, datetime] = {}
    
    # Estado anterior de métricas (para detectar cruce de umbral)
    _previous_states: Dict[str, bool] = {}
    
    # Instancia singleton
    _instance = None
    _page: Optional[ft.Page] = None
    _container: Optional[ft.Container] = None
    _toasts_column: Optional[ft.Column] = None
    _theme_getter: Optional[Callable] = None
    
    # Configuración
    RATE_LIMIT_SECONDS = 60  # 1 minuto entre notificaciones del mismo tipo
    MAX_VISIBLE_TOASTS = 3
    
    @classmethod
    def initialize(cls, page: ft.Page, theme_getter: Callable = None):
        """Inicializar el gestor de toasts"""
        cls._page = page
        cls._theme_getter = theme_getter
        
        # Crear columna para toasts
        cls._toasts_column = ft.Column(
            spacing=10,
            alignment=ft.MainAxisAlignment.END,
        )
        
        # Crear contenedor flotante
        cls._container = ft.Container(
            content=cls._toasts_column,
            right=20,
            bottom=20,
            width=350,
        )
        
        # Agregar a la página como overlay
        if cls._container not in page.overlay:
            page.overlay.append(cls._container)
    
    @classmethod
    def _get_colors(cls) -> dict:
        """Obtener colores del tema actual"""
        if cls._theme_getter:
            return cls._theme_getter()
        # Fallback colors
        return {
            "bg": "#1E2128",
            "card": "#252830",
            "text": "#FFFFFF",
            "text_secondary": "#9CA3AF",
            "green": "#10B981",
            "blue": "#3B82F6",
            "orange": "#F59E0B",
            "red": "#EF4444",
            "yellow": "#FBBF24",
        }
    
    @classmethod
    def _can_show_notification(cls, notification_key: str) -> bool:
        """Verificar si se puede mostrar una notificación (rate limiting)"""
        now = datetime.now()
        
        if notification_key in cls._last_notifications:
            last_time = cls._last_notifications[notification_key]
            if (now - last_time).total_seconds() < cls.RATE_LIMIT_SECONDS:
                return False
        
        cls._last_notifications[notification_key] = now
        return True
    
    @classmethod
    def _check_threshold_crossed(cls, metric_key: str, current_value: float, threshold: float, condition: str) -> bool:
        """
        Verificar si se cruzó el umbral (no si se mantiene)
        Retorna True solo cuando CAMBIA de normal a alerta
        """
        # Determinar si actualmente está en alerta
        if condition == "greater":
            is_alert = current_value > threshold
        elif condition == "less":
            is_alert = current_value < threshold
        else:
            is_alert = current_value == threshold
        
        # Obtener estado anterior
        was_alert = cls._previous_states.get(metric_key, False)
        
        # Guardar nuevo estado
        cls._previous_states[metric_key] = is_alert
        
        # Retornar True solo si CAMBIÓ a estado de alerta
        return is_alert and not was_alert
    
    @classmethod
    def _create_toast_control(cls, toast: Toast) -> ft.Container:
        """Crear control visual del toast"""
        colors = cls._get_colors()
        
        # Colores según tipo
        type_colors = {
            ToastType.INFO: colors["blue"],
            ToastType.SUCCESS: colors["green"],
            ToastType.WARNING: colors["orange"],
            ToastType.ERROR: colors["red"],
            ToastType.ALERT: colors["yellow"],
        }
        
        accent_color = type_colors.get(toast.toast_type, colors["blue"])
        
        def close_toast(e):
            cls._remove_toast(toast.id)
        
        toast_container = ft.Container(
            content=ft.Row([
                ft.Container(
                    width=4,
                    height=50,
                    bgcolor=accent_color,
                    border_radius=ft.BorderRadius(2, 0, 0, 2),
                ),
                ft.Container(width=10),
                ft.Icon(toast.icon, color=accent_color, size=24),
                ft.Container(width=10),
                ft.Column([
                    ft.Text(
                        toast.message,
                        size=13,
                        color=colors["text"],
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.Text(
                        toast.created_at.strftime("%H:%M:%S"),
                        size=10,
                        color=colors["text_secondary"],
                    ),
                ], spacing=2, expand=True),
                ft.IconButton(
                    icon=ft.Icons.CLOSE,
                    icon_size=16,
                    icon_color=colors["text_secondary"],
                    on_click=close_toast,
                ),
            ], spacing=0),
            bgcolor=colors["card"],
            border_radius=8,
            padding=ft.Padding(0, 10, 10, 10),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
            ),
            animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
            data=toast.id,  # Guardar ID para referencia
        )
        
        return toast_container
    
    @classmethod
    def _remove_toast(cls, toast_id: str):
        """Remover un toast específico"""
        if cls._toasts_column:
            for control in cls._toasts_column.controls[:]:
                if hasattr(control, 'data') and control.data == toast_id:
                    cls._toasts_column.controls.remove(control)
                    break
            if cls._page:
                cls._page.update()
    
    @classmethod
    def _auto_remove_toast(cls, toast_id: str, delay_ms: int):
        """Programar remoción automática del toast"""
        import asyncio
        
        async def remove_after_delay():
            await asyncio.sleep(delay_ms / 1000)
            cls._remove_toast(toast_id)
        
        if cls._page:
            cls._page.run_task(remove_after_delay)
    
    @classmethod
    def show(cls, message: str, toast_type: ToastType = ToastType.INFO, 
             icon: str = None, duration_ms: int = 5000, notification_key: str = None):
        """
        Mostrar una notificación toast
        
        Args:
            message: Mensaje a mostrar
            toast_type: Tipo de notificación
            icon: Icono personalizado (opcional)
            duration_ms: Duración en milisegundos
            notification_key: Clave para rate limiting (opcional)
        """
        if not cls._page or not cls._toasts_column:
            return
        
        # Rate limiting
        key = notification_key or f"{toast_type.value}:{message}"
        if notification_key and not cls._can_show_notification(key):
            return
        
        # Iconos por defecto según tipo
        default_icons = {
            ToastType.INFO: ft.Icons.INFO_OUTLINE,
            ToastType.SUCCESS: ft.Icons.CHECK_CIRCLE_OUTLINE,
            ToastType.WARNING: ft.Icons.WARNING_AMBER_OUTLINED,
            ToastType.ERROR: ft.Icons.ERROR_OUTLINE,
            ToastType.ALERT: ft.Icons.NOTIFICATIONS_ACTIVE,
        }
        
        toast = Toast(
            id=f"toast_{datetime.now().timestamp()}",
            message=message,
            toast_type=toast_type,
            icon=icon or default_icons.get(toast_type, ft.Icons.INFO_OUTLINE),
            duration_ms=duration_ms,
        )
        
        # Limitar cantidad visible
        while len(cls._toasts_column.controls) >= cls.MAX_VISIBLE_TOASTS:
            cls._toasts_column.controls.pop(0)
        
        # Agregar toast
        toast_control = cls._create_toast_control(toast)
        cls._toasts_column.controls.append(toast_control)
        cls._page.update()
        
        # Auto-remover después de duration
        cls._auto_remove_toast(toast.id, duration_ms)
    
    @classmethod
    def show_info(cls, message: str, **kwargs):
        """Mostrar notificación informativa"""
        cls.show(message, ToastType.INFO, **kwargs)
    
    @classmethod
    def show_success(cls, message: str, **kwargs):
        """Mostrar notificación de éxito"""
        cls.show(message, ToastType.SUCCESS, **kwargs)
    
    @classmethod
    def show_warning(cls, message: str, **kwargs):
        """Mostrar notificación de advertencia"""
        cls.show(message, ToastType.WARNING, **kwargs)
    
    @classmethod
    def show_error(cls, message: str, **kwargs):
        """Mostrar notificación de error"""
        cls.show(message, ToastType.ERROR, **kwargs)
    
    @classmethod
    def show_alert(cls, alert_name: str, metric: str, value: float, threshold: float, 
                   condition: str = "greater"):
        """
        Mostrar notificación de alerta del sistema
        Solo se muestra si cruza el umbral (no si se mantiene)
        Rate limited: 1 por métrica por minuto
        
        Args:
            alert_name: Nombre de la alerta
            metric: Nombre de la métrica (cpu, ram, etc.)
            value: Valor actual
            threshold: Umbral configurado
            condition: "greater", "less", o "equal"
        """
        metric_key = f"alert:{metric}"
        
        # Verificar si cruzó el umbral
        if not cls._check_threshold_crossed(metric_key, value, threshold, condition):
            return
        
        # Rate limiting
        if not cls._can_show_notification(metric_key):
            return
        
        # Formatear mensaje
        condition_text = "supera" if condition == "greater" else "está por debajo de" if condition == "less" else "es igual a"
        message = f"⚠️ {alert_name}: {metric.upper()} {condition_text} {threshold}% (actual: {value:.1f}%)"
        
        cls.show(
            message=message,
            toast_type=ToastType.ALERT,
            icon=ft.Icons.NOTIFICATIONS_ACTIVE,
            duration_ms=8000,  # Alertas duran más
        )
    
    @classmethod
    def clear_all(cls):
        """Limpiar todas las notificaciones"""
        if cls._toasts_column:
            cls._toasts_column.controls.clear()
            if cls._page:
                cls._page.update()
