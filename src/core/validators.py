"""
Sistema de validación de datos
"""

import pandas as pd
import os
from typing import Dict, List, Any, Optional
from .exceptions import ValidationError, FileFormatError

class DataValidator:
    """Clase para validar datos y archivos"""
    
    SUPPORTED_FORMATS = {
        'input': ['.csv', '.xlsx', '.xls', '.json', '.accdb', '.mdb'],
        'output': ['sql', 'sqlite', 'postgresql', 'supabase', 'csv', 'excel', 'json']
    }
    
    def __init__(self):
        self.max_file_size_mb = 1024  # Tamaño máximo por defecto
    
    def validate_file_path(self, file_path: str) -> bool:
        """Valida que el archivo existe y es accesible"""
        if not os.path.exists(file_path):
            raise ValidationError(f"El archivo no existe: {file_path}")
        
        if not os.path.isfile(file_path):
            raise ValidationError(f"La ruta no es un archivo: {file_path}")
        
        if not os.access(file_path, os.R_OK):
            raise ValidationError(f"No se puede leer el archivo: {file_path}")
        
        return True
    
    def validate_file_format(self, file_path: str) -> bool:
        """Valida que el formato del archivo es soportado"""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension not in self.SUPPORTED_FORMATS['input']:
            raise FileFormatError(
                f"Formato no soportado: {file_extension}. "
                f"Formatos soportados: {', '.join(self.SUPPORTED_FORMATS['input'])}"
            )
        
        return True
    
    def validate_file_size(self, file_path: str) -> bool:
        """Valida que el archivo no exceda el tamaño máximo"""
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        
        if file_size_mb > self.max_file_size_mb:
            raise ValidationError(
                f"El archivo es demasiado grande: {file_size_mb:.2f}MB. "
                f"Máximo permitido: {self.max_file_size_mb}MB"
            )
        
        return True
    
    def validate_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Valida la estructura y calidad del DataFrame"""
        validation_result = {
            'is_valid': True,
            'rows': len(df),
            'columns': len(df.columns),
            'missing_values': df.isnull().sum().sum(),
            'duplicate_rows': df.duplicated().sum(),
            'warnings': []
        }
        
        # Verificar si el DataFrame está vacío
        if df.empty:
            validation_result['is_valid'] = False
            validation_result['warnings'].append("El DataFrame está vacío")
        
        # Verificar columnas vacías
        empty_columns = df.columns[df.isnull().all()].tolist()
        if empty_columns:
            validation_result['warnings'].append(f"Columnas completamente vacías: {empty_columns}")
        
        # Verificar tipos de datos
        data_types = df.dtypes.to_dict()
        validation_result['data_types'] = data_types
        
        return validation_result
    
    def validate_output_format(self, output_format: str) -> bool:
        """Valida que el formato de salida sea soportado"""
        if output_format.lower() not in self.SUPPORTED_FORMATS['output']:
            raise ValidationError(
                f"Formato de salida no soportado: {output_format}. "
                f"Formatos soportados: {', '.join(self.SUPPORTED_FORMATS['output'])}"
            )
        
        return True
    
    def validate_table_name(self, table_name: str) -> bool:
        """Valida que el nombre de la tabla sea válido"""
        import re
        
        # Patrón para nombres de tabla válidos
        pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
        
        if not re.match(pattern, table_name):
            raise ValidationError(
                f"Nombre de tabla inválido: {table_name}. "
                "Debe comenzar con letra o guión bajo y contener solo letras, números y guiones bajos"
            )
        
        # Palabras reservadas de SQL
        reserved_words = [
            'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP',
            'TABLE', 'DATABASE', 'INDEX', 'PRIMARY', 'FOREIGN', 'KEY', 'CONSTRAINT'
        ]
        
        if table_name.upper() in reserved_words:
            raise ValidationError(f"El nombre de tabla '{table_name}' es una palabra reservada de SQL")
        
        return True
    
    def validate_output_directory(self, output_dir: str) -> bool:
        """Valida que el directorio de salida existe y es escribible"""
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except OSError as e:
                raise ValidationError(f"No se puede crear el directorio de salida: {e}")
        
        if not os.access(output_dir, os.W_OK):
            raise ValidationError(f"No se puede escribir en el directorio: {output_dir}")
        
        return True 