"""
Lector de archivos JSON
"""

import pandas as pd
import json
from typing import Dict, Any, List, Union
from src.utils.logger import get_logger

class JSONReader:
    """Clase para leer archivos JSON"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def read(self, file_path: str, **kwargs) -> pd.DataFrame:
        """
        Lee un archivo JSON y retorna un DataFrame
        
        Args:
            file_path: Ruta del archivo JSON
            **kwargs: Argumentos adicionales para pd.read_json
        
        Returns:
            DataFrame con los datos del JSON
        """
        try:
            self.logger.info(f"Leyendo archivo JSON: {file_path}")
            
            # Configuración por defecto
            default_kwargs = {
                'orient': 'records',  # Formato más común para JSON
                'encoding': 'utf-8'
            }
            
            # Combinar con kwargs proporcionados
            read_kwargs = {**default_kwargs, **kwargs}
            
            # Intentar leer como JSON de registros
            try:
                df = pd.read_json(file_path, **read_kwargs)
            except ValueError:
                # Si falla, intentar leer como JSON normal
                self.logger.warning("Intentando leer JSON con orientación diferente")
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Normalizar datos JSON
                df = self._normalize_json_data(data)
            
            # Limpiar nombres de columnas
            df.columns = df.columns.str.strip()
            
            self.logger.info(f"JSON leído exitosamente: {len(df)} filas, {len(df.columns)} columnas")
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error leyendo archivo JSON {file_path}: {str(e)}")
            raise
    
    def _normalize_json_data(self, data: Union[List, Dict]) -> pd.DataFrame:
        """
        Normaliza datos JSON a DataFrame
        
        Args:
            data: Datos JSON (lista de diccionarios o diccionario)
            
        Returns:
            DataFrame normalizado
        """
        if isinstance(data, list):
            # Lista de objetos
            if all(isinstance(item, dict) for item in data):
                return pd.DataFrame(data)
            else:
                # Lista de valores simples
                return pd.DataFrame(data, columns=['value'])
        
        elif isinstance(data, dict):
            # Diccionario
            if any(isinstance(value, list) for value in data.values()):
                # Diccionario con listas
                return pd.DataFrame(data)
            else:
                # Diccionario simple
                return pd.DataFrame([data])
        
        else:
            raise ValueError(f"Formato JSON no soportado: {type(data)}")
    
    def get_info(self, file_path: str) -> Dict[str, Any]:
        """
        Obtiene información del archivo JSON sin cargarlo completamente
        
        Args:
            file_path: Ruta del archivo JSON
            
        Returns:
            Dict con información del archivo
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Determinar estructura
            if isinstance(data, list):
                structure_type = "array"
                if data:
                    sample_item = data[0]
                    if isinstance(sample_item, dict):
                        columns = list(sample_item.keys())
                        sample_data = data[:5]  # Primeros 5 elementos
                    else:
                        columns = ['value']
                        sample_data = data[:5]
                else:
                    columns = []
                    sample_data = []
            else:
                structure_type = "object"
                columns = list(data.keys()) if isinstance(data, dict) else []
                sample_data = [data]
            
            return {
                'structure_type': structure_type,
                'columns': columns,
                'sample_data': sample_data,
                'total_items': len(data) if isinstance(data, list) else 1
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo información del JSON: {str(e)}")
            raise
    
    def read_nested_json(self, file_path: str, record_path: str = None) -> pd.DataFrame:
        """
        Lee JSON con estructura anidada
        
        Args:
            file_path: Ruta del archivo JSON
            record_path: Ruta a los registros (ej: 'data.items')
            
        Returns:
            DataFrame con datos normalizados
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Navegar a la ruta especificada
            if record_path:
                for key in record_path.split('.'):
                    data = data[key]
            
            # Normalizar datos anidados
            df = pd.json_normalize(data)
            
            self.logger.info(f"JSON anidado leído exitosamente: {len(df)} filas, {len(df.columns)} columnas")
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error leyendo JSON anidado: {str(e)}") 