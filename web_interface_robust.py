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
import time
import subprocess

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.converter import FileConverter
from src.readers.robust_access_reader import RobustAccessReader
from src.utils.logger import setup_logger
from src.utils.config import Config

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