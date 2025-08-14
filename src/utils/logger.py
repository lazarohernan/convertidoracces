"""
Sistema de logging avanzado
"""

import os
import sys
from loguru import logger
from typing import Optional

def get_logger(name: str) -> logger:
    """
    Obtiene un logger configurado
    
    Args:
        name: Nombre del logger
        
    Returns:
        Logger configurado
    """
    # Configurar logger si no está configurado
    if not logger._core.handlers:
        setup_logger()
    
    return logger.bind(name=name)

def setup_logger(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    rotation: str = "10 MB",
    retention: str = "7 days"
):
    """
    Configura el sistema de logging
    
    Args:
        log_level: Nivel de logging
        log_file: Archivo de log (opcional)
        rotation: Rotación de archivos
        retention: Retención de archivos
    """
    # Remover handlers por defecto
    logger.remove()
    
    # Handler para consola
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True
    )
    
    # Handler para archivo (si se especifica)
    if log_file:
        # Crear directorio de logs si no existe
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=log_level,
            rotation=rotation,
            retention=retention,
            compression="zip"
        )
    
    # Configurar desde variables de entorno
    env_log_level = os.getenv("LOG_LEVEL", log_level)
    env_log_file = os.getenv("LOG_FILE", log_file)
    
    if env_log_file and env_log_file != log_file:
        # Crear directorio de logs si no existe
        log_dir = os.path.dirname(env_log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        logger.add(
            env_log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=env_log_level,
            rotation=rotation,
            retention=retention,
            compression="zip"
        )

# Configurar logger por defecto
setup_logger() 