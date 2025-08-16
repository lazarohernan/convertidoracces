# 🚂 Guía Rápida - Railway MySQL

## 📋 Pasos para Configurar Railway:

### 1. Registro en Railway
- Ve a: https://railway.app
- Haz clic en "Start a new Project"
- Conéctate con GitHub (recomendado)

### 2. Crear Base de Datos MySQL
```bash
# En terminal, después de registrarte:
railway login
railway new
# Selecciona: "Empty Project"
railway add mysql
```

### 3. Obtener Credenciales
```bash
# Ver las variables de conexión:
railway variables
```

**Ejemplo de salida:**
```
MYSQL_URL=mysql://root:password@containers-us-west-123.railway.app:1234/railway
MYSQL_HOST=containers-us-west-123.railway.app
MYSQL_PORT=1234
MYSQL_USER=root
MYSQL_PASSWORD=tu-password-generado
MYSQL_DATABASE=railway
```

### 4. Configurar en tu App
En la aplicación web (http://localhost:8501):

1. Ve a **"📅 Conversión por Años"**
2. Expande **"🌐 Conexión a Base de Datos en Línea"**
3. Selecciona **"MySQL"**
4. Ingresa los datos de Railway:
   ```
   Host: containers-us-west-123.railway.app
   Puerto: 1234
   Usuario: root
   Contraseña: tu-password-generado
   Base de datos: railway
   ```
5. Haz clic en **"🔍 Probar Conexión"**

### 5. Usar con Nombres Personalizados
- Configurar prefijo: `at2-historico`
- Los archivos se crearán como: `at2-historico-2008`, `at2-historico-2009`, etc.
- Se subirán directamente a tu base de datos Railway

## 🎯 Ventajas de Railway:
- ✅ **500 horas/mes GRATIS**
- ✅ **URL pública automática**
- ✅ **Interface web incluida**
- ✅ **Backups automáticos**
- ✅ **SSL incluido**

## 🔗 Links Útiles:
- **Dashboard:** https://railway.app/dashboard
- **Documentación:** https://docs.railway.app
- **CLI Docs:** https://docs.railway.app/reference/cli

---

**¡Tu base de datos estará disponible públicamente 24/7!** 🌐
