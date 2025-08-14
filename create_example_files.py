#!/usr/bin/env python3
"""
Script para crear archivos de ejemplo para probar el sistema
"""

import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def create_example_files():
    """Crear archivos de ejemplo"""
    print("📁 Creando archivos de ejemplo...")
    
    # Crear directorio si no existe
    input_dir = Path("data/input/")
    input_dir.mkdir(parents=True, exist_ok=True)
    
    # Archivo CSV ya existe, solo crear Excel y JSON adicionales
    
    # Crear archivo JSON adicional
    json_data = {
        "empleados": [
            {"id": 1, "nombre": "Ana García", "departamento": "Ventas", "salario": 45000},
            {"id": 2, "nombre": "Carlos López", "departamento": "IT", "salario": 55000},
            {"id": 3, "nombre": "María Rodríguez", "departamento": "Marketing", "salario": 48000},
            {"id": 4, "nombre": "Juan Pérez", "departamento": "Ventas", "salario": 42000},
            {"id": 5, "nombre": "Laura Martín", "departamento": "IT", "salario": 52000}
        ]
    }
    
    with open("data/input/ejemplo_empleados.json", "w", encoding="utf-8") as f:
        import json
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    print("✅ Archivos de ejemplo creados:")
    print("   - data/input/ejemplo_clientes.csv (ya existía)")
    print("   - data/input/ejemplo_productos.json (ya existía)")
    print("   - data/input/ejemplo_empleados.json (nuevo)")

if __name__ == "__main__":
    create_example_files() 