#!/usr/bin/env python3
"""
Sistema de Conversión de Archivos a Base de Datos
================================================

Interfaz de línea de comandos para convertir archivos CSV, Excel y JSON
a diferentes formatos de base de datos.
"""

import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich import print as rprint

from src.core.converter import FileConverter
from src.utils.config import Config
from src.utils.logger import setup_logger

# Crear aplicación Typer
app = typer.Typer(
    name="file-converter",
    help="Sistema de conversión de archivos a base de datos",
    add_completion=False
)

# Configurar Rich
console = Console()

@app.command()
def convert(
    input_file: str = typer.Argument(..., help="Archivo de entrada (CSV, Excel, JSON)"),
    output_dir: str = typer.Option("data/output/", "--output", "-o", help="Directorio de salida"),
    format: str = typer.Option("sql", "--format", "-f", help="Formato de salida (sql, sqlite)"),
    table_name: str = typer.Option(None, "--table-name", "-t", help="Nombre de la tabla"),
    batch_size: int = typer.Option(1000, "--batch-size", "-b", help="Tamaño del lote para SQL"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Modo verbose")
):
    """
    Convierte un archivo a formato de base de datos
    """
    try:
        # Configurar logging
        log_level = "DEBUG" if verbose else "INFO"
        setup_logger(log_level=log_level)
        
        # Validar archivo de entrada
        input_path = Path(input_file)
        if not input_path.exists():
            console.print(f"[red]Error: El archivo no existe: {input_file}[/red]")
            raise typer.Exit(1)
        
        # Generar nombre de tabla si no se proporciona
        if not table_name:
            table_name = input_path.stem
        
        # Crear directorio de salida
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generar ruta de salida
        if format == "sqlite":
            output_file = output_path / f"{table_name}.db"
        else:
            output_file = output_path / f"{table_name}.sql"
        
        # Mostrar información
        console.print(Panel(f"[bold blue]Conversión de Archivo[/bold blue]\n"
                           f"Entrada: {input_file}\n"
                           f"Salida: {output_file}\n"
                           f"Formato: {format}\n"
                           f"Tabla: {table_name}"))
        
        # Inicializar conversor
        converter = FileConverter()
        
        # Realizar conversión con barra de progreso
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Convirtiendo archivo...", total=None)
            
            # Convertir archivo
            result = converter.convert_file(
                input_path=str(input_path),
                output_path=str(output_file),
                output_format=format,
                table_name=table_name,
                batch_size=batch_size
            )
            
            progress.update(task, description="Conversión completada")
        
        # Mostrar resultados
        show_conversion_results(result, console)
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)

@app.command()
def batch(
    input_dir: str = typer.Argument(..., help="Directorio con archivos de entrada"),
    output_dir: str = typer.Option("data/output/", "--output", "-o", help="Directorio de salida"),
    format: str = typer.Option("sql", "--format", "-f", help="Formato de salida (sql, sqlite)"),
    table_pattern: str = typer.Option("{filename}", "--table-pattern", "-p", help="Patrón para nombres de tabla"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Modo verbose")
):
    """
    Convierte múltiples archivos en un directorio
    """
    try:
        # Configurar logging
        log_level = "DEBUG" if verbose else "INFO"
        setup_logger(log_level=log_level)
        
        # Validar directorio de entrada
        input_path = Path(input_dir)
        if not input_path.exists():
            console.print(f"[red]Error: El directorio no existe: {input_dir}[/red]")
            raise typer.Exit(1)
        
        # Crear directorio de salida
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Mostrar información
        console.print(Panel(f"[bold blue]Conversión por Lotes[/bold blue]\n"
                           f"Directorio entrada: {input_dir}\n"
                           f"Directorio salida: {output_dir}\n"
                           f"Formato: {format}\n"
                           f"Patrón tabla: {table_pattern}"))
        
        # Inicializar conversor
        converter = FileConverter()
        
        # Realizar conversión por lotes
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Procesando archivos...", total=None)
            
            # Convertir archivos
            results = converter.convert_batch(
                input_dir=str(input_path),
                output_dir=str(output_path),
                output_format=format,
                table_name_pattern=table_pattern
            )
            
            progress.update(task, description="Procesamiento completado")
        
        # Mostrar resultados
        show_batch_results(results, console)
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)

@app.command()
def info(
    file_path: str = typer.Argument(..., help="Archivo a analizar")
):
    """
    Muestra información detallada de un archivo
    """
    try:
        # Validar archivo
        input_path = Path(file_path)
        if not input_path.exists():
            console.print(f"[red]Error: El archivo no existe: {file_path}[/red]")
            raise typer.Exit(1)
        
        # Inicializar conversor
        converter = FileConverter()
        
        # Obtener información del archivo
        file_info = converter.get_file_info(str(input_path))
        
        # Mostrar información
        show_file_info(file_info, console)
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)

@app.command()
def formats():
    """
    Muestra los formatos soportados
    """
    converter = FileConverter()
    supported_formats = converter.get_supported_formats()
    
    # Crear tabla de formatos
    table = Table(title="Formatos Soportados")
    table.add_column("Tipo", style="cyan", no_wrap=True)
    table.add_column("Formatos", style="green")
    
    # Formatos de entrada
    input_formats = ", ".join(supported_formats['input'])
    table.add_row("Entrada", input_formats)
    
    # Formatos de salida
    output_formats = ", ".join(supported_formats['output'])
    table.add_row("Salida", output_formats)
    
    console.print(table)

@app.command()
def config():
    """
    Muestra la configuración actual
    """
    try:
        config = Config()
        
        # Crear tabla de configuración
        table = Table(title="Configuración Actual")
        table.add_column("Clave", style="cyan", no_wrap=True)
        table.add_column("Valor", style="green")
        
        for key, value in config.to_dict().items():
            table.add_row(key, str(value))
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error cargando configuración: {str(e)}[/red]")
        raise typer.Exit(1)

def show_conversion_results(result: dict, console: Console):
    """Muestra los resultados de una conversión"""
    table = Table(title="Resultados de Conversión")
    table.add_column("Campo", style="cyan", no_wrap=True)
    table.add_column("Valor", style="green")
    
    table.add_row("Archivo de salida", result.get('output_file', 'N/A'))
    table.add_row("Nombre de tabla", result.get('table_name', 'N/A'))
    table.add_row("Filas insertadas", str(result.get('rows_inserted', 0)))
    table.add_row("Columnas", str(result.get('columns', 0)))
    table.add_row("Estado", "✅ Exitoso" if result.get('success', False) else "❌ Falló")
    
    if 'note' in result:
        table.add_row("Nota", result['note'])
    
    console.print(table)

def show_batch_results(results: list, console: Console):
    """Muestra los resultados de conversión por lotes"""
    successful = sum(1 for r in results if r.get('success', False))
    failed = len(results) - successful
    
    table = Table(title="Resultados de Conversión por Lotes")
    table.add_column("Archivo", style="cyan", no_wrap=True)
    table.add_column("Estado", style="green")
    table.add_column("Filas", style="yellow")
    table.add_column("Error", style="red")
    
    for result in results:
        if result.get('success', False):
            status = "✅ Exitoso"
            rows = str(result.get('rows_inserted', 0))
            error = ""
        else:
            status = "❌ Falló"
            rows = "0"
            error = result.get('error', 'Error desconocido')
        
        table.add_row(
            result.get('file', 'N/A'),
            status,
            rows,
            error
        )
    
    console.print(table)
    console.print(f"\n[bold]Resumen:[/bold] {successful} exitosos, {failed} fallidos")

def show_file_info(file_info: dict, console: Console):
    """Muestra información detallada de un archivo"""
    table = Table(title="Información del Archivo")
    table.add_column("Campo", style="cyan", no_wrap=True)
    table.add_column("Valor", style="green")
    
    table.add_row("Ruta del archivo", file_info.get('file_path', 'N/A'))
    table.add_row("Tamaño (MB)", f"{file_info.get('file_size_mb', 0):.2f}")
    table.add_row("Filas", str(file_info.get('rows', 0)))
    table.add_row("Columnas", str(file_info.get('columns', 0)))
    
    # Información de columnas
    column_names = file_info.get('column_names', [])
    if column_names:
        table.add_row("Nombres de columnas", ", ".join(column_names[:5]))
        if len(column_names) > 5:
            table.add_row("", f"... y {len(column_names) - 5} más")
    
    # Tipos de datos
    data_types = file_info.get('data_types', {})
    if data_types:
        type_summary = ", ".join([f"{col}: {dtype}" for col, dtype in list(data_types.items())[:3]])
        table.add_row("Tipos de datos", type_summary)
        if len(data_types) > 3:
            table.add_row("", f"... y {len(data_types) - 3} más")
    
    console.print(table)

if __name__ == "__main__":
    app() 