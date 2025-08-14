#!/bin/bash

echo "🌐 Obteniendo URL del túnel LocalTunnel..."
echo "=========================================="

# Verificar si hay un túnel activo
if pgrep -f "lt --port 8501" > /dev/null; then
    echo "✅ Túnel LocalTunnel activo detectado"
    echo ""
    echo "📋 Información del túnel:"
    echo "   - Puerto local: 8501"
    echo "   - URL local: http://localhost:8501"
    echo ""
    echo "🔍 Buscando URL pública..."
    echo ""
    echo "⚠️  Si no ves la URL pública, ejecuta manualmente:"
    echo "   lt --port 8501"
    echo ""
    echo "📱 Para compartir, copia la URL que aparece arriba"
    echo "   (formato: https://abc123.loca.lt)"
else
    echo "❌ No hay túnel LocalTunnel activo"
    echo ""
    echo "🚀 Para crear un túnel, ejecuta:"
    echo "   ./share_app.sh"
    echo "   o"
    echo "   lt --port 8501"
fi 