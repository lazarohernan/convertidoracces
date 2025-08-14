"""
Lector de archivos Excel
"""

import pandas as pd
from typing import Dict, Any, List
from src.utils.logger import get_logger

class ExcelReader:
    """Clase para leer archivos Excel"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def read(self, file_path: str, sheet_name: str = None, **kwargs) -> pd.DataFrame:
        """
        Lee un archivo Excel y retorna un DataFrame
        
        Args:
            file_path: Ruta del archivo Excel
            sheet_name: Nombre de la hoja a leer (None para la primera)
            **kwargs: Argumentos adicionales para pd.read_excel
        
        Returns:
            DataFrame con los datos del Excel
        """
        try:
            self.logger.info(f"Leyendo archivo Excel: {file_path}")
            
            # Configuración por defecto
            default_kwargs = {
                'sheet_name': sheet_name or 0,  # Primera hoja por defecto
                'header': 0,  # Primera fila como header
                'na_values': ['', 'NULL', 'null', 'NaN', 'nan'],
                'keep_default_na': True
            }
            
            # Combinar con kwargs proporcionados
            read_kwargs = {**default_kwargs, **kwargs}
            
            # Leer el archivo
            df = pd.read_excel(file_path, **read_kwargs)
            
            # Limpiar nombres de columnas
            df.columns = df.columns.str.strip()
            
            self.logger.info(f"Excel leído exitosamente: {len(df)} filas, {len(df.columns)} columnas")
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error leyendo archivo Excel {file_path}: {str(e)}")
            raise
    
    def get_sheet_names(self, file_path: str) -> List[str]:
        """
        Obtiene la lista de nombres de hojas en el archivo Excel
        
        Args:
            file_path: Ruta del archivo Excel
            
        Returns:
            Lista de nombres de hojas
        """
        try:
            excel_file = pd.ExcelFile(file_path)
            return excel_file.sheet_names
        except Exception as e:
            self.logger.error(f"Error obteniendo nombres de hojas: {str(e)}")
            raise
    
    def read_all_sheets(self, file_path: str, **kwargs) -> Dict[str, pd.DataFrame]:
        """
        Lee todas las hojas del archivo Excel
        
        Args:
            file_path: Ruta del archivo Excel
            **kwargs: Argumentos adicionales
            
        Returns:
            Dict con nombre de hoja como clave y DataFrame como valor
        """
        try:
            self.logger.info(f"Leyendo todas las hojas del archivo Excel: {file_path}")
            
            # Leer todas las hojas
            all_sheets = pd.read_excel(file_path, sheet_name=None, **kwargs)
            
            # Limpiar nombres de columnas en todas las hojas
            for sheet_name, df in all_sheets.items():
                df.columns = df.columns.str.strip()
            
            self.logger.info(f"Excel leído exitosamente: {len(all_sheets)} hojas")
            
            return all_sheets
            
        except Exception as e:
            self.logger.error(f"Error leyendo todas las hojas del Excel: {str(e)}")
            raise
    
    def get_info(self, file_path: str, sheet_name: str = None) -> Dict[str, Any]:
        """
        Obtiene información del archivo Excel sin cargarlo completamente
        
        Args:
            file_path: Ruta del archivo Excel
            sheet_name: Nombre de la hoja (None para la primera)
            
        Returns:
            Dict con información del archivo
        """
        try:
            # Obtener nombres de hojas
            sheet_names = self.get_sheet_names(file_path)
            
            # Leer solo las primeras filas para obtener información
            df_sample = pd.read_excel(
                file_path, 
                sheet_name=sheet_name or 0,
                nrows=5
            )
            
            return {
                'sheet_names': sheet_names,
                'current_sheet': sheet_name or sheet_names[0],
                'columns': df_sample.columns.tolist(),
                'sample_data': df_sample.to_dict('records'),
                'file_size_mb': df_sample.memory_usage(deep=True).sum() / (1024 * 1024)
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo información del Excel: {str(e)}")
            raise 