"""
Lector de archivos CSV
"""

import pandas as pd
from typing import Dict, Any
from src.utils.logger import get_logger

class CSVReader:
    """Clase para leer archivos CSV"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def read(self, file_path: str, **kwargs) -> pd.DataFrame:
        """
        Lee un archivo CSV y retorna un DataFrame
        
        Args:
            file_path: Ruta del archivo CSV
            **kwargs: Argumentos adicionales para pd.read_csv
        
        Returns:
            DataFrame con los datos del CSV
        """
        try:
            self.logger.info(f"Leyendo archivo CSV: {file_path}")
            
            # Configuración por defecto
            default_kwargs = {
                'encoding': 'utf-8',
                'delimiter': ',',
                'quotechar': '"',
                'escapechar': '\\',
                'na_values': ['', 'NULL', 'null', 'NaN', 'nan'],
                'keep_default_na': True
            }
            
            # Combinar con kwargs proporcionados
            read_kwargs = {**default_kwargs, **kwargs}
            
            # Leer el archivo
            df = pd.read_csv(file_path, **read_kwargs)
            
            # Limpiar nombres de columnas
            df.columns = df.columns.str.strip()
            
            self.logger.info(f"CSV leído exitosamente: {len(df)} filas, {len(df.columns)} columnas")
            
            return df
            
        except UnicodeDecodeError:
            # Intentar con diferentes encodings
            self.logger.warning(f"Error de encoding en {file_path}, intentando con 'latin-1'")
            try:
                df = pd.read_csv(file_path, encoding='latin-1', **kwargs)
                df.columns = df.columns.str.strip()
                return df
            except Exception as e:
                self.logger.error(f"Error leyendo CSV con encoding alternativo: {str(e)}")
                raise
        
        except Exception as e:
            self.logger.error(f"Error leyendo archivo CSV {file_path}: {str(e)}")
            raise
    
    def get_info(self, file_path: str) -> Dict[str, Any]:
        """
        Obtiene información del archivo CSV sin cargarlo completamente
        
        Args:
            file_path: Ruta del archivo CSV
            
        Returns:
            Dict con información del archivo
        """
        try:
            # Leer solo las primeras filas para obtener información
            df_sample = pd.read_csv(file_path, nrows=5)
            
            # Contar líneas para estimar el número de filas
            with open(file_path, 'r', encoding='utf-8') as f:
                line_count = sum(1 for _ in f)
            
            return {
                'columns': df_sample.columns.tolist(),
                'sample_data': df_sample.to_dict('records'),
                'estimated_rows': line_count - 1,  # Restar la línea del header
                'file_size_mb': df_sample.memory_usage(deep=True).sum() / (1024 * 1024)
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo información del CSV: {str(e)}")
            raise 