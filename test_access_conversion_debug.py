#!/usr/bin/env python3
"""
Script de Diagnóstico para Conversión de Archivos Access
=======================================================

Este script prueba paso a paso la conversión de archivos Access para identificar
exactamente dónde está el problema.
"""

import sys
import os
from pathlib import Path
import pandas as pd
import subprocess
import time

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.readers.robust_access_reader import RobustAccessReader
from src.core.converter import FileConverter
from src.utils.logger import setup_logger

def test_mdbtools_installation():
    """Prueba si mdb-tools está instalado correctamente"""
    print("🔍 Probando instalación de mdb-tools...")
    
    try:
        # Probar mdb-tables
        result = subprocess.run(['mdb-tables', '--version'], 
                              capture_output=True, text=True, timeout=10)
        print(f"✅ mdb-tables disponible: {result.stdout.strip()}")
        
        # Probar mdb-export
        result = subprocess.run(['mdb-export', '--version'], 
                              capture_output=True, text=True, timeout=10)
        print(f"✅ mdb-export disponible: {result.stdout.strip()}")
        
        return True
    except Exception as e:
        print(f"❌ Error con mdb-tools: {str(e)}")
        return False

def test_access_file_detection():
    """Prueba la detección de archivos Access"""
    print("\n🔍 Probando detección de archivos Access...")
    
    input_dir = Path("data/input")
    if not input_dir.exists():
        print("❌ Directorio data/input no existe")
        return []
    
    access_files = []
    for file_path in input_dir.glob("*.mdb"):
        access_files.append(file_path)
    for file_path in input_dir.glob("*.accdb"):
        access_files.append(file_path)
    
    print(f"📁 Archivos Access encontrados: {len(access_files)}")
    for file_path in access_files:
        print(f"   - {file_path.name} ({file_path.stat().st_size / 1024 / 1024:.1f} MB)")
    
    return access_files

def test_table_detection(file_path):
    """Prueba la detección de tablas en un archivo Access"""
    print(f"\n🔍 Probando detección de tablas en {file_path.name}...")
    
    try:
        reader = RobustAccessReader()
        tables = reader.get_table_names(str(file_path))
        
        print(f"✅ Tablas detectadas: {len(tables)}")
        for i, table in enumerate(tables, 1):
            print(f"   {i}. {table}")
        
        return tables
    except Exception as e:
        print(f"❌ Error detectando tablas: {str(e)}")
        return []

def test_table_reading(file_path, table_name):
    """Prueba la lectura de una tabla específica"""
    print(f"\n🔍 Probando lectura de tabla '{table_name}'...")
    
    try:
        reader = RobustAccessReader()
        
        # Probar lectura con mdb-tools
        print("   Probando método mdb-tools...")
        df = reader.read(str(file_path), table_name)
        
        print(f"✅ Lectura exitosa: {len(df)} filas, {len(df.columns)} columnas")
        print(f"   Columnas: {list(df.columns)}")
        print(f"   Tipos de datos: {df.dtypes.to_dict()}")
        
        # Mostrar primeras filas
        print(f"   Primeras 3 filas:")
        print(df.head(3).to_string())
        
        return df
    except Exception as e:
        print(f"❌ Error leyendo tabla: {str(e)}")
        return None

def test_converter_initialization():
    """Prueba la inicialización del converter"""
    print("\n🔍 Probando inicialización del converter...")
    
    try:
        converter = FileConverter()
        print("✅ Converter inicializado correctamente")
        
        # Verificar readers disponibles
        print(f"   Readers disponibles: {list(converter.readers.keys())}")
        
        # Verificar writers disponibles
        print(f"   Writers disponibles: {list(converter.writers.keys())}")
        
        return converter
    except Exception as e:
        print(f"❌ Error inicializando converter: {str(e)}")
        return None

def test_conversion_step_by_step(file_path, table_name, output_format="csv"):
    """Prueba la conversión paso a paso"""
    print(f"\n🔍 Probando conversión paso a paso...")
    print(f"   Archivo: {file_path.name}")
    print(f"   Tabla: {table_name}")
    print(f"   Formato: {output_format}")
    
    try:
        converter = FileConverter()
        
        # Paso 1: Leer archivo
        print("\n   1️⃣ Leyendo archivo...")
        df = converter._read_file(str(file_path), table_name)
        print(f"   ✅ Archivo leído: {len(df)} filas, {len(df.columns)} columnas")
        
        # Paso 2: Validar datos
        print("\n   2️⃣ Validando datos...")
        validation = converter.validator.validate_dataframe(df)
        print(f"   ✅ Datos validados: {validation}")
        
        # Paso 3: Generar ruta de salida
        print("\n   3️⃣ Generando ruta de salida...")
        output_dir = Path("data/output")
        output_dir.mkdir(exist_ok=True)
        
        if output_format == "sqlite":
            output_file = f"{output_dir}/{table_name}.db"
        elif output_format == "csv":
            output_file = f"{output_dir}/{table_name}.csv"
        elif output_format == "excel":
            output_file = f"{output_dir}/{table_name}.xlsx"
        elif output_format == "json":
            output_file = f"{output_dir}/{table_name}.json"
        else:
            output_file = f"{output_dir}/{table_name}.sql"
        
        print(f"   ✅ Ruta de salida: {output_file}")
        
        # Paso 4: Escribir archivo
        print(f"\n   4️⃣ Escribiendo archivo {output_format}...")
        result = converter._write_file(df, output_file, output_format, table_name)
        print(f"   ✅ Archivo escrito: {result}")
        
        # Paso 5: Verificar archivo generado
        print("\n   5️⃣ Verificando archivo generado...")
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file) / 1024 / 1024
            print(f"   ✅ Archivo generado: {output_file} ({file_size:.2f} MB)")
        else:
            print(f"   ❌ Archivo no encontrado: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error en conversión: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_full_conversion(file_path, table_name, output_format="csv"):
    """Prueba la conversión completa usando el método convert_file"""
    print(f"\n🔍 Probando conversión completa...")
    print(f"   Archivo: {file_path.name}")
    print(f"   Tabla: {table_name}")
    print(f"   Formato: {output_format}")
    
    try:
        converter = FileConverter()
        
        # Generar ruta de salida
        output_dir = Path("data/output")
        output_dir.mkdir(exist_ok=True)
        
        if output_format == "sqlite":
            output_file = f"{output_dir}/{table_name}.db"
        elif output_format == "csv":
            output_file = f"{output_dir}/{table_name}.csv"
        elif output_format == "excel":
            output_file = f"{output_dir}/{table_name}.xlsx"
        elif output_format == "json":
            output_file = f"{output_dir}/{table_name}.json"
        else:
            output_file = f"{output_dir}/{table_name}.sql"
        
        # Realizar conversión completa
        print("   Iniciando conversión completa...")
        result = converter.convert_file(
            input_path=str(file_path),
            output_path=output_file,
            output_format=output_format,
            table_name=table_name
        )
        
        print(f"   ✅ Conversión exitosa: {result}")
        return True
        
    except Exception as e:
        print(f"   ❌ Error en conversión completa: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal de diagnóstico"""
    print("🔄 Diagnóstico de Conversión de Archivos Access")
    print("=" * 50)
    
    # Configurar logging
    setup_logger(log_level="DEBUG")
    
    # Paso 1: Verificar mdb-tools
    mdbtools_ok = test_mdbtools_installation()
    if not mdbtools_ok:
        print("\n❌ mdb-tools no está disponible. Instálalo primero.")
        return
    
    # Paso 2: Detectar archivos Access
    access_files = test_access_file_detection()
    if not access_files:
        print("\n❌ No se encontraron archivos Access para probar.")
        return
    
    # Paso 3: Probar con el primer archivo Access
    test_file = access_files[0]
    print(f"\n🎯 Probando con archivo: {test_file.name}")
    
    # Paso 4: Detectar tablas
    tables = test_table_detection(test_file)
    if not tables:
        print("\n❌ No se pudieron detectar tablas.")
        return
    
    # Paso 5: Probar lectura de la primera tabla
    test_table = tables[0]
    df = test_table_reading(test_file, test_table)
    if df is None:
        print("\n❌ No se pudo leer la tabla.")
        return
    
    # Paso 6: Probar inicialización del converter
    converter = test_converter_initialization()
    if converter is None:
        print("\n❌ No se pudo inicializar el converter.")
        return
    
    # Paso 7: Probar conversión paso a paso
    print("\n" + "="*50)
    print("🧪 PRUEBAS DE CONVERSIÓN")
    print("="*50)
    
    # Probar diferentes formatos
    formats_to_test = ["csv", "excel", "json", "sql"]
    
    for format_type in formats_to_test:
        print(f"\n📋 Probando formato: {format_type.upper()}")
        success = test_conversion_step_by_step(test_file, test_table, format_type)
        
        if success:
            print(f"✅ Conversión a {format_type} exitosa")
        else:
            print(f"❌ Conversión a {format_type} falló")
        
        time.sleep(1)  # Pausa entre pruebas
    
    # Paso 8: Probar conversión completa
    print(f"\n🎯 Probando conversión completa a CSV...")
    success = test_full_conversion(test_file, test_table, "csv")
    
    if success:
        print("✅ Conversión completa exitosa")
    else:
        print("❌ Conversión completa falló")
    
    print("\n" + "="*50)
    print("🏁 Diagnóstico completado")
    print("="*50)

if __name__ == "__main__":
    main() 