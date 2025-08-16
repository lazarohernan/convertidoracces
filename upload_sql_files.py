#!/usr/bin/env python3
"""
Script rápido para subir archivos SQL ya existentes a MySQL Railway
"""

import os
import sys
from pathlib import Path
import glob

# Agregar src al path
sys.path.append(str(Path(__file__).parent / "src"))

from src.writers.mysql_writer import MySQLWriter

def upload_sql_files():
    """Sube archivos SQL existentes a MySQL Railway"""
    print("📤 Subiendo archivos SQL existentes a MySQL Railway...")
    
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
    
    try:
        # Conectar a MySQL
        print("🔗 Conectando a MySQL...")
        mysql_writer = MySQLWriter(db_config)
        connection_result = mysql_writer.test_connection()
        
        if not connection_result['success']:
            print(f"❌ Error de conexión: {connection_result['message']}")
            return False
        
        print(f"✅ Conexión exitosa: {connection_result['message']}")
        
        # Buscar archivos SQL
        sql_files = glob.glob('/tmp/at2_bdt_mensual*.sql')
        if not sql_files:
            print("❌ No se encontraron archivos SQL")
            return False
        
        print(f"📁 Encontrados {len(sql_files)} archivos SQL")
        
        uploaded_count = 0
        failed_count = 0
        
        for sql_file in sorted(sql_files):
            table_name = Path(sql_file).stem
            print(f"   📤 Subiendo {table_name}...")
            
            try:
                # Leer archivo SQL
                with open(sql_file, 'r', encoding='utf-8') as f:
                    sql_content = f.read()
                
                # Verificar contenido
                if not sql_content.strip():
                    print(f"     ⚠️  Archivo vacío: {sql_file}")
                    continue
                
                # Ejecutar en MySQL
                exec_result = mysql_writer.execute_sql(sql_content)
                
                if exec_result['success']:
                    uploaded_count += 1
                    print(f"     ✅ {table_name} - {exec_result['statements_executed']} statements ejecutados")
                else:
                    failed_count += 1
                    error_msg = exec_result.get('error', 'Error desconocido')
                    print(f"     ❌ {table_name} - Error: {error_msg[:100]}...")
                    
            except Exception as e:
                failed_count += 1
                print(f"     ❌ {table_name} - Error procesando: {str(e)}")
        
        # Resumen
        print(f"\n📊 Resumen de carga:")
        print(f"   ✅ Tablas subidas exitosamente: {uploaded_count}")
        print(f"   ❌ Tablas fallidas: {failed_count}")
        print(f"   🏠 Base de datos: {db_config['database']}")
        print(f"   🌐 Host: {db_config['host']}:{db_config['port']}")
        
        if uploaded_count > 0:
            print("\n🔍 Verificando tablas en Railway...")
            # Verificar que las tablas existen
            verification_query = "SHOW TABLES"
            tables_result = mysql_writer.execute_sql(verification_query)
            if tables_result['success']:
                print("   📋 Tablas en la base de datos:")
                # El resultado está en statements_executed, necesitamos ejecutar una query de consulta
                tables_check = mysql_writer.engine.execute("SHOW TABLES")
                for row in tables_check:
                    print(f"      - {row[0]}")
        
        return uploaded_count > 0
        
    except Exception as e:
        print(f"❌ Error general: {str(e)}")
        return False

if __name__ == "__main__":
    success = upload_sql_files()
    if success:
        print("\n🎉 ¡Carga de archivos SQL completada!")
        sys.exit(0)
    else:
        print("\n💥 Error en la carga de archivos SQL")
        sys.exit(1)
