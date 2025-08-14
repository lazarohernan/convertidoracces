"""
Configuración de la aplicación
"""

import os
from pathlib import Path

# Rutas base
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"

# Crear directorios si no existen
for directory in [DATA_DIR, INPUT_DIR, OUTPUT_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

# Configuración de logging
LOG_CONFIG = {
    'level': os.getenv('LOG_LEVEL', 'INFO'),
    'file': str(LOGS_DIR / 'converter.log'),
    'rotation': '10 MB',
    'retention': '7 days',
    'compression': 'zip'
}

# Configuración de archivos
FILE_CONFIG = {
    'max_size_mb': int(os.getenv('MAX_FILE_SIZE_MB', 100)),
    'supported_input_formats': ['.csv', '.xlsx', '.xls', '.json'],
    'supported_output_formats': ['sql', 'sqlite']
}

# Configuración de base de datos
DATABASE_CONFIG = {
    'sqlite': {
        'default_path': str(OUTPUT_DIR / 'database.db')
    },
    'postgresql': {
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': int(os.getenv('POSTGRES_PORT', 5432)),
        'database': os.getenv('POSTGRES_DB', ''),
        'user': os.getenv('POSTGRES_USER', ''),
        'password': os.getenv('POSTGRES_PASSWORD', '')
    }
}

# Configuración de conversión
CONVERSION_CONFIG = {
    'default_output_format': os.getenv('DEFAULT_OUTPUT_FORMAT', 'sql'),
    'default_table_name': os.getenv('DEFAULT_TABLE_NAME', 'data_table'),
    'batch_size': int(os.getenv('BATCH_SIZE', 1000)),
    'chunk_size': int(os.getenv('CHUNK_SIZE', 10000))
} 