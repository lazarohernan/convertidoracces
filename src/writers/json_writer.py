"""
Writer para archivos JSON
========================

Convierte DataFrames a archivos JSON con opciones de configuración.
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, Any, Optional
from src.utils.logger import get_logger


class JSONWriter:
    """Writer para archivos JSON"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.default_kwargs = {
            'orient': 'records',
            'indent': 2,
            'date_format': 'iso',
            'default_handler': str,
            'force_ascii': False
        }
    
    def write(self, df: pd.DataFrame, output_path: str, table_name: str = None, **kwargs) -> Dict[str, Any]:
        """
        Escribe un DataFrame a un archivo JSON
        
        Args:
            df: DataFrame a escribir
            output_path: Ruta del archivo de salida
            **kwargs: Opciones adicionales (orient, indent, etc.)
        
        Returns:
            Dict con información del resultado
        """
        try:
            # Combinar kwargs por defecto con los proporcionados
            write_kwargs = {**self.default_kwargs, **kwargs}
            
            # Asegurar que la extensión sea .json
            output_path = Path(output_path)
            if output_path.suffix.lower() != '.json':
                output_path = output_path.with_suffix('.json')
            
            self.logger.info(f"Escribiendo archivo JSON: {output_path}")
            
            # Crear directorio si no existe
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Escribir archivo JSON
            df.to_json(output_path, **write_kwargs)
            
            # Obtener estadísticas del archivo
            file_size = output_path.stat().st_size
            file_size_mb = file_size / 1024 / 1024
            
            result = {
                'success': True,
                'output_path': str(output_path),
                'file_size_bytes': file_size,
                'file_size_mb': file_size_mb,
                'rows_written': len(df),
                'columns_written': len(df.columns),
                'format': 'json',
                'orient': write_kwargs.get('orient', 'records'),
                'indent': write_kwargs.get('indent', 2)
            }
            
            self.logger.info(f"Archivo JSON escrito exitosamente: {output_path} ({file_size_mb:.2f} MB)")
            return result
            
        except Exception as e:
            self.logger.error(f"Error escribiendo archivo JSON: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'format': 'json'
            }
    
    def get_supported_options(self) -> Dict[str, Any]:
        """Retorna las opciones soportadas por este writer"""
        return {
            'format': 'json',
            'description': 'Archivo JSON (JavaScript Object Notation)',
            'extensions': ['.json'],
            'options': {
                'orient': ['records', 'index', 'columns', 'values', 'split', 'table'],
                'indent': [0, 2, 4],
                'date_format': ['iso', 'epoch']
            }
        } 