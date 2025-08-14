#!/usr/bin/env python3
"""
Punto de entrada principal para el paquete src
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

if __name__ == "__main__":
    print("Paquete src ejecutándose correctamente")
    print(f"Directorio raíz: {root_dir}")
    print(f"Path de Python: {sys.path[:3]}")
