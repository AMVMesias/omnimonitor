#!/bin/bash
# OmniMonitor - Ejecutar en modo ESCRITORIO
# Datos reales del sistema via psutil

cd "$(dirname "$0")"

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "🖥️  OmniMonitor - Modo Escritorio"
echo "   Datos REALES del sistema"
echo ""

# Verificar dependencias
if ! python -c "import flet, psutil" 2>/dev/null; then
    echo "📦 Instalando dependencias..."
    pip install -r requirements.txt --quiet
fi

# Suprimir warnings de GTK
export GTK_A11Y=none 2>/dev/null

python app.py 2>/dev/null
