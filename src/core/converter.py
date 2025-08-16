"""
Clase principal para la conversión de archivos
"""

import pandas as pd
import os
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

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
    
    def convert_access_by_year(
        self,
        input_path: str,
        output_format: str = "sql",
        output_dir: str = None,
        parallel: bool = False,
        max_workers: Optional[int] = None,
        naming_config: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Convierte un archivo Access por años, creando archivos separados para cada año
        
        Args:
            input_path: Ruta del archivo Access (.mdb o .accdb)
            output_format: Formato de salida (sql, sqlite, csv, excel, json)
            output_dir: Directorio de salida (opcional)
            **kwargs: Argumentos adicionales para el writer
        
        Returns:
            Dict con información del resultado de la conversión por años
        """
        try:
            self.logger.info(f"Iniciando conversión por años: {input_path} -> {output_format}")
            
            # Validar archivo de entrada
            input_path_obj = Path(input_path)
            if not input_path_obj.exists():
                raise ValidationError(f"El archivo no existe: {input_path}")
            
            if input_path_obj.suffix.lower() not in ['.mdb', '.accdb']:
                raise ValidationError(f"El archivo debe ser .mdb o .accdb: {input_path}")
            
            # Crear directorio de salida
            if output_dir is None:
                output_dir = f"data/output/{input_path_obj.stem}_por_años"
            
            output_path_obj = Path(output_dir)
            output_path_obj.mkdir(parents=True, exist_ok=True)
            
            # Obtener resumen de años del archivo
            access_reader = self.readers['.mdb']  # Usar el reader de Access
            year_summary = access_reader.get_year_summary(input_path)
            
            if 'error' in year_summary:
                raise ConversionError(f"Error obteniendo resumen de años: {year_summary['error']}")
            
            if not year_summary['tables']:
                raise ConversionError("No se encontraron tablas en el archivo Access")
            
            # Resultado general
            result = {
                'input_file': input_path,
                'output_directory': str(output_path_obj),
                'output_format': output_format,
                'total_tables': len(year_summary['tables']),
                'conversions_by_year': {},
                'summary': year_summary
            }
            
            # Preparar lista de trabajos (tabla, año)
            jobs: List[Tuple[str, int]] = []
            for table_name, table_info in year_summary['tables'].items():
                if 'error' in table_info:
                    self.logger.warning(f"Error en tabla {table_name}: {table_info['error']}")
                    continue
                if not table_info['available_years']:
                    self.logger.warning(f"Tabla {table_name} no tiene años disponibles")
                    continue
                for year in table_info['available_years']:
                    jobs.append((table_name, year))

            def process_single_year(table_name: str, year: int) -> Tuple[str, Dict[str, Any]]:
                try:
                    self.logger.info(f"Procesando tabla {table_name}, año {year}")
                    df = access_reader.read_by_year(input_path, table_name, year)
                    if df.empty:
                        self.logger.warning(f"No hay datos para tabla {table_name}, año {year}")
                        return (
                            f"{table_name}_{year}",
                            {
                                'table': table_name,
                                'year': year,
                                'status': 'error',
                                'error': 'Sin datos',
                                'rows_converted': 0,
                                'columns': 0
                            }
                        )

                    # Generar nombre de archivo de salida con configuración personalizada
                    output_filename = self._generate_year_filename(
                        table_name, 
                        year, 
                        output_format, 
                        naming_config
                    )
                    output_file_path = output_path_obj / output_filename

                    conversion_result = self._write_file(
                        df,
                        str(output_file_path),
                        output_format,
                        f"{table_name}_{year}",
                        **kwargs
                    )

                    conv = {
                        'table': table_name,
                        'year': year,
                        'status': 'success',
                        'output_file': str(output_file_path),
                        'rows_converted': len(df),
                        'columns': len(df.columns),
                        'file_size_mb': output_file_path.stat().st_size / (1024 * 1024),
                        'conversion_details': conversion_result
                    }
                    self.logger.info(f"✅ Tabla {table_name}, año {year}: {len(df)} filas convertidas")
                    return (f"{table_name}_{year}", conv)
                except Exception as e:
                    self.logger.error(f"Error procesando tabla {table_name}, año {year}: {str(e)}")
                    return (
                        f"{table_name}_{year}",
                        {
                            'table': table_name,
                            'year': year,
                            'status': 'error',
                            'error': str(e),
                            'rows_converted': 0,
                            'columns': 0
                        }
                    )

            if parallel and jobs:
                workers = max_workers or min(4, os.cpu_count() or 2)
                self.logger.info(f"Ejecutando en paralelo con {workers} workers ({len(jobs)} tareas)")
                with ThreadPoolExecutor(max_workers=workers) as executor:
                    futures = [executor.submit(process_single_year, t, y) for (t, y) in jobs]
                    for future in as_completed(futures):
                        conv_key, conv_data = future.result()
                        result['conversions_by_year'][conv_key] = conv_data
            else:
                for table_name, year in jobs:
                    conv_key, conv_data = process_single_year(table_name, year)
                    result['conversions_by_year'][conv_key] = conv_data
            
            # Calcular estadísticas finales
            successful_conversions = [conv for conv in result['conversions_by_year'].values() 
                                   if conv['status'] == 'success']
            
            if successful_conversions:
                result['total_rows_converted'] = sum(conv['rows_converted'] for conv in successful_conversions)
                result['total_files_created'] = len(successful_conversions)
                result['total_size_mb'] = sum(conv.get('file_size_mb', 0) for conv in successful_conversions)
            else:
                result['total_rows_converted'] = 0
                result['total_files_created'] = 0
                result['total_size_mb'] = 0
            
            self.logger.info(f"Conversión por años completada: {len(successful_conversions)} archivos creados")
            return result
            
        except Exception as e:
            self.logger.error(f"Error en conversión por años: {str(e)}")
            raise ConversionError(f"Error en conversión por años: {str(e)}")
    
    def _generate_year_filename(
        self, 
        table_name: str, 
        year: int, 
        output_format: str, 
        naming_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Genera un nombre de archivo personalizado para conversiones por año
        
        Args:
            table_name: Nombre de la tabla
            year: Año
            output_format: Formato de salida
            naming_config: Configuración de nombres personalizada
            
        Returns:
            Nombre de archivo generado
        """
        import re
        from datetime import datetime
        
        # Configuración por defecto
        if not naming_config:
            if output_format == 'sqlite':
                return f"{table_name}_{year}.db"
            else:
                return f"{table_name}_{year}.{output_format}"
        
        # Crear patrón base
        base_name = table_name.lower() if naming_config.get('lowercase_names', True) else table_name
        
        # Aplicar prefijo si existe
        if naming_config.get('table_prefix'):
            prefix = naming_config['table_prefix']
            # Verificar si el prefijo debe incluir año
            if '{year}' in prefix:
                prefix = prefix.replace('{year}', str(year))
            base_name = f"{prefix}{base_name}"
        else:
            # Prefijo por defecto con año si no se especifica otro
            base_name = f"{base_name}-{year}"
        
        # Aplicar sufijo si existe
        if naming_config.get('table_suffix'):
            suffix = naming_config['table_suffix']
            # Verificar si el sufijo debe incluir año
            if '{year}' in suffix:
                suffix = suffix.replace('{year}', str(year))
            base_name = f"{base_name}{suffix}"
        
        # Aplicar timestamp si está configurado
        if naming_config.get('use_timestamp'):
            timestamp = datetime.now().strftime("_%Y%m%d_%H%M%S")
            base_name = f"{base_name}{timestamp}"
        
        # Limpiar espacios y caracteres especiales
        if naming_config.get('replace_spaces', True):
            base_name = base_name.replace(' ', '_')
        
        if naming_config.get('remove_special_chars', True):
            # Mantener solo letras, números, guiones y guiones bajos
            base_name = re.sub(r'[^a-zA-Z0-9_-]', '', base_name)
        
        # Añadir extensión
        if output_format == 'sqlite':
            extension = 'db'
        else:
            extension = output_format
            
        return f"{base_name}.{extension}"