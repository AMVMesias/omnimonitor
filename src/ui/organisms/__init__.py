# ==============================================
# OmniMonitor - Atomic Design: ORGANISMS
# ==============================================
# Los organismos son grupos de moléculas que forman
# secciones de interfaz: paneles completos, navegación, grids

from .cpu_panel import create_cpu_card
from .ram_panel import create_ram_card
from .gpu_panel import create_gpu_card
from .disk_panel import create_disk_card
from .network_panel import create_network_chart_card
from .navigation import create_sidebar, create_header

__all__ = [
    'create_cpu_card',
    'create_ram_card',
    'create_gpu_card',
    'create_disk_card',
    'create_network_chart_card',
    'create_sidebar',
    'create_header',
]
