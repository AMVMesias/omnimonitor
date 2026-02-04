# OmniMonitor - Documentación Técnica

## 📋 Índice
- [Introducción](#introducción)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Atomic Design (Frontend)](#-atomic-design-frontend)
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

| Modo             | Datos                 | Acceso            |
| ---------------- | --------------------- | ----------------- |
| 🖥️ **Escritorio** | REALES (psutil)       | Aplicación nativa |
| 🌐 **Web**        | **REALES** (API HTTP) | Navegador web     |

**Ambos modos muestran datos REALES del sistema.**

---

## Estructura del Proyecto

```
Proyecto/
├── app.py                      # Aplicación principal (UI + lógica)
├── src/
│   ├── core/
│   │   └── monitor.py          # Monitor del sistema (psutil)
│   ├── ui/                     # Frontend con Atomic Design
│   │   ├── tokens.py           # Design Tokens (colores, tamaños)
│   │   ├── atoms/              # ⚛️ Componentes básicos
│   │   │   ├── button.py
│   │   │   ├── text.py
│   │   │   ├── icon.py
│   │   │   ├── input.py
│   │   │   ├── progress.py
│   │   │   └── divider.py
│   │   ├── molecules/          # 🧬 Combinaciones de átomos
│   │   │   ├── metric_card.py
│   │   │   ├── stat_row.py
│   │   │   ├── stat_box.py
│   │   │   └── chart.py
│   │   ├── organisms/          # 🦠 Secciones completas
│   │   │   ├── cpu_panel.py
│   │   │   ├── ram_panel.py
│   │   │   ├── gpu_panel.py
│   │   │   ├── disk_panel.py
│   │   │   ├── network_panel.py
│   │   │   └── navigation.py
│   │   ├── components.py       # (Legacy - compatibilidad)
│   │   └── chart_manager.py    # Gestión de gráficos
│   ├── crud/                   # CRUD de datos
│   │   ├── alerts.py
│   │   ├── processes.py
│   │   └── history.py
│   ├── database/
│   │   └── db.py               # Base de datos SQLite
│   └── server/
│       └── api.py              # Servidor API HTTP
├── docs/                       # Documentación
├── requirements.txt            # Dependencias
└── run.sh                      # Scripts de ejecución
```

---

## 🔬 Atomic Design (Frontend)

### ¿Qué es Atomic Design?

**Atomic Design** es una metodología creada por Brad Frost para diseñar sistemas de componentes UI. Organiza los componentes en 5 niveles jerárquicos, de más simple a más complejo:

```
⚛️ Átomos → 🧬 Moléculas → 🦠 Organismos → 📄 Templates → 📱 Pages
```

### Implementación en OmniMonitor

| Nivel           | Descripción                      | Ejemplos                                |
| --------------- | -------------------------------- | --------------------------------------- |
| **⚛️ Atoms**     | Elementos básicos e indivisibles | Botones, textos, iconos, inputs         |
| **🧬 Molecules** | Combinaciones de átomos          | Tarjeta de métrica, fila de estadística |
| **🦠 Organisms** | Grupos de moléculas              | Panel de CPU, Sidebar, Header           |
| **📱 Pages**     | Vistas completas                 | Dashboard, vista de alertas             |

### Estructura de Archivos

```
src/ui/
├── tokens.py           # 🎨 Design Tokens (colores, tamaños, espaciado)
│
├── atoms/              # ⚛️ ÁTOMOS
│   ├── button.py       # create_button, create_icon_button, create_detail_button
│   ├── text.py         # create_title, create_subtitle, create_label, create_value
│   ├── icon.py         # create_icon, create_icon_with_bg
│   ├── input.py        # create_text_input, create_dropdown, create_switch
│   ├── progress.py     # create_progress_ring, create_progress_bar
│   └── divider.py      # create_divider, create_spacer
│
├── molecules/          # 🧬 MOLÉCULAS
│   ├── metric_card.py  # Tarjeta de métrica con anillo de progreso
│   ├── stat_row.py     # Filas de estadísticas (label + valor)
│   ├── stat_box.py     # Cajas compactas de estadísticas
│   └── chart.py        # Mini gráficos y grupos de barras
│
└── organisms/          # 🦠 ORGANISMOS
    ├── cpu_panel.py    # Panel completo de CPU
    ├── ram_panel.py    # Panel completo de RAM
    ├── gpu_panel.py    # Panel completo de GPU
    ├── disk_panel.py   # Panel completo de Disco
    ├── network_panel.py # Panel de red con gráfico
    └── navigation.py   # Sidebar + Header de la app
```

### Design Tokens (tokens.py)

Los **Design Tokens** son variables centralizadas que definen el sistema de diseño:

```python
# Colores del tema oscuro
DARK_BG = "#0D1117"        # Fondo principal
CARD_BG = "#161B22"        # Fondo de tarjetas
GREEN_PRIMARY = "#4ADE80"  # CPU, éxito
BLUE_PRIMARY = "#60A5FA"   # Enlaces, info
ORANGE_PRIMARY = "#FB923C" # GPU, advertencias
RED_PRIMARY = "#F87171"    # Errores

# Tamaños
BORDER_RADIUS_LG = 15
SPACING_LG = 15
FONT_SIZE_XL = 18
```

### Ejemplo de Uso

```python
# Importar desde cada nivel
from src.ui.atoms import create_button, create_icon
from src.ui.molecules import create_metric_card
from src.ui.organisms import create_cpu_card, create_sidebar

# Crear un botón (átomo)
btn = create_button("Guardar", on_click=save_handler, variant="primary")

# Crear una tarjeta de métrica (molécula)
card = create_metric_card(
    title="CPU",
    icon=ft.Icons.MEMORY,
    color=GREEN_PRIMARY,
    progress_value=0.75
)

# Crear panel completo de CPU (organismo)
cpu_panel = create_cpu_card(
    cpu_name=ft.Text("Intel Core i7"),
    progress_ring=ring,
    percent_text=ft.Text("45%"),
    temp_text=ft.Text("65°C"),
    speed_text=ft.Text("3.6 GHz"),
    on_details_click=show_details
)
```

### Beneficios de Atomic Design

| Beneficio            | Descripción                                       |
| -------------------- | ------------------------------------------------- |
| ✅ **Reutilización**  | Componentes se usan en múltiples partes de la app |
| ✅ **Consistencia**   | Estilos centralizados en Design Tokens            |
| ✅ **Mantenibilidad** | Cambios en un átomo se reflejan en toda la app    |
| ✅ **Testing**        | Componentes pequeños son más fáciles de probar    |
| ✅ **Documentación**  | Estructura clara y autodocumentada                |
| ✅ **Escalabilidad**  | Agregar nuevos componentes es sistemático         |

### Principios de Diseño Aplicados

Esta arquitectura cumple con los principios de:

- **HCI** (Human-Computer Interaction): Componentes intuitivos y consistentes
- **UX/UI**: Diseño modular que mejora la experiencia del usuario
- **IxD** (Interaction Design): Interacciones predecibles y reutilizables
- **UCD** (User-Centered Design): Componentes centrados en las necesidades del usuario

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

| Aspecto      | Detalles                |
| ------------ | ----------------------- |
| **Datos**    | REALES (psutil directo) |
| **Ventana**  | Aplicación nativa       |
| **Puerto**   | No necesita             |
| **Latencia** | Mínima (local)          |

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

| Aspecto    | Detalles                  |
| ---------- | ------------------------- |
| **Datos**  | **REALES** (via API HTTP) |
| **API**    | http://localhost:8765     |
| **UI**     | http://localhost:8550     |
| **Acceso** | Cualquier navegador       |

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

| Endpoint           | Descripción                  |
| ------------------ | ---------------------------- |
| `GET /api/all`     | Todas las métricas           |
| `GET /api/cpu`     | CPU (uso, cores, temp, freq) |
| `GET /api/memory`  | Memoria RAM                  |
| `GET /api/disk`    | Disco (uso, velocidad)       |
| `GET /api/network` | Red (upload, download)       |
| `GET /api/gpu`     | GPU (si está disponible)     |
| `GET /api/system`  | Info del sistema             |
| `GET /health`      | Estado del servidor          |

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

| Librería      | Uso                             |
| ------------- | ------------------------------- |
| **Flet**      | Framework UI (Flutter + Python) |
| **psutil**    | Acceso a métricas del sistema   |
| **urllib**    | Peticiones HTTP (modo web)      |
| **json**      | Serialización de datos          |
| **threading** | Servidor API en background      |
| **asyncio**   | Programación asincrónica        |

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

| Feature             | Escritorio   | Web                   |
| ------------------- | ------------ | --------------------- |
| **Datos reales**    | ✅ Sí         | ✅ **Sí (via API)**    |
| **Acceso GPU**      | ✅ nvidia-smi | ✅ via API             |
| **Temperatura**     | ✅ Sí         | ✅ via API             |
| **Multiplataforma** | ⚠️ Por SO     | ✅ Cualquier navegador |
| **Instalación**     | ⚠️ Requiere   | ✅ No (solo servidor)  |
| **Rendimiento**     | ✅ Máximo     | ✅ Muy bueno           |
| **Latencia**        | ✅ Local      | ⚠️ ~100ms (red local)  |

---

## Referencias

- [Documentación oficial de Flet](https://flet.dev)
- [Documentación de psutil](https://psutil.readthedocs.io)
- [Flutter (motor de Flet)](https://flutter.dev)
