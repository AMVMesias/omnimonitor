#!/bin/bash
# OmniMonitor - Ejecutar en modo WEB
# Datos REALES via API HTTP

cd "$(dirname "$0")"

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "🌐 OmniMonitor - Modo Web"
echo "   Datos REALES via servidor API"
echo ""
echo "📡 API:  http://localhost:8765/api/all"
echo "📍 UI:   http://localhost:8550"
echo ""

# Verificar dependencias
if ! python -c "import flet, psutil" 2>/dev/null; then
    echo "📦 Instalando dependencias..."
    pip install -r requirements.txt --quiet
fi

# Suprimir warnings de GTK
export GTK_A11Y=none 2>/dev/null

python app.py --web 2>/dev/null
