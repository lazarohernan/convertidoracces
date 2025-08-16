"""
Verificador de integridad de datos
"""

import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from src.utils.logger import get_logger

class DataIntegrityChecker:
    """Clase para verificar la integridad de datos durante conversiones"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def check_data_integrity(
        self, 
        original_df: pd.DataFrame, 
        converted_df: Optional[pd.DataFrame] = None,
        file_path: str = ""
    ) -> Dict[str, Any]:
        """
        Verifica la integridad de los datos
        
        Args:
            original_df: DataFrame original
            converted_df: DataFrame convertido (opcional)
            file_path: Ruta del archivo
            
        Returns:
            Dict con reporte de integridad
        """
        self.logger.info(f"Verificando integridad de datos para: {file_path}")
        
        report = {
            'file_path': file_path,
            'timestamp': pd.Timestamp.now().isoformat(),
            'original_stats': self._get_dataframe_stats(original_df, "original"),
            'issues': [],
            'warnings': [],
            'summary': 'OK'
        }
        
        # Verificaciones básicas del DataFrame original
        issues = self._check_basic_issues(original_df)
        report['issues'].extend(issues)
        
        # Si hay DataFrame convertido, comparar
        if converted_df is not None:
            report['converted_stats'] = self._get_dataframe_stats(converted_df, "converted")
            comparison_issues = self._compare_dataframes(original_df, converted_df)
            report['issues'].extend(comparison_issues)
        
        # Determinar estado general
        if report['issues']:
            critical_issues = [i for i in report['issues'] if i.get('severity') == 'critical']
            if critical_issues:
                report['summary'] = 'CRITICAL'
            else:
                report['summary'] = 'WARNING'
        
        self.logger.info(f"Verificación completada. Estado: {report['summary']}")
        return report
    
    def _get_dataframe_stats(self, df: pd.DataFrame, label: str) -> Dict[str, Any]:
        """
        Obtiene estadísticas básicas de un DataFrame
        
        Args:
            df: DataFrame a analizar
            label: Etiqueta descriptiva
            
        Returns:
            Dict con estadísticas
        """
        try:
            return {
                'label': label,
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': list(df.columns),
                'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
                'null_counts': df.isnull().sum().to_dict(),
                'memory_usage_mb': round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
                'duplicate_rows': df.duplicated().sum(),
                'empty_cells': df.isnull().sum().sum()
            }
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {str(e)}")
            return {'label': label, 'error': str(e)}
    
    def _check_basic_issues(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Verifica problemas básicos en el DataFrame
        
        Args:
            df: DataFrame a verificar
            
        Returns:
            Lista de problemas encontrados
        """
        issues = []
        
        try:
            # Verificar DataFrame vacío
            if df.empty:
                issues.append({
                    'type': 'empty_dataframe',
                    'severity': 'critical',
                    'message': 'El DataFrame está vacío',
                    'details': 'No se encontraron datos para procesar'
                })
                return issues
            
            # Verificar columnas duplicadas
            duplicate_columns = df.columns[df.columns.duplicated()].tolist()
            if duplicate_columns:
                issues.append({
                    'type': 'duplicate_columns',
                    'severity': 'warning',
                    'message': f'Columnas duplicadas encontradas: {duplicate_columns}',
                    'details': f'Se encontraron {len(duplicate_columns)} columnas con nombres duplicados'
                })
            
            # Verificar columnas completamente vacías
            empty_columns = df.columns[df.isnull().all()].tolist()
            if empty_columns:
                issues.append({
                    'type': 'empty_columns',
                    'severity': 'warning',
                    'message': f'Columnas completamente vacías: {empty_columns}',
                    'details': f'{len(empty_columns)} columnas no contienen datos'
                })
            
            # Verificar filas completamente vacías
            empty_rows = df.isnull().all(axis=1).sum()
            if empty_rows > 0:
                issues.append({
                    'type': 'empty_rows',
                    'severity': 'warning',
                    'message': f'Filas completamente vacías: {empty_rows}',
                    'details': f'{empty_rows} filas no contienen datos válidos'
                })
            
            # Verificar tipos de datos inconsistentes
            mixed_types_columns = self._check_mixed_types(df)
            if mixed_types_columns:
                issues.append({
                    'type': 'mixed_data_types',
                    'severity': 'warning',
                    'message': f'Columnas con tipos de datos mixtos: {mixed_types_columns}',
                    'details': 'Algunas columnas contienen tipos de datos inconsistentes'
                })
            
            # Verificar porcentaje alto de valores nulos
            null_percentages = (df.isnull().sum() / len(df) * 100)
            high_null_columns = null_percentages[null_percentages > 50].index.tolist()
            if high_null_columns:
                issues.append({
                    'type': 'high_null_percentage',
                    'severity': 'warning',
                    'message': f'Columnas con >50% valores nulos: {high_null_columns}',
                    'details': f'{len(high_null_columns)} columnas tienen alta proporción de datos faltantes'
                })
            
        except Exception as e:
            issues.append({
                'type': 'verification_error',
                'severity': 'critical',
                'message': f'Error durante verificación: {str(e)}',
                'details': 'No se pudo completar la verificación de integridad'
            })
        
        return issues
    
    def _check_mixed_types(self, df: pd.DataFrame) -> List[str]:
        """
        Verifica columnas con tipos de datos mixtos
        
        Args:
            df: DataFrame a verificar
            
        Returns:
            Lista de nombres de columnas con tipos mixtos
        """
        mixed_columns = []
        
        for col in df.columns:
            try:
                # Solo verificar columnas de tipo object
                if df[col].dtype == 'object':
                    # Verificar si hay mezcla de números y texto
                    non_null_values = df[col].dropna()
                    if not non_null_values.empty:
                        numeric_count = sum(pd.to_numeric(non_null_values, errors='coerce').notna())
                        total_count = len(non_null_values)
                        
                        # Si hay mezcla significativa (ni todo numérico ni todo texto)
                        if 0 < numeric_count < total_count * 0.9:
                            mixed_columns.append(col)
            except:
                continue
        
        return mixed_columns
    
    def _compare_dataframes(self, original_df: pd.DataFrame, converted_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Compara dos DataFrames para verificar integridad en la conversión
        
        Args:
            original_df: DataFrame original
            converted_df: DataFrame convertido
            
        Returns:
            Lista de problemas encontrados en la comparación
        """
        issues = []
        
        try:
            # Comparar dimensiones
            if len(original_df) != len(converted_df):
                issues.append({
                    'type': 'row_count_mismatch',
                    'severity': 'critical',
                    'message': f'Diferencia en número de filas: {len(original_df)} vs {len(converted_df)}',
                    'details': f'Se perdieron o añadieron {abs(len(original_df) - len(converted_df))} filas'
                })
            
            if len(original_df.columns) != len(converted_df.columns):
                issues.append({
                    'type': 'column_count_mismatch',
                    'severity': 'warning',
                    'message': f'Diferencia en número de columnas: {len(original_df.columns)} vs {len(converted_df.columns)}',
                    'details': 'El número de columnas cambió durante la conversión'
                })
            
            # Comparar nombres de columnas
            original_cols = set(original_df.columns)
            converted_cols = set(converted_df.columns)
            
            if original_cols != converted_cols:
                missing_cols = original_cols - converted_cols
                new_cols = converted_cols - original_cols
                
                if missing_cols:
                    issues.append({
                        'type': 'missing_columns',
                        'severity': 'warning',
                        'message': f'Columnas faltantes: {list(missing_cols)}',
                        'details': f'{len(missing_cols)} columnas no se transfirieron'
                    })
                
                if new_cols:
                    issues.append({
                        'type': 'new_columns',
                        'severity': 'info',
                        'message': f'Columnas nuevas: {list(new_cols)}',
                        'details': f'{len(new_cols)} columnas se añadieron durante la conversión'
                    })
            
        except Exception as e:
            issues.append({
                'type': 'comparison_error',
                'severity': 'critical',
                'message': f'Error comparando DataFrames: {str(e)}',
                'details': 'No se pudo completar la comparación de integridad'
            })
        
        return issues
    
    def generate_report_summary(self, report: Dict[str, Any]) -> str:
        """
        Genera un resumen legible del reporte de integridad
        
        Args:
            report: Reporte de integridad
            
        Returns:
            Resumen en texto
        """
        summary_lines = [
            f"📊 **Reporte de Integridad - {report.get('summary', 'UNKNOWN')}**",
            f"📁 Archivo: {report.get('file_path', 'N/A')}",
            f"🕒 Timestamp: {report.get('timestamp', 'N/A')}",
            ""
        ]
        
        # Estadísticas originales
        if 'original_stats' in report:
            stats = report['original_stats']
            summary_lines.extend([
                f"📈 **Datos Originales:**",
                f"- Filas: {stats.get('rows', 'N/A'):,}",
                f"- Columnas: {stats.get('columns', 'N/A')}",
                f"- Memoria: {stats.get('memory_usage_mb', 'N/A')} MB",
                f"- Filas duplicadas: {stats.get('duplicate_rows', 'N/A'):,}",
                f"- Celdas vacías: {stats.get('empty_cells', 'N/A'):,}",
                ""
            ])
        
        # Estadísticas convertidas
        if 'converted_stats' in report:
            stats = report['converted_stats']
            summary_lines.extend([
                f"📤 **Datos Convertidos:**",
                f"- Filas: {stats.get('rows', 'N/A'):,}",
                f"- Columnas: {stats.get('columns', 'N/A')}",
                f"- Memoria: {stats.get('memory_usage_mb', 'N/A')} MB",
                ""
            ])
        
        # Problemas encontrados
        issues = report.get('issues', [])
        if issues:
            summary_lines.append("⚠️ **Problemas Detectados:**")
            for issue in issues:
                severity_icon = {
                    'critical': '🔴',
                    'warning': '🟡',
                    'info': '🔵'
                }.get(issue.get('severity', 'info'), '⚪')
                
                summary_lines.append(f"{severity_icon} {issue.get('message', 'Error desconocido')}")
        else:
            summary_lines.append("✅ **No se detectaron problemas**")
        
        return "\n".join(summary_lines)
