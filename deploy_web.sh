#!/bin/bash

# Script para desplegar la aplicación web de conversión de archivos
# Autor: Sistema de Conversión de Archivos
# Fecha: $(date)

echo "🌐 Desplegando Aplicación Web de Conversión de Archivos"
echo "======================================================"

# Función para mostrar ayuda
show_help() {
    echo "Uso: ./deploy_web.sh [OPCIÓN]"
    echo ""
    echo "Opciones:"
    echo "  local       - Ejecutar solo localmente (localhost:8501)"
    echo "  localtunnel - Compartir con LocalTunnel (túnel público, sin registro)"
    echo "  ngrok       - Compartir con ngrok (túnel público, requiere registro)"
    echo "  cloud       - Desplegar en Streamlit Cloud (requiere cuenta)"
    echo "  heroku      - Desplegar en Heroku (requiere cuenta)"
    echo "  help        - Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  ./deploy_web.sh local"
    echo "  ./deploy_web.sh localtunnel"
    echo "  ./deploy_web.sh ngrok"
    echo ""
}

# Función para ejecutar localmente
run_local() {
    echo "🚀 Iniciando aplicación localmente..."
    echo "📍 URL: http://localhost:8501"
    echo "🔄 Presiona Ctrl+C para detener"
    echo ""
    
    source venv/bin/activate
    python start_robust.py
}

# Función para usar ngrok
run_ngrok() {
    echo "🌐 Configurando túnel público con ngrok..."
    echo ""
    
    # Verificar si ngrok está instalado
    if ! command -v ngrok &> /dev/null; then
        echo "❌ ngrok no está instalado. Instalando..."
        brew install ngrok
    fi
    
    # Verificar si la aplicación está corriendo
    if ! pgrep -f "streamlit" > /dev/null; then
        echo "⚠️  La aplicación no está corriendo. Iniciando..."
        echo "🔄 Iniciando aplicación en segundo plano..."
        
        source venv/bin/activate
        nohup python start_robust.py > streamlit.log 2>&1 &
        sleep 5
    fi
    
    echo "✅ Aplicación corriendo en http://localhost:8501"
    echo "🌐 Creando túnel público..."
    echo ""
    echo "📋 Información del túnel:"
    echo "   - URL pública: Se mostrará abajo"
    echo "   - Duración: Hasta que cierres ngrok"
    echo "   - Acceso: Cualquier persona con el enlace"
    echo ""
    echo "⚠️  IMPORTANTE:"
    echo "   - Cualquier persona puede acceder a tu aplicación"
    echo "   - No compartas archivos sensibles"
    echo "   - Cierra ngrok cuando termines"
    echo ""
    
    # Crear túnel con ngrok
    ngrok http 8501
}

# Función para usar LocalTunnel
run_localtunnel() {
    echo "🌐 Configurando túnel público con LocalTunnel..."
    echo ""
    
    # Verificar si localtunnel está instalado
    if ! command -v lt &> /dev/null; then
        echo "❌ LocalTunnel no está instalado. Instalando..."
        npm install -g localtunnel
    fi
    
    # Verificar si la aplicación está corriendo
    if ! pgrep -f "streamlit" > /dev/null; then
        echo "⚠️  La aplicación no está corriendo. Iniciando..."
        echo "🔄 Iniciando aplicación en segundo plano..."
        
        source venv/bin/activate
        nohup python start_robust.py > streamlit.log 2>&1 &
        sleep 5
    fi
    
    echo "✅ Aplicación corriendo en http://localhost:8501"
    echo "🌐 Creando túnel público..."
    echo ""
    echo "📋 Información del túnel:"
    echo "   - URL pública: Se mostrará abajo"
    echo "   - Duración: Hasta que cierres LocalTunnel"
    echo "   - Acceso: Cualquier persona con el enlace"
    echo ""
    echo "⚠️  IMPORTANTE:"
    echo "   - Cualquier persona puede acceder a tu aplicación"
    echo "   - No compartas archivos sensibles"
    echo "   - Cierra LocalTunnel cuando termines"
    echo ""
    
    # Crear túnel con LocalTunnel
    lt --port 8501
}

# Función para Streamlit Cloud
deploy_streamlit_cloud() {
    echo "☁️  Desplegando en Streamlit Cloud..."
    echo ""
    echo "📋 Requisitos:"
    echo "   1. Cuenta en https://share.streamlit.io"
    echo "   2. Repositorio Git con tu código"
    echo "   3. Archivo requirements.txt"
    echo ""
    echo "🔧 Pasos:"
    echo "   1. Sube tu código a GitHub/GitLab"
    echo "   2. Ve a https://share.streamlit.io"
    echo "   3. Conecta tu repositorio"
    echo "   4. Configura el archivo principal: web_interface_robust.py"
    echo ""
    echo "📁 Archivos necesarios:"
    echo "   - requirements.txt (dependencias)"
    echo "   - .streamlit/config.toml (configuración)"
    echo "   - README.md (documentación)"
    echo ""
    
    # Crear requirements.txt si no existe
    if [ ! -f "requirements.txt" ]; then
        echo "📝 Creando requirements.txt..."
        cat > requirements.txt << EOF
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.15.0
altair>=5.0.0
pyodbc>=4.0.39
sqlalchemy>=2.0.0
openpyxl>=3.1.0
xlrd>=2.0.1
EOF
        echo "✅ requirements.txt creado"
    fi
    
    # Crear configuración de Streamlit
    if [ ! -d ".streamlit" ]; then
        mkdir .streamlit
    fi
    
    if [ ! -f ".streamlit/config.toml" ]; then
        echo "📝 Creando configuración de Streamlit..."
        cat > .streamlit/config.toml << EOF
[server]
port = 8501
address = "0.0.0.0"
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
EOF
        echo "✅ Configuración de Streamlit creada"
    fi
    
    echo "🎯 Listo para desplegar en Streamlit Cloud!"
    echo "📤 Sube tu código a GitHub y sigue los pasos en share.streamlit.io"
}

# Función para Heroku
deploy_heroku() {
    echo "🚀 Desplegando en Heroku..."
    echo ""
    echo "📋 Requisitos:"
    echo "   1. Cuenta en Heroku"
    echo "   2. Heroku CLI instalado"
    echo "   3. Repositorio Git"
    echo ""
    
    # Verificar Heroku CLI
    if ! command -v heroku &> /dev/null; then
        echo "❌ Heroku CLI no está instalado."
        echo "📥 Instala desde: https://devcenter.heroku.com/articles/heroku-cli"
        return 1
    fi
    
    # Crear Procfile
    if [ ! -f "Procfile" ]; then
        echo "📝 Creando Procfile..."
        echo "web: streamlit run web_interface_robust.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile
        echo "✅ Procfile creado"
    fi
    
    # Crear runtime.txt
    if [ ! -f "runtime.txt" ]; then
        echo "📝 Creando runtime.txt..."
        echo "python-3.11.7" > runtime.txt
        echo "✅ runtime.txt creado"
    fi
    
    echo "🔧 Pasos para desplegar:"
    echo "   1. git init"
    echo "   2. git add ."
    echo "   3. git commit -m 'Initial commit'"
    echo "   4. heroku create tu-app-name"
    echo "   5. git push heroku main"
    echo ""
    echo "📚 Más información: https://devcenter.heroku.com/articles/getting-started-with-python"
}

# Procesar argumentos
case "${1:-help}" in
    "local")
        run_local
        ;;
    "localtunnel")
        run_localtunnel
        ;;
    "ngrok")
        run_ngrok
        ;;
    "cloud")
        deploy_streamlit_cloud
        ;;
    "heroku")
        deploy_heroku
        ;;
    "help"|*)
        show_help
        ;;
esac 