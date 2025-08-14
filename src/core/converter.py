"""
Clase principal para la conversión de archivos
"""

import pandas as pd
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

from .validators import DataValidator
from .exceptions import ConversionError, ValidationError
from src.readers import CSVReader, ExcelReader, JSONReader
from src.readers.robust_access_reader import RobustAccessReader
from src.writers import SQLWriter, SQLiteWriter, SupabaseWriter, CSVWriter, ExcelWriter, JSONWriter
from src.utils.logger import get_logger

class FileConverter:
    """
    Clase principal para convertir archivos a diferentes formatos de base de datos
    """
    
    def __init__(self):
        self.validator = DataValidator()
        self.logger = get_logger(__name__)
        
        # Inicializar readers
        self.readers = {
            '.csv': CSVReader(),
            '.xlsx': ExcelReader(),
            '.xls': ExcelReader(),
            '.json': JSONReader(),
            '.accdb': RobustAccessReader(),
            '.mdb': RobustAccessReader()
        }
        
        # Inicializar writers
        self.writers = {
            'sql': SQLWriter(),
            'sqlite': SQLiteWriter(),
            'supabase': SupabaseWriter(),
            'csv': CSVWriter(),
            'excel': ExcelWriter(),
            'json': JSONWriter()
        }
    
    def convert_file(
        self,
        input_path: str,
        output_path: str,
        output_format: str,
        table_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Convierte un archivo a un formato específico de base de datos
        
        Args:
            input_path: Ruta del archivo de entrada
            output_path: Ruta del archivo de salida
            output_format: Formato de salida (sql, sqlite, supabase)
            table_name: Nombre de la tabla
            **kwargs: Argumentos adicionales para el writer
        
        Returns:
            Dict con información del resultado de la conversión
        """
        try:
            self.logger.info(f"Iniciando conversión: {input_path} -> {output_format}")
            
            # Validaciones
            self._validate_input(input_path, output_format, table_name, output_path)
            
            # Leer archivo (pasar table_name para archivos Access)
            df = self._read_file(input_path, table_name)
            
            # Validar datos
            validation_result = self.validator.validate_dataframe(df)
            self.logger.info(f"Datos validados: {validation_result['rows']} filas, {validation_result['columns']} columnas")
            
            # Convertir
            result = self._write_file(df, output_path, output_format, table_name, **kwargs)
            
            # Agregar información de validación al resultado
            result.update({
                'validation': validation_result,
                'input_file': input_path,
                'output_file': output_path,
                'table_name': table_name,
                'format': output_format
            })
            
            self.logger.info(f"Conversión completada exitosamente: {output_path}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error en la conversión: {str(e)}")
            raise ConversionError(f"Error convirtiendo archivo: {str(e)}")
    
    def convert_batch(
        self,
        input_dir: str,
        output_dir: str,
        output_format: str,
        table_name_pattern: str = "{filename}",
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Convierte múltiples archivos en un directorio
        
        Args:
            input_dir: Directorio con archivos de entrada
            output_dir: Directorio de salida
            output_format: Formato de salida
            table_name_pattern: Patrón para nombres de tabla (usa {filename})
            **kwargs: Argumentos adicionales
        
        Returns:
            Lista de resultados de conversión
        """
        results = []
        input_path = Path(input_dir)
        
        if not input_path.exists():
            raise ValidationError(f"El directorio de entrada no existe: {input_dir}")
        
        # Obtener archivos soportados
        supported_files = []
        for ext in self.validator.SUPPORTED_FORMATS['input']:
            supported_files.extend(input_path.glob(f"*{ext}"))
        
        if not supported_files:
            self.logger.warning(f"No se encontraron archivos soportados en: {input_dir}")
            return results
        
        self.logger.info(f"Procesando {len(supported_files)} archivos")
        
        for file_path in supported_files:
            try:
                # Generar nombre de tabla
                filename = file_path.stem
                table_name = table_name_pattern.format(filename=filename)
                
                # Generar ruta de salida
                output_filename = f"{filename}.{output_format}"
                output_file_path = Path(output_dir) / output_filename
                
                # Convertir archivo
                result = self.convert_file(
                    str(file_path),
                    str(output_file_path),
                    output_format,
                    table_name,
                    **kwargs
                )
                
                results.append(result)
                
            except Exception as e:
                self.logger.error(f"Error procesando {file_path}: {str(e)}")
                results.append({
                    'error': str(e),
                    'file': str(file_path),
                    'success': False
                })
        
        return results
    
    def _validate_input(self, input_path: str, output_format: str, table_name: str, output_path: str):
        """Realiza todas las validaciones necesarias"""
        # Validar archivo de entrada
        self.validator.validate_file_path(input_path)
        self.validator.validate_file_format(input_path)
        self.validator.validate_file_size(input_path)
        
        # Validar formato de salida
        self.validator.validate_output_format(output_format)
        
        # Validar nombre de tabla
        self.validator.validate_table_name(table_name)
        
        # Validar directorio de salida
        output_dir = os.path.dirname(output_path)
        self.validator.validate_output_directory(output_dir)
    
    def _read_file(self, file_path: str, table_name: str = None) -> pd.DataFrame:
        """Lee el archivo usando el reader apropiado"""
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension not in self.readers:
            raise ValidationError(f"No hay reader disponible para: {file_extension}")
        
        reader = self.readers[file_extension]
        
        # Para archivos Access, pasar el table_name
        if file_extension in ['.accdb', '.mdb']:
            return reader.read(file_path, table_name)
        else:
            return reader.read(file_path)
    
    def _write_file(
        self,
        df: pd.DataFrame,
        output_path: str,
        output_format: str,
        table_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Escribe el archivo usando el writer apropiado"""
        if output_format not in self.writers:
            raise ValidationError(f"No hay writer disponible para: {output_format}")
        
        writer = self.writers[output_format]
        
        # Filtrar kwargs según el formato
        if output_format == 'sql':
            # Para SQL, pasar batch_size si está presente
            filtered_kwargs = {k: v for k, v in kwargs.items() if k in ['batch_size']}
        else:
            # Para otros formatos, no pasar batch_size
            filtered_kwargs = {k: v for k, v in kwargs.items() if k not in ['batch_size']}
        
        return writer.write(df, output_path, table_name, **filtered_kwargs)
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """Retorna los formatos soportados"""
        return self.validator.SUPPORTED_FORMATS
    
    def get_file_info(self, file_path: str, table_name: str = None) -> Dict[str, Any]:
        """Obtiene información detallada de un archivo"""
        try:
            df = self._read_file(file_path, table_name)
            validation = self.validator.validate_dataframe(df)
            
            return {
                'file_path': file_path,
                'file_size_mb': os.path.getsize(file_path) / (1024 * 1024),
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': df.columns.tolist(),
                'data_types': df.dtypes.to_dict(),
                'missing_values': df.isnull().sum().to_dict(),
                'validation': validation
            }
        except Exception as e:
            self.logger.error(f"Error obteniendo información del archivo: {str(e)}")
            raise 