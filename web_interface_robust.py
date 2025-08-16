#!/usr/bin/env python3
"""
Interfaz Web Robusta para el Sistema de Conversión de Archivos
============================================================

Interfaz gráfica moderna y robusta para gestionar y visualizar la conversión de archivos
a diferentes formatos de base de datos.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
import os
from datetime import datetime
import json
try:
    from src.writers.mysql_writer import MySQLWriter
    from src.ui.mysql_config import MySQLConfigUI
    from src.utils.data_integrity import DataIntegrityChecker
    MYSQL_AVAILABLE = True
except ImportError as e:
    print(f"MySQL features not available: {e}")
    MYSQL_AVAILABLE = False
    MySQLWriter = None
    MySQLConfigUI = None
    DataIntegrityChecker = None
import time
import subprocess

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.converter import FileConverter
from src.readers.robust_access_reader import RobustAccessReader
from src.utils.logger import setup_logger
from src.utils.config import Config

# Inicializar componentes nuevos solo si están disponibles
mysql_ui = MySQLConfigUI() if MYSQL_AVAILABLE and MySQLConfigUI else None
integrity_checker = DataIntegrityChecker() if MYSQL_AVAILABLE and DataIntegrityChecker else None

def convert_to_mysql_by_year(file_path, db_config, naming_config):
    """
    Convierte archivos Access por años y los sube directamente a MySQL
    """
    try:
        # Inicializar writer de MySQL
        mysql_writer = MySQLWriter(db_config)
        
        # Verificar conexión
        test_result = mysql_writer.test_connection()
        if not test_result['success']:
            return {
                'success': False,
                'message': f'❌ Error: No se pudo conectar a MySQL - {test_result["message"]}',
                'details': None
            }
        
        # Inicializar conversor
        converter = FileConverter()
        
        # Realizar conversión por años usando el método existente
        result = converter.convert_access_by_year(
            input_path=file_path,
            output_format='sql',  # Generar SQL temporalmente
            output_dir='/tmp',     # Directorio temporal
            naming_config=naming_config
        )
        
        if result['success']:
            # Procesar cada archivo generado y subirlo a MySQL
            uploaded_tables = []
            failed_tables = []
            
            for file_info in result['files_created']:
                file_path_sql = file_info['path']
                table_name = Path(file_path_sql).stem
                
                try:
                    # Leer el archivo SQL y ejecutarlo en MySQL
                    with open(file_path_sql, 'r', encoding='utf-8') as f:
                        sql_content = f.read()
                    
                    # Ejecutar en MySQL
                    exec_result = mysql_writer.execute_sql(sql_content)
                    
                    if exec_result['success']:
                        uploaded_tables.append({
                            'name': table_name,
                            'statements': exec_result['statements_executed']
                        })
                    else:
                        failed_tables.append({
                            'name': table_name,
                            'error': exec_result.get('error', 'Error desconocido')
                        })
                    
                    # Limpiar archivo temporal
                    if os.path.exists(file_path_sql):
                        os.remove(file_path_sql)
                        
                except Exception as table_error:
                    failed_tables.append({
                        'name': table_name,
                        'error': str(table_error)
                    })
            
            if uploaded_tables:
                return {
                    'success': True,
                    'message': f'✅ {len(uploaded_tables)} tablas subidas exitosamente a MySQL',
                    'details': {
                        'database': db_config['database'],
                        'host': db_config['host'],
                        'tables_uploaded': uploaded_tables,
                        'tables_failed': failed_tables,
                        'total_success': len(uploaded_tables),
                        'total_failed': len(failed_tables)
                    }
                }
            else:
                return {
                    'success': False,
                    'message': f'❌ Error: No se pudo subir ninguna tabla. {len(failed_tables)} errores.',
                    'details': {'failed_tables': failed_tables}
                }
        else:
            return result
            
    except Exception as e:
        return {
            'success': False,
            'message': f'❌ Error durante conversión MySQL: {str(e)}',
            'details': {'error': str(e)}
        }

# Configurar página con sidebar siempre visible
st.set_page_config(
    page_title="Sistema de Conversión de Archivos - Robusto",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS minimalista y moderno
st.markdown("""
<style>
    /* Diseño minimalista general */
    .main {
        padding: 1rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Header simple */
    .main-header {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        border: 1px solid #e9ecef;
        text-align: center;
    }
    
    /* Tarjetas simples */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        margin: 0.5rem 0;
        text-align: center;
    }
    
    /* Sidebar limpio y siempre visible */
    .sidebar .sidebar-content {
        background: #f8f9fa;
        border-right: 1px solid #e9ecef;
        position: fixed;
        width: 300px;
        height: 100vh;
        overflow-y: auto;
    }
    
    /* Asegurar que el contenido principal no se superponga */
    .main .block-container {
        margin-left: 320px;
    }
    
    /* Botones generales (para el contenido principal) */
    .main .stButton > button {
        background: #007bff !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        transition: background 0.2s ease !important;
        margin-bottom: 0.5rem !important;
    }
    
    .main .stButton > button:hover {
        background: #0056b3 !important;
    }
    
    /* Botones de navegación en sidebar - SIN COLOR */
    .sidebar .stButton > button {
        background: transparent !important;
        color: #212529 !important;
        border: 1px solid #dee2e6 !important;
        font-size: 0.9rem !important;
        box-shadow: none !important;
        border-radius: 4px !important;
        padding: 0.5rem 1rem !important;
        font-weight: normal !important;
    }
    
    .sidebar .stButton > button:hover {
        background: #f8f9fa !important;
        border-color: #adb5bd !important;
    }
    
    /* Botones de acción en sidebar (Recargar, Limpiar caché) */
    .sidebar .stButton > button:contains("🔄"), 
    .sidebar .stButton > button:contains("🧹") {
        background: #f8f9fa !important;
        color: #495057 !important;
        border: 1px solid #dee2e6 !important;
        font-size: 0.8rem !important;
    }
    
    /* Mensajes simples */
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 6px;
        border: 1px solid #c3e6cb;
        margin: 0.5rem 0;
    }
    
    .error-message {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 6px;
        border: 1px solid #f5c6cb;
        margin: 0.5rem 0;
    }
    }
    
    .info-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    }
    
    .file-card {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 2px solid #e9ecef;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    
    .file-card:hover {
        border-color: #667eea;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    }
    
    .progress-container {
        background: #f8f9fa;
        border-radius: 1rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Configurar logging
setup_logger(log_level="INFO")

# Inicializar session state
if 'converter' not in st.session_state:
    st.session_state.converter = FileConverter()

if 'config' not in st.session_state:
    st.session_state.config = Config()

def main():
    """Función principal de la aplicación"""
    
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>🔄 Sistema de Conversión de Archivos</h1>
        <p>Conversión robusta y confiable de archivos a formatos de base de datos</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar colapsable
    with st.sidebar:
        # Botón para mostrar/ocultar menú
        if 'sidebar_expanded' not in st.session_state:
            st.session_state.sidebar_expanded = True
        
        if st.button("☰ Menú", use_container_width=True):
            st.session_state.sidebar_expanded = not st.session_state.sidebar_expanded
            st.rerun()
        
        # Menú expandible
        if st.session_state.sidebar_expanded:
            st.markdown("**Navegación**")
            
            # Botones de navegación
            if st.button("🏠 Dashboard", use_container_width=True):
                st.session_state.page = "🏠 Dashboard"
                st.rerun()
            
            if st.button("📁 Convertir", use_container_width=True):
                st.session_state.page = "📁 Convertir"
                st.rerun()
            
            if st.button("📋 Visualizar", use_container_width=True):
                st.session_state.page = "📋 Visualizar"
                st.rerun()
            
            if st.button("📊 Resultados", use_container_width=True):
                st.session_state.page = "📊 Resultados"
                st.rerun()
            
            if st.button("📅 Conversión por Años", use_container_width=True):
                st.session_state.page = "📅 Conversión por Años"
                st.rerun()
            
            if st.button("⚙️ Configuración", use_container_width=True):
                st.session_state.page = "⚙️ Configuración"
                st.rerun()
            
            st.markdown("---")
            
            # Estado del sistema
            access_reader = RobustAccessReader()
            support_info = access_reader.check_access_support()
            
            if support_info['supported']:
                st.success("✅ Access disponible")
            else:
                st.error("❌ Access no disponible")
            
            # Archivos
            input_files = get_input_files()
            output_files = get_output_files()
            
            st.markdown(f"**Archivos:** {len(input_files)} entrada, {len(output_files)} salida")
            
            st.markdown("---")
            
            # Gestión de archivos
            st.markdown("**🗂️ Gestión de Archivos**")
            
            # Eliminar archivos de entrada
            if input_files:
                with st.expander("🗑️ Eliminar archivos de entrada"):
                    for file_info in input_files:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"📄 {file_info['name']} ({file_info['size']:.1f} MB)")
                        with col2:
                            if st.button(f"❌", key=f"del_input_{file_info['name']}"):
                                try:
                                    file_path = f"data/input/{file_info['name']}"
                                    os.remove(file_path)
                                    st.success(f"✅ {file_info['name']} eliminado")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error eliminando {file_info['name']}: {str(e)}")
            
            # Eliminar archivos de salida
            if output_files:
                with st.expander("🗑️ Eliminar archivos de salida"):
                    for file_info in output_files:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"📄 {file_info['name']} ({file_info['size']:.1f} MB)")
                        with col2:
                            if st.button(f"❌", key=f"del_output_{file_info['name']}"):
                                try:
                                    file_path = f"data/output/{file_info['name']}"
                                    os.remove(file_path)
                                    st.success(f"✅ {file_info['name']} eliminado")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error eliminando {file_info['name']}: {str(e)}")
            
            # Eliminar todos los archivos
            if input_files or output_files:
                st.markdown("---")
                if st.button("🗑️ Eliminar todos los archivos", type="secondary", use_container_width=True):
                    try:
                        # Eliminar archivos de entrada
                        for file_info in input_files:
                            file_path = f"data/input/{file_info['name']}"
                            if os.path.exists(file_path):
                                os.remove(file_path)
                        
                        # Eliminar archivos de salida
                        for file_info in output_files:
                            file_path = f"data/output/{file_info['name']}"
                            if os.path.exists(file_path):
                                os.remove(file_path)
                        
                        st.success("✅ Todos los archivos eliminados")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error eliminando archivos: {str(e)}")
            
            st.markdown("---")
            
            # Acciones del sistema
            st.markdown("**⚙️ Sistema**")
            
            if st.button("🔄 Recargar", use_container_width=True):
                st.rerun()
            
            if st.button("🧹 Limpiar caché", use_container_width=True):
                st.session_state.clear()
                st.rerun()
    
    # Navegación de páginas usando session_state
    if 'page' not in st.session_state:
        st.session_state.page = "🏠 Dashboard"
    
    page = st.session_state.page
    
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "📁 Convertir":
        show_converter()
    elif page == "📋 Visualizar":
        show_data_viewer()
    elif page == "📊 Resultados":
        show_results()
    elif page == "📅 Conversión por Años":
        if 'show_year_conversion' in globals():
            show_year_conversion()
        else:
            st.error("La función de conversión por años no está disponible en esta ejecución. Guarda el archivo y recarga la app.")
    elif page == "⚙️ Configuración":
        show_configuration()

def show_dashboard():
    """Dashboard minimalista"""
    st.markdown("## Dashboard")
    
    # Métricas simples
    input_files = get_input_files()
    output_files = get_output_files()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Archivos entrada", len(input_files))
    
    with col2:
        st.metric("Archivos salida", len(output_files))
    
    with col3:
        total_size = sum(f['size'] for f in input_files)
        st.metric("Tamaño total", f"{total_size:.1f} MB")
    
    # Archivos recientes
    st.markdown("**Archivos recientes:**")
    
    if input_files:
        recent_files = input_files[-3:]  # Solo últimos 3
        
        for file_info in recent_files:
            st.write(f"📄 {file_info['name']} ({file_info['size']:.1f} MB)")
    else:
        st.info("No hay archivos de entrada")
        st.write("Coloca archivos en `data/input/` para comenzar")

def show_converter():
    """Interfaz de conversión minimalista"""
    st.markdown("## Convertir Archivos")
    
    # Subir archivos
    st.markdown("### 📤 Subir Archivos")
    uploaded_files = st.file_uploader(
        "Selecciona archivos para subir:",
        type=['csv', 'xlsx', 'xls', 'json', 'accdb', 'mdb'],
        accept_multiple_files=True,
        help="Puedes subir múltiples archivos a la vez"
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            # Guardar archivo subido
            input_dir = Path("data/input")
            input_dir.mkdir(exist_ok=True)
            
            file_path = input_dir / uploaded_file.name
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.success(f"✅ Archivo subido: {uploaded_file.name}")
    
    # Verificar archivos disponibles
    input_files = get_input_files()
    if not input_files:
        st.error("No hay archivos de entrada disponibles")
        st.write("Sube archivos usando el botón de arriba o colócalos en la carpeta `data/input/`")
        return
    
    # Selección de archivo
    st.markdown("**Seleccionar archivo:**")
    
    file_options = [f"{f['name']} ({f['size']:.1f} MB)" for f in input_files]
    selected_file = st.selectbox("Archivo:", file_options)
    
    if selected_file:
        file_name = selected_file.split(" (")[0]
        file_path = f"data/input/{file_name}"
        
        # Configuración de exportación
        st.markdown("**Configuración de Exportación:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            export_formats = st.multiselect(
                "Formatos de exportación",
                options=["CSV", "Excel", "JSON", "MySQL"],
                default=["CSV"],
                help="Selecciona uno o más formatos de salida"
            )
        
        with col2:
            use_chunks = st.checkbox(
                "Procesamiento por chunks",
                value=False,
                help="Recomendado para archivos >500MB"
            )
        
        # Configuración de nombres si se selecciona algún formato
        naming_config = {}
        if export_formats:
            with st.expander("🏷️ Personalización de Nombres", expanded=False):
                if mysql_ui:
                    naming_config = mysql_ui.render_naming_config()
                else:
                    st.info("🔧 Funcionalidad de personalización de nombres no disponible")
                    naming_config = {}
        
        # Configuración MySQL si se selecciona
        mysql_config = None
        if "MySQL" in export_formats:
            st.markdown("**🗄️ Configuración MySQL:**")
            if mysql_ui:
                mysql_config = mysql_ui.render_full_config()
                
                if not mysql_config:
                    st.warning("⚠️ Configura la conexión MySQL para continuar")
            else:
                st.error("❌ Funcionalidad MySQL no disponible")
                st.info("Para usar MySQL, asegúrate de que el módulo MySQL esté instalado y configurado")
                # Remover MySQL de los formatos seleccionados
                if "MySQL" in export_formats:
                    export_formats.remove("MySQL")
                st.warning("MySQL ha sido removido de los formatos de exportación")
                # Continuar con otros formatos disponibles
                if not export_formats:
                    st.error("No hay formatos de exportación disponibles")
                    return
        # Información del archivo
        with st.expander("Información del archivo"):
            try:
                # Para archivos Access, mostrar información de tablas disponibles
                if file_name.lower().endswith(('.accdb', '.mdb')):
                    from src.readers.robust_access_reader import RobustAccessReader
                    access_reader = RobustAccessReader()
                    available_tables = access_reader.get_table_names(file_path)
                    
                    st.write(f"Archivo Access detectado")
                    st.write(f"Tablas disponibles: {len(available_tables)}")
                    
                    for i, table in enumerate(available_tables, 1):
                        with st.expander(f"Tabla {i}: {table}"):
                            try:
                                # Leer muestra de la tabla para mostrar información
                                df_sample = access_reader.read(file_path, table)
                                st.write(f"Filas: {len(df_sample):,}")
                                st.write(f"Columnas: {len(df_sample.columns)}")
                                st.write(f"Columnas: {list(df_sample.columns)}")
                                
                                # Mostrar primeras filas
                                st.write("Primeras 3 filas:")
                                st.dataframe(df_sample.head(3), use_container_width=True)
                            except Exception as e:
                                st.error(f"Error leyendo tabla {table}: {str(e)}")
                else:
                    # Para otros archivos, usar el método normal
                    file_info = st.session_state.converter.get_file_info(file_path)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"Filas: {file_info['rows']:,}")
                        st.write(f"Columnas: {file_info['columns']}")
                        st.write(f"Tamaño: {file_info['file_size_mb']:.1f} MB")
                    
                    with col2:
                        st.write("Columnas:")
                        for col in file_info['column_names'][:5]:
                            st.write(f"• {col}")
                        if len(file_info['column_names']) > 5:
                            st.write(f"• ... y {len(file_info['column_names']) - 5} más")
                
            except Exception as e:
                st.error(f"Error obteniendo información: {str(e)}")
        
        # Configuración de conversión
        st.markdown("**Configuración:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            output_format = st.selectbox(
                "Formato de salida:",
                ["sql", "sqlite", "csv", "excel", "json"]
            )
        
        with col2:
            # Para archivos Access, mostrar información de todas las tablas
            if file_name.lower().endswith(('.accdb', '.mdb')):
                try:
                    from src.readers.robust_access_reader import RobustAccessReader
                    access_reader = RobustAccessReader()
                    
                    # Mostrar indicador de carga
                    with st.spinner("🔍 Analizando archivo Access..."):
                        available_tables = access_reader.get_table_names(file_path)
                    
                    if available_tables:
                        st.success(f"✅ Archivo Access cargado")
                        st.info(f"📋 {len(available_tables)} tablas detectadas")
                        
                        # Mostrar información de cada tabla
                        for i, table_name in enumerate(available_tables):
                            with st.expander(f"📊 Tabla {i+1}: {table_name}", expanded=True):
                                col_info1, col_info2 = st.columns(2)
                                
                                with col_info1:
                                    st.write(f"**Nombre:** {table_name}")
                                    st.write(f"**Posición:** {i+1} de {len(available_tables)}")
                                
                                with col_info2:
                                    # Leer muestra de datos para mostrar información
                                    try:
                                        with st.spinner(f"Analizando {table_name}..."):
                                            df_sample = access_reader.read(file_path, table_name)
                                        
                                        st.write(f"**Filas:** {len(df_sample):,}")
                                        st.write(f"**Columnas:** {len(df_sample.columns)}")
                                        
                                        # Mostrar tipos de datos
                                        data_types = df_sample.dtypes.value_counts()
                                        st.write("**Tipos de datos:**")
                                        for dtype, count in data_types.items():
                                            st.write(f"  • {dtype}: {count}")
                                            
                                    except Exception as e:
                                        st.error(f"❌ Error analizando tabla: {str(e)}")
                        
                        st.success(f"🎯 Se convertirán automáticamente todas las {len(available_tables)} tablas")
                    else:
                        st.warning("⚠️ No se detectaron tablas en el archivo Access")
                        return
                except Exception as e:
                    st.error(f"❌ Error analizando archivo Access: {str(e)}")
                    return
            else:
                # Para otros archivos, mostrar información básica
                st.success(f"✅ Archivo {file_name} cargado")
                table_name = st.text_input(
                    "Nombre de tabla:",
                    value=Path(file_name).stem.replace(' ', '_')
                )
        
        # Opciones avanzadas
        with st.expander("Opciones avanzadas"):
            col1, col2 = st.columns(2)
            
            with col1:
                batch_size = st.number_input(
                    "Tamaño del lote:",
                    min_value=100,
                    value=1000,
                    step=100
                )
            
            with col2:
                output_dir = st.text_input(
                    "Directorio de salida:",
                    value="data/output/"
                )
        
        
        
        # Botón de conversión
        st.markdown("**Convertir:**")
        
        # Botón de conversión mejorado
        if st.button("🚀 Iniciar Conversión Mejorada", type="primary", use_container_width=True):
            if not export_formats:
                st.error("❌ Selecciona al menos un formato de exportación")
            else:
                convert_with_new_features(file_path, file_name, export_formats, naming_config, mysql_config, use_chunks)
        
        st.markdown("---")
        st.markdown("**Conversión Original:**")        
        if st.button("🔄 Iniciar conversión de todas las tablas", type="primary"):
            # Verificar si es archivo Access
            is_access_file = file_name.lower().endswith(('.accdb', '.mdb'))
            
            if is_access_file:
                # Verificar soporte para Access
                access_reader = RobustAccessReader()
                support_info = access_reader.check_access_support()
                
                if not support_info['supported']:
                    st.error("Soporte para Access no disponible")
                    st.write(f"Error: {support_info['error_message']}")
                    return
                
                # Obtener todas las tablas
                available_tables = access_reader.get_table_names(file_path)
                if not available_tables:
                    st.error("No se detectaron tablas en el archivo Access")
                    return
                
                # Progreso de conversión múltiple
                progress_bar = st.progress(0)
                status_text = st.empty()
                results_container = st.container()
                
                all_results = []
                total_tables = len(available_tables)
                
                status_text.text(f"🔄 Iniciando conversión de {total_tables} tablas...")
                
                for i, table_name in enumerate(available_tables):
                    try:
                        # Actualizar progreso
                        progress = (i / total_tables)
                        progress_bar.progress(progress)
                        status_text.text(f"📊 Procesando tabla {i+1}/{total_tables}: {table_name}")
                        
                        # Generar ruta de salida para esta tabla
                        safe_table_name = table_name.replace(' ', '_')
                        if output_format == "sqlite":
                            output_file = f"{output_dir}/{safe_table_name}.db"
                        elif output_format == "csv":
                            output_file = f"{output_dir}/{safe_table_name}.csv"
                        elif output_format == "excel":
                            output_file = f"{output_dir}/{safe_table_name}.xlsx"
                        elif output_format == "json":
                            output_file = f"{output_dir}/{safe_table_name}.json"
                        else:
                            output_file = f"{output_dir}/{safe_table_name}.sql"
                        
                        # Realizar conversión de esta tabla
                        result = st.session_state.converter.convert_file(
                            input_path=file_path,
                            output_path=output_file,
                            output_format=output_format,
                            table_name=table_name,
                            batch_size=batch_size
                        )
                        
                        # Agregar información de la tabla al resultado
                        result['table_name'] = table_name
                        result['output_file'] = output_file
                        result['table_index'] = i + 1
                        all_results.append(result)
                        
                    except Exception as e:
                        error_result = {
                            'table_name': table_name,
                            'success': False,
                            'error': str(e),
                            'table_index': i + 1
                        }
                        all_results.append(error_result)
                
                # Completar progreso
                progress_bar.progress(1.0)
                status_text.text("✅ Conversión de todas las tablas completada!")
                
                # Mostrar resultados
                with results_container:
                    st.success(f"✅ Conversión completada: {len([r for r in all_results if r.get('success', False)])}/{total_tables} tablas exitosas")
                    
                    # Resumen de resultados
                    col1, col2, col3 = st.columns(3)
                    successful_tables = [r for r in all_results if r.get('success', False)]
                    failed_tables = [r for r in all_results if not r.get('success', False)]
                    
                    with col1:
                        st.metric("Tablas exitosas", len(successful_tables))
                    with col2:
                        st.metric("Tablas fallidas", len(failed_tables))
                    with col3:
                        total_rows = sum(r.get('rows_inserted', 0) for r in successful_tables)
                        st.metric("Total filas", f"{total_rows:,}")
                    
                    # Detalles por tabla
                    with st.expander("📊 Detalles por tabla", expanded=True):
                        for result in all_results:
                            table_name = result['table_name']
                            table_index = result['table_index']
                            
                            if result.get('success', False):
                                with st.container():
                                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                                    with col1:
                                        st.write(f"**{table_index}. {table_name}** ✅")
                                    with col2:
                                        st.write(f"Filas: {result.get('rows_inserted', 0):,}")
                                    with col3:
                                        st.write(f"Columnas: {result.get('columns', 0)}")
                                    with col4:
                                        st.write(f"Archivo: {Path(result['output_file']).name}")
                            else:
                                with st.container():
                                    col1, col2 = st.columns([3, 1])
                                    with col1:
                                        st.write(f"**{table_index}. {table_name}** ❌")
                                    with col2:
                                        st.error(f"Error: {result.get('error', 'Desconocido')}")
                    
                    # Descargar reporte
                    if all_results:
                        report_data = []
                        for result in all_results:
                            report_data.append({
                                'Tabla': result['table_name'],
                                'Estado': '✅ Exitoso' if result.get('success', False) else '❌ Fallido',
                                'Filas': result.get('rows_inserted', 0),
                                'Columnas': result.get('columns', 0),
                                'Archivo': Path(result.get('output_file', '')).name if result.get('output_file') else '',
                                'Error': result.get('error', '')
                            })
                        
                        report_df = pd.DataFrame(report_data)
                        report_csv = report_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Descargar reporte de conversión",
                            data=report_csv,
                            file_name=f"conversion_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                
            else:
                # Para archivos no-Access, conversión individual
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Generar ruta de salida
                    if output_format == "sqlite":
                        output_file = f"{output_dir}/{table_name}.db"
                    elif output_format == "csv":
                        output_file = f"{output_dir}/{table_name}.csv"
                    elif output_format == "excel":
                        output_file = f"{output_dir}/{table_name}.xlsx"
                    elif output_format == "json":
                        output_file = f"{output_dir}/{table_name}.json"
                    else:
                        output_file = f"{output_dir}/{table_name}.sql"
                    
                    status_text.text("Iniciando conversión...")
                    progress_bar.progress(0.25)
                    
                    # Realizar conversión
                    result = st.session_state.converter.convert_file(
                        input_path=file_path,
                        output_path=output_file,
                        output_format=output_format,
                        table_name=table_name,
                        batch_size=batch_size
                    )
                    
                    progress_bar.progress(1.0)
                    status_text.text("Conversión completada!")
                    
                    # Resultados
                    st.success("Conversión exitosa!")
                    
                    # Métricas de resultado
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Filas procesadas", f"{result.get('rows_inserted', 0):,}")
                    with col2:
                        st.metric("Columnas", result.get('columns', 0))
                    with col3:
                        st.metric("Archivo generado", Path(output_file).name)
                    
                    # Detalles
                    with st.expander("Detalles de la conversión"):
                        st.json(result)
                    
                    # Mostrar tabla de datos convertidos
                    with st.expander("Vista previa de datos convertidos"):
                        try:
                            # Leer los datos convertidos
                            if output_format == "sqlite":
                                import sqlite3
                                conn = sqlite3.connect(output_file)
                                df_preview = pd.read_sql(f"SELECT * FROM {table_name} LIMIT 100", conn)
                                conn.close()
                            else:
                                # Para archivos de texto (SQL, CSV, JSON), mostrar los primeros datos del archivo original
                                if file_name.lower().endswith(('.accdb', '.mdb')):
                                    # Para archivos Access, usar el reader específico
                                    df_preview = access_reader.read(file_path, table_name)
                                else:
                                    # Para otros archivos
                                    df_preview = st.session_state.converter.readers[Path(file_path).suffix].read(file_path)
                                df_preview = df_preview.head(100)
                            
                            st.write(f"**Vista previa de {len(df_preview)} filas:**")
                            st.dataframe(df_preview, use_container_width=True)
                            
                            # Estadísticas de la tabla
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Filas totales", f"{len(df_preview):,}")
                            with col2:
                                st.metric("Columnas", len(df_preview.columns))
                            with col3:
                                st.metric("Tamaño en memoria", f"{df_preview.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
                            
                            # Información de columnas
                            st.write("**Información de columnas:**")
                            column_info = pd.DataFrame({
                                'Columna': df_preview.columns,
                                'Tipo': df_preview.dtypes.astype(str),
                                'Valores únicos': [df_preview[col].nunique() for col in df_preview.columns],
                                'Valores nulos': df_preview.isnull().sum()
                            })
                            st.dataframe(column_info, use_container_width=True)
                            
                        except Exception as e:
                            st.error(f"Error mostrando vista previa: {str(e)}")
                    
                    # Descargar archivo
                    if os.path.exists(output_file):
                        with open(output_file, 'r') as f:
                            file_content = f.read()
                        
                        st.download_button(
                            label=f"📥 Descargar {Path(output_file).name}",
                            data=file_content,
                            file_name=Path(output_file).name,
                            mime="text/plain"
                        )
                
                except Exception as e:
                    progress_bar.progress(0)
                    status_text.text("❌ Error en la conversión")
                    
                    st.error(f"❌ **Error en la conversión:** {str(e)}")
                    
                    if is_access_file:
                        st.info("🔧 **Solución de problemas para archivos Access:**")
                        st.markdown("""
                        1. **Verifica el archivo**: Asegúrate de que no esté corrupto
                        2. **Cierra el archivo**: No debe estar abierto en Access
                        3. **Convierte manualmente**: Exporta a CSV/Excel desde Access
                        4. **Usa mdb-tools**: Ejecuta el script de conversión automática
                        """)

def show_data_viewer():
    """Página para visualizar datos de archivos con paginación"""
    st.markdown("## 📊 Visualizar Datos con Paginación")
    
    input_files = get_input_files()
    
    if not input_files:
        st.info("📁 No hay archivos de entrada disponibles")
        return
    
    # Selección de archivo
    st.markdown("### 📂 Seleccionar Archivo para Visualizar")
    
    file_options = [f"{f['name']} ({f['size']:.2f} MB)" for f in input_files]
    selected_file = st.selectbox("Archivo a visualizar:", file_options)
    
    if selected_file:
        file_name = selected_file.split(" (")[0]
        file_path = f"data/input/{file_name}"
        
        # Para archivos Access, mostrar selector de tablas
        selected_table = None
        if file_name.lower().endswith(('.accdb', '.mdb')):
            try:
                from src.readers.robust_access_reader import RobustAccessReader
                access_reader = RobustAccessReader()
                available_tables = access_reader.get_table_names(file_path)
                
                if available_tables:
                    st.markdown("### 📋 Tablas Disponibles")
                    st.info(f"Archivo Access detectado con {len(available_tables)} tablas:")
                    for i, table in enumerate(available_tables, 1):
                        st.write(f"{i}. **{table}**")
                    
                    selected_table = st.selectbox(
                        "Selecciona la tabla a visualizar:",
                        available_tables,
                        help="Elige la tabla específica que quieres ver"
                    )
                else:
                    st.warning("No se pudieron detectar las tablas del archivo Access")
            except Exception as e:
                st.error(f"Error detectando tablas: {str(e)}")
        
        # Configuración de paginación
        st.markdown("### ⚙️ Configuración de Paginación")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            page_size = st.number_input(
                "Filas por página:",
                min_value=10,
                max_value=1000,
                value=100,
                step=10,
                help="Número de filas a mostrar por página"
            )
        
        with col2:
            max_total_rows = st.number_input(
                "Máximo filas totales:",
                min_value=100,
                max_value=1000000,
                value=10000,
                step=1000,
                help="Límite total de filas a cargar (para archivos muy grandes)"
            )
        
        with col3:
            show_stats = st.checkbox("Mostrar estadísticas", value=True)
        
        # Inicializar session state para paginación
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 0
        if 'total_rows' not in st.session_state:
            st.session_state.total_rows = 0
        if 'df_loaded' not in st.session_state:
            st.session_state.df_loaded = False
        if 'df_data' not in st.session_state:
            st.session_state.df_data = None
        
        # Botón para cargar datos
        if st.button("📊 Cargar Datos", type="primary"):
            with st.spinner("Cargando datos..."):
                try:
                    # Leer archivo
                    file_extension = Path(file_name).suffix.lower()
                    
                    if file_extension in ['.accdb', '.mdb']:
                        # Para archivos Access, usar el reader robusto
                        from src.readers.robust_access_reader import RobustAccessReader
                        reader = RobustAccessReader()
                        if selected_table:
                            df = reader.read(file_path, selected_table)
                        else:
                            df = reader.read(file_path)
                    else:
                        # Para otros archivos, usar el converter
                        df = st.session_state.converter.readers[file_extension].read(file_path)
                    
                    # Limitar filas totales para archivos muy grandes
                    if len(df) > max_total_rows:
                        st.warning(f"⚠️ Archivo muy grande ({len(df):,} filas). Mostrando solo las primeras {max_total_rows:,} filas.")
                        df = df.head(max_total_rows)
                    
                    # Guardar en session state
                    st.session_state.df_data = df
                    st.session_state.total_rows = len(df)
                    st.session_state.current_page = 0
                    st.session_state.df_loaded = True
                    
                    st.success(f"✅ Datos cargados: {len(df):,} filas, {len(df.columns)} columnas")
                    
                except Exception as e:
                    st.error(f"❌ Error cargando datos: {str(e)}")
        
        # Mostrar datos con paginación
        if st.session_state.df_loaded and st.session_state.df_data is not None:
            df = st.session_state.df_data
            total_rows = st.session_state.total_rows
            total_pages = (total_rows + page_size - 1) // page_size
            
            # Información de paginación
            st.markdown("### 📋 Vista de Datos")
            
            col1, col2, col3 = st.columns([2, 1, 2])
            
            with col1:
                st.write(f"**Página {st.session_state.current_page + 1} de {total_pages}**")
                st.write(f"**Mostrando filas {st.session_state.current_page * page_size + 1} - {min((st.session_state.current_page + 1) * page_size, total_rows)} de {total_rows:,}**")
            
            with col2:
                if st.button("⬅️ Anterior", disabled=st.session_state.current_page == 0):
                    st.session_state.current_page = max(0, st.session_state.current_page - 1)
                    st.rerun()
            
            with col3:
                if st.button("➡️ Siguiente", disabled=st.session_state.current_page >= total_pages - 1):
                    st.session_state.current_page = min(total_pages - 1, st.session_state.current_page + 1)
                    st.rerun()
            
            # Navegación rápida
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                if st.button("⏮️ Primera", disabled=st.session_state.current_page == 0):
                    st.session_state.current_page = 0
                    st.rerun()
            
            with col2:
                # Selector de página
                page_options = list(range(1, total_pages + 1))
                selected_page = st.selectbox(
                    "Ir a página:",
                    page_options,
                    index=st.session_state.current_page,
                    key="page_selector"
                )
                if selected_page != st.session_state.current_page + 1:
                    st.session_state.current_page = selected_page - 1
                    st.rerun()
            
            with col3:
                if st.button("⏭️ Última", disabled=st.session_state.current_page >= total_pages - 1):
                    st.session_state.current_page = total_pages - 1
                    st.rerun()
            
            # Mostrar datos de la página actual
            start_idx = st.session_state.current_page * page_size
            end_idx = min(start_idx + page_size, total_rows)
            df_page = df.iloc[start_idx:end_idx]
            
            st.dataframe(df_page, use_container_width=True)
            
            # Barra de progreso de paginación
            progress = (st.session_state.current_page + 1) / total_pages
            st.progress(progress, text=f"Página {st.session_state.current_page + 1} de {total_pages}")
            
            # Estadísticas
            if show_stats:
                st.markdown("### 📊 Estadísticas")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Filas totales", f"{total_rows:,}")
                with col2:
                    st.metric("Columnas", len(df.columns))
                with col3:
                    st.metric("Tamaño en memoria", f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
                with col4:
                    st.metric("Valores nulos", f"{df.isnull().sum().sum():,}")
                
                # Información de columnas
                st.markdown("#### 📋 Información de Columnas")
                column_info = pd.DataFrame({
                    'Columna': df.columns,
                    'Tipo': df.dtypes.astype(str),
                    'Valores únicos': [df[col].nunique() for col in df.columns],
                    'Valores nulos': df.isnull().sum(),
                    'Porcentaje nulos': [f"{(df[col].isnull().sum() / len(df) * 100):.1f}%" for col in df.columns]
                })
                st.dataframe(column_info, use_container_width=True)
                
                # Gráficos de distribución (usando muestra para archivos grandes)
                st.markdown("#### 📈 Distribución de Datos")
                
                # Usar muestra para gráficos si el archivo es muy grande
                sample_size = min(10000, len(df))
                df_sample = df.sample(n=sample_size, random_state=42) if len(df) > sample_size else df
                
                # Seleccionar columna para gráfico
                numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
                categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
                
                if numeric_columns:
                    selected_numeric = st.selectbox("Columna numérica para histograma:", numeric_columns)
                    if selected_numeric:
                        fig = px.histogram(df_sample, x=selected_numeric, title=f"Distribución de {selected_numeric} (muestra de {len(df_sample):,} filas)")
                        st.plotly_chart(fig, use_container_width=True)
                
                if categorical_columns:
                    selected_cat = st.selectbox("Columna categórica para gráfico de barras:", categorical_columns)
                    if selected_cat:
                        value_counts = df_sample[selected_cat].value_counts().head(10)
                        fig = px.bar(x=value_counts.index, y=value_counts.values, 
                                   title=f"Top 10 valores en {selected_cat} (muestra de {len(df_sample):,} filas)")
                        st.plotly_chart(fig, use_container_width=True)
            
            # Descargar datos como CSV
            col1, col2 = st.columns(2)
            
            with col1:
                csv_data = df.to_csv(index=False)
                st.download_button(
                    label="📥 Descargar CSV completo",
                    data=csv_data,
                    file_name=f"{Path(file_name).stem}_datos.csv",
                    mime="text/csv"
                )
            
            with col2:
                # Descargar solo la página actual
                csv_page = df_page.to_csv(index=False)
                st.download_button(
                    label="📥 Descargar página actual",
                    data=csv_page,
                    file_name=f"{Path(file_name).stem}_pagina_{st.session_state.current_page + 1}.csv",
                    mime="text/csv"
                )

def show_results():
    """Página de resultados"""
    st.markdown("## 📊 Resultados")
    
    output_files = get_output_files()
    
    if not output_files:
        st.info("📁 No hay archivos de salida disponibles")
        return
    
    # Estadísticas de archivos de salida
    col1, col2, col3 = st.columns(3)
    
    total_files = len(output_files)
    total_size = sum(f['size'] for f in output_files)
    
    with col1:
        st.metric("Archivos generados", total_files)
    with col2:
        st.metric("Tamaño total", f"{total_size:.2f} MB")
    with col3:
        st.metric("Promedio por archivo", f"{total_size/total_files:.2f} MB")
    
    # Lista de archivos
    st.markdown("### 📁 Archivos Generados")
    
    for file_info in output_files:
        with st.expander(f"📄 {file_info['name']} ({file_info['size']:.2f} MB)"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Tamaño:** {file_info['size']:.2f} MB")
                st.write(f"**Fecha:** {file_info['modified']}")
                st.write(f"**Tipo:** {Path(file_info['name']).suffix}")
            
            with col2:
                if st.button(f"📥 Descargar", key=f"download_{file_info['name']}"):
                    file_path = f"data/output/{file_info['name']}"
                    if os.path.exists(file_path):
                        with open(file_path, 'r') as f:
                            st.download_button(
                                label="Descargar archivo",
                                data=f.read(),
                                file_name=file_info['name'],
                                mime="text/plain"
                            )

def show_configuration():
    """Página de configuración"""
    st.markdown("## ⚙️ Configuración")
    
    st.markdown("### 🔧 Configuración del Sistema")
    
    # Verificar dependencias
    st.markdown("#### 📦 Dependencias")
    
    dependencies = {
        "pandas": "Procesamiento de datos",
        "pyodbc": "Conexión a Access (Windows)",
        "sqlalchemy": "Conexión a bases de datos",
        "streamlit": "Interfaz web"
    }
    
    for dep, description in dependencies.items():
        try:
            __import__(dep)
            st.success(f"✅ {dep} - {description}")
        except ImportError:
            st.error(f"❌ {dep} - {description}")
    
    # Verificar herramientas del sistema
    st.markdown("#### 🛠️ Herramientas del Sistema")
    
    # Verificar mdb-tools
    try:
        result = subprocess.run(['mdb-tables', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            st.success("✅ mdb-tools - Conversión de Access")
        else:
            st.warning("⚠️ mdb-tools - No disponible")
    except:
        st.warning("⚠️ mdb-tools - No instalado")
    
    # Configuración de archivos
    st.markdown("### 📁 Configuración de Archivos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        max_file_size = st.number_input(
            "Tamaño máximo de archivo (MB):",
            min_value=1,
            value=100,
            help="Archivos más grandes serán rechazados"
        )
    
    with col2:
        supported_formats = st.multiselect(
            "Formatos soportados:",
            [".csv", ".xlsx", ".xls", ".json", ".accdb", ".mdb"],
            default=[".csv", ".xlsx", ".xls", ".json", ".accdb", ".mdb"]
        )

def show_year_conversion():
    """Página de conversión por años"""
    st.markdown("## 📅 Conversión por Años")
    st.markdown("Convierte archivos Access (.mdb/.accdb) separando los datos por años")
    
    # Verificar archivos Access disponibles
    input_files = get_input_files()
    access_files = [f for f in input_files if f['name'].lower().endswith(('.mdb', '.accdb'))]
    
    if not access_files:
        st.error("❌ No hay archivos Access disponibles")
        st.write("Sube archivos .mdb o .accdb en la sección '📁 Convertir' o colócalos en `data/input/`")
        return
    
    # Selección de archivo
    st.markdown("### 📁 Seleccionar Archivo Access")
    
    file_options = [f"{f['name']} ({f['size']:.1f} MB)" for f in access_files]
    selected_file = st.selectbox("Archivo Access:", file_options)
    
    if selected_file:
        file_name = selected_file.split(" (")[0]
        file_path = f"data/input/{file_name}"
        
        # Mostrar información del archivo
        with st.expander("📊 Información del Archivo"):
            try:
                access_reader = RobustAccessReader()
                year_summary = access_reader.get_year_summary(file_path)
                
                if 'error' in year_summary:
                    st.error(f"Error analizando archivo: {year_summary['error']}")
                else:
                    st.success(f"✅ Archivo analizado correctamente")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Tamaño", f"{year_summary['file_size_mb']:.1f} MB")
                        st.metric("Total de tablas", len(year_summary['tables']))
                    
                    with col2:
                        total_rows = sum(t.get('total_rows', 0) for t in year_summary['tables'].values())
                        st.metric("Total de filas", f"{total_rows:,}")
                    
                    # Mostrar detalles de tablas y años
                    st.markdown("**📋 Tablas y Años Disponibles:**")
                    for table_name, table_info in year_summary['tables'].items():
                        if 'error' not in table_info:
                            with st.expander(f"📊 {table_name}"):
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Filas", f"{table_info['total_rows']:,}")
                                with col2:
                                    st.metric("Columnas", table_info['columns'])
                                with col3:
                                    st.metric("Años", table_info['year_count'])
                                
                                if table_info['available_years']:
                                    st.write(f"**Años disponibles:** {', '.join(map(str, table_info['available_years']))}")
                                    st.write(f"**Rango:** {table_info['year_range']}")
                        else:
                            st.error(f"Error en tabla {table_name}: {table_info['error']}")
                            
            except Exception as e:
                st.error(f"Error analizando archivo: {str(e)}")
        
        # Configuración de conversión
        st.markdown("### ⚙️ Configuración de Conversión")
        
        col1, col2 = st.columns(2)
        with col1:
            output_format = st.selectbox(
                "Formato de salida:",
                ["sql", "sqlite", "csv", "excel", "json"],
                help="Formato de los archivos generados por año"
            )
        
        with col2:
            output_dir = st.text_input(
                "Directorio de salida:",
                value=f"data/output/{Path(file_name).stem}_por_años",
                help="Directorio donde se guardarán los archivos por año"
            )
        
        # Configuración de nombres para archivos por año
        with st.expander("🏷️ Personalización de Nombres para Archivos por Año", expanded=False):
            st.markdown("**Ejemplos de patrones disponibles:**")
            st.markdown("- `at2-historico-{year}` → at2-historico-2008, at2-historico-2009...")
            st.markdown("- `datos-{year}-v1` → datos-2008-v1, datos-2009-v1...")
            st.markdown("- `backup-{year}` → backup-2008, backup-2009...")
            
            col3, col4 = st.columns(2)
            
            with col3:
                year_prefix = st.text_input(
                    "Prefijo personalizado:",
                    value="",
                    help="Prefijo que se añadirá antes del nombre. Usa {year} para incluir el año."
                )
                
                use_year_timestamp = st.checkbox(
                    "Incluir timestamp",
                    value=False,
                    help="Añadir fecha y hora al nombre del archivo"
                )
            
            with col4:
                year_suffix = st.text_input(
                    "Sufijo personalizado:",
                    value="",
                    help="Sufijo que se añadirá después del nombre. Usa {year} para incluir el año."
                )
                
                year_lowercase = st.checkbox(
                    "Convertir a minúsculas",
                    value=True,
                    help="Convertir todos los nombres a minúsculas"
                )
            
            # Crear configuración de nombres para años
            naming_config = {
                'table_prefix': year_prefix if year_prefix else None,
                'table_suffix': year_suffix if year_suffix else None,
                'use_timestamp': use_year_timestamp,
                'lowercase_names': year_lowercase,
                'replace_spaces': True,
                'remove_special_chars': True
            }
            
            # Vista previa del nombre generado
            if year_prefix or year_suffix:
                example_name = "ejemplo_tabla"
                preview_year = 2008
                
                # Simular el nombre generado
                preview_base = example_name.lower() if year_lowercase else example_name
                
                if year_prefix:
                    prefix = year_prefix.replace('{year}', str(preview_year))
                    preview_base = f"{prefix}{preview_base}"
                else:
                    preview_base = f"{preview_base}-{preview_year}"
                    
                if year_suffix:
                    suffix = year_suffix.replace('{year}', str(preview_year))
                    preview_base = f"{preview_base}{suffix}"
                    
                if use_year_timestamp:
                    from datetime import datetime
                    timestamp = datetime.now().strftime("_%Y%m%d_%H%M%S")
                    preview_base = f"{preview_base}{timestamp}"
                
                st.info(f"📋 Vista previa: `{preview_base}.{output_format}`")
        
        # Configuración de Base de Datos en Línea
        with st.expander("🌐 Conexión a Base de Datos en Línea", expanded=False):
            st.markdown("**Conecta directamente a bases de datos remotas:**")
            
            # Selección de tipo de base de datos
            db_type = st.selectbox(
                "Tipo de Base de Datos:",
                ["Ninguna (solo archivos)", "MySQL", "PostgreSQL", "Supabase"],
                help="Selecciona el tipo de base de datos remota"
            )
            
            db_config = None
            
            if db_type == "MySQL":
                st.markdown("**🗄️ Configuración MySQL:**")
                col5, col6 = st.columns(2)
                
                with col5:
                    mysql_host = st.text_input("Host MySQL:", value="", placeholder="ejemplo: mysql.tuservidor.com")
                    mysql_port = st.number_input("Puerto:", value=3306, min_value=1, max_value=65535)
                    mysql_database = st.text_input("Base de datos:", value="", placeholder="nombre_base_datos")
                
                with col6:
                    mysql_user = st.text_input("Usuario:", value="", placeholder="tu_usuario")
                    mysql_password = st.text_input("Contraseña:", type="password", value="")
                
                if mysql_host and mysql_database and mysql_user and mysql_password:
                    db_config = {
                        'type': 'mysql',
                        'host': mysql_host,
                        'port': mysql_port,
                        'database': mysql_database,
                        'user': mysql_user,
                        'password': mysql_password
                    }
                    
                    if st.button("🔍 Probar Conexión MySQL"):
                        try:
                            from src.writers.mysql_writer import MySQLWriter
                            mysql_writer = MySQLWriter(db_config)
                            test_result = mysql_writer.test_connection()
                            
                            if test_result['success']:
                                st.success(f"✅ Conexión exitosa: {test_result['message']}")
                                if 'server_info' in test_result:
                                    info = test_result['server_info']
                                    st.info(f"🗄️ Servidor: {info.get('version', 'N/A')} | Base de datos: {info.get('database', 'N/A')}")
                            else:
                                st.error(f"❌ Error de conexión: {test_result['message']}")
                                
                        except Exception as e:
                            st.error(f"❌ Error probando conexión: {str(e)}")
            
            elif db_type == "PostgreSQL":
                st.markdown("**🐘 Configuración PostgreSQL:**")
                col7, col8 = st.columns(2)
                
                with col7:
                    pg_host = st.text_input("Host PostgreSQL:", value="", placeholder="ejemplo: postgres.tuservidor.com")
                    pg_port = st.number_input("Puerto:", value=5432, min_value=1, max_value=65535)
                    pg_database = st.text_input("Base de datos:", value="", placeholder="nombre_base_datos")
                
                with col8:
                    pg_user = st.text_input("Usuario:", value="", placeholder="tu_usuario")
                    pg_password = st.text_input("Contraseña:", type="password", value="")
                
                if pg_host and pg_database and pg_user and pg_password:
                    db_config = {
                        'type': 'postgresql',
                        'host': pg_host,
                        'port': pg_port,
                        'database': pg_database,
                        'user': pg_user,
                        'password': pg_password
                    }
                    
                    st.info("🔧 Funcionalidad PostgreSQL disponible próximamente...")
            
            elif db_type == "Supabase":
                st.markdown("**⚡ Configuración Supabase:**")
                col9, col10 = st.columns(2)
                
                with col9:
                    supabase_url = st.text_input(
                        "URL del Proyecto:", 
                        value="", 
                        placeholder="https://tuproyecto.supabase.co"
                    )
                
                with col10:
                    supabase_key = st.text_input(
                        "Clave Anon:", 
                        type="password", 
                        value="",
                        placeholder="tu-clave-anonima"
                    )
                
                if supabase_url and supabase_key:
                    db_config = {
                        'type': 'supabase',
                        'url': supabase_url,
                        'key': supabase_key
                    }
                    
                    st.info("🔧 Funcionalidad Supabase mejorada disponible próximamente...")
            
            # Información sobre proveedores recomendados
            if db_type != "Ninguna (solo archivos)":
                with st.expander("💡 Proveedores Recomendados de Bases de Datos", expanded=False):
                    st.markdown("**MySQL en línea:**")
                    st.markdown("- **PlanetScale** (gratis hasta 5GB): https://planetscale.com")
                    st.markdown("- **Railway** (gratis con límites): https://railway.app")
                    st.markdown("- **Aiven** (trial gratuito): https://aiven.io")
                    st.markdown("- **DigitalOcean Managed Database**: https://digitalocean.com")
                    
                    st.markdown("**PostgreSQL en línea:**")
                    st.markdown("- **Supabase** (gratis hasta 500MB): https://supabase.com")
                    st.markdown("- **Neon** (gratis con límites): https://neon.tech")
                    st.markdown("- **ElephantSQL** (gratis hasta 20MB): https://elephantsql.com")
                    st.markdown("- **Render** (gratis con límites): https://render.com")
                    
                    st.markdown("**💰 Todos los proveedores ofrecen planes gratuitos perfectos para pruebas!**")
        
        # Botón de conversión
        conversion_type = "a archivos" if not db_config else f"a {db_config['type'].upper()}"
        
        if st.button(f"🔄 Iniciar Conversión por Años {conversion_type}", type="primary", use_container_width=True):
            try:
                with st.spinner(f"🔄 Convirtiendo archivo por años {conversion_type}..."):
                    # Crear conversor
                    converter = FileConverter()
                    
                    # Realizar conversión
                    if db_config and db_config['type'] == 'mysql':
                        # Conversión directa a MySQL
                        st.info("🗄️ Conectando a MySQL...")
                        result = convert_to_mysql_by_year(file_path, db_config, naming_config)
                    else:
                        # Conversión a archivos
                        result = converter.convert_access_by_year(
                            input_path=file_path,
                            output_format=output_format,
                            output_dir=output_dir,
                            naming_config=naming_config
                        )
                
                # Mostrar resultados
                success_msg = "✅ Conversión por años completada exitosamente!"
                if db_config:
                    success_msg += f" Los datos se han insertado en {db_config['type'].upper()}."
                st.success(success_msg)
                
                # Resumen de resultados - Adaptado para MySQL y archivos
                if db_config and db_config['type'] == 'mysql':
                    # Resultados para MySQL
                    details = result.get('details', {})
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Tablas subidas", details.get('total_success', 0))
                    with col2:
                        st.metric("Tablas fallidas", details.get('total_failed', 0))
                    with col3:
                        st.metric("Base de datos", details.get('database', 'N/A'))
                    
                    # Mostrar tablas subidas exitosamente
                    if details.get('tables_uploaded'):
                        st.markdown("### ✅ Tablas Subidas Exitosamente")
                        for table_info in details['tables_uploaded']:
                            st.success(f"📋 **{table_info['name']}** - {table_info['statements']} statements ejecutados")
                    
                    # Mostrar errores si los hay
                    if details.get('tables_failed'):
                        st.markdown("### ❌ Tablas con Errores")
                        for table_error in details['tables_failed']:
                            st.error(f"📋 **{table_error['name']}**: {table_error['error']}")
                            
                else:
                    # Resultados para archivos tradicionales
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Archivos creados", result.get('total_files_created', 0))
                    with col2:
                        st.metric("Total de filas", f"{result.get('total_rows_converted', 0):,}")
                    with col3:
                        st.metric("Tamaño total", f"{result.get('total_size_mb', 0):.1f} MB")
                
                # Detalles de conversiones (solo para archivos)
                if 'conversions_by_year' in result:
                    st.markdown("### 📊 Detalles de Conversiones")
                    
                    successful_conversions = [conv for conv in result['conversions_by_year'].values() 
                                           if conv['status'] == 'success']
                    error_conversions = [conv for conv in result['conversions_by_year'].values() 
                                       if conv['status'] == 'error']
                    
                    if successful_conversions:
                        st.success(f"✅ **Conversiones exitosas:** {len(successful_conversions)}")
                        
                        # Tabla de resultados
                        results_data = []
                        for conv in successful_conversions:
                            results_data.append({
                                'Tabla': conv['table'],
                                'Año': conv['year'],
                                'Filas': f"{conv['rows_converted']:,}",
                                'Archivo': conv['output_file'],
                                'Tamaño (MB)': f"{conv.get('file_size_mb', 0):.1f}"
                            })
                        
                        df_results = pd.DataFrame(results_data)
                    st.dataframe(df_results, use_container_width=True)
                
                if error_conversions:
                    st.error(f"❌ **Errores:** {len(error_conversions)}")
                    for conv in error_conversions:
                        st.error(f"Tabla {conv['table']}, Año {conv['year']}: {conv['error']}")
                
                # Enlace al directorio de salida
                st.markdown(f"**📁 Archivos guardados en:** `{result['output_directory']}`")
                
            except Exception as e:
                st.error(f"❌ Error durante la conversión: {str(e)}")
                st.exception(e)

def show_statistics():
    """Página de estadísticas"""
    st.markdown("## 📈 Estadísticas")
    
    # Estadísticas generales
    input_files = get_input_files()
    output_files = get_output_files()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Archivos de entrada", len(input_files))
    with col2:
        st.metric("Archivos de salida", len(output_files))
    with col3:
        total_input_size = sum(f['size'] for f in input_files)
        st.metric("Tamaño entrada", f"{total_input_size:.2f} MB")
    with col4:
        total_output_size = sum(f['size'] for f in output_files)
        st.metric("Tamaño salida", f"{total_output_size:.2f} MB")
    
    # Gráficos
    if input_files:
        st.markdown("### 📊 Distribución por Formato")
        
        # Contar formatos
        format_counts = {}
        for file_info in input_files:
            ext = Path(file_info['name']).suffix.lower()
            format_counts[ext] = format_counts.get(ext, 0) + 1
        
        if format_counts:
            fig = px.pie(
                values=list(format_counts.values()),
                names=list(format_counts.keys()),
                title="Distribución de archivos por formato"
            )
            st.plotly_chart(fig, use_container_width=True)

# Funciones auxiliares
def get_input_files():
    """Obtiene lista de archivos de entrada"""
    input_dir = Path("data/input")
    if not input_dir.exists():
        return []
    
    files = []
    for file_path in input_dir.iterdir():
        if file_path.is_file():
            stat = file_path.stat()
            files.append({
                'name': file_path.name,
                'size': stat.st_size / (1024 * 1024),
                'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
            })
    
    return sorted(files, key=lambda x: x['modified'], reverse=True)

def get_output_files():
    """Obtiene lista de archivos de salida"""
    output_dir = Path("data/output")
    if not output_dir.exists():
        return []
    
    files = []
    for file_path in output_dir.iterdir():
        if file_path.is_file():
            stat = file_path.stat()
            files.append({
                'name': file_path.name,
                'size': stat.st_size / (1024 * 1024),
                'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
            })
    
    return sorted(files, key=lambda x: x['modified'], reverse=True)

def get_success_rate():
    """Calcula la tasa de éxito de conversiones"""
    input_files = get_input_files()
    output_files = get_output_files()
    
    if not input_files:
        return 0
    
    # Estimación simple basada en archivos de salida vs entrada
    return min(100, (len(output_files) / len(input_files)) * 100)

if __name__ == "__main__":
    main() 
def convert_with_new_features(file_path, file_name, export_formats, naming_config, mysql_config, use_chunks):
    """Función mejorada de conversión con soporte para MySQL, chunks e integridad"""
    try:
        # Inicializar componentes
        access_reader = RobustAccessReader()
        
        # Verificar si DataIntegrityChecker está disponible
        if MYSQL_AVAILABLE and DataIntegrityChecker:
            integrity_checker = DataIntegrityChecker()
        else:
            integrity_checker = None
            st.info("🔧 Verificación de integridad no disponible")
        
        # Verificar soporte para Access
        support_info = access_reader.check_access_support()
        if not support_info['supported']:
            st.error("❌ Soporte para Access no disponible")
            st.write(f"Error: {support_info['error_message']}")
            return
        
        # Obtener tablas disponibles
        available_tables = access_reader.get_table_names(file_path)
        if not available_tables:
            st.error("❌ No se detectaron tablas en el archivo Access")
            return
        
        # Configurar MySQL si es necesario
        mysql_writer = None
        if "MySQL" in export_formats and mysql_config:
            mysql_writer = MySQLWriter(mysql_config)
            if not mysql_writer.test_connection():
                st.error("❌ No se pudo conectar a MySQL")
                return
        
        # Progreso de conversión
        progress_bar = st.progress(0)
        status_text = st.empty()
        results_container = st.container()
        
        total_tables = len(available_tables)
        all_results = []
        integrity_reports = []
        
        status_text.text(f"🔄 Iniciando conversión mejorada de {total_tables} tablas...")
        
        for i, table_name in enumerate(available_tables):
            try:
                # Actualizar progreso
                progress = (i / total_tables)
                progress_bar.progress(progress)
                status_text.text(f"📊 Procesando tabla {i+1}/{total_tables}: {table_name}")
                
                # Leer datos (con chunks si es necesario)
                if use_chunks:
                    df = access_reader.read_in_chunks(file_path, table_name, chunk_size=10000)
                else:
                    df = access_reader.read_table(file_path, table_name)
                
                if df is None or df.empty:
                    st.warning(f"⚠️ Tabla '{table_name}' está vacía o no se pudo leer")
                    continue
                
                # Calcular estadísticas originales para integridad
                original_stats = integrity_checker.get_dataframe_stats(df)
                
                # Aplicar configuración de nombres
                safe_table_name = apply_naming_config(table_name, naming_config)
                
                # Exportar según formatos seleccionados
                table_results = []
                
                for format_type in export_formats:
                    try:
                        if format_type == "CSV":
                            output_file = f"data/output/{safe_table_name}.csv"
                            df.to_csv(output_file, index=False, encoding='utf-8')
                            table_results.append({"format": "CSV", "file": output_file, "status": "✅"})
                        
                        elif format_type == "Excel":
                            output_file = f"data/output/{safe_table_name}.xlsx"
                            df.to_excel(output_file, index=False, engine='openpyxl')
                            table_results.append({"format": "Excel", "file": output_file, "status": "✅"})
                        
                        elif format_type == "JSON":
                            output_file = f"data/output/{safe_table_name}.json"
                            df.to_json(output_file, orient='records', indent=2, force_ascii=False)
                            table_results.append({"format": "JSON", "file": output_file, "status": "✅"})
                        
                        elif format_type == "MySQL" and mysql_writer:
                            mysql_table_name = safe_table_name.lower()
                            success = mysql_writer.write_dataframe(df, mysql_table_name)
                            if success:
                                table_results.append({"format": "MySQL", "table": mysql_table_name, "status": "✅"})
                            else:
                                table_results.append({"format": "MySQL", "table": mysql_table_name, "status": "❌"})
                        
                        # Verificar integridad para archivos exportados
                        if format_type in ["CSV", "Excel"] and table_results:
                            last_result = table_results[-1]
                            if "file" in last_result:
                                integrity_report = integrity_checker.verify_export_integrity(
                                    df, last_result["file"], format_type.lower()
                                )
                                integrity_reports.append({
                                    "table": table_name,
                                    "format": format_type,
                                    "report": integrity_report
                                })
                    
                    except Exception as e:
                        table_results.append({"format": format_type, "status": "❌", "error": str(e)})
                
                all_results.append({
                    "table": table_name,
                    "rows": len(df),
                    "columns": len(df.columns),
                    "results": table_results
                })
                
            except Exception as e:
                st.error(f"❌ Error procesando tabla '{table_name}': {str(e)}")
                all_results.append({
                    "table": table_name,
                    "error": str(e),
                    "results": []
                })
        
        # Completar progreso
        progress_bar.progress(1.0)
        status_text.text("✅ Conversión completada")
        
        # Mostrar resultados
        with results_container:
            st.success(f"🎉 Conversión completada: {len(all_results)} tablas procesadas")
            
            # Resumen de resultados
            for result in all_results:
                with st.expander(f"📊 {result['table']} ({result.get('rows', 0)} filas)"):
                    if "error" in result:
                        st.error(f"❌ Error: {result['error']}")
                    else:
                        for export_result in result['results']:
                            if export_result['status'] == "✅":
                                if 'file' in export_result:
                                    st.success(f"✅ {export_result['format']}: {export_result['file']}")
                                elif 'table' in export_result:
                                    st.success(f"✅ {export_result['format']}: tabla '{export_result['table']}'")
                            else:
                                error_msg = export_result.get('error', 'Error desconocido')
                                st.error(f"❌ {export_result['format']}: {error_msg}")
            
            # Mostrar reportes de integridad
            if integrity_reports:
                st.markdown("### 🔍 Reportes de Integridad")
                for report_data in integrity_reports:
                    with st.expander(f"🔍 Integridad: {report_data['table']} ({report_data['format']})"):
                        report = report_data['report']
                        if report['integrity_passed']:
                            st.success("✅ Integridad verificada correctamente")
                        else:
                            st.warning("⚠️ Se detectaron diferencias")
                        
                        st.write(f"**Filas originales:** {report['original_rows']}")
                        st.write(f"**Filas exportadas:** {report['exported_rows']}")
                        st.write(f"**Columnas originales:** {report['original_columns']}")
                        st.write(f"**Columnas exportadas:** {report['exported_columns']}")
                        
                        if report['differences']:
                            st.write("**Diferencias detectadas:**")
                            for diff in report['differences']:
                                st.write(f"- {diff}")
    
    except Exception as e:
        st.error(f"❌ Error general en la conversión: {str(e)}")
        st.exception(e)

def apply_naming_config(original_name, naming_config):
    """Aplica la configuración de nombres personalizada"""
    if not naming_config:
        return original_name.replace(' ', '_')
    
    import re
    from datetime import datetime
    
    # Aplicar prefijo
    name = original_name
    if naming_config.get('table_prefix'):
        name = f"{naming_config['table_prefix']}{name}"
    
    # Aplicar sufijo
    if naming_config.get('table_suffix'):
        name = f"{name}{naming_config['table_suffix']}"
    
    # Añadir timestamp si está configurado
    if naming_config.get('use_timestamp'):
        timestamp = datetime.now().strftime("_%Y%m%d_%H%M%S")
        name = f"{name}{timestamp}"
    
    # Aplicar transformaciones de texto
    if naming_config.get('lowercase_names', True):
        name = name.lower()
    
    if naming_config.get('replace_spaces', True):
        name = name.replace(' ', '_')
    
    # Limpiar caracteres adicionales
    name = name.replace('-', '_')
    
    if naming_config.get('remove_special_chars', True):
        # Mantener solo letras, números, guiones y guiones bajos
        name = re.sub(r'[^a-zA-Z0-9_-]', '', name)
    
    return name


def convert_to_mysql_by_year(file_path: str, db_config: dict, naming_config: dict) -> dict:
    """
    Convierte archivo Access por años directamente a MySQL
    
    Args:
        file_path: Ruta del archivo Access
        db_config: Configuración de la base de datos MySQL
        naming_config: Configuración de nombres personalizados
        
    Returns:
        Dict con resultado de la conversión
    """
    import streamlit as st
    import re
    from src.readers.robust_access_reader import RobustAccessReader
    from src.writers.mysql_writer import MySQLWriter
    
    try:
        # Conectar a MySQL
        mysql_writer = MySQLWriter(db_config)
        test_result = mysql_writer.test_connection()
        
        if not test_result['success']:
            raise Exception(f"No se pudo conectar a MySQL: {test_result['message']}")
        
        st.info("✅ Conectado a MySQL exitosamente")
        
        # Obtener resumen de años
        access_reader = RobustAccessReader()
        year_summary = access_reader.get_year_summary(file_path)
        
        if 'error' in year_summary:
            raise Exception(f"Error obteniendo resumen de años: {year_summary['error']}")
        
        # Contadores
        total_tables_inserted = 0
        total_rows_inserted = 0
        conversions_by_year = {}
        
        # Procesar cada tabla y año
        progress_bar = st.progress(0)
        total_jobs = sum(
            len(table_info.get('available_years', []))
            for table_info in year_summary['tables'].values()
            if 'error' not in table_info
        )
        current_job = 0
        
        for table_name, table_info in year_summary['tables'].items():
            if 'error' in table_info:
                st.warning(f"⚠️ Saltando tabla {table_name}: {table_info['error']}")
                continue
                
            if not table_info.get('available_years'):
                st.warning(f"⚠️ Tabla {table_name} no tiene años disponibles")
                continue
            
            for year in table_info['available_years']:
                try:
                    current_job += 1
                    progress_bar.progress(current_job / total_jobs)
                    
                    st.write(f"📊 Procesando tabla {table_name}, año {year}...")
                    
                    # Leer datos del año específico
                    df = access_reader.read_by_year(file_path, table_name, year)
                    
                    if df.empty:
                        st.warning(f"⚠️ No hay datos para {table_name}, año {year}")
                        continue
                    
                    # Generar nombre de tabla personalizado
                    if naming_config and (naming_config.get('table_prefix') or naming_config.get('table_suffix')):
                        # Usar configuración personalizada
                        table_base = table_name.lower() if naming_config.get('lowercase_names', True) else table_name
                        
                        if naming_config.get('table_prefix'):
                            prefix = naming_config['table_prefix'].replace('{year}', str(year))
                            mysql_table_name = f"{prefix}{table_base}"
                        else:
                            mysql_table_name = f"{table_base}_{year}"
                            
                        if naming_config.get('table_suffix'):
                            suffix = naming_config['table_suffix'].replace('{year}', str(year))
                            mysql_table_name = f"{mysql_table_name}{suffix}"
                    else:
                        # Nombre por defecto
                        mysql_table_name = f"{table_name}_{year}".lower()
                    
                    # Limpiar nombre para MySQL
                    mysql_table_name = mysql_table_name.replace('-', '_').replace(' ', '_')
                    mysql_table_name = re.sub(r'[^a-zA-Z0-9_]', '', mysql_table_name)
                    
                    # Escribir a MySQL
                    write_result = mysql_writer.write(
                        df, 
                        mysql_table_name,
                        if_exists='replace'  # Reemplazar si existe
                    )
                    
                    if write_result['success']:
                        total_tables_inserted += 1
                        total_rows_inserted += write_result['rows_written']
                        
                        conversions_by_year[f"{table_name}_{year}"] = {
                            'table': table_name,
                            'year': year,
                            'mysql_table': mysql_table_name,
                            'status': 'success',
                            'rows_inserted': write_result['rows_written'],
                            'columns': write_result['columns_written']
                        }
                        
                        st.success(f"✅ {mysql_table_name}: {write_result['rows_written']:,} filas insertadas")
                    else:
                        st.error(f"❌ Error insertando {mysql_table_name}: {write_result.get('error', 'Error desconocido')}")
                        conversions_by_year[f"{table_name}_{year}"] = {
                            'table': table_name,
                            'year': year,
                            'mysql_table': mysql_table_name,
                            'status': 'error',
                            'error': write_result.get('error', 'Error desconocido')
                        }
                
                except Exception as e:
                    st.error(f"❌ Error procesando {table_name} año {year}: {str(e)}")
                    conversions_by_year[f"{table_name}_{year}"] = {
                        'table': table_name,
                        'year': year,
                        'status': 'error',
                        'error': str(e)
                    }
        
        # Cerrar conexión MySQL
        mysql_writer.close()
        
        return {
            'input_file': file_path,
            'database_type': 'mysql',
            'database_host': db_config['host'],
            'database_name': db_config['database'],
            'total_tables_inserted': total_tables_inserted,
            'total_rows_inserted': total_rows_inserted,
            'total_files_created': total_tables_inserted,  # Para compatibilidad con la interfaz
            'total_rows_converted': total_rows_inserted,  # Para compatibilidad con la interfaz
            'conversions_by_year': conversions_by_year
        }
        
    except Exception as e:
        st.error(f"❌ Error en conversión a MySQL: {str(e)}")
        raise