"""
Base de datos SQLite para OmniMonitor
Maneja alertas, historial de métricas y configuración
"""
import sqlite3
import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

# Ruta de la base de datos
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'omnimonitor.db')


class Database:
    """Clase principal para manejo de base de datos SQLite"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.conn = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Conectar a la base de datos"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
    
    def _create_tables(self):
        """Crear tablas si no existen"""
        cursor = self.conn.cursor()
        
        # Tabla de Alertas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                metric TEXT NOT NULL,
                operator TEXT NOT NULL,
                threshold REAL NOT NULL,
                enabled INTEGER DEFAULT 1,
                notify_sound INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                triggered_count INTEGER DEFAULT 0,
                last_triggered TIMESTAMP
            )
        ''')
        
        # Tabla de Historial de Métricas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                cpu_usage REAL,
                cpu_temp REAL,
                ram_usage REAL,
                ram_used_gb REAL,
                disk_usage REAL,
                disk_read_speed REAL,
                disk_write_speed REAL,
                net_upload REAL,
                net_download REAL,
                gpu_usage REAL,
                gpu_temp REAL
            )
        ''')
        
        # Tabla de Configuración
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insertar configuración por defecto si no existe
        default_config = {
            'theme': 'dark',
            'update_interval': '1000',
            'history_retention_days': '7',
            'enable_notifications': 'true',
            'enable_sounds': 'true',
            'start_minimized': 'false',
            'language': 'es'
        }
        
        for key, value in default_config.items():
            cursor.execute('''
                INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)
            ''', (key, value))
        
        self.conn.commit()
    
    def close(self):
        """Cerrar conexión"""
        if self.conn:
            self.conn.close()
    
    # ==================== CRUD ALERTAS ====================
    
    def create_alert(self, name: str, metric: str, operator: str, threshold: float,
                     enabled: bool = True, notify_sound: bool = True) -> int:
        """Crear nueva alerta"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO alerts (name, metric, operator, threshold, enabled, notify_sound)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, metric, operator, threshold, int(enabled), int(notify_sound)))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_alerts(self, only_enabled: bool = False) -> List[Dict]:
        """Obtener todas las alertas"""
        cursor = self.conn.cursor()
        if only_enabled:
            cursor.execute('SELECT * FROM alerts WHERE enabled = 1 ORDER BY created_at DESC')
        else:
            cursor.execute('SELECT * FROM alerts ORDER BY created_at DESC')
        return [dict(row) for row in cursor.fetchall()]
    
    def get_alert(self, alert_id: int) -> Optional[Dict]:
        """Obtener alerta por ID"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM alerts WHERE id = ?', (alert_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def update_alert(self, alert_id: int, **kwargs) -> bool:
        """Actualizar alerta"""
        allowed_fields = ['name', 'metric', 'operator', 'threshold', 'enabled', 'notify_sound']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
        
        set_clause = ', '.join(f'{k} = ?' for k in updates.keys())
        values = list(updates.values()) + [alert_id]
        
        cursor = self.conn.cursor()
        cursor.execute(f'UPDATE alerts SET {set_clause} WHERE id = ?', values)
        self.conn.commit()
        return cursor.rowcount > 0
    
    def delete_alert(self, alert_id: int) -> bool:
        """Eliminar alerta"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM alerts WHERE id = ?', (alert_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def trigger_alert(self, alert_id: int):
        """Marcar alerta como disparada"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE alerts 
            SET triggered_count = triggered_count + 1, last_triggered = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (alert_id,))
        self.conn.commit()
    
    # ==================== CRUD HISTORIAL ====================
    
    def save_metrics(self, cpu_usage: float = None, cpu_temp: float = None,
                     ram_usage: float = None, ram_used_gb: float = None,
                     disk_usage: float = None, disk_read_speed: float = None,
                     disk_write_speed: float = None, net_upload: float = None,
                     net_download: float = None, gpu_usage: float = None,
                     gpu_temp: float = None) -> int:
        """Guardar métricas en historial"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO metrics_history 
            (cpu_usage, cpu_temp, ram_usage, ram_used_gb, disk_usage, 
             disk_read_speed, disk_write_speed, net_upload, net_download, 
             gpu_usage, gpu_temp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (cpu_usage, cpu_temp, ram_usage, ram_used_gb, disk_usage,
              disk_read_speed, disk_write_speed, net_upload, net_download,
              gpu_usage, gpu_temp))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_metrics_history(self, hours: int = 1, limit: int = 1000) -> List[Dict]:
        """Obtener historial de métricas de las últimas N horas"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM metrics_history 
            WHERE timestamp >= datetime('now', '-' || ? || ' hours')
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (hours, limit))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_metrics_summary(self, hours: int = 24) -> Dict:
        """Obtener resumen estadístico de métricas"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT 
                AVG(cpu_usage) as avg_cpu,
                MAX(cpu_usage) as max_cpu,
                MIN(cpu_usage) as min_cpu,
                AVG(ram_usage) as avg_ram,
                MAX(ram_usage) as max_ram,
                AVG(cpu_temp) as avg_cpu_temp,
                MAX(cpu_temp) as max_cpu_temp,
                COUNT(*) as total_records
            FROM metrics_history 
            WHERE timestamp >= datetime('now', '-' || ? || ' hours')
        ''', (hours,))
        row = cursor.fetchone()
        return dict(row) if row else {}
    
    def cleanup_old_metrics(self, days: int = 7) -> int:
        """Eliminar métricas más antiguas que N días"""
        cursor = self.conn.cursor()
        cursor.execute('''
            DELETE FROM metrics_history 
            WHERE timestamp < datetime('now', '-' || ? || ' days')
        ''', (days,))
        self.conn.commit()
        return cursor.rowcount
    
    def get_metrics_count(self) -> int:
        """Obtener cantidad total de registros"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM metrics_history')
        return cursor.fetchone()[0]
    
    # ==================== CRUD CONFIGURACIÓN ====================
    
    def get_config(self, key: str, default: str = None) -> Optional[str]:
        """Obtener valor de configuración"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT value FROM config WHERE key = ?', (key,))
        row = cursor.fetchone()
        return row['value'] if row else default
    
    def get_all_config(self) -> Dict[str, str]:
        """Obtener toda la configuración"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT key, value FROM config')
        return {row['key']: row['value'] for row in cursor.fetchall()}
    
    def set_config(self, key: str, value: str) -> bool:
        """Establecer/actualizar configuración"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO config (key, value, updated_at) 
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (key, value))
        self.conn.commit()
        return True
    
    def delete_config(self, key: str) -> bool:
        """Eliminar configuración"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM config WHERE key = ?', (key,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def reset_config(self):
        """Resetear configuración a valores por defecto"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM config')
        self.conn.commit()
        self._create_tables()  # Re-crear con valores por defecto


# Instancia global
_db_instance: Optional[Database] = None


def get_db() -> Database:
    """Obtener instancia de base de datos (singleton)"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance


if __name__ == "__main__":
    # Test
    db = get_db()
    
    # Test alertas
    alert_id = db.create_alert("CPU Alto", "cpu", ">", 80)
    print(f"Alerta creada: {alert_id}")
    print(f"Alertas: {db.get_alerts()}")
    
    # Test métricas
    db.save_metrics(cpu_usage=45.5, ram_usage=60.2, cpu_temp=55.0)
    print(f"Historial: {db.get_metrics_history(hours=1)}")
    
    # Test config
    print(f"Config: {db.get_all_config()}")
    
    db.close()
