"""
Writer para archivos CSV
=======================

Convierte DataFrames a archivos CSV con opciones de configuración.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional
from src.utils.logger import get_logger


class CSVWriter:
    """Writer para archivos CSV"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.default_kwargs = {
            'index': False,
            'encoding': 'utf-8',
            'sep': ',',
            'decimal': '.',
            'date_format': '%Y-%m-%d'
        }
    
    def write(self, df: pd.DataFrame, output_path: str, table_name: str = None, **kwargs) -> Dict[str, Any]:
        """
        Escribe un DataFrame a un archivo CSV
        
        Args:
            df: DataFrame a escribir
            output_path: Ruta del archivo de salida
            **kwargs: Opciones adicionales (encoding, sep, decimal, etc.)
        
        Returns:
            Dict con información del resultado
        """
        try:
            # Combinar kwargs por defecto con los proporcionados
            write_kwargs = {**self.default_kwargs, **kwargs}
            
            # Asegurar que la extensión sea .csv
            output_path = Path(output_path)
            if output_path.suffix.lower() != '.csv':
                output_path = output_path.with_suffix('.csv')
            
            self.logger.info(f"Escribiendo archivo CSV: {output_path}")
            
            # Crear directorio si no existe
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Escribir archivo CSV
            df.to_csv(output_path, **write_kwargs)
            
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
                'format': 'csv',
                'encoding': write_kwargs.get('encoding', 'utf-8'),
                'separator': write_kwargs.get('sep', ',')
            }
            
            self.logger.info(f"Archivo CSV escrito exitosamente: {output_path} ({file_size_mb:.2f} MB)")
            return result
            
        except Exception as e:
            self.logger.error(f"Error escribiendo archivo CSV: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'format': 'csv'
            }
    
    def get_supported_options(self) -> Dict[str, Any]:
        """Retorna las opciones soportadas por este writer"""
        return {
            'format': 'csv',
            'description': 'Archivo CSV (Comma-Separated Values)',
            'extensions': ['.csv'],
            'options': {
                'encoding': ['utf-8', 'latin-1', 'cp1252'],
                'separator': [',', ';', '\t', '|'],
                'decimal': ['.', ','],
                'index': [True, False]
            }
        } 