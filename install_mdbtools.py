#!/usr/bin/env python3
"""
Script para instalar mdb-tools automáticamente
============================================

Instala mdb-tools en diferentes sistemas operativos para permitir
la lectura de archivos Microsoft Access.
"""

import subprocess
import platform
import sys
import os

def check_mdbtools():
    """Verifica si mdb-tools está instalado"""
    try:
        result = subprocess.run(['mdb-tables', '--version'], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        return False

def install_mdbtools_macos():
    """Instala mdb-tools en macOS usando Homebrew"""
    print("🍎 Instalando mdb-tools en macOS...")
    
    try:
        # Verificar si Homebrew está instalado
        result = subprocess.run(['brew', '--version'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            print("❌ Homebrew no está instalado")
            print("💡 Instala Homebrew primero: https://brew.sh")
            return False
        
        # Instalar mdb-tools
        print("📦 Instalando mdb-tools...")
        result = subprocess.run(['brew', 'install', 'mdbtools'], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ mdb-tools instalado exitosamente")
            return True
        else:
            print(f"❌ Error instalando mdb-tools: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout durante la instalación")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def install_mdbtools_linux():
    """Instala mdb-tools en Linux usando apt-get"""
    print("🐧 Instalando mdb-tools en Linux...")
    
    try:
        # Actualizar repositorios
        print("🔄 Actualizando repositorios...")
        result = subprocess.run(['sudo', 'apt-get', 'update'], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            print(f"❌ Error actualizando repositorios: {result.stderr}")
            return False
        
        # Instalar mdb-tools
        print("📦 Instalando mdb-tools...")
        result = subprocess.run(['sudo', 'apt-get', 'install', '-y', 'mdbtools'], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ mdb-tools instalado exitosamente")
            return True
        else:
            print(f"❌ Error instalando mdb-tools: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout durante la instalación")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def install_mdbtools_windows():
    """Instala mdb-tools en Windows usando Chocolatey"""
    print("🪟 Instalando mdb-tools en Windows...")
    
    try:
        # Verificar si Chocolatey está instalado
        result = subprocess.run(['choco', '--version'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            print("❌ Chocolatey no está instalado")
            print("💡 Instala Chocolatey primero: https://chocolatey.org/install")
            return False
        
        # Instalar mdb-tools
        print("📦 Instalando mdb-tools...")
        result = subprocess.run(['choco', 'install', 'mdbtools', '-y'], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ mdb-tools instalado exitosamente")
            return True
        else:
            print(f"❌ Error instalando mdb-tools: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout durante la instalación")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Función principal"""
    print("🚀 Instalador de mdb-tools")
    print("=" * 40)
    
    # Verificar si ya está instalado
    if check_mdbtools():
        print("✅ mdb-tools ya está instalado")
        print("🎉 Puedes usar archivos Access ahora!")
        return True
    
    # Detectar sistema operativo
    system = platform.system().lower()
    print(f"🖥️ Sistema detectado: {system}")
    
    # Instalar según el sistema
    success = False
    
    if system == "darwin":  # macOS
        success = install_mdbtools_macos()
    elif system == "linux":
        success = install_mdbtools_linux()
    elif system == "windows":
        success = install_mdbtools_windows()
    else:
        print(f"❌ Sistema no soportado: {system}")
        return False
    
    if success:
        # Verificar instalación
        if check_mdbtools():
            print("\n🎉 ¡Instalación completada exitosamente!")
            print("✅ mdb-tools está listo para usar")
            print("🔄 Ahora puedes convertir archivos Access desde la interfaz web")
            return True
        else:
            print("\n⚠️ Instalación completada pero mdb-tools no se detecta")
            print("💡 Intenta reiniciar la terminal o el sistema")
            return False
    else:
        print("\n❌ La instalación falló")
        print("💡 Instrucciones manuales:")
        
        if system == "darwin":
            print("   brew install mdbtools")
        elif system == "linux":
            print("   sudo apt-get install mdbtools")
        elif system == "windows":
            print("   choco install mdbtools")
        
        return False

if __name__ == "__main__":
    main() 