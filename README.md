# 🔄 Convertidor de Access a Base de Datos

Un sistema robusto y moderno para convertir archivos de Microsoft Access (.mdb) a diferentes formatos de base de datos, con interfaz web intuitiva y soporte para múltiples formatos de salida.

## ✨ Características Principales

- **🔄 Conversión Robusta**: Soporte completo para archivos Access (.mdb) usando mdb-tools
- **🌐 Interfaz Web Moderna**: Interfaz gráfica con Streamlit, responsive y fácil de usar
- **📊 Múltiples Formatos**: Exporta a SQL, SQLite, CSV, Excel, JSON
- **🚀 Integración Supabase**: Soporte nativo para bases de datos en la nube
- **📱 Multiplataforma**: Funciona en Windows, macOS y Linux
- **⚡ Alto Rendimiento**: Procesamiento optimizado para archivos grandes

## 🚀 Instalación Rápida

### Prerrequisitos
- Python 3.8+
- mdb-tools (para lectura de archivos Access)

### Instalación
```bash
# Clonar el repositorio
git clone https://github.com/lazarohernan/convertidoracces.git
cd convertidoracces

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Instalar mdb-tools
# macOS:
brew install mdbtools
# Ubuntu/Debian:
sudo apt-get install mdbtools
# Windows: Descargar desde https://github.com/mdbtools/mdbtools/releases
```

## 🎯 Uso

### Interfaz Web (Recomendado)
```bash
# Lanzar interfaz web
streamlit run web_interface_robust.py

# Acceder en: http://localhost:8501
```

### Línea de Comandos
```bash
# Convertir archivo Access a SQL
python main.py convert archivo.mdb --format sql --output-dir output/

# Convertir a SQLite
python main.py convert archivo.mdb --format sqlite --table-name mi_tabla

# Modo verbose
python main.py convert archivo.mdb --verbose
```

## 📁 Estructura del Proyecto

```
convertidoracces/
├── src/
│   ├── core/           # Lógica principal de conversión
│   ├── readers/        # Lectores de archivos (Access, CSV, Excel, JSON)
│   ├── writers/        # Escritores de salida (SQL, SQLite, Supabase)
│   └── utils/          # Utilidades y configuración
├── data/               # Archivos de entrada y salida
├── config/             # Configuraciones
├── web_interface_robust.py  # Interfaz web principal
├── main.py             # CLI principal
└── requirements.txt    # Dependencias Python
```

## 🔧 Configuración

### Variables de Entorno
```bash
# Copiar archivo de ejemplo
cp env.example .env

# Configurar variables
SUPABASE_URL=tu_url_supabase
SUPABASE_KEY=tu_clave_supabase
```

### Configuración de Supabase
```python
# En config/settings.py
SUPABASE_CONFIG = {
    "url": "https://tu-proyecto.supabase.co",
    "key": "tu-anon-key"
}
```

## 📊 Formatos Soportados

### Entrada
- ✅ **Microsoft Access (.mdb)** - Soporte completo con mdb-tools
- ✅ **CSV** - Con detección automática de codificación
- ✅ **Excel (.xlsx, .xls)** - Múltiples hojas
- ✅ **JSON** - Arrays y objetos anidados

### Salida
- ✅ **SQL** - Scripts SQL estándar
- ✅ **SQLite** - Base de datos local
- ✅ **CSV** - Con opciones de codificación
- ✅ **Excel** - Múltiples formatos
- ✅ **JSON** - Estructurado y validado
- ✅ **Supabase** - Base de datos en la nube

## 🌐 Interfaz Web

La interfaz web incluye:

- **📁 Gestor de Archivos**: Subida y selección de archivos
- **🔍 Vista Previa**: Exploración de datos antes de la conversión
- **⚙️ Configuración**: Opciones avanzadas de conversión
- **📊 Visualizaciones**: Gráficos y estadísticas de datos
- **📈 Historial**: Seguimiento de conversiones realizadas
- **🚀 Exportación**: Múltiples formatos de salida

## 🚀 Despliegue

### Local
```bash
# Script de inicio rápido
./compartir_simple.sh

# O manualmente
streamlit run web_interface_robust.py --server.port 8501
```

### Producción
```bash
# Script de despliegue
./deploy_web.sh

# Con ngrok para acceso externo
ngrok http 8501
```

## 🧪 Testing

```bash
# Ejecutar tests
python -m pytest tests/

# Test específico
python test_converter.py
```

## 📝 Logs

```bash
# Ver logs en tiempo real
tail -f streamlit.log

# Logs de conversión
tail -f logs/conversion.log
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🆘 Soporte

- **Issues**: [GitHub Issues](https://github.com/lazarohernan/convertidoracces/issues)
- **Documentación**: [Wiki del Proyecto](https://github.com/lazarohernan/convertidoracces/wiki)
- **Contacto**: Abre un issue para consultas

## 🎉 Agradecimientos

- **mdb-tools**: Por el soporte robusto de archivos Access
- **Streamlit**: Por la interfaz web moderna
- **Pandas**: Por el procesamiento eficiente de datos
- **Supabase**: Por la infraestructura de base de datos en la nube

---

⭐ **¡Si te gusta este proyecto, dale una estrella en GitHub!** 