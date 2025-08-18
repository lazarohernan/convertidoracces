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
        
        # Cargar datos de tablas solo una vez (usar information_schema para conteo aproximado, rápido)
        if st.session_state.tables_data is None:
            with st.spinner("📊 Cargando información de tablas..."):
                mysql_writer = st.session_state.mysql_writer
                
                with mysql_writer.engine.connect() as conn:
                    from sqlalchemy import text
                    overview_result = conn.execute(text(
                        """
                        SELECT table_name, table_rows
                        FROM information_schema.tables
                        WHERE table_schema = DATABASE()
                        """
                    ))
                    rows = overview_result.fetchall()
                    
                    tables_info = []
                    total_rows = 0
                    for name, approx_count in rows:
                        if name.endswith('_test'):
                            continue
                        count_val = int(approx_count) if approx_count is not None else 0
                        total_rows += count_val
                        tables_info.append({'name': name, 'count': count_val})
                    
                    # Ordenar por nombre para una mejor UX
                    tables_info.sort(key=lambda t: t['name'])
                    
                    st.session_state.tables_data = {
                        'tables': tables_info,
                        'total_rows': total_rows
                    }
        
        # Mostrar datos cargados
        tables_data = st.session_state.tables_data
        
        if not tables_data['tables']:
            st.warning("No hay tablas disponibles")
            return
        
        # Acción para recalcular conteos exactos de TODAS las tablas
        if st.button("🔄 Recalcular conteos exactos de todas las tablas"):
            try:
                with st.spinner("🧮 Calculando conteos exactos de todas las tablas..."):
                    mysql_writer = st.session_state.mysql_writer
                    from sqlalchemy import text
                    refreshed = []
                    total_exact = 0
                    with mysql_writer.engine.connect() as conn:
                        for t in tables_data['tables']:
                            name = t['name']
                            try:
                                exact = conn.execute(text(f"SELECT COUNT(*) FROM `{name}`")).scalar()
                                exact_int = int(exact or 0)
                            except Exception:
                                exact_int = int(t.get('count') or 0)
                            refreshed.append({'name': name, 'count': exact_int})
                            total_exact += exact_int
                    st.session_state.tables_data = {
                        'tables': refreshed,
                        'total_rows': total_exact
                    }
                st.success("Conteos exactos actualizados")
                st.rerun()
            except Exception as e:
                st.error(f"No se pudieron recalcular los conteos: {e}")

        st.markdown(f"**📋 Encontradas {len(tables_data['tables'])} tablas:**")
        
        # Mostrar resumen de tablas sin recargar
        col1, col2, col3 = st.columns(3)
        
        for i, table_info in enumerate(tables_data['tables']):
            with [col1, col2, col3][i % 3]:
                st.metric(
                    f"📊 {table_info['name']}",
                    f"{table_info['count']:,} filas"
                )
        
        st.markdown(f"**📈 Total de filas en todas las tablas (aprox.): {tables_data['total_rows']:,}**")
        
        # Selector de tabla para ver datos
        st.markdown("---")
        st.subheader("🔍 Explorar Datos de las Tablas")
        
        table_names = [t['name'] for t in tables_data['tables']]
        selected_table = st.selectbox("Selecciona una tabla para ver:", table_names)
        
        if selected_table:
            mysql_writer = st.session_state.mysql_writer
            
            # Calcular conteo exacto automáticamente al seleccionar la tabla
            auto_exact_key = f"exact_count_{selected_table}"
            # Recalcular si nunca se calculó o si cambió la tabla
            if st.session_state.get('last_selected_table') != selected_table:
                st.session_state['last_selected_table'] = selected_table
                st.session_state[auto_exact_key] = None
            
            if st.session_state.get(auto_exact_key) is None:
                with st.spinner(f"🧮 Calculando conteo exacto de {selected_table}..."):
                    try:
                        from sqlalchemy import text
                        with mysql_writer.engine.connect() as conn:
                            exact_total = conn.execute(text(f"SELECT COUNT(*) FROM `{selected_table}`")).scalar()
                        st.session_state[auto_exact_key] = int(exact_total)
                        # Actualizar cache de tablas y total global
                        for t in tables_data['tables']:
                            if t['name'] == selected_table:
                                t['count'] = st.session_state[auto_exact_key]
                                break
                        tables_data['total_rows'] = sum(t['count'] for t in tables_data['tables'])
                    except Exception as e:
                        st.warning(f"No se pudo obtener conteo exacto: {e}")
            
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
                # Controles para la consulta (paginación)
                st.markdown("**⚙️ Opciones de consulta:**")
                page_size = st.slider("Filas por página:", 10, 1000, 100)
                page_number = st.number_input("Página:", min_value=1, value=1, step=1)
                show_sample = st.button("📄 Mostrar Datos", type="primary")
            
            if show_sample:
                # Consultar datos con estado de carga mejorado - SIN mostrar tabla anterior
                data_container = st.container()
                
                # Calcular offset para paginación
                import math
                # Usar conteo exacto si ya fue calculado; sino aproximado
                table_info = next(t for t in tables_data['tables'] if t['name'] == selected_table)
                exact_total_val = st.session_state.get(auto_exact_key)
                effective_total = int(exact_total_val) if exact_total_val is not None else int(table_info['count'] or 0)
                total_pages = max(1, math.ceil(effective_total / page_size)) if effective_total > 0 else 1
                current_page = min(page_number, total_pages)
                offset = (current_page - 1) * page_size
                
                with st.spinner(f"📥 Cargando {page_size} filas de {selected_table} (página {current_page}/{total_pages})..."):
                    query = f"SELECT * FROM `{selected_table}` LIMIT {page_size} OFFSET {offset}"
                    
                    try:
                        mysql_writer = st.session_state.mysql_writer
                        
                        # Usar pandas para mostrar los datos
                        import sqlalchemy
                        df = pd.read_sql(query, mysql_writer.engine)
                        
                        # Guardar datos en session_state
                        st.session_state.current_data = {
                            'df': df,
                            'table_name': selected_table,
                            'page_size': page_size,
                            'page': current_page,
                            'total_rows_effective': effective_total,
                            'total_pages': total_pages
                        }
                    
                    except Exception as e:
                        st.error(f"Error al consultar datos: {str(e)}")
                        st.session_state.current_data = None
                
                # Mostrar datos SOLO cuando la carga termine
                if st.session_state.current_data:
                    current_data = st.session_state.current_data
                    df = current_data['df']
                    
                    with data_container:
                        st.markdown(f"**📊 Datos de la tabla `{current_data['table_name']}` (mostrando {len(df)} filas):**")
                        
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
                                st.metric("Total en tabla (exacto)", f"{current_data['total_rows_effective']:,}")
                            
                            # Mostrar paginación y notas
                            colp1, colp2, colp3 = st.columns(3)
                            with colp1:
                                st.caption(f"Página {current_data['page']} de {current_data['total_pages']}")
                            with colp2:
                                st.caption("Mostrando conteo exacto")
                                
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
        🚀 <strong>Datos convertidos desde Microsoft Access a MySQL</strong>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
