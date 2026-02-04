"""
CRUD de Alertas para OmniMonitor
Gestiona alertas de métricas del sistema
"""
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src.database.db import get_db


class MetricType(Enum):
    """Tipos de métricas disponibles"""
    CPU_USAGE = "cpu_usage"
    CPU_TEMP = "cpu_temp"
    RAM_USAGE = "ram_usage"
    DISK_USAGE = "disk_usage"
    GPU_USAGE = "gpu_usage"
    GPU_TEMP = "gpu_temp"
    NET_UPLOAD = "net_upload"
    NET_DOWNLOAD = "net_download"


class Operator(Enum):
    """Operadores de comparación"""
    GREATER = ">"
    LESS = "<"
    GREATER_EQ = ">="
    LESS_EQ = "<="
    EQUAL = "=="


@dataclass
class Alert:
    """Modelo de Alerta"""
    id: int
    name: str
    metric: str
    operator: str
    threshold: float
    enabled: bool
    notify_sound: bool
    triggered_count: int
    last_triggered: Optional[str]
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Alert':
        return cls(
            id=data['id'],
            name=data['name'],
            metric=data['metric'],
            operator=data['operator'],
            threshold=data['threshold'],
            enabled=bool(data['enabled']),
            notify_sound=bool(data['notify_sound']),
            triggered_count=data.get('triggered_count', 0),
            last_triggered=data.get('last_triggered')
        )


class AlertManager:
    """Gestor de alertas con CRUD completo"""
    
    METRICS_LABELS = {
        "cpu_usage": "Uso de CPU (%)",
        "cpu_temp": "Temperatura CPU (°C)",
        "ram_usage": "Uso de RAM (%)",
        "disk_usage": "Uso de Disco (%)",
        "gpu_usage": "Uso de GPU (%)",
        "gpu_temp": "Temperatura GPU (°C)",
        "net_upload": "Subida de Red (MB/s)",
        "net_download": "Bajada de Red (MB/s)"
    }
    
    OPERATORS = {
        ">": "Mayor que",
        "<": "Menor que",
        ">=": "Mayor o igual",
        "<=": "Menor o igual",
        "==": "Igual a"
    }
    
    def __init__(self):
        self.db = get_db()
        self._callbacks: List[Callable] = []
    
    # ============ CREATE ============
    def create(self, name: str, metric: str, operator: str, threshold: float,
               enabled: bool = True, notify_sound: bool = True) -> Alert:
        """Crear nueva alerta"""
        alert_id = self.db.create_alert(name, metric, operator, threshold, enabled, notify_sound)
        return self.get(alert_id)
    
    # ============ READ ============
    def get(self, alert_id: int) -> Optional[Alert]:
        """Obtener alerta por ID"""
        data = self.db.get_alert(alert_id)
        return Alert.from_dict(data) if data else None
    
    def get_all(self, only_enabled: bool = False) -> List[Alert]:
        """Obtener todas las alertas"""
        alerts = self.db.get_alerts(only_enabled)
        return [Alert.from_dict(a) for a in alerts]
    
    def count(self) -> int:
        """Contar alertas"""
        return len(self.db.get_alerts())
    
    # ============ UPDATE ============
    def update(self, alert_id: int, **kwargs) -> bool:
        """Actualizar alerta"""
        return self.db.update_alert(alert_id, **kwargs)
    
    def toggle(self, alert_id: int) -> bool:
        """Alternar estado de alerta"""
        alert = self.get(alert_id)
        if alert:
            return self.update(alert_id, enabled=not alert.enabled)
        return False
    
    # ============ DELETE ============
    def delete(self, alert_id: int) -> bool:
        """Eliminar alerta"""
        return self.db.delete_alert(alert_id)
    
    def delete_all(self) -> int:
        """Eliminar todas las alertas"""
        alerts = self.get_all()
        count = 0
        for alert in alerts:
            if self.delete(alert.id):
                count += 1
        return count
    
    # ============ EVALUACIÓN ============
    def check_alert(self, alert: Alert, current_value: float) -> bool:
        """Verificar si una alerta debe dispararse"""
        ops = {
            ">": lambda a, b: a > b,
            "<": lambda a, b: a < b,
            ">=": lambda a, b: a >= b,
            "<=": lambda a, b: a <= b,
            "==": lambda a, b: a == b
        }
        op_func = ops.get(alert.operator)
        if op_func:
            return op_func(current_value, alert.threshold)
        return False
    
    def evaluate_all(self, metrics: Dict[str, float]) -> List[Alert]:
        """Evaluar todas las alertas activas contra métricas actuales"""
        triggered = []
        for alert in self.get_all(only_enabled=True):
            if alert.metric in metrics:
                value = metrics[alert.metric]
                if value is not None and self.check_alert(alert, value):
                    self.db.trigger_alert(alert.id)
                    triggered.append(alert)
        return triggered
    
    def register_callback(self, callback: Callable[[Alert], None]):
        """Registrar callback para cuando se dispara una alerta"""
        self._callbacks.append(callback)
    
    def _notify(self, alert: Alert):
        """Notificar a todos los callbacks"""
        for cb in self._callbacks:
            try:
                cb(alert)
            except Exception:
                pass


if __name__ == "__main__":
    # Test
    manager = AlertManager()
    
    # CREATE
    alert = manager.create("CPU Alto", "cpu_usage", ">", 80)
    print(f"Creada: {alert}")
    
    # READ
    all_alerts = manager.get_all()
    print(f"Todas: {all_alerts}")
    
    # UPDATE
    manager.update(alert.id, threshold=90)
    print(f"Actualizada: {manager.get(alert.id)}")
    
    # EVALUATE
    triggered = manager.evaluate_all({"cpu_usage": 95})
    print(f"Disparadas: {triggered}")
    
    # DELETE
    manager.delete(alert.id)
    print(f"Eliminada. Total: {manager.count()}")
