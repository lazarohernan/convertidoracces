#!/bin/bash

echo "🌐 Compartiendo Aplicación - Opciones Simples"
echo "============================================="

# Obtener IP local
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)

echo "✅ Aplicación corriendo en:"
echo "   Local: http://localhost:8501"
echo "   Red local: http://$LOCAL_IP:8501"
echo ""

echo "📱 Para compartir en tu red WiFi:"
echo "   URL: http://$LOCAL_IP:8501"
echo "   ✅ Sin contraseña"
echo "   ✅ Cualquier dispositivo en tu WiFi puede acceder"
echo ""

echo "🌐 Para compartir en internet:"
echo "   1. Regístrate en: https://dashboard.ngrok.com/signup"
echo "   2. Obtén tu authtoken"
echo "   3. Ejecuta: ngrok config add-authtoken TU_TOKEN"
echo "   4. Ejecuta: ngrok http 8501"
echo ""

echo "🔧 Comandos útiles:"
echo "   - Verificar aplicación: curl http://localhost:8501"
echo "   - Detener aplicación: pkill -f streamlit"
echo "   - Ver logs: tail -f streamlit.log" 