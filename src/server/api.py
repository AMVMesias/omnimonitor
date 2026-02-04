"""
Servidor API para OmniMonitor - Datos REALES del sistema
Proporciona métricas vía HTTP para la versión web
"""
import json
import http.server
import socketserver
import threading
import sys
import os

# Agregar el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.core.monitor import SystemMonitor

PORT = 8765
monitor = None

class MonitorAPIHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global monitor
        if monitor is None:
            monitor = SystemMonitor()
            
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        try:
            if self.path == '/api/all':
                data = get_all_metrics()
            elif self.path == '/api/cpu':
                data = {
                    "usage": monitor.get_cpu_usage(),
                    "per_core": monitor.get_cpu_per_core(),
                    "count": monitor.get_cpu_count(),
                    "freq": monitor.get_cpu_freq(),
                    "temp": monitor.get_cpu_temp()
                }
            elif self.path == '/api/memory':
                data = monitor.get_memory_usage()
            elif self.path == '/api/disk':
                data = {
                    "usage": monitor.get_disk_usage(),
                    "info": monitor.get_disk_info(),
                    "io": monitor.get_disk_io()
                }
            elif self.path == '/api/network':
                data = {
                    "speed": monitor.get_network_speed(),
                    "info": monitor.get_network_info()
                }
            elif self.path == '/api/gpu':
                data = monitor.get_gpu_info() or {"name": "No detectada", "usage": 0, "temp": 0}
            elif self.path == '/api/system':
                data = {
                    "info": monitor.get_system_info(),
                    "uptime": str(monitor.get_uptime()),
                    "battery": monitor.get_battery_info()
                }
            elif self.path == '/health':
                data = {"status": "ok", "message": "Server running"}
            else:
                data = {
                    "error": "Endpoint no encontrado",
                    "available": ["/api/all", "/api/cpu", "/api/memory", "/api/disk", "/api/network", "/api/gpu", "/api/system", "/health"]
                }
        except Exception as e:
            data = {"error": str(e)}
        
        self.wfile.write(json.dumps(data).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Silenciar logs


def get_all_metrics():
    """Obtiene todas las métricas REALES del sistema"""
    global monitor
    if monitor is None:
        monitor = SystemMonitor()
    
    return {
        "cpu": {
            "usage": monitor.get_cpu_usage(),
            "per_core": monitor.get_cpu_per_core(),
            "count": monitor.get_cpu_count(),
            "freq": monitor.get_cpu_freq(),
            "temp": monitor.get_cpu_temp()
        },
        "memory": monitor.get_memory_usage(),
        "disk": {
            "usage": monitor.get_disk_usage(),
            "info": monitor.get_disk_info(),
            "io": monitor.get_disk_io()
        },
        "network": {
            "speed": monitor.get_network_speed(),
            "info": monitor.get_network_info()
        },
        "gpu": monitor.get_gpu_info(),
        "system": {
            "info": monitor.get_system_info(),
            "uptime": str(monitor.get_uptime()),
            "battery": monitor.get_battery_info()
        }
    }


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True


_server = None
_server_thread = None

def start_server(port=PORT):
    """Inicia el servidor API"""
    global _server, monitor
    monitor = SystemMonitor()
    
    _server = ThreadedTCPServer(("0.0.0.0", port), MonitorAPIHandler)
    print(f"🌐 API Server: http://localhost:{port}")
    _server.serve_forever()


def run_server_background(port=PORT):
    """Ejecuta el servidor en background (hilo separado)"""
    global _server_thread, monitor
    monitor = SystemMonitor()
    
    _server_thread = threading.Thread(target=start_server, args=(port,), daemon=True)
    _server_thread.start()
    return _server_thread


def stop_server():
    """Detiene el servidor"""
    global _server
    if _server:
        _server.shutdown()
        _server = None


if __name__ == "__main__":
    print(f"🖥️  OmniMonitor API Server")
    print(f"📡 Puerto: {PORT}")
    print(f"🔗 Endpoints:")
    print(f"   GET http://localhost:{PORT}/api/all     - Todas las métricas")
    print(f"   GET http://localhost:{PORT}/api/cpu     - CPU")
    print(f"   GET http://localhost:{PORT}/api/memory  - Memoria")
    print(f"   GET http://localhost:{PORT}/api/disk    - Disco")
    print(f"   GET http://localhost:{PORT}/api/network - Red")
    print(f"   GET http://localhost:{PORT}/api/gpu     - GPU")
    print(f"   GET http://localhost:{PORT}/api/system  - Sistema")
    print(f"   GET http://localhost:{PORT}/health      - Estado")
    print()
    print("Presiona Ctrl+C para detener")
    print()
    
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido")
