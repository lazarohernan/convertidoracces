"""
Excepciones personalizadas para el sistema de conversión
"""

class ConversionError(Exception):
    """Excepción base para errores de conversión"""
    pass

class ValidationError(Exception):
    """Excepción para errores de validación de datos"""
    pass

class FileFormatError(Exception):
    """Excepción para formatos de archivo no soportados"""
    pass

class DatabaseConnectionError(Exception):
    """Excepción para errores de conexión a base de datos"""
    pass

class ConfigurationError(Exception):
    """Excepción para errores de configuración"""
    pass 