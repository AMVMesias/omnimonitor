"""
CRUD de Procesos para OmniMonitor
Gestiona la visualización y control de procesos del sistema
"""
import psutil
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Process:
    """Modelo de Proceso"""
    pid: int
    name: str
    status: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    username: str
    create_time: str
    num_threads: int
    cmdline: str
    
    @classmethod
    def from_psutil(cls, proc: psutil.Process) -> Optional['Process']:
        """Crear desde objeto psutil.Process"""
        try:
            with proc.oneshot():
                info = proc.as_dict(attrs=[
                    'pid', 'name', 'status', 'cpu_percent', 'memory_percent',
                    'memory_info', 'username', 'create_time', 'num_threads', 'cmdline'
                ])
                
                # Formatear tiempo de creación
                create_time = datetime.fromtimestamp(info['create_time']).strftime('%Y-%m-%d %H:%M:%S')
                
                # Obtener memoria en MB
                memory_mb = info['memory_info'].rss / (1024 * 1024) if info.get('memory_info') else 0
                
                # Obtener línea de comando
                cmdline = ' '.join(info['cmdline']) if info.get('cmdline') else info['name']
                
                return cls(
                    pid=info['pid'],
                    name=info['name'] or 'Unknown',
                    status=info['status'] or 'unknown',
                    cpu_percent=info['cpu_percent'] or 0,
                    memory_percent=info['memory_percent'] or 0,
                    memory_mb=round(memory_mb, 2),
                    username=info['username'] or 'unknown',
                    create_time=create_time,
                    num_threads=info['num_threads'] or 0,
                    cmdline=cmdline[:100] if cmdline else ''  # Limitar longitud
                )
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return None


class ProcessManager:
    """Gestor de procesos con CRUD (principalmente Read y Delete)"""
    
    def __init__(self):
        self._sort_by = 'cpu_percent'
        self._sort_reverse = True
        self._filter_text = ''
    
    # ============ CREATE ============
    # (No aplica - no creamos procesos desde el monitor)
    
    # ============ READ ============
    def get_all(self, limit: int = 50) -> List[Process]:
        """Obtener lista de procesos"""
        processes = []
        
        # Primero hacer un pase para actualizar CPU percent
        for proc in psutil.process_iter():
            try:
                proc.cpu_percent(interval=None)
            except:
                pass
        
        # Luego obtener la info
        for proc in psutil.process_iter():
            p = Process.from_psutil(proc)
            if p:
                # Aplicar filtro
                if self._filter_text:
                    if self._filter_text.lower() not in p.name.lower():
                        continue
                processes.append(p)
        
        # Ordenar
        processes.sort(
            key=lambda x: getattr(x, self._sort_by, 0) or 0,
            reverse=self._sort_reverse
        )
        
        return processes[:limit]
    
    def get(self, pid: int) -> Optional[Process]:
        """Obtener proceso por PID"""
        try:
            proc = psutil.Process(pid)
            return Process.from_psutil(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None
    
    def get_count(self) -> int:
        """Obtener cantidad de procesos"""
        return len(list(psutil.process_iter()))
    
    def get_by_name(self, name: str) -> List[Process]:
        """Buscar procesos por nombre"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if name.lower() in proc.info['name'].lower():
                    p = Process.from_psutil(proc)
                    if p:
                        processes.append(p)
            except:
                pass
        return processes
    
    def get_top_cpu(self, n: int = 5) -> List[Process]:
        """Obtener los N procesos con más uso de CPU"""
        self._sort_by = 'cpu_percent'
        self._sort_reverse = True
        return self.get_all(limit=n)
    
    def get_top_memory(self, n: int = 5) -> List[Process]:
        """Obtener los N procesos con más uso de RAM"""
        self._sort_by = 'memory_percent'
        self._sort_reverse = True
        return self.get_all(limit=n)
    
    # ============ UPDATE ============
    def set_sort(self, field: str, reverse: bool = True):
        """Establecer ordenamiento"""
        valid_fields = ['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_mb']
        if field in valid_fields:
            self._sort_by = field
            self._sort_reverse = reverse
    
    def set_filter(self, text: str):
        """Establecer filtro de búsqueda"""
        self._filter_text = text
    
    def set_priority(self, pid: int, priority: int) -> bool:
        """Cambiar prioridad de un proceso (nice value)"""
        try:
            proc = psutil.Process(pid)
            proc.nice(priority)
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, PermissionError):
            return False
    
    # ============ DELETE ============
    def kill(self, pid: int) -> bool:
        """Terminar proceso (SIGKILL)"""
        try:
            proc = psutil.Process(pid)
            proc.kill()
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, PermissionError):
            return False
    
    def terminate(self, pid: int) -> bool:
        """Terminar proceso gracefully (SIGTERM)"""
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, PermissionError):
            return False
    
    def kill_by_name(self, name: str) -> int:
        """Terminar todos los procesos con un nombre"""
        killed = 0
        for proc in self.get_by_name(name):
            if self.kill(proc.pid):
                killed += 1
        return killed
    
    # ============ ESTADÍSTICAS ============
    def get_stats(self) -> Dict:
        """Obtener estadísticas generales de procesos"""
        running = sleeping = stopped = zombie = 0
        total_threads = 0
        
        for proc in psutil.process_iter(['status', 'num_threads']):
            try:
                status = proc.info['status']
                if status == psutil.STATUS_RUNNING:
                    running += 1
                elif status == psutil.STATUS_SLEEPING:
                    sleeping += 1
                elif status == psutil.STATUS_STOPPED:
                    stopped += 1
                elif status == psutil.STATUS_ZOMBIE:
                    zombie += 1
                total_threads += proc.info['num_threads'] or 0
            except:
                pass
        
        return {
            'total': self.get_count(),
            'running': running,
            'sleeping': sleeping,
            'stopped': stopped,
            'zombie': zombie,
            'threads': total_threads
        }


if __name__ == "__main__":
    # Test
    manager = ProcessManager()
    
    # READ
    print(f"Total procesos: {manager.get_count()}")
    
    print("\nTop 5 CPU:")
    for p in manager.get_top_cpu(5):
        print(f"  {p.pid}: {p.name} - CPU: {p.cpu_percent}%")
    
    print("\nTop 5 RAM:")
    for p in manager.get_top_memory(5):
        print(f"  {p.pid}: {p.name} - RAM: {p.memory_mb} MB")
    
    print("\nEstadísticas:")
    stats = manager.get_stats()
    print(f"  {stats}")
    
    # Buscar
    print("\nProcesos 'python':")
    for p in manager.get_by_name('python'):
        print(f"  {p.pid}: {p.name}")
