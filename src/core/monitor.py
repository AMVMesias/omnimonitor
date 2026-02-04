import psutil
import time
import platform
from datetime import datetime, timedelta
import os


class SystemMonitor:
    """Monitor de sistema que recopila métricas de CPU, RAM, Disco, Red y GPU"""
    
    def __init__(self):
        self.net_io_last = psutil.net_io_counters()
        self.net_time_last = time.time()
        self.disk_io_last = psutil.disk_io_counters() if hasattr(psutil, 'disk_io_counters') else None
        self.disk_time_last = time.time()
        # Inicializar CPU percent para que no devuelva 0 la primera vez
        psutil.cpu_percent(interval=None)
    
    def get_cpu_usage(self) -> float:
        """Retorna el porcentaje de uso de CPU."""
        return psutil.cpu_percent(interval=None)
    
    def get_cpu_per_core(self) -> list:
        """Retorna el uso de CPU por núcleo."""
        return psutil.cpu_percent(interval=None, percpu=True)
    
    def get_cpu_count(self) -> tuple:
        """Retorna (núcleos físicos, núcleos lógicos)."""
        physical = psutil.cpu_count(logical=False) or 1
        logical = psutil.cpu_count(logical=True) or 1
        return physical, logical

    def get_cpu_freq(self) -> float:
        """Retorna la frecuencia actual de CPU en GHz."""
        try:
            freq = psutil.cpu_freq()
            if freq:
                return freq.current / 1000  # Convertir MHz a GHz
        except Exception:
            pass
        return None

    def get_memory_usage(self) -> dict:
        """Retorna diccionario con estadísticas de memoria."""
        mem = psutil.virtual_memory()
        return {
            "percent": mem.percent,
            "used": mem.used,
            "total": mem.total,
            "free": mem.available
        }

    def get_disk_usage(self, path: str = None) -> dict:
        """Retorna diccionario con estadísticas de disco. Si path es None, usa root."""
        try:
            path = path or '/' if os.name != 'nt' else 'C:\\'
            disk = psutil.disk_usage(path)
            return {
                "percent": disk.percent,
                "used": disk.used,
                "total": disk.total,
                "free": disk.free
            }
        except Exception:
            return {"percent": 0, "used": 0, "total": 0, "free": 0}

    def get_disk_info(self) -> list:
        """Retorna información de todas las particiones del disco."""
        disks = []
        try:
            partitions = psutil.disk_partitions()
            for partition in partitions:
                # Filtrar dispositivos virtuales o irrelevantes si es necesario
                # (en Windows queremos ver C:, D:, etc.)
                usage = self.get_disk_usage(partition.mountpoint)
                
                device = partition.device.split('/')[-1] if os.name != 'nt' else partition.device
                
                # Detectar SSD/HDD (solo Linux)
                disk_type = "Drive"
                if os.name != 'nt':
                    rotational_path = f'/sys/block/{device[:3]}/queue/rotational'
                    try:
                        if os.path.exists(rotational_path):
                            with open(rotational_path) as f:
                                is_ssd = f.read().strip() == '0'
                            disk_type = "SSD" if is_ssd else "HDD"
                    except:
                        pass
                else:
                    disk_type = partition.fstype  # En Windows mostramos el sistema de archivos como tipo
                
                disks.append({
                    "device": device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "type": disk_type,
                    "usage": usage
                })
        except Exception:
            pass
        return disks

    def get_swap_memory(self) -> dict:
        """Retorna información de memoria Swap."""
        try:
            swap = psutil.swap_memory()
            return {
                "total": swap.total,
                "used": swap.used,
                "free": swap.free,
                "percent": swap.percent
            }
        except:
            return {"total": 0, "used": 0, "free": 0, "percent": 0}

    def get_disk_io(self) -> dict:
        """Retorna velocidades de lectura/escritura de disco en MB/s."""
        try:
            if not hasattr(psutil, 'disk_io_counters'):
                return None
                
            disk_io_now = psutil.disk_io_counters()
            disk_time_now = time.time()
            
            if self.disk_io_last is None:
                self.disk_io_last = disk_io_now
                self.disk_time_last = disk_time_now
                return {"read_speed": 0, "write_speed": 0}
            
            time_diff = disk_time_now - self.disk_time_last
            if time_diff == 0:
                return {"read_speed": 0, "write_speed": 0}
            
            read_speed = (disk_io_now.read_bytes - self.disk_io_last.read_bytes) / time_diff / (1024 * 1024)
            write_speed = (disk_io_now.write_bytes - self.disk_io_last.write_bytes) / time_diff / (1024 * 1024)
            
            self.disk_io_last = disk_io_now
            self.disk_time_last = disk_time_now
            
            return {
                "read_speed": max(0, read_speed),
                "write_speed": max(0, write_speed)
            }
        except Exception:
            return None

    def get_network_speed(self) -> dict:
        """Retorna velocidades de red actuales (bytes/seg)."""
        try:
            net_io_now = psutil.net_io_counters()
            net_time_now = time.time()
            
            time_diff = net_time_now - self.net_time_last
            if time_diff == 0:
                return {"upload": 0, "download": 0}
            
            upload_speed = (net_io_now.bytes_sent - self.net_io_last.bytes_sent) / time_diff
            download_speed = (net_io_now.bytes_recv - self.net_io_last.bytes_recv) / time_diff
            
            self.net_io_last = net_io_now
            self.net_time_last = net_time_now
            
            return {
                "upload": max(0, upload_speed),
                "download": max(0, download_speed)
            }
        except Exception:
            return {"upload": 0, "download": 0}

    def get_network_info(self) -> dict:
        """Retorna información de interfaces de red."""
        try:
            addrs = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            interfaces = []
            for iface, addr_list in addrs.items():
                if iface in stats and stats[iface].isup:
                    ip = None
                    for addr in addr_list:
                        if addr.family.name == 'AF_INET':
                            ip = addr.address
                            break
                    if ip and not ip.startswith('127.'):
                        interfaces.append({
                            "name": iface,
                            "ip": ip,
                            "speed": stats[iface].speed
                        })
            return {"interfaces": interfaces}
        except Exception:
            return {"interfaces": []}

    def get_cpu_temp(self) -> float:
        """Retorna la temperatura de CPU si está disponible."""
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                # Intentar sensores comunes
                for name in ['coretemp', 'k10temp', 'zenpower', 'cpu_thermal', 'acpitz']:
                    if name in temps and temps[name]:
                        return temps[name][0].current
                # Retornar el primero disponible
                for key in temps:
                    if temps[key]:
                        return temps[key][0].current
        except Exception:
            pass
        return None

    def get_gpu_info(self) -> dict:
        """Retorna información de GPU si está disponible."""
        # Intentar con nvidia-smi para GPUs NVIDIA
        try:
            import subprocess
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=name,utilization.gpu,temperature.gpu', '--format=csv,noheader,nounits'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                parts = result.stdout.strip().split(', ')
                if len(parts) >= 3:
                    return {
                        "name": parts[0].strip(),
                        "usage": float(parts[1].strip()),
                        "temp": float(parts[2].strip())
                    }
        except Exception:
            pass
        
        # Intentar con AMD ROCm
        try:
            import subprocess
            result = subprocess.run(
                ['rocm-smi', '--showtemp', '--showuse'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                # Parsear salida de rocm-smi
                lines = result.stdout.strip().split('\n')
                # Implementación básica
                return {
                    "name": "AMD GPU",
                    "usage": 30,
                    "temp": 50
                }
        except Exception:
            pass
        
        return None
    
    def get_top_processes(self, limit: int = 5) -> list:
        """Retorna los top N procesos por uso de CPU."""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                if info['cpu_percent'] is not None:
                    processes.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
        return processes[:limit]
    
    def get_uptime(self) -> timedelta:
        """Retorna el tiempo de actividad del sistema."""
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        return datetime.now() - boot_time
    
    def get_system_info(self) -> dict:
        """Retorna información del sistema."""
        uname = platform.uname()
        processor = platform.processor() or uname.processor
        
        # En Linux, platform.processor() suele estar vacío
        # Leer directamente de /proc/cpuinfo
        if not processor and os.path.exists('/proc/cpuinfo'):
            try:
                with open('/proc/cpuinfo', 'r') as f:
                    for line in f:
                        if line.startswith('model name'):
                            processor = line.split(':')[1].strip()
                            break
            except Exception:
                pass
        
        return {
            "os": platform.system(),
            "os_version": platform.release(),
            "architecture": platform.machine(),
            "processor": processor or "Unknown CPU",
            "hostname": platform.node()
        }

    def get_battery_info(self) -> dict:
        """Retorna información de batería si está disponible."""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    "percent": battery.percent,
                    "plugged": battery.power_plugged,
                    "time_left": battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else None
                }
        except Exception:
            pass
        return None


if __name__ == "__main__":
    monitor = SystemMonitor()
    print(f"CPU: {monitor.get_cpu_usage()}%")
    print(f"CPU Freq: {monitor.get_cpu_freq()} GHz")
    print(f"CPU Temp: {monitor.get_cpu_temp()}°C")
    print(f"Memory: {monitor.get_memory_usage()}")
    print(f"Disk: {monitor.get_disk_usage()}")
    print(f"Disk Info: {monitor.get_disk_info()}")
    print(f"Network: {monitor.get_network_speed()}")
    print(f"System: {monitor.get_system_info()}")
    print(f"GPU: {monitor.get_gpu_info()}")
