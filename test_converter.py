#!/usr/bin/env python3
"""
Script de prueba para el sistema de conversión
"""

import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.converter import FileConverter
from utils.logger import setup_logger

def test_conversion():
    """Prueba básica de conversión"""
    print("🧪 Iniciando pruebas del sistema de conversión...")
    
    # Configurar logging
    setup_logger(log_level="INFO")
    
    # Inicializar conversor
    converter = FileConverter()
    
    # Probar con archivo CSV
    csv_file = "data/input/ejemplo_clientes.csv"
    if Path(csv_file).exists():
        print(f"✅ Probando conversión de CSV: {csv_file}")
        
        try:
            # Convertir a SQL
            result = converter.convert_file(
                input_path=csv_file,
                output_path="data/output/clientes.sql",
                output_format="sql",
                table_name="clientes"
            )
            
            print(f"✅ Conversión CSV exitosa: {result['rows_inserted']} filas")
            
        except Exception as e:
            print(f"❌ Error en conversión CSV: {e}")
    
    # Probar con archivo JSON
    json_file = "data/input/ejemplo_productos.json"
    if Path(json_file).exists():
        print(f"✅ Probando conversión de JSON: {json_file}")
        
        try:
            # Convertir a SQLite
            result = converter.convert_file(
                input_path=json_file,
                output_path="data/output/productos.db",
                output_format="sqlite",
                table_name="productos"
            )
            
            print(f"✅ Conversión JSON exitosa: {result['rows_inserted']} filas")
            
        except Exception as e:
            print(f"❌ Error en conversión JSON: {e}")
    
    # Mostrar formatos soportados
    print("\n📋 Formatos soportados:")
    formats = converter.get_supported_formats()
    print(f"Entrada: {', '.join(formats['input'])}")
    print(f"Salida: {', '.join(formats['output'])}")
    
    print("\n🎉 Pruebas completadas!")

if __name__ == "__main__":
    test_conversion() 