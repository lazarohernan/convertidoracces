#!/usr/bin/env python3
"""
Script de prueba para la funcionalidad de conversión por año
"""

import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.converter import FileConverter
from src.readers.robust_access_reader import RobustAccessReader

def test_year_detection():
    """Prueba la detección de años disponibles"""
    print("🧪 Probando detección de años...")
    
    try:
        # Archivo de prueba
        test_file = "data/input/ATA2/AT2-2008-2011/AT2.mdb"
        
        if not Path(test_file).exists():
            print(f"❌ Archivo de prueba no encontrado: {test_file}")
            return False
        
        # Crear lector
        reader = RobustAccessReader()
        
        # Obtener resumen de años
        print(f"📁 Analizando archivo: {test_file}")
        year_summary = reader.get_year_summary(test_file)
        
        print(f"✅ Resumen obtenido:")
        print(f"   - Archivo: {year_summary['file_path']}")
        print(f"   - Tamaño: {year_summary['file_size_mb']:.1f} MB")
        print(f"   - Tablas: {len(year_summary['tables'])}")
        
        for table_name, table_info in year_summary['tables'].items():
            print(f"   📊 Tabla: {table_name}")
            print(f"      - Años disponibles: {table_info['year_range']}")
            print(f"      - Total de años: {table_info['year_count']}")
            print(f"      - Años específicos: {', '.join(map(str, table_info['available_years']))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en detección de años: {str(e)}")
        return False

def test_year_filtering():
    """Prueba el filtrado de datos por año"""
    print("\n🧪 Probando filtrado por año...")
    
    try:
        test_file = "data/input/ATA2/AT2-2008-2011/AT2.mdb"
        reader = RobustAccessReader()
        
        # Obtener años disponibles
        year_summary = reader.get_year_summary(test_file)
        
        if not year_summary['tables']:
            print("❌ No hay tablas disponibles para probar")
            return False
        
        # Probar con la primera tabla
        table_name = list(year_summary['tables'].keys())[0]
        available_years = year_summary['tables'][table_name]['available_years']
        
        if not available_years:
            print("❌ No hay años disponibles para probar")
            return False
        
        # Probar con el primer año disponible
        test_year = available_years[0]
        print(f"📊 Probando tabla: {table_name}, año: {test_year}")
        
        # Leer datos del año específico
        df = reader.read_by_year(test_file, table_name, test_year)
        
        if df.empty:
            print(f"❌ No se obtuvieron datos para año {test_year}")
            return False
        
        print(f"✅ Datos filtrados exitosamente:")
        print(f"   - Filas obtenidas: {len(df):,}")
        print(f"   - Columnas: {len(df.columns)}")
        print(f"   - Años únicos en datos: {df['N_ANIO'].unique()}")
        
        # Verificar que solo hay datos del año especificado
        if len(df['N_ANIO'].unique()) == 1 and df['N_ANIO'].unique()[0] == test_year:
            print(f"✅ Filtrado correcto: solo datos del año {test_year}")
        else:
            print(f"⚠️ Advertencia: se encontraron años adicionales: {df['N_ANIO'].unique()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en filtrado por año: {str(e)}")
        return False

def test_year_conversion():
    """Prueba la conversión completa por año"""
    print("\n🧪 Probando conversión por año...")
    
    try:
        test_file = "data/input/ATA2/AT2-2008-2011/AT2.mdb"
        converter = FileConverter()
        
        print(f"🔄 Iniciando conversión por año...")
        print(f"   - Archivo: {test_file}")
        print(f"   - Formato: SQL")
        
        # Convertir por año
        result = converter.convert_access_by_year(
            input_path=test_file,
            output_format="sql"
        )
        
        print(f"✅ Conversión por año completada!")
        print(f"   - Directorio de salida: {result['output_directory']}")
        print(f"   - Total de tablas: {result['total_tables']}")
        print(f"   - Conversiones realizadas: {len(result['conversions_by_year'])}")
        
        # Contar éxitos y errores
        successful = sum(1 for conv in result['conversions_by_year'].values() if conv['status'] == 'success')
        errors = sum(1 for conv in result['conversions_by_year'].values() if conv['status'] == 'error')
        
        print(f"   - ✅ Exitosas: {successful}")
        print(f"   - ❌ Errores: {errors}")
        
        # Mostrar detalles de conversiones exitosas
        print("\n📊 Detalles de conversiones:")
        for conv_key, conv_info in result['conversions_by_year'].items():
            if conv_info['status'] == 'success':
                print(f"   ✅ {conv_info['table']} - Año {conv_info['year']}: {conv_info['rows_converted']:,} filas")
            else:
                print(f"   ❌ {conv_info['table']} - Año {conv_info['year']}: {conv_info['error']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en conversión por año: {str(e)}")
        return False

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas de conversión por año")
    print("=" * 50)
    
    tests = [
        ("Detección de años", test_year_detection),
        ("Filtrado por año", test_year_filtering),
        ("Conversión por año", test_year_conversion)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Ejecutando: {test_name}")
        try:
            success = test_func()
            results.append((test_name, success))
            if success:
                print(f"✅ {test_name}: PASÓ")
            else:
                print(f"❌ {test_name}: FALLÓ")
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {str(e)}")
            results.append((test_name, False))
    
    # Resumen final
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASÓ" if success else "❌ FALLÓ"
        print(f"   {test_name}: {status}")
    
    print(f"\n🎯 Resultado final: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! La funcionalidad está funcionando correctamente.")
    else:
        print("⚠️ Algunas pruebas fallaron. Revisa los errores arriba.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

