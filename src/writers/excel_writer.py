"""
Writer para archivos Excel
=========================

Convierte DataFrames a archivos Excel (.xlsx) con opciones de configuración.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional
from src.utils.logger import get_logger


class ExcelWriter:
    """Writer para archivos Excel"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.default_kwargs = {
            'index': False,
            'engine': 'openpyxl',
            'sheet_name': 'Sheet1',
            'na_rep': '',
            'float_format': None,
            'date_format': 'YYYY-MM-DD',
            'datetime_format': 'YYYY-MM-DD HH:MM:SS'
        }
    
    def write(self, df: pd.DataFrame, output_path: str, table_name: str = None, **kwargs) -> Dict[str, Any]:
        """
        Escribe un DataFrame a un archivo Excel
        
        Args:
            df: DataFrame a escribir
            output_path: Ruta del archivo de salida
            **kwargs: Opciones adicionales (sheet_name, engine, etc.)
        
        Returns:
            Dict con información del resultado
        """
        try:
            # Combinar kwargs por defecto con los proporcionados
            write_kwargs = {**self.default_kwargs, **kwargs}
            
            # Asegurar que la extensión sea .xlsx
            output_path = Path(output_path)
            if output_path.suffix.lower() not in ['.xlsx', '.xls']:
                output_path = output_path.with_suffix('.xlsx')
            
            self.logger.info(f"Escribiendo archivo Excel: {output_path}")
            
            # Crear directorio si no existe
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Escribir archivo Excel
            with pd.ExcelWriter(output_path, engine=write_kwargs.get('engine', 'openpyxl')) as writer:
                df.to_excel(writer, sheet_name=write_kwargs.get('sheet_name', 'Sheet1'), 
                           index=write_kwargs.get('index', False))
            
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
                'format': 'excel',
                'sheet_name': write_kwargs.get('sheet_name', 'Sheet1'),
                'engine': write_kwargs.get('engine', 'openpyxl')
            }
            
            self.logger.info(f"Archivo Excel escrito exitosamente: {output_path} ({file_size_mb:.2f} MB)")
            return result
            
        except Exception as e:
            self.logger.error(f"Error escribiendo archivo Excel: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'format': 'excel'
            }
    
    def get_supported_options(self) -> Dict[str, Any]:
        """Retorna las opciones soportadas por este writer"""
        return {
            'format': 'excel',
            'description': 'Archivo Excel (.xlsx)',
            'extensions': ['.xlsx', '.xls'],
            'options': {
                'engine': ['openpyxl', 'xlsxwriter'],
                'sheet_name': ['Sheet1', 'Data', 'Datos'],
                'index': [True, False]
            }
        } 