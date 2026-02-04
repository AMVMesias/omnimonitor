# OmniMonitor - Documentación Técnica

## 📋 Índice
- [Introducción](#introducción)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Librería Principal: Flet](#librería-principal-flet)
- [Modo Escritorio](#-modo-escritorio)
- [Modo Web (Datos Reales)](#-modo-web-datos-reales)
- [Arquitectura](#arquitectura)
- [Dependencias](#dependencias)
- [Cómo Ejecutar](#cómo-ejecutar)

---

## Introducción

**OmniMonitor** es un monitor de sistema multiplataforma que muestra métricas en tiempo real:
- CPU, RAM, Disco, Red, GPU
- Temperatura, frecuencia, velocidades
- Interfaz gráfica moderna con tema oscuro

### Modos de Ejecución

| Modo | Datos | Acceso |
|------|-------|--------|
| 🖥️ **Escritorio** | REALES (psutil) | Aplicación nativa |
| 🌐 **Web** | **REALES** (API HTTP) | Navegador web |

**Ambos modos muestran datos REALES del sistema.**

---

## Estructura del Proyecto

```
Proyecto/
├── app.py                  # Aplicación principal (UI + lógica)
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   └── monitor.py      # Monitor del sistema (psutil)
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── components.py   # Componentes visuales
│   │   └── chart_manager.py # Gestión de gráficos
│   └── server/
│       ├── __init__.py
│       └── api.py          # Servidor API HTTP
├── run.sh                  # Script interactivo
├── run_desktop.sh          # Script modo escritorio
├── run_web.sh              # Script modo web
├── requirements.txt        # Dependencias
└── DOCUMENTACION.md        # Este archivo
```

---

## Librería Principal: Flet

### ¿Qué es Flet?

**Flet** es un framework de UI multiplataforma basado en Flutter que permite crear interfaces con Python para:
- ✅ Windows, macOS, Linux (escritorio)
- ✅ Web (navegador)
- ✅ iOS, Android (móvil)

### Ejemplo básico

```python
import flet as ft

def main(page: ft.Page):
    page.add(ft.Text("¡Hola Mundo!"))

# Modo escritorio
ft.run(main)

# Modo web
ft.run(main, view=ft.AppView.WEB_BROWSER, port=8550)
```

---

## 🖥️ Modo Escritorio

### Características

| Aspecto | Detalles |
|---------|----------|
| **Datos** | REALES (psutil directo) |
| **Ventana** | Aplicación nativa |
| **Puerto** | No necesita |
| **Latencia** | Mínima (local) |

### Cómo funciona

```
┌─────────────────────────────────────┐
│  Aplicación (app.py)                │
│    ↓                                │
│  SystemMonitor (psutil)             │
│    ↓                                │
│  Datos del Sistema Operativo        │
│  (/proc, /sys, nvidia-smi)          │
└─────────────────────────────────────┘
```

### Ejecución

```bash
python app.py
# o
./run_desktop.sh
```

---

## 🌐 Modo Web (Datos Reales)

### Características

| Aspecto | Detalles |
|---------|----------|
| **Datos** | **REALES** (via API HTTP) |
| **API** | http://localhost:8765 |
| **UI** | http://localhost:8550 |
| **Acceso** | Cualquier navegador |

### Arquitectura Backend + Frontend

```
┌─────────────────────────────────────────────────────┐
│ BACKEND (Python)                     Puerto 8765   │
│  • src/server/api.py                               │
│  • psutil → datos reales del sistema               │
│  • API REST: /api/cpu, /api/memory, /api/all       │
└────────────────┬────────────────────────────────────┘
                 │
            HTTP / JSON
                 │
┌────────────────▼────────────────────────────────────┐
│ FRONTEND (Flet WebAssembly)          Puerto 8550   │
│  • app.py + WebMonitor                             │
│  • Peticiones HTTP al backend                      │
│  • Renderiza UI con datos reales                   │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│ NAVEGADOR (Chrome, Firefox, Safari, Edge)          │
│  • Renderiza WebAssembly                           │
│  • Muestra métricas en tiempo real                 │
└─────────────────────────────────────────────────────┘
```

### Endpoints de la API

| Endpoint | Descripción |
|----------|-------------|
| `GET /api/all` | Todas las métricas |
| `GET /api/cpu` | CPU (uso, cores, temp, freq) |
| `GET /api/memory` | Memoria RAM |
| `GET /api/disk` | Disco (uso, velocidad) |
| `GET /api/network` | Red (upload, download) |
| `GET /api/gpu` | GPU (si está disponible) |
| `GET /api/system` | Info del sistema |
| `GET /health` | Estado del servidor |

### Ejemplo de respuesta API

```bash
$ curl http://localhost:8765/api/cpu
```

```json
{
  "usage": 23.4,
  "per_core": [20.0, 17.6, 16.5, 15.7, 31.1, 16.4],
  "count": [6, 12],
  "freq": 2.87,
  "temp": 76.4
}
```

### Ejecución

```bash
python app.py --web
# o
./run_web.sh
```

---

## Arquitectura del Código

### app.py - Aplicación Principal

```python
# Detectar modo de ejecución
IS_WEB = "--web" in sys.argv

# Seleccionar monitor
if IS_WEB:
    monitor = WebMonitor(API_URL)  # Datos via HTTP
else:
    monitor = SystemMonitor()       # Datos via psutil

# UI idéntica para ambos modos
def main(page: ft.Page):
    # ... componentes UI
    
# Iniciar según modo
if IS_WEB:
    # 1. Iniciar servidor API en background
    from src.server.api import run_server_background
    run_server_background(8765)
    
    # 2. Iniciar UI web
    ft.run(main, view=ft.AppView.WEB_BROWSER, port=8550)
else:
    ft.run(main)
```

### src/core/monitor.py - Monitor del Sistema

```python
import psutil

class SystemMonitor:
    def get_cpu_usage(self) -> float:
        return psutil.cpu_percent()
    
    def get_memory_usage(self) -> dict:
        mem = psutil.virtual_memory()
        return {"percent": mem.percent, "used": mem.used, ...}
    
    # ... más métodos
```

### src/server/api.py - Servidor API

```python
import http.server
from src.core.monitor import SystemMonitor

class MonitorAPIHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/cpu':
            data = {"usage": monitor.get_cpu_usage(), ...}
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.wfile.write(json.dumps(data).encode())
```

---

## Dependencias

### requirements.txt

```
flet>=0.21.0      # Framework UI multiplataforma
psutil>=5.9.0     # Monitor del sistema
```

### Instalación

```bash
pip install -r requirements.txt
```

### Descripción de librerías

| Librería | Uso |
|----------|-----|
| **Flet** | Framework UI (Flutter + Python) |
| **psutil** | Acceso a métricas del sistema |
| **urllib** | Peticiones HTTP (modo web) |
| **json** | Serialización de datos |
| **threading** | Servidor API en background |
| **asyncio** | Programación asincrónica |

---

## Cómo Ejecutar

### Opción 1: Script interactivo

```bash
./run.sh
# Seleccionar: 1=Escritorio, 2=Web
```

### Opción 2: Modo Escritorio directo

```bash
./run_desktop.sh
# o
python app.py
```

### Opción 3: Modo Web directo

```bash
./run_web.sh
# o
python app.py --web
```

### URLs en Modo Web

- **API:** http://localhost:8765/api/all
- **UI:** http://localhost:8550

---

## Comparativa Final

| Feature | Escritorio | Web |
|---------|-----------|-----|
| **Datos reales** | ✅ Sí | ✅ **Sí (via API)** |
| **Acceso GPU** | ✅ nvidia-smi | ✅ via API |
| **Temperatura** | ✅ Sí | ✅ via API |
| **Multiplataforma** | ⚠️ Por SO | ✅ Cualquier navegador |
| **Instalación** | ⚠️ Requiere | ✅ No (solo servidor) |
| **Rendimiento** | ✅ Máximo | ✅ Muy bueno |
| **Latencia** | ✅ Local | ⚠️ ~100ms (red local) |

---

## Referencias

- [Documentación oficial de Flet](https://flet.dev)
- [Documentación de psutil](https://psutil.readthedocs.io)
- [Flutter (motor de Flet)](https://flutter.dev)
