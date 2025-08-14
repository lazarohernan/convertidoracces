#!/bin/bash

echo "🌐 Compartiendo Aplicación Web con LocalTunnel"
echo "=============================================="

# Verificar si la aplicación está corriendo
if ! pgrep -f "streamlit" > /dev/null; then
    echo "❌ La aplicación no está corriendo."
    echo "🚀 Iniciando aplicación..."
    source venv/bin/activate
    python start_robust.py &
    sleep 5
fi

echo "✅ Aplicación corriendo en http://localhost:8501"
echo "🌐 Creando túnel público con LocalTunnel..."
echo ""
echo "📋 Información:"
echo "   - URL pública: Se mostrará abajo"
echo "   - Acceso: Cualquier persona con el enlace"
echo "   - Duración: Hasta que presiones Ctrl+C"
echo ""
echo "⚠️  IMPORTANTE:"
echo "   - Cualquier persona puede acceder a tu aplicación"
echo "   - No compartas archivos sensibles"
echo "   - Presiona Ctrl+C para cerrar el túnel"
echo ""

# Crear túnel
lt --port 8501 