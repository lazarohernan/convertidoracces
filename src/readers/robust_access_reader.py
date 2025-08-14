"""
Reader robusto para archivos de Microsoft Access
Implementación mejorada con múltiples métodos de fallback
"""

import pandas as pd
import os
import platform
import subprocess
import tempfile
import shutil
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from src.utils.logger import get_logger

class RobustAccessReader:
    """
    Reader robusto para archivos de Microsoft Access con múltiples métodos de fallback
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.system = platform.system().lower()
        self._cache = {}
        self._temp_dir = None
        self._access_support_checked = False
        self._access_supported = False
    
    def read(self, file_path: str, table_name: Optional[str] = None) -> pd.DataFrame:
        """
        Lee un archivo Access usando el mejor método disponible
        
        Args:
            file_path: Ruta del archivo .accdb o .mdb
            table_name: Nombre de la tabla específica (opcional)
            
        Returns:
            DataFrame con los datos
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"El archivo no existe: {file_path}")
        
        if file_path.stat().st_size == 0:
            raise ValueError(f"El archivo está vacío: {file_path}")
        
        self.logger.info(f"Leyendo archivo Access: {file_path.name} ({file_path.stat().st_size / 1024 / 1024:.2f} MB)")
        
        # Intentar diferentes métodos en orden de preferencia
        methods = [
            self._try_mdbtools,
            self._try_pyodbc,
            self._try_sqlalchemy,
            self._try_manual_conversion
        ]
        
        last_error = None
        
        for method in methods:
            try:
                self.logger.info(f"Intentando método: {method.__name__}")
                df = method(file_path, table_name)
                
                if df is not None and not df.empty:
                    self.logger.info(f"✅ Éxito con {method.__name__}: {len(df)} filas, {len(df.columns)} columnas")
                    return df
                    
            except Exception as e:
                last_error = e
                self.logger.warning(f"❌ Falló {method.__name__}: {str(e)}")
                continue
        
        # Si todos los métodos fallaron
        raise ValueError(
            f"No se pudo leer el archivo Access {file_path.name}. "
            f"Último error: {str(last_error)}. "
            f"Recomendación: Convierte el archivo a CSV/Excel primero."
        )
    
    def _try_mdbtools(self, file_path: Path, table_name: Optional[str] = None) -> Optional[pd.DataFrame]:
        """Intenta usar mdb-tools (método más confiable en Unix/macOS)"""
        try:
            # Verificar si mdb-tools está disponible
            if not self._check_mdbtools():
                raise RuntimeError("mdb-tools no está instalado")
            
            # Listar tablas
            tables = self._list_tables_mdbtools(file_path)
            if not tables:
                raise ValueError("No se encontraron tablas en el archivo")
            
            # Si no se especifica tabla, mostrar todas las disponibles
            if not table_name:
                available_tables = ", ".join(tables)
                raise ValueError(
                    f"No se especificó una tabla. Tablas disponibles: {available_tables}. "
                    f"Especifica una tabla usando el parámetro table_name."
                )
            
            if table_name not in tables:
                raise ValueError(f"Tabla '{table_name}' no encontrada. Tablas disponibles: {tables}")
            
            # Exportar tabla a CSV temporal
            temp_csv = self._export_table_mdbtools(file_path, table_name)
            
            # Leer CSV
            df = pd.read_csv(temp_csv, encoding='utf-8')
            
            # Limpiar archivo temporal
            os.unlink(temp_csv)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error con mdb-tools: {str(e)}")
            raise
    
    def _try_pyodbc(self, file_path: Path, table_name: Optional[str] = None) -> Optional[pd.DataFrame]:
        """Intenta usar pyodbc (método para Windows)"""
        try:
            import pyodbc
            
            # Crear string de conexión
            conn_str = f"Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={file_path};"
            
            # Conectar
            with pyodbc.connect(conn_str, timeout=30) as conn:
                # Obtener tablas si no se especifica
                if not table_name:
                    cursor = conn.cursor()
                    tables = [table.table_name for table in cursor.tables(tableType='TABLE')]
                    if tables:
                        table_name = tables[0]
                        self.logger.info(f"Usando tabla por defecto: {table_name}")
                    else:
                        raise ValueError("No se encontraron tablas")
                
                # Leer tabla
                query = f"SELECT * FROM [{table_name}]"
                df = pd.read_sql(query, conn)
                
                return df
                
        except Exception as e:
            self.logger.error(f"Error con pyodbc: {str(e)}")
            raise
    
    def _try_sqlalchemy(self, file_path: Path, table_name: Optional[str] = None) -> Optional[pd.DataFrame]:
        """Intenta usar SQLAlchemy"""
        try:
            from sqlalchemy import create_engine
            
            # Crear engine
            engine = create_engine(f'access+pyodbc:///{file_path}')
            
            # Obtener tablas si no se especifica
            if not table_name:
                table_names = engine.table_names()
                if table_names:
                    table_name = table_names[0]
                    self.logger.info(f"Usando tabla por defecto: {table_name}")
                else:
                    raise ValueError("No se encontraron tablas")
            
            # Leer tabla
            df = pd.read_sql_table(table_name, engine)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error con SQLAlchemy: {str(e)}")
            raise
    
    def _try_manual_conversion(self, file_path: Path, table_name: Optional[str] = None) -> Optional[pd.DataFrame]:
        """Método de último recurso: sugerir conversión manual"""
        raise ValueError(
            f"No se pudo leer {file_path.name} automáticamente. "
            f"Por favor, convierte el archivo a CSV/Excel usando Microsoft Access o mdb-tools."
        )
    
    def check_access_support(self) -> Dict[str, Any]:
        """Verifica si el sistema puede leer archivos Access"""
        if self._access_support_checked:
            return {
                'supported': self._access_supported,
                'system': self.system,
                'drivers_available': self._check_drivers(),
                'supported_methods': self._get_supported_methods()
            }
        
        self._access_support_checked = True
        
        # Verificar métodos disponibles
        supported_methods = self._get_supported_methods()
        
        # Determinar si Access está soportado
        self._access_supported = len(supported_methods) > 0
        
        return {
            'supported': self._access_supported,
            'system': self.system,
            'drivers_available': self._check_drivers(),
            'supported_methods': supported_methods,
            'error_message': self._get_error_message(supported_methods)
        }
    
    def _get_supported_methods(self) -> List[str]:
        """Obtiene lista de métodos soportados"""
        methods = []
        
        # Verificar mdb-tools
        if self._check_mdbtools():
            methods.append('mdb-tools')
        
        # Verificar pyodbc
        try:
            import pyodbc
            if self.system == "windows":
                methods.append('pyodbc')
        except ImportError:
            pass
        
        # Verificar sqlalchemy
        try:
            import sqlalchemy
            methods.append('sqlalchemy')
        except ImportError:
            pass
        
        return methods
    
    def _get_error_message(self, supported_methods: List[str]) -> str:
        """Obtiene mensaje de error apropiado"""
        if supported_methods:
            return ""
        
        if self.system == "darwin":
            return "macOS no tiene soporte nativo para Access. Se requiere mdb-tools o conversión manual."
        elif self.system == "windows":
            return "No se encontraron drivers ODBC para Access. Instala Microsoft Access Database Engine."
        else:
            return "No se encontraron métodos para leer archivos Access. Instala mdb-tools o pyodbc."
    
    def _check_drivers(self) -> List[str]:
        """Verifica qué drivers ODBC están disponibles"""
        try:
            import pyodbc
            drivers = pyodbc.drivers()
            access_drivers = [d for d in drivers if 'access' in d.lower() or 'mdb' in d.lower()]
            return access_drivers
        except:
            return []
    
    def _check_mdbtools(self) -> bool:
        """Verifica si mdb-tools está instalado"""
        try:
            result = subprocess.run(['mdb-tables', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False
    
    def _list_tables_mdbtools(self, file_path: Path) -> List[str]:
        """Lista las tablas usando mdb-tools"""
        try:
            result = subprocess.run(
                ['mdb-tables', '-1', str(file_path)],
                capture_output=True, text=True, check=True, timeout=30
            )
            tables = [table.strip() for table in result.stdout.split('\n') if table.strip()]
            return tables
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error listando tablas: {e.stderr}")
    
    def _export_table_mdbtools(self, file_path: Path, table_name: str) -> str:
        """Exporta una tabla a CSV usando mdb-tools"""
        try:
            # Crear archivo temporal
            temp_fd, temp_path = tempfile.mkstemp(suffix='.csv')
            os.close(temp_fd)
            
            # Exportar tabla
            result = subprocess.run(
                ['mdb-export', str(file_path), table_name],
                capture_output=True, text=True, check=True, timeout=60
            )
            
            # Escribir a archivo temporal
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(result.stdout)
            
            return temp_path
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error exportando tabla {table_name}: {e.stderr}")
    
    def get_table_names(self, file_path: str) -> List[str]:
        """Obtiene la lista de tablas disponibles"""
        file_path = Path(file_path)
        
        # Intentar con mdb-tools primero (más confiable)
        if self._check_mdbtools():
            try:
                tables = self._list_tables_mdbtools(file_path)
                if tables:
                    self.logger.info(f"Tablas detectadas con mdb-tools: {tables}")
                    return tables
            except Exception as e:
                self.logger.warning(f"Error con mdb-tools: {str(e)}")
        
        # Intentar con pyodbc como fallback
        try:
            import pyodbc
            conn_str = f"Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={file_path};"
            with pyodbc.connect(conn_str, timeout=30) as conn:
                cursor = conn.cursor()
                tables = [table.table_name for table in cursor.tables(tableType='TABLE')]
                if tables:
                    self.logger.info(f"Tablas detectadas con pyodbc: {tables}")
                    return tables
        except Exception as e:
            self.logger.warning(f"Error con pyodbc: {str(e)}")
        
        self.logger.error("No se pudieron detectar tablas")
        return []
    
    def get_info(self, file_path: str) -> Dict[str, Any]:
        """Obtiene información detallada del archivo Access"""
        file_path = Path(file_path)
        
        info = {
            'file_path': str(file_path),
            'file_size_mb': file_path.stat().st_size / (1024 * 1024),
            'tables': [],
            'total_rows': 0,
            'total_columns': 0,
            'supported_methods': []
        }
        
        # Verificar métodos disponibles
        if self._check_mdbtools():
            info['supported_methods'].append('mdb-tools')
        
        try:
            import pyodbc
            info['supported_methods'].append('pyodbc')
        except ImportError:
            pass
        
        try:
            import sqlalchemy
            info['supported_methods'].append('sqlalchemy')
        except ImportError:
            pass
        
        # Obtener información de tablas
        try:
            table_names = self.get_table_names(file_path)
            
            for table_name in table_names:
                try:
                    df = self.read(file_path, table_name)
                    table_info = {
                        'name': table_name,
                        'rows': len(df),
                        'columns': len(df.columns),
                        'column_names': df.columns.tolist(),
                        'data_types': df.dtypes.to_dict()
                    }
                    info['tables'].append(table_info)
                    info['total_rows'] += len(df)
                    info['total_columns'] += len(df.columns)
                except Exception as e:
                    self.logger.warning(f"Error leyendo tabla {table_name}: {str(e)}")
                    
        except Exception as e:
            self.logger.error(f"Error obteniendo información: {str(e)}")
        
        return info
    
    def read_all_tables(self, file_path: str) -> Dict[str, pd.DataFrame]:
        """Lee todas las tablas del archivo Access"""
        file_path = Path(file_path)
        tables = {}
        
        try:
            table_names = self.get_table_names(file_path)
            
            for table_name in table_names:
                try:
                    df = self.read(file_path, table_name)
                    tables[table_name] = df
                    self.logger.info(f"Tabla '{table_name}' leída: {len(df)} filas")
                except Exception as e:
                    self.logger.warning(f"Error leyendo tabla '{table_name}': {str(e)}")
                    
        except Exception as e:
            self.logger.error(f"Error leyendo todas las tablas: {str(e)}")
            raise
        
        return tables
    
    def __del__(self):
        """Limpieza al destruir el objeto"""
        if self._temp_dir and os.path.exists(self._temp_dir):
            try:
                shutil.rmtree(self._temp_dir)
            except:
                pass 