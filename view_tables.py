#!/usr/bin/env python3
"""
Script para ver el contenido de las tablas en Railway MySQL
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.append(str(Path(__file__).parent / "src"))

from src.writers.mysql_writer import MySQLWriter

def view_tables():
    """Ver tablas y su contenido en Railway"""
    print("🔍 Explorando tablas en Railway MySQL...")
    
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
        # Conectar
        mysql_writer = MySQLWriter(db_config)
        connection_result = mysql_writer.test_connection()
        
        if not connection_result['success']:
            print(f"❌ Error de conexión: {connection_result['message']}")
            return
        
        print(f"✅ Conectado a Railway MySQL")
        print(f"🌐 {db_config['host']}:{db_config['port']}/{db_config['database']}")
        
        # Obtener lista de tablas
        with mysql_writer.engine.connect() as conn:
            # Mostrar todas las tablas
            print(f"\n📋 TABLAS DISPONIBLES:")
            tables_result = conn.execute("SHOW TABLES")
            tables = [row[0] for row in tables_result]
            
            for i, table_name in enumerate(tables, 1):
                # Contar filas
                count_result = conn.execute(f"SELECT COUNT(*) FROM `{table_name}`")
                count = count_result.fetchone()[0]
                print(f"  {i}. 📊 {table_name} ({count:,} filas)")
            
            print(f"\n🔍 MUESTRA DE DATOS:")
            for table_name in tables:
                if table_name != 'at2_bdt_mensual_test':  # Skip test table
                    print(f"\n📋 Tabla: {table_name}")
                    
                    # Mostrar estructura
                    desc_result = conn.execute(f"DESCRIBE `{table_name}`")
                    columns = [row[0] for row in desc_result]
                    print(f"   📝 Columnas: {', '.join(columns)}")
                    
                    # Mostrar primeras 3 filas
                    sample_result = conn.execute(f"SELECT * FROM `{table_name}` LIMIT 3")
                    print(f"   📄 Primeras 3 filas:")
                    for j, row in enumerate(sample_result, 1):
                        row_data = [str(val) if val is not None else 'NULL' for val in row]
                        print(f"      {j}: {' | '.join(row_data)}")
                    
                    if table_name in ['at2_bdt_mensual_2008', 'at2_bdt_mensual_2009']:
                        # Solo mostrar muestra para las primeras 2 tablas
                        pass
                    else:
                        print(f"   ...")
            
            # Estadísticas finales
            print(f"\n📊 ESTADÍSTICAS GENERALES:")
            total_rows = 0
            for table_name in tables:
                if table_name != 'at2_bdt_mensual_test':
                    count_result = conn.execute(f"SELECT COUNT(*) FROM `{table_name}`")
                    count = count_result.fetchone()[0]
                    total_rows += count
            
            print(f"   📈 Total de tablas: {len(tables)-1} (excluyendo test)")
            print(f"   📈 Total de filas: {total_rows:,}")
            print(f"   🗄️  Base de datos: railway")
            print(f"   🌐 Acceso público: {db_config['host']}:{db_config['port']}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    view_tables()
