#!/usr/bin/env python3
"""
Script de inicio rápido para el Sistema de Conversión de Archivos
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Menú principal del sistema"""
    print("🔄 Sistema de Conversión de Archivos")
    print("=" * 50)
    print()
    
    while True:
        print("Selecciona una opción:")
        print("1. 🌐 Ejecutar interfaz web")
        print("2. 💻 Ejecutar interfaz CLI")
        print("3. 🧪 Ejecutar pruebas")
        print("4. 📁 Ver archivos de ejemplo")
        print("5. 📋 Ver formatos soportados")
        print("6. ❌ Salir")
        print()
        
        choice = input("Opción (1-6): ").strip()
        
        if choice == "1":
            run_web_interface()
        elif choice == "2":
            run_cli_interface()
        elif choice == "3":
            run_tests()
        elif choice == "4":
            show_example_files()
        elif choice == "5":
            show_supported_formats()
        elif choice == "6":
            print("👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción no válida. Intenta de nuevo.")
        
        print()

def run_web_interface():
    """Ejecutar interfaz web"""
    print("🌐 Iniciando interfaz web...")
    try:
        subprocess.run([sys.executable, "run_web_interface.py"])
    except KeyboardInterrupt:
        print("👋 Interfaz web detenida")
    except Exception as e:
        print(f"❌ Error: {e}")

def run_cli_interface():
    """Ejecutar interfaz CLI"""
    print("💻 Iniciando interfaz CLI...")
    print("Comandos disponibles:")
    print("  python main.py convert --help")
    print("  python main.py batch --help")
    print("  python main.py info --help")
    print()
    
    try:
        subprocess.run([sys.executable, "main.py", "--help"])
    except Exception as e:
        print(f"❌ Error: {e}")

def run_tests():
    """Ejecutar pruebas"""
    print("🧪 Ejecutando pruebas...")
    try:
        subprocess.run([sys.executable, "test_converter.py"])
    except Exception as e:
        print(f"❌ Error: {e}")

def show_example_files():
    """Mostrar archivos de ejemplo"""
    print("📁 Archivos de ejemplo disponibles:")
    input_dir = Path("data/input/")
    
    if input_dir.exists():
        files = list(input_dir.glob("*"))
        if files:
            for file in files:
                if file.is_file():
                    size_mb = file.stat().st_size / (1024 * 1024)
                    print(f"  • {file.name} ({size_mb:.2f} MB)")
        else:
            print("  No hay archivos de ejemplo")
    else:
        print("  Directorio data/input/ no existe")

def show_supported_formats():
    """Mostrar formatos soportados"""
    print("📋 Formatos soportados:")
    print()
    print("Entrada:")
    print("  • CSV (.csv)")
    print("  • Excel (.xlsx, .xls)")
    print("  • JSON (.json)")
    print()
    print("Salida:")
    print("  • SQL (.sql)")
    print("  • SQLite (.db)")

if __name__ == "__main__":
    main() 