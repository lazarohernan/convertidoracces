"""
Configuración UI para MySQL y personalización de nombres
"""

import streamlit as st
from typing import Dict, Any, Optional

class MySQLConfigUI:
    """Interfaz de usuario para configuración de MySQL y nombres personalizados"""
    
    def __init__(self):
        pass
    
    def render_naming_config(self) -> Dict[str, Any]:
        """
        Renderiza la configuración de nombres personalizados
        
        Returns:
            Dict con configuración de nombres
        """
        st.markdown("**🏷️ Personalización de Nombres de Archivos:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            table_prefix = st.text_input(
                "Prefijo de archivos",
                value="",
                help="Prefijo que se añadirá al inicio del nombre de cada archivo de salida"
            )
        
        with col2:
            table_suffix = st.text_input(
                "Sufijo de archivos", 
                value="",
                help="Sufijo que se añadirá al final del nombre de cada archivo de salida"
            )
        
        # Configuraciones adicionales
        st.markdown("**📁 Opciones de Nomenclatura:**")
        
        col3, col4 = st.columns(2)
        
        with col3:
            use_timestamp = st.checkbox(
                "Incluir timestamp",
                value=False,
                help="Añadir fecha y hora al nombre del archivo"
            )
            
            lowercase_names = st.checkbox(
                "Convertir a minúsculas",
                value=True,
                help="Convertir todos los nombres a minúsculas"
            )
        
        with col4:
            replace_spaces = st.checkbox(
                "Reemplazar espacios por _",
                value=True,
                help="Reemplazar espacios en blanco por guiones bajos"
            )
            
            remove_special_chars = st.checkbox(
                "Remover caracteres especiales",
                value=True,
                help="Eliminar caracteres especiales del nombre"
            )
        
        # Previsualización del nombre
        if table_prefix or table_suffix:
            sample_name = "ejemplo_tabla"
            preview_name = self._preview_name(
                sample_name, 
                table_prefix, 
                table_suffix, 
                use_timestamp,
                lowercase_names,
                replace_spaces,
                remove_special_chars
            )
            st.info(f"📋 Vista previa: `{preview_name}`")
        
        return {
            'table_prefix': table_prefix,
            'table_suffix': table_suffix,
            'use_timestamp': use_timestamp,
            'lowercase_names': lowercase_names,
            'replace_spaces': replace_spaces,
            'remove_special_chars': remove_special_chars
        }
    
    def render_full_config(self) -> Optional[Dict[str, Any]]:
        """
        Renderiza configuración completa de MySQL
        
        Returns:
            Dict con configuración de MySQL o None si incompleta
        """
        st.markdown("**🔧 Configuración de Conexión MySQL:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            host = st.text_input("Host", value="localhost")
            port = st.number_input("Puerto", value=3306, min_value=1, max_value=65535)
            database = st.text_input("Base de datos", value="")
        
        with col2:
            username = st.text_input("Usuario", value="")
            password = st.text_input("Contraseña", type="password", value="")
        
        # Configuraciones avanzadas
        with st.expander("⚙️ Configuración Avanzada", expanded=False):
            col3, col4 = st.columns(2)
            
            with col3:
                charset = st.selectbox(
                    "Codificación",
                    options=['utf8mb4', 'utf8', 'latin1'],
                    index=0
                )
                
                timeout = st.number_input(
                    "Timeout (segundos)",
                    value=30,
                    min_value=1,
                    max_value=300
                )
            
            with col4:
                ssl_mode = st.selectbox(
                    "Modo SSL",
                    options=['DISABLED', 'REQUIRED', 'VERIFY_CA', 'VERIFY_IDENTITY'],
                    index=0
                )
                
                autocommit = st.checkbox(
                    "Auto-commit",
                    value=True,
                    help="Confirmar transacciones automáticamente"
                )
        
        # Validar configuración
        if not all([host, database, username, password]):
            st.warning("⚠️ Complete todos los campos obligatorios para habilitar MySQL")
            return None
        
        config = {
            'host': host,
            'port': int(port),
            'database': database,
            'user': username,
            'password': password,
            'charset': charset,
            'connect_timeout': int(timeout),
            'ssl_disabled': ssl_mode == 'DISABLED',
            'autocommit': autocommit
        }
        
        # Botón de prueba de conexión
        if st.button("🔍 Probar Conexión"):
            st.info("🔄 Funcionalidad de prueba de conexión disponible próximamente...")
        
        return config
    
    def _preview_name(
        self, 
        original_name: str,
        prefix: str = "",
        suffix: str = "",
        use_timestamp: bool = False,
        lowercase_names: bool = True,
        replace_spaces: bool = True,
        remove_special_chars: bool = True
    ) -> str:
        """
        Genera una vista previa del nombre procesado
        
        Args:
            original_name: Nombre original
            prefix: Prefijo a añadir
            suffix: Sufijo a añadir
            use_timestamp: Si incluir timestamp
            lowercase_names: Si convertir a minúsculas
            replace_spaces: Si reemplazar espacios
            remove_special_chars: Si remover caracteres especiales
            
        Returns:
            Nombre procesado
        """
        import re
        from datetime import datetime
        
        name = original_name
        
        # Aplicar prefijo
        if prefix:
            name = f"{prefix}{name}"
        
        # Aplicar sufijo
        if suffix:
            name = f"{name}{suffix}"
        
        # Timestamp
        if use_timestamp:
            timestamp = datetime.now().strftime("_%Y%m%d_%H%M%S")
            name = f"{name}{timestamp}"
        
        # Procesar texto
        if lowercase_names:
            name = name.lower()
        
        if replace_spaces:
            name = name.replace(' ', '_')
        
        if remove_special_chars:
            # Mantener solo letras, números, guiones y guiones bajos
            name = re.sub(r'[^a-zA-Z0-9_-]', '', name)
        
        return name
