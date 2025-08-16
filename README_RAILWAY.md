# Railway Deployment - Access to MySQL Converter

## Aplicación Web para Visualizar Base de Datos MySQL

Esta aplicación permite visualizar públicamente los datos convertidos desde Access a MySQL en Railway.

### Archivos principales:
- `railway_viewer.py` - Aplicación web Streamlit para visualizar datos
- `Procfile` - Configuración de deployment para Railway
- `requirements.txt` - Dependencias Python
- `src/` - Código fuente del convertidor

### Variables de entorno necesarias:
- `MYSQLHOST` - Host de la base de datos
- `MYSQLPORT` - Puerto de la base de datos  
- `MYSQLUSER` - Usuario de la base de datos
- `MYSQLPASSWORD` - Contraseña de la base de datos
- `MYSQLDATABASE` - Nombre de la base de datos

### Deployment:
Railway detecta automáticamente la aplicación Python y usa el Procfile para ejecutar Streamlit.
