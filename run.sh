#!/bin/bash
# OmniMonitor - Script principal
cd "$(dirname "$0")"

echo "╔══════════════════════════════════════╗"
echo "║       🖥️  OmniMonitor v2.2.0        ║"
echo "║   Monitor de Sistema Multiplataforma ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "Selecciona el modo de ejecución:"
echo ""
echo "  1) 🖥️  Escritorio (Nativo)"
echo "     Datos reales via psutil"
echo ""
echo "  2) 🌐 Web (Navegador)"  
echo "     Datos REALES via API HTTP"
echo ""
read -p "Opción [1]: " opcion

case $opcion in
    2)
        ./run_web.sh
        ;;
    *)
        ./run_desktop.sh
        ;;
esac
