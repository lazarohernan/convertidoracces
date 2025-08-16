# Guía de Configuración de Bases de Datos En Línea

Esta guía te ayudará a configurar conexiones a bases de datos en línea para usar con el sistema de conversión de archivos.

## 🗄️ MySQL

### Proveedores Recomendados

#### 1. PlanetScale (Recomendado para MySQL)
- **Plan gratuito:** 5GB, 1 millón de lecturas/mes
- **URL:** https://planetscale.com
- **Configuración:**
  ```
  Host: aws.connect.psdb.cloud
  Puerto: 3306
  Base de datos: nombre-de-tu-base-datos
  Usuario: tu-usuario
  Contraseña: tu-contraseña
  ```

#### 2. Railway
- **Plan gratuito:** 500 horas/mes, 1GB RAM
- **URL:** https://railway.app
- **Configuración:**
  ```
  Host: containers-us-west-xxx.railway.app
  Puerto: xxxx
  Base de datos: railway
  Usuario: root
  Contraseña: tu-contraseña-generada
  ```

#### 3. DigitalOcean Managed Database
- **Plan desde $15/mes** (sin plan gratuito)
- **URL:** https://digitalocean.com
- **Configuración:**
  ```
  Host: db-mysql-xxx-do-user-xxx.b.db.ondigitalocean.com
  Puerto: 25060
  Base de datos: defaultdb
  Usuario: doadmin
  Contraseña: tu-contraseña
  ```

## 🐘 PostgreSQL

### Proveedores Recomendados

#### 1. Supabase (Recomendado para PostgreSQL)
- **Plan gratuito:** 500MB base de datos, 2GB transferencia
- **URL:** https://supabase.com
- **Configuración:**
  ```
  Host: db.xxx.supabase.co
  Puerto: 5432
  Base de datos: postgres
  Usuario: postgres
  Contraseña: tu-contraseña
  ```

#### 2. Neon
- **Plan gratuito:** 512MB, 3GB transferencia/mes
- **URL:** https://neon.tech
- **Configuración:**
  ```
  Host: xxx-xxx.us-east-2.aws.neon.tech
  Puerto: 5432
  Base de datos: neondb
  Usuario: tu-usuario
  Contraseña: tu-contraseña
  ```

#### 3. ElephantSQL
- **Plan gratuito:** 20MB
- **URL:** https://elephantsql.com
- **Configuración:**
  ```
  Host: stampy.db.elephantsql.com
  Puerto: 5432
  Base de datos: tu-usuario
  Usuario: tu-usuario
  Contraseña: tu-contraseña
  ```

## ⚡ Supabase (Configuración Especial)

Para Supabase necesitas:
1. **URL del proyecto:** https://tuproyecto.supabase.co
2. **Clave anónima (anon key):** Disponible en Settings > API

```
URL: https://tuproyecto.supabase.co
Clave: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 🚀 Pasos para Configurar Cualquier Proveedor

### 1. Crear una Cuenta
- Regístrate en el proveedor elegido
- Verifica tu email si es necesario

### 2. Crear una Base de Datos
- Sigue el proceso de creación del proveedor
- Guarda las credenciales de conexión

### 3. Configurar la Conexión en la App
- Ve a "📅 Conversión por Años"
- Expande "🌐 Conexión a Base de Datos en Línea"
- Selecciona el tipo de base de datos
- Ingresa las credenciales
- Haz clic en "🔍 Probar Conexión"

### 4. Convertir y Subir
- Configura los nombres de archivo como desees
- Por ejemplo: `at2-historico-{year}` → `at2-historico-2008`
- Inicia la conversión

## 💡 Consejos de Uso

### Nombres Recomendados para Archivos por Año
```
at2-historico-{year}     → at2-historico-2008, at2-historico-2009
datos-{year}-v1          → datos-2008-v1, datos-2009-v1
backup-mensual-{year}    → backup-mensual-2008, backup-mensual-2009
bdm-{year}-final         → bdm-2008-final, bdm-2009-final
```

### Seguridad
- ⚠️ **Nunca compartas tus credenciales de base de datos**
- 🔐 Usa contraseñas fuertes y únicas
- 🛡️ Considera usar variables de entorno para producción

### Rendimiento
- 📊 Los archivos grandes pueden tardar más en subirse
- 🔄 Usa el procesamiento por chunks para archivos >500MB
- ⏰ Las bases de datos gratuitas pueden tener límites de velocidad

## 🆘 Solución de Problemas

### Error de Conexión
```
❌ Error de conexión: Can't connect to MySQL server
```
**Soluciones:**
- Verifica que el host y puerto sean correctos
- Asegúrate de que la base de datos esté activa
- Revisa que las credenciales sean válidas

### Error de Permisos
```
❌ Access denied for user 'usuario'@'host'
```
**Soluciones:**
- Verifica usuario y contraseña
- Asegúrate de tener permisos de escritura
- Contacta al soporte del proveedor

### Límites Excedidos
```
❌ Too many connections / Storage limit exceeded
```
**Soluciones:**
- Espera unos minutos y vuelve a intentar
- Considera actualizar a un plan de pago
- Divide el archivo en partes más pequeñas

---

## 🎯 ¡Ya estás listo!

Con esta guía puedes conectar tu sistema a cualquier base de datos en línea y comenzar a subir tus archivos Access convertidos directamente a la nube. 

**Recuerda:** Todos los proveedores mencionados ofrecen planes gratuitos perfectos para probar el sistema. ¡Comienza hoy mismo!
