#!/usr/bin/env python3
"""
Script simple para probar convert_to_mysql_by_year con syntaxis corregida
"""

import sys
import os
from pathlib import Path

# Configuración Railway
db_config = {
    'type': 'mysql',  
    'host': 'shinkansen.proxy.rlwy.net',
    'port': 50498,
    'user': 'root',
    'password': 'OZLeLlikuBETQMzrldNVSJNryrYEZkZJ',
    'database': 'railway',
    'charset': 'utf8mb4',
    'ssl_disabled': True
}

naming_config = {
    'prefix': 'at2-historico',
    'suffix': '',
    'replacement_pattern': '{year}'
}

file_path = "data/input/AT2.mdb"

print("🚀 Probando conversión MySQL con sintaxis corregida...")
print(f"📁 Archivo: {file_path}")
print(f"🗄️  MySQL: {db_config['host']}:{db_config['port']}/{db_config['database']}")

# Agregar src al path  
sys.path.append(str(Path(__file__).parent / "src"))

try:
    # Importar y ejecutar
    from web_interface_robust import convert_to_mysql_by_year
    
    result = convert_to_mysql_by_year(file_path, db_config, naming_config)
    
    if result['success']:
        print(f"✅ {result['message']}")
        
        if 'details' in result:
            details = result['details']
            print(f"📊 Tablas subidas: {details.get('total_success', 0)}")
            print(f"📊 Tablas fallidas: {details.get('total_failed', 0)}")
            print(f"🗄️  Base: {details.get('database', 'N/A')}")
    else:
        print(f"❌ {result['message']}")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
