#!/usr/bin/env python3
"""
Aplicación para ver las tablas de Railway MySQL públicamente
"""

import streamlit as st
import pandas as pd
import sys
import os
from pathlib import Path

# Agregar src al path
sys.path.append(str(Path(__file__).parent / "src"))

from src.writers.mysql_writer import MySQLWriter

# Configuración de página
st.set_page_config(
    page_title="Visor de Base de Datos MySQL",
    page_icon="🗄️",
    layout="wide"
)

def get_mysql_connection():
    """Obtener conexión MySQL usando variables de entorno"""
    db_config = {
        'type': 'mysql',
        'host': os.getenv('MYSQLHOST', 'shinkansen.proxy.rlwy.net'),
        'port': int(os.getenv('MYSQLPORT', '50498')),
        'user': os.getenv('MYSQLUSER', 'root'),
        'password': os.getenv('MYSQLPASSWORD', 'OZLeLlikuBETQMzrldNVSJNryrYEZkZJ'),
        'database': os.getenv('MYSQLDATABASE', 'railway'),
        'charset': 'utf8mb4',
        'ssl_disabled': True
    }
    return MySQLWriter(db_config)

def main():
    st.title("🗄️ Visor de Base de Datos MySQL")
    st.markdown("**Acceso público a los datos convertidos desde Access**")
    
    # Información de conexión - OCULTA por defecto
    with st.expander("� Información Técnica de Conexión", expanded=False):
        st.markdown("*Solo para administradores o desarrolladores*")
        st.code("""
Host: shinkansen.proxy.rlwy.net
Puerto: 50498
Usuario: root
Base de datos: railway
        """)
    
    # Estado de carga centralizado
    if 'loading' not in st.session_state:
        st.session_state.loading = True
    if 'connected' not in st.session_state:
        st.session_state.connected = False
    if 'tables_data' not in st.session_state:
        st.session_state.tables_data = None
    if 'current_data' not in st.session_state:
        st.session_state.current_data = None
    
    try:
        # Conectar solo una vez
        if not st.session_state.connected:
            with st.spinner("🔗 Conectando a la base de datos..."):
                mysql_writer = get_mysql_connection()
                connection_result = mysql_writer.test_connection()
                
                if not connection_result['success']:
                    st.error(f"❌ Error de conexión: {connection_result['message']}")
                    return
                
                st.session_state.connected = True
                st.session_state.mysql_writer = mysql_writer
        
        # Mostrar estado de conexión simple
        st.success("✅ Conectado a la base de datos MySQL")
        
        # Cargar datos de tablas solo una vez
        if st.session_state.tables_data is None:
            with st.spinner("📊 Cargando información de tablas..."):
                mysql_writer = st.session_state.mysql_writer
                
                with mysql_writer.engine.connect() as conn:
                    from sqlalchemy import text
                    tables_result = conn.execute(text("SHOW TABLES"))
                    tables = [row[0] for row in tables_result if not row[0].endswith('_test')]
                    
                    # Cargar conteos de una vez
                    tables_info = []
                    total_rows = 0
                    
                    for table_name in tables:
                        count_result = conn.execute(text(f"SELECT COUNT(*) FROM `{table_name}`"))
                        count = count_result.fetchone()[0]
                        total_rows += count
                        tables_info.append({
                            'name': table_name,
                            'count': count
                        })
                    
                    st.session_state.tables_data = {
                        'tables': tables_info,
                        'total_rows': total_rows
                    }
        
        # Mostrar datos cargados
        tables_data = st.session_state.tables_data
        
        if not tables_data['tables']:
            st.warning("No hay tablas disponibles")
            return
        
        st.markdown(f"**📋 Encontradas {len(tables_data['tables'])} tablas:**")
        
        # Mostrar resumen de tablas sin recargar
        col1, col2, col3 = st.columns(3)
        
        for i, table_info in enumerate(tables_data['tables']):
            with [col1, col2, col3][i % 3]:
                st.metric(
                    f"📊 {table_info['name']}",
                    f"{table_info['count']:,} filas"
                )
        
        st.markdown(f"**📈 Total de filas en todas las tablas: {tables_data['total_rows']:,}**")
            
        st.markdown(f"**📈 Total de filas en todas las tablas: {tables_data['total_rows']:,}**")
        
        # Selector de tabla para ver datos
        st.markdown("---")
        st.subheader("🔍 Explorar Datos de las Tablas")
        
        table_names = [t['name'] for t in tables_data['tables']]
        selected_table = st.selectbox("Selecciona una tabla para ver:", table_names)
        
        if selected_table:
            mysql_writer = st.session_state.mysql_writer
            
            # Cache para estructura de tabla
            cache_key = f"structure_{selected_table}"
            if cache_key not in st.session_state:
                with st.spinner(f"📋 Cargando estructura de {selected_table}..."):
                    with mysql_writer.engine.connect() as conn:
                        from sqlalchemy import text
                        desc_result = conn.execute(text(f"DESCRIBE `{selected_table}`"))
                        columns_info = list(desc_result)
                        st.session_state[cache_key] = columns_info
            
            columns_info = st.session_state[cache_key]
            columns_info = st.session_state[cache_key]
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown("**📝 Estructura de la tabla:**")
                structure_data = []
                for col_info in columns_info:
                    structure_data.append({
                        "Columna": col_info[0],
                        "Tipo": col_info[1],
                        "Nulo": col_info[2],
                        "Clave": col_info[3] or ""
                    })
                st.dataframe(structure_data, hide_index=True)
            
            with col2:
                # Controles para la consulta
                st.markdown("**⚙️ Opciones de consulta:**")
                limit = st.slider("Número de filas a mostrar:", 5, 1000, 100)
                
                show_sample = st.button("📄 Mostrar Datos", type="primary")
            
            if show_sample:
                # Consultar datos con estado de carga mejorado - SIN mostrar tabla anterior
                data_container = st.container()
                
                with st.spinner(f"📥 Cargando {limit} filas de {selected_table}..."):
                    query = f"SELECT * FROM `{selected_table}` LIMIT {limit}"
                    
                    try:
                        mysql_writer = st.session_state.mysql_writer
                        
                        # Usar pandas para mostrar los datos
                        import sqlalchemy
                        df = pd.read_sql(query, mysql_writer.engine)
                        
                        # Guardar datos en session_state
                        st.session_state.current_data = {
                            'df': df,
                            'table_name': selected_table,
                            'limit': limit
                        }
                    
                    except Exception as e:
                        st.error(f"Error al consultar datos: {str(e)}")
                        st.session_state.current_data = None
                
                # Mostrar datos SOLO cuando la carga termine
                if st.session_state.current_data:
                    current_data = st.session_state.current_data
                    df = current_data['df']
                    
                    with data_container:
                        st.markdown(f"**📊 Datos de la tabla `{current_data['table_name']}` ({len(df)} filas):**")
                        
                        # Mostrar dataframe
                        st.dataframe(
                            df,
                            use_container_width=True,
                            hide_index=False
                        )
                        
                        # Estadísticas básicas
                        if not df.empty:
                            st.markdown("**📈 Estadísticas de la consulta:**")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Filas mostradas", len(df))
                            with col2:
                                st.metric("Columnas", len(df.columns))
                            with col3:
                                # Usar datos en cache
                                table_info = next(t for t in tables_data['tables'] if t['name'] == current_data['table_name'])
                                st.metric("Total en tabla", f"{table_info['count']:,}")
                                
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.session_state.connected = False  # Reset conexión en caso de error
    
    # Botones de control
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Recargar Conexión"):
            # Limpiar cache de conexión
            for key in ['tables_data', 'connected', 'current_data']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    with col2:
        if st.button("🗑️ Limpiar Consulta"):
            # Solo limpiar datos de consulta
            if 'current_data' in st.session_state:
                del st.session_state['current_data']
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        🚀 <strong>Datos convertidos desde Microsoft Access a MySQL</strong><br>
        🌐 Base de datos accesible públicamente desde cualquier lugar del mundo
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
