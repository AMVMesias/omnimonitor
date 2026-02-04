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

# Importar SoundManager
try:
    from .sound_manager import SoundManager
except ImportError:
    try:
        from src.ui.sound_manager import SoundManager
    except ImportError:
        SoundManager = None


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
    RATE_LIMIT_SECONDS = 30  # 30 segundos entre notificaciones del mismo tipo (más frecuente)
    MAX_VISIBLE_TOASTS = 5
    
    # Flag para primera ejecución
    _first_run: bool = True
    
    @classmethod
    def initialize(cls, page: ft.Page, theme_getter: Callable = None):
        """Inicializar el gestor de toasts"""
        cls._page = page
        # Reiniciar estados al inicializar para que las alertas disparen
        cls._previous_states = {}
        cls._last_notifications = {}
        cls._first_run = True
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
        Verificar si se cruzó el umbral o si es la primera vez que se evalúa
        Retorna True cuando:
        - Es la primera vez que se evalúa Y está en alerta
        - CAMBIA de normal a alerta
        
        Además, limpia el rate limit cuando SALE del estado de alerta
        para permitir que vuelva a sonar cuando regrese al estado de alerta.
        """
        # Determinar si actualmente está en alerta según la condición
        if condition == "greater":
            is_alert = current_value > threshold
        elif condition == "greater_equal":
            is_alert = current_value >= threshold
        elif condition == "less":
            is_alert = current_value < threshold
        elif condition == "less_equal":
            is_alert = current_value <= threshold
        else:  # equal
            is_alert = current_value == threshold
        
        # Si es la primera vez que evaluamos esta métrica
        if metric_key not in cls._previous_states:
            cls._previous_states[metric_key] = is_alert
            # Disparar si ya está en estado de alerta al inicio
            return is_alert
        
        # Obtener estado anterior
        was_alert = cls._previous_states[metric_key]
        
        # Guardar nuevo estado
        cls._previous_states[metric_key] = is_alert
        
        # Si SALIÓ del estado de alerta (estaba en alerta y ya no)
        # Limpiar el rate limit para que pueda volver a sonar cuando regrese
        if was_alert and not is_alert:
            if metric_key in cls._last_notifications:
                del cls._last_notifications[metric_key]
        
        # Retornar True si CAMBIÓ de normal a alerta
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
    def show_info(cls, message: str, play_sound: bool = False, **kwargs):
        """Mostrar notificación informativa"""
        cls.show(message, ToastType.INFO, **kwargs)
        if play_sound and SoundManager:
            SoundManager.play_info()
    
    @classmethod
    def show_success(cls, message: str, play_sound: bool = False, **kwargs):
        """Mostrar notificación de éxito"""
        cls.show(message, ToastType.SUCCESS, **kwargs)
        if play_sound and SoundManager:
            SoundManager.play_success()
    
    @classmethod
    def show_warning(cls, message: str, play_sound: bool = True, **kwargs):
        """Mostrar notificación de advertencia"""
        cls.show(message, ToastType.WARNING, **kwargs)
        if play_sound and SoundManager:
            SoundManager.play_warning()
    
    @classmethod
    def show_error(cls, message: str, play_sound: bool = True, **kwargs):
        """Mostrar notificación de error"""
        cls.show(message, ToastType.ERROR, **kwargs)
        if play_sound and SoundManager:
            SoundManager.play_error()
    
    @classmethod
    def show_alert(cls, alert_name: str, metric: str, value: float, threshold: float, 
                   condition: str = "greater", play_sound: bool = True, 
                   on_triggered: callable = None, alert_id: int = None):
        """
        Mostrar notificación de alerta del sistema
        Solo se muestra si cruza el umbral (no si se mantiene)
        Rate limited: 30 segundos por métrica
        
        Args:
            alert_name: Nombre de la alerta
            metric: Nombre de la métrica (cpu, ram, etc.)
            value: Valor actual
            threshold: Umbral configurado
            condition: "greater", "greater_equal", "less", "less_equal", "equal"
            play_sound: Si reproducir sonido de alerta
            on_triggered: Callback cuando se dispara la alerta (para guardar en BD)
            alert_id: ID de la alerta para el callback
        """
        metric_key = f"alert:{alert_name}:{metric}"  # Clave única por alerta+métrica
        
        # Verificar si cruzó el umbral (de normal a alerta)
        if not cls._check_threshold_crossed(metric_key, value, threshold, condition):
            return False  # Retornar False para indicar que no se disparó
        
        # Rate limiting (30 segundos entre alertas del mismo tipo)
        if not cls._can_show_notification(metric_key):
            return False
        
        # Determinar unidad según la métrica
        if 'temp' in metric:
            unit = "°C"
        elif 'net_' in metric:
            unit = " MB/s"
        else:
            unit = "%"
        
        # Formatear texto de condición
        condition_texts = {
            "greater": "supera",
            "greater_equal": "supera o iguala",
            "less": "está por debajo de",
            "less_equal": "está por debajo o igual a",
            "equal": "es igual a"
        }
        condition_text = condition_texts.get(condition, "supera")
        
        # Formatear nombre de métrica legible
        metric_names = {
            "cpu_usage": "CPU",
            "cpu_temp": "Temp. CPU",
            "ram_usage": "RAM",
            "disk_usage": "Disco",
            "gpu_usage": "GPU",
            "gpu_temp": "Temp. GPU",
            "net_download": "Descarga",
            "net_upload": "Subida"
        }
        metric_display = metric_names.get(metric, metric.upper())
        
        message = f"⚠️ {alert_name}: {metric_display} {condition_text} {threshold}{unit} (actual: {value:.2f}{unit})"
        
        cls.show(
            message=message,
            toast_type=ToastType.ALERT,
            icon=ft.Icons.NOTIFICATIONS_ACTIVE,
            duration_ms=8000,  # Alertas duran más
        )
        
        # Reproducir sonido de alerta
        if play_sound and SoundManager:
            SoundManager.play_alert()
        
        # Ejecutar callback si se proporcionó (para guardar en BD)
        if on_triggered and alert_id is not None:
            try:
                on_triggered(alert_id)
            except Exception as e:
                print(f"Error en callback de alerta: {e}")
        
        return True  # Retornar True para indicar que se disparó
    
    @classmethod
    def clear_all(cls):
        """Limpiar todas las notificaciones"""
        if cls._toasts_column:
            cls._toasts_column.controls.clear()
            if cls._page:
                cls._page.update()
