#!/usr/bin/env python3
"""
Script para limpiar archivos SQL divididos y prepararlos para inserción
"""

import sys
import os
import re

def clean_sql_file(input_file, output_file):
    """Limpia un archivo SQL dividido para inserción"""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Normalizar saltos de línea y espacios
    content = content.replace('\r', '')
    content = content.replace('\n', '')
    
    # Ubicar la sección de VALUES
    idx = content.upper().find('VALUES')
    if idx != -1:
        values_part = content[idx + len('VALUES'):]
    else:
        # Si no hay VALUES, asumir que el archivo contiene solo tuplas
        values_part = content
    
    # Extraer todas las tuplas (…)
    tuples = re.findall(r"\(([^)]*)\)", values_part)
    if not tuples:
        print("Error: No se encontraron tuplas de valores")
        sys.exit(1)
    
    # Reconstruir INSERT único
    cleaned_lines = []
    for t in tuples:
        cleaned_lines.append(f"({t.strip().rstrip(';')})")
    
    sql = "INSERT INTO `AT2_BDT_MENSUAL_DETALLE_2008` VALUES\n" + ",\n".join(cleaned_lines) + ";\n"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(sql)
    
    print(f"Archivo limpiado: {output_file}")
    print(f"Tuplas procesadas: {len(cleaned_lines)}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python clean_sql_file.py <archivo_entrada> <archivo_salida>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not os.path.exists(input_file):
        print(f"Error: El archivo {input_file} no existe")
        sys.exit(1)
    
    clean_sql_file(input_file, output_file)
