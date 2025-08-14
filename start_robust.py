#!/usr/bin/env python3
"""
Script de inicio para la interfaz robusta
=======================================

Inicia la interfaz web robusta del sistema de conversión de archivos
con verificaciones automáticas y mejor manejo de errores.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Verifica que todas las dependencias estén instaladas"""
    print("🔍 Verificando dependencias...")
    
    dependencies = [
        ("streamlit", "Interfaz web"),
        ("pandas", "Procesamiento de datos"),
        ("plotly", "Gráficos interactivos"),
        ("altair", "Visualizaciones")
    ]
    
    missing = []
    
    for dep, description in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} - {description}")
        except ImportError:
            print(f"❌ {dep} - {description}")
            missing.append(dep)
    
    if missing:
        print(f"\n❌ Faltan dependencias: {', '.join(missing)}")
        print("💡 Instala las dependencias con: pip install -r requirements.txt")
        return False
    
    return True

def check_mdbtools():
    """Verifica si mdb-tools está disponible"""
    print("\n🔍 Verificando mdb-tools...")
    
    try:
        result = subprocess.run(['mdb-tables', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ mdb-tools está disponible")
            return True
        else:
            print("⚠️ mdb-tools no está disponible")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        print("⚠️ mdb-tools no está instalado")
        return False

def check_directories():
    """Verifica que los directorios necesarios existan"""
    print("\n📁 Verificando directorios...")
    
    directories = [
        "data/input",
        "data/output",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ {directory}/")
    
    return True

def start_interface():
    """Inicia la interfaz web"""
    print("\n🚀 Iniciando interfaz web robusta...")
    
    try:
        # Verificar que el archivo existe
        if not os.path.exists("web_interface_robust.py"):
            print("❌ Error: web_interface_robust.py no encontrado")
            return False
        
        # Iniciar Streamlit
        print("🌐 Abriendo navegador...")
        result = subprocess.run([
            sys.executable, "-m", "streamlit", "run", "web_interface_robust.py",
            "--server.port", "8501",
            "--server.headless", "false"
        ])
        
        return result.returncode == 0
        
    except KeyboardInterrupt:
        print("\n👋 Interfaz cerrada por el usuario")
        return True
    except Exception as e:
        print(f"❌ Error iniciando la interfaz: {str(e)}")
        return False

def main():
    """Función principal"""
    print("🔄 Sistema de Conversión de Archivos - Interfaz Robusta")
    print("=" * 60)
    
    # Verificar dependencias
    if not check_dependencies():
        print("\n❌ No se pueden iniciar las dependencias")
        return 1
    
    # Verificar mdb-tools
    mdbtools_available = check_mdbtools()
    if not mdbtools_available:
        print("\n💡 Para soporte completo de archivos Access, instala mdb-tools:")
        print("   python install_mdbtools.py")
        print("   O manualmente: brew install mdbtools (macOS)")
    
    # Verificar directorios
    if not check_directories():
        print("\n❌ Error creando directorios")
        return 1
    
    # Iniciar interfaz
    print("\n" + "=" * 60)
    success = start_interface()
    
    if success:
        print("\n✅ Interfaz cerrada correctamente")
        return 0
    else:
        print("\n❌ Error en la interfaz")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 