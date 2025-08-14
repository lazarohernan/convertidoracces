"""
Sistema de configuración
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from src.utils.logger import get_logger

class Config:
    """Clase para manejar la configuración de la aplicación"""
    
    def __init__(self, env_file: str = ".env"):
        self.logger = get_logger(__name__)
        
        # Cargar variables de entorno
        load_dotenv(env_file)
        
        # Configuración por defecto
        self.defaults = {
            'DEFAULT_OUTPUT_FORMAT': 'sql',
            'DEFAULT_TABLE_NAME': 'data_table',
            'MAX_FILE_SIZE_MB': 100,
            'LOG_LEVEL': 'INFO',
            'LOG_FILE': 'logs/converter.log'
        }
        
        # Cargar configuración
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Carga la configuración desde variables de entorno"""
        config = {}
        
        for key, default_value in self.defaults.items():
            env_value = os.getenv(key, default_value)
            
            # Convertir tipos según sea necesario
            if key == 'MAX_FILE_SIZE_MB':
                config[key] = int(env_value)
            else:
                config[key] = env_value
        
        self.logger.info("Configuración cargada exitosamente")
        return config
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor de configuración
        
        Args:
            key: Clave de configuración
            default: Valor por defecto si no existe
            
        Returns:
            Valor de configuración
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """
        Establece un valor de configuración
        
        Args:
            key: Clave de configuración
            value: Valor a establecer
        """
        self.config[key] = value
        self.logger.info(f"Configuración actualizada: {key} = {value}")
    
    def get_supported_formats(self) -> Dict[str, list]:
        """Retorna los formatos soportados"""
        return {
            'input': ['.csv', '.xlsx', '.xls', '.json'],
            'output': ['sql', 'sqlite']
        }
    
    def validate_config(self) -> bool:
        """
        Valida la configuración actual
        
        Returns:
            True si la configuración es válida
        """
        try:
            # Validar formato de salida por defecto
            default_format = self.get('DEFAULT_OUTPUT_FORMAT')
            supported_formats = self.get_supported_formats()['output']
            
            if default_format not in supported_formats:
                self.logger.warning(f"Formato de salida por defecto no soportado: {default_format}")
                return False
            
            # Validar tamaño máximo de archivo
            max_size = self.get('MAX_FILE_SIZE_MB')
            if not isinstance(max_size, int) or max_size <= 0:
                self.logger.error("MAX_FILE_SIZE_MB debe ser un entero positivo")
                return False
            
            self.logger.info("Configuración validada exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error validando configuración: {str(e)}")
            return False
    
    def get_database_config(self, db_type: str) -> Dict[str, Any]:
        """
        Obtiene configuración de base de datos específica
        
        Args:
            db_type: Tipo de base de datos
            
        Returns:
            Configuración de la base de datos
        """
        if db_type.lower() == 'postgresql':
            return {
                'host': os.getenv('POSTGRES_HOST', 'localhost'),
                'port': int(os.getenv('POSTGRES_PORT', 5432)),
                'database': os.getenv('POSTGRES_DB', ''),
                'user': os.getenv('POSTGRES_USER', ''),
                'password': os.getenv('POSTGRES_PASSWORD', '')
            }
        elif db_type.lower() == 'supabase':
            return {
                'url': os.getenv('SUPABASE_URL', ''),
                'key': os.getenv('SUPABASE_KEY', '')
            }
        else:
            return {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Retorna la configuración como diccionario"""
        return self.config.copy() 