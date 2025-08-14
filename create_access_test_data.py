#!/usr/bin/env python3
"""
Script para crear datos de prueba que se pueden usar para crear archivos Access
"""

import pandas as pd
import random
from datetime import datetime, timedelta

def create_test_data():
    """Crear datos de prueba para diferentes tipos de archivos"""
    
    # Datos de clientes
    clientes_data = {
        'ID': range(1, 21),
        'Nombre': [
            'Juan Pérez', 'María García', 'Carlos López', 'Ana Martínez', 'Luis Rodríguez',
            'Carmen Sánchez', 'Jorge Torres', 'Isabel Flores', 'Roberto Vargas', 'Patricia Ruiz',
            'Miguel Herrera', 'Sofia Morales', 'Diego Castro', 'Valeria Jiménez', 'Fernando Silva',
            'Camila Rojas', 'Andrés Mendoza', 'Daniela Ortiz', 'Ricardo Guzmán', 'Natalia Vega'
        ],
        'Email': [
            'juan.perez@email.com', 'maria.garcia@email.com', 'carlos.lopez@email.com',
            'ana.martinez@email.com', 'luis.rodriguez@email.com', 'carmen.sanchez@email.com',
            'jorge.torres@email.com', 'isabel.flores@email.com', 'roberto.vargas@email.com',
            'patricia.ruiz@email.com', 'miguel.herrera@email.com', 'sofia.morales@email.com',
            'diego.castro@email.com', 'valeria.jimenez@email.com', 'fernando.silva@email.com',
            'camila.rojas@email.com', 'andres.mendoza@email.com', 'daniela.ortiz@email.com',
            'ricardo.guzman@email.com', 'natalia.vega@email.com'
        ],
        'Telefono': [
            '+1-555-0101', '+1-555-0102', '+1-555-0103', '+1-555-0104', '+1-555-0105',
            '+1-555-0106', '+1-555-0107', '+1-555-0108', '+1-555-0109', '+1-555-0110',
            '+1-555-0111', '+1-555-0112', '+1-555-0113', '+1-555-0114', '+1-555-0115',
            '+1-555-0116', '+1-555-0117', '+1-555-0118', '+1-555-0119', '+1-555-0120'
        ],
        'Ciudad': [
            'Madrid', 'Barcelona', 'Valencia', 'Sevilla', 'Zaragoza',
            'Málaga', 'Murcia', 'Palma', 'Las Palmas', 'Bilbao',
            'Alicante', 'Córdoba', 'Valladolid', 'Vigo', 'Gijón',
            'L\'Hospitalet', 'A Coruña', 'Vitoria', 'Granada', 'Tarrasa'
        ],
        'Fecha_Registro': [
            datetime.now() - timedelta(days=random.randint(1, 365)) for _ in range(20)
        ]
    }
    
    # Datos de productos
    productos_data = {
        'ID': range(1, 16),
        'Nombre': [
            'Laptop HP Pavilion', 'iPhone 15 Pro', 'Samsung Galaxy S24', 'MacBook Air M2',
            'iPad Pro 12.9"', 'Dell XPS 13', 'Sony WH-1000XM5', 'Apple Watch Series 9',
            'Nintendo Switch OLED', 'PlayStation 5', 'Xbox Series X', 'Canon EOS R6',
            'DJI Mini 3 Pro', 'GoPro Hero 11', 'Samsung QLED 4K TV'
        ],
        'Categoria': [
            'Computadoras', 'Smartphones', 'Smartphones', 'Computadoras',
            'Tablets', 'Computadoras', 'Audio', 'Wearables',
            'Gaming', 'Gaming', 'Gaming', 'Fotografía',
            'Drones', 'Fotografía', 'TV'
        ],
        'Precio': [
            899.99, 1199.99, 1099.99, 1299.99, 1099.99,
            999.99, 349.99, 399.99, 349.99, 499.99,
            499.99, 2499.99, 759.99, 399.99, 1299.99
        ],
        'Stock': [
            random.randint(5, 50) for _ in range(15)
        ],
        'Disponible': [
            random.choice([True, False]) for _ in range(15)
        ]
    }
    
    # Datos de ventas
    ventas_data = {
        'ID_Venta': range(1, 31),
        'ID_Cliente': [random.randint(1, 20) for _ in range(30)],
        'ID_Producto': [random.randint(1, 15) for _ in range(30)],
        'Cantidad': [random.randint(1, 5) for _ in range(30)],
        'Precio_Unitario': [round(random.uniform(100, 2000), 2) for _ in range(30)],
        'Fecha_Venta': [
            datetime.now() - timedelta(days=random.randint(1, 90)) for _ in range(30)
        ],
        'Metodo_Pago': [
            random.choice(['Tarjeta', 'Efectivo', 'Transferencia', 'PayPal']) for _ in range(30)
        ]
    }
    
    # Crear DataFrames
    df_clientes = pd.DataFrame(clientes_data)
    df_productos = pd.DataFrame(productos_data)
    df_ventas = pd.DataFrame(ventas_data)
    
    return df_clientes, df_productos, df_ventas

def save_test_files():
    """Guardar archivos de prueba en diferentes formatos"""
    
    df_clientes, df_productos, df_ventas = create_test_data()
    
    # Crear directorio si no existe
    import os
    os.makedirs('data/input', exist_ok=True)
    
    # Guardar como CSV
    df_clientes.to_csv('data/input/clientes_test.csv', index=False)
    df_productos.to_csv('data/input/productos_test.csv', index=False)
    df_ventas.to_csv('data/input/ventas_test.csv', index=False)
    
    # Guardar como Excel
    with pd.ExcelWriter('data/input/datos_test.xlsx', engine='openpyxl') as writer:
        df_clientes.to_excel(writer, sheet_name='Clientes', index=False)
        df_productos.to_excel(writer, sheet_name='Productos', index=False)
        df_ventas.to_excel(writer, sheet_name='Ventas', index=False)
    
    # Guardar como JSON
    df_clientes.to_json('data/input/clientes_test.json', orient='records', indent=2)
    df_productos.to_json('data/input/productos_test.json', orient='records', indent=2)
    df_ventas.to_json('data/input/ventas_test.json', orient='records', indent=2)
    
    print("✅ Archivos de prueba creados exitosamente!")
    print("\n📁 Archivos generados:")
    print("• data/input/clientes_test.csv")
    print("• data/input/productos_test.csv") 
    print("• data/input/ventas_test.csv")
    print("• data/input/datos_test.xlsx")
    print("• data/input/clientes_test.json")
    print("• data/input/productos_test.json")
    print("• data/input/ventas_test.json")
    
    print("\n💡 Para crear un archivo Access:")
    print("1. Abre Microsoft Access")
    print("2. Crea una nueva base de datos")
    print("3. Importa estos archivos CSV/Excel")
    print("4. Guarda como .accdb")

if __name__ == "__main__":
    save_test_files() 