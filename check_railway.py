#!/usr/bin/env python3
"""
Script para verificar las tablas en Railway MySQL
"""

import mysql.connector
import sys

def check_railway_tables():
    """Verifica las tablas en Railway MySQL"""
    try:
        # Configuración de Railway
        config = {
            'host': 'shinkansen.proxy.rlwy.net',
            'port': 50498,
            'user': 'root',
            'password': 'OZLeLlikuBETQMzrldNVSJNryrYEZkZJ',
            'database': 'railway'
        }
        
        # Conectar
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        # Mostrar tablas
        print("🔍 Verificando tablas en Railway MySQL...")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        if tables:
            print(f"✅ Encontradas {len(tables)} tablas:")
            for table in tables:
                table_name = table[0]
                print(f"  📋 {table_name}")
                
                # Contar filas
                cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
                count = cursor.fetchone()[0]
                print(f"      🔢 {count:,} filas")
                
        else:
            print("❌ No se encontraron tablas")
            
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error conectando a Railway: {e}")
        return False
        
    return True

if __name__ == "__main__":
    check_railway_tables()
