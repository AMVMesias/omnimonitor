# ==============================================
# OmniMonitor - UI Package
# ==============================================
# Sistema de componentes basado en Atomic Design
#
# Estructura:
#   - tokens.py    → Colores, tamaños, espaciado (Design Tokens)
#   - atoms/       → Componentes básicos indivisibles
#   - molecules/   → Combinaciones de átomos
#   - organisms/   → Secciones completas de UI
#
# Para usar la nueva estructura:
#   from src.ui.atoms import create_button, create_icon
#   from src.ui.molecules import create_metric_card
#   from src.ui.organisms import create_cpu_card, create_sidebar

# ============ DESIGN TOKENS ============
from .tokens import (
    # Colors
    DARK_BG, CARD_BG, SIDEBAR_BG,
    GREEN_PRIMARY, BLUE_PRIMARY, ORANGE_PRIMARY, RED_PRIMARY, YELLOW_PRIMARY, PURPLE_PRIMARY,
    TEXT_WHITE, TEXT_GRAY, TEXT_DARK_GRAY,
    BORDER_DARK, BORDER_LIGHT,
    NET_DOWNLOAD, NET_UPLOAD,
    # Sizes
    BORDER_RADIUS_SM, BORDER_RADIUS_MD, BORDER_RADIUS_LG, BORDER_RADIUS_XL,
    SPACING_XS, SPACING_SM, SPACING_MD, SPACING_LG, SPACING_XL,
    FONT_SIZE_XS, FONT_SIZE_SM, FONT_SIZE_MD, FONT_SIZE_LG, FONT_SIZE_XL, FONT_SIZE_XXL,
)

# ============ ATOMIC DESIGN LAYERS ============
from . import atoms
from . import molecules
from . import organisms

# ============ BACKWARD COMPATIBILITY ============
# Legacy exports from components.py (for existing code)
from .components import (
    create_circular_progress,
    create_sidebar as legacy_create_sidebar,
    create_header as legacy_create_header,
    create_detail_button as legacy_create_detail_button,
    create_cpu_card as legacy_create_cpu_card,
    create_ram_card as legacy_create_ram_card,
    create_gpu_card as legacy_create_gpu_card,
    create_disk_card as legacy_create_disk_card,
    create_network_chart_card as legacy_create_network_chart_card,
    create_info_row as legacy_create_info_row,
    create_stat_box as legacy_create_stat_box,
)

# ============ CHART MANAGER ============
from .chart_manager import ChartManager

__all__ = [
    # Design Tokens
    'DARK_BG', 'CARD_BG', 'SIDEBAR_BG',
    'GREEN_PRIMARY', 'BLUE_PRIMARY', 'ORANGE_PRIMARY', 'RED_PRIMARY', 'YELLOW_PRIMARY', 'PURPLE_PRIMARY',
    'TEXT_WHITE', 'TEXT_GRAY', 'TEXT_DARK_GRAY',
    # Atomic Design
    'atoms', 'molecules', 'organisms',
    # Chart Manager
    'ChartManager',
]
