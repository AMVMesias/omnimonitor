"""
CRUD de Historial de Métricas para OmniMonitor
Gestiona el almacenamiento y consulta de métricas históricas
"""
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src.database.db import get_db


@dataclass
class MetricRecord:
    """Modelo de registro de métricas"""
    id: int
    timestamp: str
    cpu_usage: Optional[float]
    cpu_temp: Optional[float]
    ram_usage: Optional[float]
    ram_used_gb: Optional[float]
    disk_usage: Optional[float]
    disk_read_speed: Optional[float]
    disk_write_speed: Optional[float]
    net_upload: Optional[float]
    net_download: Optional[float]
    gpu_usage: Optional[float]
    gpu_temp: Optional[float]
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MetricRecord':
        return cls(
            id=data['id'],
            timestamp=data['timestamp'],
            cpu_usage=data.get('cpu_usage'),
            cpu_temp=data.get('cpu_temp'),
            ram_usage=data.get('ram_usage'),
            ram_used_gb=data.get('ram_used_gb'),
            disk_usage=data.get('disk_usage'),
            disk_read_speed=data.get('disk_read_speed'),
            disk_write_speed=data.get('disk_write_speed'),
            net_upload=data.get('net_upload'),
            net_download=data.get('net_download'),
            gpu_usage=data.get('gpu_usage'),
            gpu_temp=data.get('gpu_temp')
        )


class HistoryManager:
    """Gestor de historial de métricas con CRUD completo"""
    
    def __init__(self):
        self.db = get_db()
    
    # ============ CREATE ============
    def save(self, cpu_usage: float = None, cpu_temp: float = None,
             ram_usage: float = None, ram_used_gb: float = None,
             disk_usage: float = None, disk_read_speed: float = None,
             disk_write_speed: float = None, net_upload: float = None,
             net_download: float = None, gpu_usage: float = None,
             gpu_temp: float = None) -> int:
        """Guardar métricas actuales"""
        return self.db.save_metrics(
            cpu_usage=cpu_usage, cpu_temp=cpu_temp,
            ram_usage=ram_usage, ram_used_gb=ram_used_gb,
            disk_usage=disk_usage, disk_read_speed=disk_read_speed,
            disk_write_speed=disk_write_speed, net_upload=net_upload,
            net_download=net_download, gpu_usage=gpu_usage,
            gpu_temp=gpu_temp
        )
    
    def save_from_monitor(self, monitor) -> int:
        """Guardar métricas directamente desde un monitor"""
        try:
            cpu_usage = monitor.get_cpu_usage()
            cpu_temp = monitor.get_cpu_temp()
            memory = monitor.get_memory_usage()
            disk = monitor.get_disk_usage()
            disk_io = monitor.get_disk_io()
            network = monitor.get_network_speed()
            gpu = monitor.get_gpu_info()
            
            return self.save(
                cpu_usage=cpu_usage,
                cpu_temp=cpu_temp,
                ram_usage=memory.get('percent'),
                ram_used_gb=memory.get('used', 0) / (1024**3),
                disk_usage=disk.get('percent'),
                disk_read_speed=disk_io.get('read_speed') if disk_io else None,
                disk_write_speed=disk_io.get('write_speed') if disk_io else None,
                net_upload=network.get('upload'),
                net_download=network.get('download'),
                gpu_usage=gpu.get('load') if gpu else None,
                gpu_temp=gpu.get('temperature') if gpu else None
            )
        except Exception as e:
            print(f"Error guardando métricas: {e}")
            return -1
    
    # ============ READ ============
    def get_history(self, hours: int = 1, limit: int = 1000) -> List[MetricRecord]:
        """Obtener historial de las últimas N horas"""
        data = self.db.get_metrics_history(hours, limit)
        return [MetricRecord.from_dict(d) for d in data]
    
    def get_summary(self, hours: int = 24) -> Dict:
        """Obtener resumen estadístico"""
        return self.db.get_metrics_summary(hours)
    
    def get_count(self) -> int:
        """Obtener cantidad total de registros"""
        return self.db.get_metrics_count()
    
    def get_latest(self) -> Optional[MetricRecord]:
        """Obtener último registro"""
        data = self.db.get_metrics_history(hours=24, limit=1)
        return MetricRecord.from_dict(data[0]) if data else None
    
    def get_metric_series(self, metric: str, hours: int = 1) -> List[Dict]:
        """Obtener serie temporal de una métrica específica"""
        history = self.get_history(hours)
        return [
            {"timestamp": r.timestamp, "value": getattr(r, metric, None)}
            for r in history
            if getattr(r, metric, None) is not None
        ]
    
    # ============ UPDATE ============
    # (No aplica para historial - los registros son inmutables)
    
    # ============ DELETE ============
    def cleanup(self, days: int = 7) -> int:
        """Eliminar registros antiguos"""
        return self.db.cleanup_old_metrics(days)
    
    def clear_all(self) -> int:
        """Eliminar todo el historial"""
        count = self.get_count()
        self.db.cleanup_old_metrics(days=0)
        return count


if __name__ == "__main__":
    # Test
    manager = HistoryManager()
    
    # CREATE
    record_id = manager.save(cpu_usage=45.5, ram_usage=62.3, cpu_temp=55.0)
    print(f"Guardado: {record_id}")
    
    # READ
    history = manager.get_history(hours=1)
    print(f"Historial: {len(history)} registros")
    
    summary = manager.get_summary(hours=24)
    print(f"Resumen: {summary}")
    
    latest = manager.get_latest()
    print(f"Último: {latest}")
    
    # DELETE
    deleted = manager.cleanup(days=7)
    print(f"Limpiados: {deleted} registros antiguos")
