#!/usr/bin/env python3
"""
Script de prueba para generar un archivo SQL de prueba con sintaxis MySQL correcta
"""

import os
import sys
from pathlib import Path
import pandas as pd

# Agregar src al path
sys.path.append(str(Path(__file__).parent / "src"))

from src.writers.sql_writer import SQLWriter
from src.writers.mysql_writer import MySQLWriter
from src.readers.robust_access_reader import RobustAccessReader

def test_mysql_sql_generation():
    """Prueba la generación de SQL con sintaxis MySQL correcta"""
    print("🔧 Probando generación de SQL con sintaxis MySQL...")
    
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
        # 1. Leer una muestra pequeña de datos Access
        print("📖 Leyendo muestra de datos Access...")
        access_reader = RobustAccessReader()
        df = access_reader.read("data/input/AT2.mdb", "AT2_BDT_MENSUAL")
        
        # Tomar solo los primeros 100 registros para prueba rápida
        df_sample = df.head(100)
        print(f"   ✅ Muestra obtenida: {len(df_sample)} filas, {len(df_sample.columns)} columnas")
        
        # 2. Generar archivo SQL
        print("🔧 Generando archivo SQL de prueba...")
        sql_writer = SQLWriter()
        
        output_path = "/tmp/test_mysql_syntax.sql"
        table_name = "at2_bdt_mensual_test"
        
        result = sql_writer.write(df_sample, output_path, table_name)
        
        if result['success']:
            print(f"   ✅ SQL generado exitosamente: {output_path}")
            print(f"   - Filas: {result['rows_inserted']}")
            print(f"   - Columnas: {result['columns']}")
        else:
            print(f"   ❌ Error generando SQL")
            return False
        
        # 3. Revisar la sintaxis generada
        print("\n🔍 Revisando sintaxis generada...")
        with open(output_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Mostrar las primeras líneas
        lines = sql_content.split('\n')
        print("   Primeras 10 líneas del SQL:")
        for i, line in enumerate(lines[:10], 1):
            print(f"   {i:2d}: {line}")
        
        # Verificar que usa backticks en lugar de comillas dobles
        if '`' in sql_content and '"' not in sql_content.replace('"Archivo SQL generado', '').replace('"Tabla:', '').replace('"Filas:', '').replace('"Columnas:', ''):
            print("   ✅ Sintaxis correcta: usa backticks para MySQL")
        else:
            print("   ⚠️  Posible problema de sintaxis")
        
        # 4. Probar conexión y ejecución en MySQL
        print("\n🗄️  Probando subida a MySQL...")
        mysql_writer = MySQLWriter(db_config)
        connection_result = mysql_writer.test_connection()
        
        if not connection_result['success']:
            print(f"   ❌ Error de conexión: {connection_result['message']}")
            return False
        
        print("   ✅ Conexión exitosa a MySQL")
        
        # Ejecutar SQL
        exec_result = mysql_writer.execute_sql(sql_content)
        
        if exec_result['success']:
            print(f"   ✅ SQL ejecutado exitosamente: {exec_result['statements_executed']} statements")
            
            # Verificar que la tabla existe
            verify_result = mysql_writer.execute_sql(f"SELECT COUNT(*) FROM `{table_name}`")
            if verify_result['success']:
                print(f"   ✅ Tabla verificada en la base de datos")
            else:
                print(f"   ⚠️  No se pudo verificar la tabla")
                
        else:
            print(f"   ❌ Error ejecutando SQL: {exec_result.get('error', 'Desconocido')}")
            return False
        
        # Limpiar
        if os.path.exists(output_path):
            os.remove(output_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Error general: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_mysql_sql_generation()
    if success:
        print("\n🎉 ¡Prueba de sintaxis MySQL exitosa!")
        sys.exit(0)
    else:
        print("\n💥 Error en la prueba de sintaxis MySQL")
        sys.exit(1)
