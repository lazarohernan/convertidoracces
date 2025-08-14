#!/usr/bin/env python3
"""
Script para crear archivos de prueba
==================================

Genera archivos de ejemplo en diferentes formatos para probar
el sistema de conversión.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime, timedelta
import random

def create_test_data():
    """Crea datos de prueba realistas"""
    
    # Datos de productos
    productos = {
        'ID_Producto': range(1, 101),
        'Nombre': [f'Producto {i}' for i in range(1, 101)],
        'Categoria': random.choices(['Electrónicos', 'Ropa', 'Hogar', 'Deportes', 'Libros'], k=100),
        'Precio': [round(random.uniform(10, 1000), 2) for _ in range(100)],
        'Stock': [random.randint(0, 500) for _ in range(100)],
        'Proveedor': [f'Proveedor {random.randint(1, 20)}' for _ in range(100)]
    }
    
    # Datos de clientes
    clientes = {
        'ID_Cliente': range(1, 51),
        'Nombre': [f'Cliente {i}' for i in range(1, 51)],
        'Email': [f'cliente{i}@email.com' for i in range(1, 51)],
        'Telefono': [f'+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}' for _ in range(50)],
        'Ciudad': random.choices(['Madrid', 'Barcelona', 'Valencia', 'Sevilla', 'Bilbao'], k=50),
        'Fecha_Registro': [(datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d') for _ in range(50)]
    }
    
    # Datos de ventas
    ventas = {
        'ID_Venta': range(1, 201),
        'ID_Cliente': [random.randint(1, 50) for _ in range(200)],
        'ID_Producto': [random.randint(1, 100) for _ in range(200)],
        'Cantidad': [random.randint(1, 10) for _ in range(200)],
        'Precio_Unitario': [round(random.uniform(10, 500), 2) for _ in range(200)],
        'Fecha_Venta': [(datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d') for _ in range(200)]
    }
    
    # Datos de empleados
    empleados = {
        'ID_Empleado': range(1, 21),
        'Nombre': [f'Empleado {i}' for i in range(1, 21)],
        'Apellido': [f'Apellido {i}' for i in range(1, 21)],
        'Departamento': random.choices(['Ventas', 'Marketing', 'IT', 'RRHH', 'Finanzas'], k=20),
        'Salario': [round(random.uniform(2000, 8000), 2) for _ in range(20)],
        'Fecha_Contratacion': [(datetime.now() - timedelta(days=random.randint(30, 1000))).strftime('%Y-%m-%d') for _ in range(20)]
    }
    
    return {
        'productos': productos,
        'clientes': clientes,
        'ventas': ventas,
        'empleados': empleados
    }

def create_csv_files(data):
    """Crea archivos CSV"""
    print("📄 Creando archivos CSV...")
    
    input_dir = Path("data/input")
    input_dir.mkdir(parents=True, exist_ok=True)
    
    for name, data_dict in data.items():
        df = pd.DataFrame(data_dict)
        file_path = input_dir / f"{name}.csv"
        df.to_csv(file_path, index=False)
        print(f"✅ {file_path} ({len(df)} filas, {len(df.columns)} columnas)")

def create_excel_files(data):
    """Crea archivos Excel"""
    print("📊 Creando archivos Excel...")
    
    input_dir = Path("data/input")
    
    # Archivo Excel con múltiples hojas
    excel_path = input_dir / "datos_completos.xlsx"
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        for name, data_dict in data.items():
            df = pd.DataFrame(data_dict)
            df.to_excel(writer, sheet_name=name.capitalize(), index=False)
    
    print(f"✅ {excel_path} (múltiples hojas)")
    
    # Archivos Excel individuales
    for name, data_dict in data.items():
        df = pd.DataFrame(data_dict)
        file_path = input_dir / f"{name}.xlsx"
        df.to_excel(file_path, index=False)
        print(f"✅ {file_path} ({len(df)} filas)")

def create_json_files(data):
    """Crea archivos JSON"""
    print("📋 Creando archivos JSON...")
    
    input_dir = Path("data/input")
    
    # Archivo JSON con todos los datos
    all_data = {}
    for name, data_dict in data.items():
        df = pd.DataFrame(data_dict)
        all_data[name] = df.to_dict('records')
    
    json_path = input_dir / "datos_completos.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ {json_path} (datos completos)")
    
    # Archivos JSON individuales
    for name, data_dict in data.items():
        df = pd.DataFrame(data_dict)
        file_path = input_dir / f"{name}.json"
        df.to_json(file_path, orient='records', indent=2, force_ascii=False)
        print(f"✅ {file_path} ({len(df)} registros)")

def create_sample_files():
    """Crea archivos de muestra más pequeños"""
    print("🎯 Creando archivos de muestra...")
    
    input_dir = Path("data/input")
    
    # Archivo CSV pequeño
    sample_data = {
        'ID': range(1, 11),
        'Nombre': [f'Item {i}' for i in range(1, 11)],
        'Valor': [random.randint(10, 100) for _ in range(10)],
        'Activo': [random.choice([True, False]) for _ in range(10)]
    }
    
    df_sample = pd.DataFrame(sample_data)
    sample_path = input_dir / "muestra.csv"
    df_sample.to_csv(sample_path, index=False)
    print(f"✅ {sample_path} (10 filas)")
    
    # Archivo JSON pequeño
    sample_json_path = input_dir / "muestra.json"
    df_sample.to_json(sample_json_path, orient='records', indent=2)
    print(f"✅ {sample_json_path} (10 registros)")

def main():
    """Función principal"""
    print("🚀 Generador de Archivos de Prueba")
    print("=" * 40)
    
    # Crear directorio de entrada
    input_dir = Path("data/input")
    input_dir.mkdir(parents=True, exist_ok=True)
    
    # Generar datos
    print("📊 Generando datos de prueba...")
    data = create_test_data()
    
    # Crear archivos en diferentes formatos
    create_csv_files(data)
    create_excel_files(data)
    create_json_files(data)
    create_sample_files()
    
    print("\n🎉 ¡Archivos de prueba creados exitosamente!")
    print(f"📁 Ubicación: {input_dir.absolute()}")
    print("\n📋 Archivos creados:")
    
    for file_path in input_dir.iterdir():
        if file_path.is_file():
            size_mb = file_path.stat().st_size / (1024 * 1024)
            print(f"   • {file_path.name} ({size_mb:.2f} MB)")
    
    print("\n💡 Ahora puedes:")
    print("   1. Ejecutar: python start_robust.py")
    print("   2. Abrir la interfaz web")
    print("   3. Probar la conversión de archivos")

if __name__ == "__main__":
    main() 