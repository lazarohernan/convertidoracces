#!/usr/bin/env python3
"""
Script para probar la función completa convert_to_mysql_by_year
"""

import os
import sys
from pathlib import Path

# Agregar src al path
sys.path.append(str(Path(__file__).parent / "src"))

# Importar función desde web_interface_robust.py
from web_interface_robust import convert_to_mysql_by_year

def test_complete_mysql_conversion():
    """Prueba la función completa convert_to_mysql_by_year"""
    print("🚀 Probando función completa convert_to_mysql_by_year...")
    
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
        print(f"📁 Procesando archivo: {file_path}")
        print(f"🗄️  Base de datos: {db_config['host']}:{db_config['port']}/{db_config['database']}")
        print(f"🏷️  Configuración nombres: {naming_config}")
        
        # Llamar a la función
        result = convert_to_mysql_by_year(file_path, db_config, naming_config)
        
        if result['success']:
            print(f"✅ {result['message']}")
            
            if 'details' in result:
                details = result['details']
                print(f"\n📊 Detalles:")
                print(f"   🗄️  Base de datos: {details.get('database', 'N/A')}")
                print(f"   🌐 Host: {details.get('host', 'N/A')}")
                print(f"   ✅ Tablas subidas: {details.get('total_success', 0)}")
                print(f"   ❌ Tablas fallidas: {details.get('total_failed', 0)}")
                
                if 'tables_uploaded' in details:
                    print(f"\n📋 Tablas subidas exitosamente:")
                    for table in details['tables_uploaded']:
                        print(f"      - {table['name']}: {table['statements']} statements")
                
                if 'tables_failed' in details and details['tables_failed']:
                    print(f"\n⚠️  Tablas con errores:")
                    for table in details['tables_failed']:
                        print(f"      - {table['name']}: {table['error'][:100]}...")
                        
            return True
        else:
            print(f"❌ {result['message']}")
            if 'details' in result:
                print(f"   Detalles: {result['details']}")
            return False
            
    except Exception as e:
        print(f"❌ Error general: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = test_complete_mysql_conversion()
    if success:
        print("\n🎉 ¡Función convert_to_mysql_by_year exitosa!")
        
        # Verificar resultado en Railway
        print("\n🔍 Verificando resultado final en Railway...")
        sys.path.append(str(Path(__file__).parent / "src"))
        from writers.mysql_writer import MySQLWriter
        
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
            mysql_writer = MySQLWriter(db_config)
            
            # Obtener lista de tablas
            tables_result = mysql_writer.execute_sql("SHOW TABLES")
            if tables_result['success']:
                print("✅ Estado final de la base de datos Railway:")
                # Las tablas se muestran en el check_railway.py
                os.system("cd \"/Users/lazarohernan/Documents/DE Acces a archivo para base de datos \" && source venv/bin/activate && python check_railway.py")
        except:
            print("⚠️  No se pudo verificar el estado final")
            
        sys.exit(0)
    else:
        print("\n💥 Error en convert_to_mysql_by_year")
        sys.exit(1)
