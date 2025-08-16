"""
Escritor de archivos MySQL
"""

import pandas as pd
import mysql.connector
from typing import Dict, Any, List, Optional
import sqlalchemy
from sqlalchemy import create_engine, text
from src.utils.logger import get_logger

class MySQLWriter:
    """Clase para escribir datos a una base de datos MySQL"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa el escritor MySQL
        
        Args:
            config: Configuración de conexión MySQL
        """
        self.logger = get_logger(__name__)
        self.config = config
        self.engine = None
        self._create_engine()
    
    def _create_engine(self):
        """Crea el engine de SQLAlchemy para MySQL"""
        try:
            # Construir URL de conexión
            connection_url = (
                f"mysql+mysqlconnector://"
                f"{self.config['user']}:{self.config['password']}"
                f"@{self.config['host']}:{self.config['port']}"
                f"/{self.config['database']}"
            )
            
            # Configuración adicional
            connect_args = {
                'charset': self.config.get('charset', 'utf8mb4'),
                'connect_timeout': self.config.get('connect_timeout', 30),
                'autocommit': self.config.get('autocommit', True)
            }
            
            if self.config.get('ssl_disabled', True):
                connect_args['ssl_disabled'] = True
            
            self.engine = create_engine(
                connection_url,
                connect_args=connect_args,
                echo=False
            )
            
            self.logger.info("Engine MySQL creado exitosamente")
            
        except Exception as e:
            self.logger.error(f"Error creando engine MySQL: {str(e)}")
            raise
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Prueba la conexión a MySQL
        
        Returns:
            Dict con resultado de la prueba
        """
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT 1 as test"))
                row = result.fetchone()
                
                if row and row[0] == 1:
                    return {
                        'success': True,
                        'message': 'Conexión exitosa a MySQL',
                        'server_info': self._get_server_info(connection)
                    }
                else:
                    return {
                        'success': False,
                        'message': 'No se pudo verificar la conexión'
                    }
                    
        except Exception as e:
            self.logger.error(f"Error probando conexión MySQL: {str(e)}")
            return {
                'success': False,
                'message': f'Error de conexión: {str(e)}'
            }
    
    def _get_server_info(self, connection) -> Dict[str, Any]:
        """Obtiene información del servidor MySQL"""
        try:
            version_result = connection.execute(text("SELECT VERSION() as version"))
            version = version_result.fetchone()[0]
            
            db_result = connection.execute(text("SELECT DATABASE() as db_name"))
            db_name = db_result.fetchone()[0]
            
            return {
                'version': version,
                'database': db_name,
                'host': self.config['host'],
                'port': self.config['port']
            }
        except:
            return {}
    
    def write(
        self, 
        df: pd.DataFrame, 
        table_name: str, 
        if_exists: str = 'replace',
        **kwargs
    ) -> Dict[str, Any]:
        """
        Escribe un DataFrame a una tabla MySQL
        
        Args:
            df: DataFrame a escribir
            table_name: Nombre de la tabla
            if_exists: Qué hacer si la tabla existe ('fail', 'replace', 'append')
            **kwargs: Argumentos adicionales
        
        Returns:
            Dict con información del resultado
        """
        try:
            self.logger.info(f"Escribiendo {len(df)} filas a tabla MySQL: {table_name}")
            
            # Validar DataFrame
            if df.empty:
                raise ValueError("DataFrame está vacío")
            
            # Limpiar nombre de tabla
            clean_table_name = self._clean_table_name(table_name)
            
            # Preparar DataFrame para MySQL
            df_prepared = self._prepare_dataframe(df)
            
            # Escribir a MySQL usando pandas
            rows_written = df_prepared.to_sql(
                name=clean_table_name,
                con=self.engine,
                if_exists=if_exists,
                index=False,
                method='multi',
                chunksize=kwargs.get('chunksize', 1000)
            )
            
            # Verificar escritura
            verification = self._verify_write(clean_table_name, len(df))
            
            result = {
                'success': True,
                'table_name': clean_table_name,
                'rows_written': len(df),
                'columns_written': len(df.columns),
                'if_exists_action': if_exists,
                'verification': verification
            }
            
            self.logger.info(f"✅ Escritura MySQL exitosa: {len(df)} filas en '{clean_table_name}'")
            return result
            
        except Exception as e:
            self.logger.error(f"Error escribiendo a MySQL: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'table_name': table_name,
                'rows_attempted': len(df) if not df.empty else 0
            }
    
    def _clean_table_name(self, table_name: str) -> str:
        """
        Limpia el nombre de tabla para MySQL
        
        Args:
            table_name: Nombre original
            
        Returns:
            Nombre limpio para MySQL
        """
        import re
        
        # Remover caracteres especiales y espacios
        clean_name = re.sub(r'[^\w]', '_', table_name)
        
        # Asegurar que no empiece con número
        if clean_name[0].isdigit():
            clean_name = f"table_{clean_name}"
        
        # Limitar longitud (MySQL tiene límite de 64 caracteres)
        clean_name = clean_name[:64]
        
        return clean_name
    
    def _prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepara el DataFrame para escritura en MySQL
        
        Args:
            df: DataFrame original
            
        Returns:
            DataFrame preparado
        """
        df_prepared = df.copy()
        
        # Convertir tipos problemáticos
        for col in df_prepared.columns:
            # Limpiar nombres de columnas
            new_col = col.replace(' ', '_').replace('-', '_')
            if new_col != col:
                df_prepared = df_prepared.rename(columns={col: new_col})
            
            # Convertir tipos de datos problemáticos
            if df_prepared[new_col].dtype == 'object':
                # Intentar convertir a string limpio
                df_prepared[new_col] = df_prepared[new_col].astype(str)
                df_prepared[new_col] = df_prepared[new_col].replace('nan', None)
            
            # Manejar fechas
            if df_prepared[new_col].dtype.name.startswith('datetime'):
                # Convertir a formato compatible con MySQL
                df_prepared[new_col] = pd.to_datetime(df_prepared[new_col], errors='coerce')
        
        return df_prepared
    
    def _verify_write(self, table_name: str, expected_rows: int) -> Dict[str, Any]:
        """
        Verifica que los datos se escribieron correctamente
        
        Args:
            table_name: Nombre de la tabla
            expected_rows: Número esperado de filas
            
        Returns:
            Dict con información de verificación
        """
        try:
            with self.engine.connect() as connection:
                # Contar filas
                count_result = connection.execute(
                    text(f"SELECT COUNT(*) FROM `{table_name}`")
                )
                actual_rows = count_result.fetchone()[0]
                
                # Obtener información de columnas
                columns_result = connection.execute(
                    text(f"DESCRIBE `{table_name}`")
                )
                columns_info = columns_result.fetchall()
                
                return {
                    'success': True,
                    'expected_rows': expected_rows,
                    'actual_rows': actual_rows,
                    'rows_match': actual_rows == expected_rows,
                    'columns_count': len(columns_info),
                    'columns_info': [
                        {
                            'name': col[0],
                            'type': col[1],
                            'null': col[2] == 'YES',
                            'key': col[3],
                            'default': col[4]
                        }
                        for col in columns_info
                    ]
                }
                
        except Exception as e:
            self.logger.error(f"Error verificando escritura: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_tables(self) -> List[str]:
        """
        Lista las tablas en la base de datos
        
        Returns:
            Lista de nombres de tablas
        """
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SHOW TABLES"))
                tables = [row[0] for row in result.fetchall()]
                return tables
                
        except Exception as e:
            self.logger.error(f"Error listando tablas: {str(e)}")
            return []
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        Obtiene información detallada de una tabla
        
        Args:
            table_name: Nombre de la tabla
            
        Returns:
            Dict con información de la tabla
        """
        try:
            with self.engine.connect() as connection:
                # Información de estructura
                describe_result = connection.execute(
                    text(f"DESCRIBE `{table_name}`")
                )
                structure = describe_result.fetchall()
                
                # Contar filas
                count_result = connection.execute(
                    text(f"SELECT COUNT(*) FROM `{table_name}`")
                )
                row_count = count_result.fetchone()[0]
                
                # Información de índices
                indexes_result = connection.execute(
                    text(f"SHOW INDEX FROM `{table_name}`")
                )
                indexes = indexes_result.fetchall()
                
                return {
                    'table_name': table_name,
                    'row_count': row_count,
                    'columns': [
                        {
                            'name': col[0],
                            'type': col[1],
                            'null': col[2] == 'YES',
                            'key': col[3],
                            'default': col[4],
                            'extra': col[5] if len(col) > 5 else None
                        }
                        for col in structure
                    ],
                    'indexes': [
                        {
                            'name': idx[2],
                            'column': idx[4],
                            'unique': idx[1] == 0
                        }
                        for idx in indexes
                    ]
                }
                
        except Exception as e:
            self.logger.error(f"Error obteniendo info de tabla {table_name}: {str(e)}")
            return {
                'table_name': table_name,
                'error': str(e)
            }
    
    def execute_sql(self, sql_content: str) -> Dict[str, Any]:
        """
        Ejecuta contenido SQL en la base de datos
        
        Args:
            sql_content: Contenido SQL a ejecutar
            
        Returns:
            Dict con resultado de la ejecución
        """
        try:
            with self.engine.connect() as connection:
                # Dividir el SQL en statements individuales
                statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
                
                executed_statements = 0
                for statement in statements:
                    if statement:
                        connection.execute(text(statement))
                        executed_statements += 1
                
                connection.commit()
                
                return {
                    'success': True,
                    'statements_executed': executed_statements,
                    'message': f'Se ejecutaron {executed_statements} statements exitosamente'
                }
                
        except Exception as e:
            self.logger.error(f"Error ejecutando SQL: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Error ejecutando SQL: {str(e)}'
            }

    def close(self):
        """Cierra la conexión"""
        if self.engine:
            self.engine.dispose()
            self.logger.info("Conexión MySQL cerrada")
