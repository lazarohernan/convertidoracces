"""
Escritor de archivos SQLite
"""

import pandas as pd
import sqlite3
from typing import Dict, Any
from src.utils.logger import get_logger

class SQLiteWriter:
    """Clase para escribir archivos SQLite"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def write(
        self, 
        df: pd.DataFrame, 
        output_path: str, 
        table_name: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """
        Escribe un DataFrame a una base de datos SQLite
        
        Args:
            df: DataFrame a convertir
            output_path: Ruta del archivo SQLite
            table_name: Nombre de la tabla
            **kwargs: Argumentos adicionales (if_exists, index, etc.)
        
        Returns:
            Dict con información del resultado
        """
        try:
            self.logger.info(f"Escribiendo base de datos SQLite: {output_path}")
            
            # Configuración por defecto
            default_kwargs = {
                'if_exists': 'replace',  # Reemplazar tabla si existe
                'index': False  # No incluir índice
            }
            
            # Combinar con kwargs proporcionados
            write_kwargs = {**default_kwargs, **kwargs}
            
            # Crear conexión y escribir
            with sqlite3.connect(output_path) as conn:
                # Escribir DataFrame a SQLite
                df.to_sql(table_name, conn, **write_kwargs)
                
                # Obtener información de la tabla
                table_info = self._get_table_info(conn, table_name)
                
                # Verificar que los datos se escribieron correctamente
                row_count = pd.read_sql(f"SELECT COUNT(*) as count FROM {table_name}", conn).iloc[0]['count']
            
            result = {
                'success': True,
                'output_file': output_path,
                'table_name': table_name,
                'rows_inserted': row_count,
                'columns': len(df.columns),
                'table_info': table_info,
                'file_size_mb': self._get_file_size(output_path)
            }
            
            self.logger.info(f"Base de datos SQLite creada exitosamente: {output_path}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error escribiendo SQLite: {str(e)}")
            raise
    
    def _get_table_info(self, conn: sqlite3.connect, table_name: str) -> Dict[str, Any]:
        """
        Obtiene información de la tabla creada
        
        Args:
            conn: Conexión SQLite
            table_name: Nombre de la tabla
            
        Returns:
            Dict con información de la tabla
        """
        try:
            # Obtener schema de la tabla
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = cursor.fetchall()
            
            # Obtener estadísticas
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            return {
                'columns': [
                    {
                        'name': col[1],
                        'type': col[2],
                        'not_null': bool(col[3]),
                        'primary_key': bool(col[5])
                    }
                    for col in columns_info
                ],
                'row_count': row_count
            }
            
        except Exception as e:
            self.logger.warning(f"Error obteniendo información de tabla: {str(e)}")
            return {}
    
    def _get_file_size(self, file_path: str) -> float:
        """
        Obtiene el tamaño del archivo en MB
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            Tamaño en MB
        """
        import os
        return os.path.getsize(file_path) / (1024 * 1024)
    
    def write_multiple_tables(
        self, 
        dataframes: Dict[str, pd.DataFrame], 
        output_path: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """
        Escribe múltiples DataFrames como tablas separadas
        
        Args:
            dataframes: Dict con nombre de tabla como clave y DataFrame como valor
            output_path: Ruta del archivo SQLite
            **kwargs: Argumentos adicionales
        
        Returns:
            Dict con información del resultado
        """
        try:
            self.logger.info(f"Escribiendo múltiples tablas a SQLite: {output_path}")
            
            results = {}
            
            with sqlite3.connect(output_path) as conn:
                for table_name, df in dataframes.items():
                    try:
                        # Escribir tabla
                        df.to_sql(table_name, conn, if_exists='replace', index=False, **kwargs)
                        
                        # Obtener información
                        table_info = self._get_table_info(conn, table_name)
                        
                        results[table_name] = {
                            'success': True,
                            'rows_inserted': len(df),
                            'columns': len(df.columns),
                            'table_info': table_info
                        }
                        
                        self.logger.info(f"Tabla '{table_name}' escrita exitosamente")
                        
                    except Exception as e:
                        self.logger.error(f"Error escribiendo tabla '{table_name}': {str(e)}")
                        results[table_name] = {
                            'success': False,
                            'error': str(e)
                        }
            
            result = {
                'success': True,
                'output_file': output_path,
                'tables': results,
                'total_tables': len(dataframes),
                'successful_tables': sum(1 for r in results.values() if r.get('success', False)),
                'file_size_mb': self._get_file_size(output_path)
            }
            
            self.logger.info(f"Base de datos SQLite con múltiples tablas creada: {output_path}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error escribiendo múltiples tablas: {str(e)}")
            raise
    
    def create_indexes(
        self, 
        db_path: str, 
        table_name: str, 
        columns: list, 
        index_name: str = None
    ) -> Dict[str, Any]:
        """
        Crea índices en la tabla SQLite
        
        Args:
            db_path: Ruta de la base de datos
            table_name: Nombre de la tabla
            columns: Lista de columnas para el índice
            index_name: Nombre del índice (opcional)
        
        Returns:
            Dict con información del resultado
        """
        try:
            if not index_name:
                index_name = f"idx_{table_name}_{'_'.join(columns)}"
            
            with sqlite3.connect(db_path) as conn:
                columns_str = ', '.join(columns)
                create_index_sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({columns_str})"
                
                conn.execute(create_index_sql)
                conn.commit()
            
            result = {
                'success': True,
                'index_name': index_name,
                'table_name': table_name,
                'columns': columns
            }
            
            self.logger.info(f"Índice creado exitosamente: {index_name}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error creando índice: {str(e)}")
            raise 