#!/usr/bin/env python3
"""
Script de prueba para conversión directa a MySQL Railway
"""

import os
import sys
from pathlib import Path

# Agregar src al path
sys.path.append(str(Path(__file__).parent / "src"))

from src.writers.mysql_writer import MySQLWriter
from src.core.converter import FileConverter

def test_mysql_conversion():
    """Prueba la conversión directa a MySQL Railway"""
    print("🔄 Iniciando prueba de conversión MySQL...")
    
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
    
    # Configuración de nombres
    naming_config = {
        'prefix': 'at2-historico',
        'suffix': '',
        'replacement_pattern': '{year}'
    }
    
    # Archivo de prueba
    file_path = "data/input/AT2.mdb"
    
    if not os.path.exists(file_path):
        print(f"❌ Error: Archivo no encontrado: {file_path}")
        return False
    
    try:
        # 1. Probar conexión MySQL
        print("🔗 Probando conexión MySQL...")
        mysql_writer = MySQLWriter(db_config)
        connection_result = mysql_writer.test_connection()
        
        if not connection_result['success']:
            print(f"❌ Error de conexión: {connection_result['message']}")
            return False
        
        print(f"✅ Conexión exitosa: {connection_result['message']}")
        if 'server_info' in connection_result:
            info = connection_result['server_info']
            print(f"   - Base de datos: {info.get('database', 'N/A')}")
            print(f"   - Host: {info.get('host', 'N/A')}:{info.get('port', 'N/A')}")
            print(f"   - Versión: {info.get('version', 'N/A')}")
        
        # 2. Realizar conversión usando el convertidor
        print("\n🔄 Iniciando conversión por años...")
        converter = FileConverter()
        
        result = converter.convert_access_by_year(
            input_path=file_path,
            output_format='sql',
            output_dir='/tmp',
            naming_config=naming_config
        )
        
        if not result['success']:
            print(f"❌ Error en conversión: {result.get('message', 'Error desconocido')}")
            return False
        
        print(f"✅ Conversión completada: {len(result['files_created'])} archivos generados")
        
        # 3. Subir cada archivo SQL a MySQL
        print("\n📤 Subiendo archivos a MySQL...")
        uploaded_count = 0
        failed_count = 0
        
        for file_info in result['files_created']:
            sql_file = file_info['path']
            table_name = Path(sql_file).stem
            
            print(f"   - Subiendo {table_name}...")
            
            try:
                # Leer archivo SQL
                with open(sql_file, 'r', encoding='utf-8') as f:
                    sql_content = f.read()
                
                # Ejecutar en MySQL
                exec_result = mysql_writer.execute_sql(sql_content)
                
                if exec_result['success']:
                    uploaded_count += 1
                    print(f"     ✅ {table_name} - {exec_result['statements_executed']} statements ejecutados")
                else:
                    failed_count += 1
                    print(f"     ❌ {table_name} - Error: {exec_result.get('error', 'Desconocido')}")
                
                # Limpiar archivo temporal
                if os.path.exists(sql_file):
                    os.remove(sql_file)
                    
            except Exception as e:
                failed_count += 1
                print(f"     ❌ {table_name} - Error procesando: {str(e)}")
        
        # 4. Resumen final
        print(f"\n📊 Resumen:")
        print(f"   - Tablas subidas: {uploaded_count}")
        print(f"   - Tablas fallidas: {failed_count}")
        print(f"   - Base de datos: {db_config['database']}")
        print(f"   - Host: {db_config['host']}:{db_config['port']}")
        
        return uploaded_count > 0
        
    except Exception as e:
        print(f"❌ Error general: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_mysql_conversion()
    if success:
        print("\n🎉 ¡Conversión MySQL completada exitosamente!")
        sys.exit(0)
    else:
        print("\n💥 Error en la conversión MySQL")
        sys.exit(1)
