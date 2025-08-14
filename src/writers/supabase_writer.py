"""
Escritor de Supabase (placeholder para uso futuro)
"""

import pandas as pd
from typing import Dict, Any
from src.utils.logger import get_logger

class SupabaseWriter:
    """Clase para escribir a Supabase (implementación futura)"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.logger.warning("SupabaseWriter no está implementado aún. Usando SQL como fallback.")
    
    def write(
        self, 
        df: pd.DataFrame, 
        output_path: str, 
        table_name: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """
        Placeholder para escritura a Supabase
        
        Args:
            df: DataFrame a convertir
            output_path: Ruta del archivo de salida
            table_name: Nombre de la tabla
            **kwargs: Argumentos adicionales
        
        Returns:
            Dict con información del resultado
        """
        # Por ahora, generar SQL como fallback
        from src.writers.sql_writer import SQLWriter
        
        sql_writer = SQLWriter()
        result = sql_writer.write(df, output_path, table_name, **kwargs)
        
        result['note'] = 'SupabaseWriter no implementado. Se generó SQL como alternativa.'
        
        return result 