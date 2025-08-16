import streamlit as st
import os

# Configuración para archivos grandes
st.set_page_config(
    page_title="Conversor de Archivos - Versión Grande",
    page_icon="📁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurar límites de archivo
os.environ['STREAMLIT_SERVER_MAX_UPLOAD_SIZE'] = '1024'  # 1GB en MB

# Configuración adicional
st.config.set_option('server.maxUploadSize', 1024)
st.config.set_option('server.enableCORS', False)
st.config.set_option('server.enableXsrfProtection', False)

print("✅ Configuración de archivos grandes aplicada")
print("📁 Límite de archivo: 1GB")
print("🚀 Streamlit configurado para archivos pesados")
