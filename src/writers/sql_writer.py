"""
Escritor de archivos SQL
"""

import pandas as pd
from typing import Dict, Any, List
from src.utils.logger import get_logger

class SQLWriter:
    """Clase para escribir archivos SQL"""
    
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
        Escribe un DataFrame a un archivo SQL
        
        Args:
            df: DataFrame a convertir
            output_path: Ruta del archivo de salida
            table_name: Nombre de la tabla
            **kwargs: Argumentos adicionales
        
        Returns:
            Dict con información del resultado
        """
        try:
            # Si se especifica batch_size, usar escritura en lotes para mejor rendimiento
            batch_size = kwargs.get('batch_size')
            if isinstance(batch_size, int) and batch_size > 0:
                return self.write_batch_insert(df, output_path, table_name, batch_size=batch_size)

            self.logger.info(f"Escribiendo archivo SQL: {output_path}")
            
            # Generar SQL
            create_table_sql = self._generate_create_table(df, table_name)
            insert_statements = self._generate_insert_statements(df, table_name)
            
            # Escribir archivo
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"-- Archivo SQL generado automáticamente\n")
                f.write(f"-- Tabla: {table_name}\n")
                f.write(f"-- Filas: {len(df)}\n")
                f.write(f"-- Columnas: {len(df.columns)}\n\n")
                
                # CREATE TABLE
                f.write(create_table_sql)
                f.write("\n\n")
                
                # INSERT statements
                for insert_sql in insert_statements:
                    f.write(insert_sql + "\n")
            
            result = {
                'success': True,
                'output_file': output_path,
                'table_name': table_name,
                'rows_inserted': len(df),
                'columns': len(df.columns),
                'create_table_sql': create_table_sql,
                'insert_count': len(insert_statements)
            }
            
            self.logger.info(f"Archivo SQL escrito exitosamente: {output_path}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error escribiendo archivo SQL: {str(e)}")
            raise
    
    def _generate_create_table(self, df: pd.DataFrame, table_name: str) -> str:
        """
        Genera el statement CREATE TABLE
        
        Args:
            df: DataFrame
            table_name: Nombre de la tabla
            
        Returns:
            String con el CREATE TABLE
        """
        columns = []
        
        for col_name, dtype in df.dtypes.items():
            # Mapear tipos de pandas a SQL
            sql_type = self._map_pandas_to_sql_type(dtype)
            # Usar backticks para MySQL, comillas dobles para otros
            columns.append(f'    `{col_name}` {sql_type}')
        
        create_sql = f"CREATE TABLE IF NOT EXISTS `{table_name}` (\n"
        create_sql += ",\n".join(columns)
        create_sql += "\n);"
        
        return create_sql
    
    def _generate_insert_statements(self, df: pd.DataFrame, table_name: str) -> List[str]:
        """
        Genera los statements INSERT
        
        Args:
            df: DataFrame
            table_name: Nombre de la tabla
            
        Returns:
            Lista de statements INSERT
        """
        insert_statements = []
        columns = [f'`{col}`' for col in df.columns]
        columns_str = ', '.join(columns)
        
        for _, row in df.iterrows():
            # Escapar valores
            values = []
            for val in row.values:
                if pd.isna(val):
                    values.append('NULL')
                elif isinstance(val, (int, float)):
                    values.append(str(val))
                else:
                    # Escapar comillas simples
                    escaped_val = str(val).replace("'", "''")
                    values.append(f"'{escaped_val}'")
            
            values_str = ', '.join(values)
            insert_sql = f"INSERT INTO `{table_name}` ({columns_str}) VALUES ({values_str});"
            insert_statements.append(insert_sql)
        
        return insert_statements
    
    def _map_pandas_to_sql_type(self, pandas_dtype) -> str:
        """
        Mapea tipos de pandas a tipos SQL
        
        Args:
            pandas_dtype: Tipo de datos de pandas
            
        Returns:
            Tipo SQL correspondiente
        """
        dtype_str = str(pandas_dtype).lower()
        
        if 'int' in dtype_str:
            return 'INTEGER'
        elif 'float' in dtype_str:
            return 'REAL'
        elif 'datetime' in dtype_str:
            return 'DATETIME'
        elif 'bool' in dtype_str:
            return 'BOOLEAN'
        else:
            return 'TEXT'
    
    def write_batch_insert(self, df: pd.DataFrame, output_path: str, table_name: str, batch_size: int = 1000) -> Dict[str, Any]:
        """
        Escribe INSERT statements en lotes para mejor rendimiento
        
        Args:
            df: DataFrame
            output_path: Ruta del archivo
            table_name: Nombre de la tabla
            batch_size: Tamaño del lote
            
        Returns:
            Dict con información del resultado
        """
        try:
            self.logger.info(f"Escribiendo INSERT en lotes: {output_path}")
            
            create_table_sql = self._generate_create_table(df, table_name)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"-- Archivo SQL con INSERT en lotes\n")
                f.write(f"-- Tabla: {table_name}\n")
                f.write(f"-- Filas: {len(df)}\n\n")
                
                f.write(create_table_sql)
                f.write("\n\n")
                
                # Procesar en lotes
                for i in range(0, len(df), batch_size):
                    batch_df = df.iloc[i:i+batch_size]
                    batch_insert = self._generate_batch_insert(batch_df, table_name)
                    f.write(batch_insert + "\n")
            
            result = {
                'success': True,
                'output_file': output_path,
                'table_name': table_name,
                'rows_inserted': len(df),
                'batches': (len(df) + batch_size - 1) // batch_size
            }
            
            self.logger.info(f"Archivo SQL con lotes escrito exitosamente: {output_path}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error escribiendo INSERT en lotes: {str(e)}")
            raise
    
    def _generate_batch_insert(self, df: pd.DataFrame, table_name: str) -> str:
        """
        Genera un INSERT en lote
        
        Args:
            df: DataFrame del lote
            table_name: Nombre de la tabla
            
        Returns:
            String con el INSERT en lote
        """
        if df.empty:
            return ""
        
        columns = [f'"{col}"' for col in df.columns]
        columns_str = ', '.join(columns)
        
        values_list = []
        for _, row in df.iterrows():
            values = []
            for val in row.values:
                if pd.isna(val):
                    values.append('NULL')
                elif isinstance(val, (int, float)):
                    values.append(str(val))
                else:
                    escaped_val = str(val).replace("'", "''")
                    values.append(f"'{escaped_val}'")
            
            values_str = f"({', '.join(values)})"
            values_list.append(values_str)
        
        all_values = ',\n    '.join(values_list)
        insert_sql = f"INSERT INTO {table_name} ({columns_str}) VALUES\n    {all_values};"
        
        return insert_sql 