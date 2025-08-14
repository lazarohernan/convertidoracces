# 🌐 Guía de Despliegue - Sistema de Conversión de Archivos

## 📋 Opciones de Despliegue

### 🚀 **1. Ngrok (Más Rápido - Recomendado para pruebas)**

**Ventajas:**
- ✅ Rápido y fácil
- ✅ No requiere cuenta
- ✅ URL pública temporal
- ✅ Ideal para demostraciones

**Cómo usar:**
```bash
# Opción 1: Usar el script automático
./deploy_web.sh ngrok

# Opción 2: Manual
# Terminal 1: Iniciar la aplicación
source venv/bin/activate
python start_robust.py

# Terminal 2: Crear túnel público
ngrok http 8501
```

**Resultado:**
- URL local: `http://localhost:8501`
- URL pública: `https://abc123.ngrok.io` (se muestra en la terminal)

---

### ☁️ **2. Streamlit Cloud (Gratuito - Recomendado para producción)**

**Ventajas:**
- ✅ Gratuito
- ✅ Siempre disponible
- ✅ Fácil de configurar
- ✅ Integración con GitHub

**Pasos:**

1. **Preparar el código:**
```bash
# Crear archivos necesarios
./deploy_web.sh cloud
```

2. **Subir a GitHub:**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/tu-usuario/tu-repositorio.git
git push -u origin main
```

3. **Desplegar en Streamlit Cloud:**
- Ve a https://share.streamlit.io
- Conecta tu cuenta de GitHub
- Selecciona tu repositorio
- Configura el archivo principal: `web_interface_robust.py`
- ¡Listo!

**Resultado:**
- URL: `https://tu-app.streamlit.app`

---

### 🚀 **3. Heroku (Pago - Para aplicaciones empresariales)**

**Ventajas:**
- ✅ Escalable
- ✅ Confiable
- ✅ Integración con bases de datos
- ✅ SSL automático

**Pasos:**

1. **Preparar para Heroku:**
```bash
./deploy_web.sh heroku
```

2. **Instalar Heroku CLI:**
```bash
# macOS
brew install heroku/brew/heroku

# O descargar desde: https://devcenter.heroku.com/articles/heroku-cli
```

3. **Desplegar:**
```bash
heroku login
heroku create tu-app-name
git push heroku main
heroku open
```

**Resultado:**
- URL: `https://tu-app-name.herokuapp.com`

---

### 🏠 **4. Local (Solo para desarrollo)**

```bash
./deploy_web.sh local
```

---

## 🔧 **Configuración Avanzada**

### **Variables de Entorno**

Para configuraciones específicas, crea un archivo `.env`:

```bash
# .env
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

### **Configuración de Streamlit**

El archivo `.streamlit/config.toml` se crea automáticamente:

```toml
[server]
port = 8501
address = "0.0.0.0"
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

---

## 📊 **Monitoreo y Logs**

### **Ver logs en tiempo real:**
```bash
# Para ngrok
tail -f streamlit.log

# Para Heroku
heroku logs --tail

# Para Streamlit Cloud
# Los logs están disponibles en el dashboard
```

### **Métricas de rendimiento:**
- **Tiempo de carga:** < 5 segundos
- **Memoria:** ~200-500 MB
- **CPU:** Bajo uso
- **Archivos soportados:** Hasta 100 MB

---

## 🛡️ **Seguridad**

### **Recomendaciones:**
1. **No compartir archivos sensibles** en versiones públicas
2. **Usar autenticación** para aplicaciones en producción
3. **Limitar acceso** a archivos de entrada/salida
4. **Monitorear logs** regularmente

### **Configuración de seguridad:**
```bash
# Habilitar autenticación básica
export STREAMLIT_AUTHENTICATION=true
export STREAMLIT_USERNAME=admin
export STREAMLIT_PASSWORD=tu-password-seguro
```

---

## 🚨 **Solución de Problemas**

### **Error: Puerto ocupado**
```bash
# Encontrar proceso
lsof -i :8501

# Terminar proceso
kill -9 <PID>
```

### **Error: Ngrok no funciona**
```bash
# Verificar instalación
ngrok version

# Reinstalar
brew uninstall ngrok
brew install ngrok
```

### **Error: Dependencias faltantes**
```bash
# Reinstalar dependencias
pip install -r requirements.txt

# Verificar versión de Python
python --version  # Debe ser 3.8+
```

---

## 📞 **Soporte**

### **Comandos útiles:**
```bash
# Ver estado de la aplicación
./deploy_web.sh help

# Verificar dependencias
pip list | grep streamlit

# Limpiar caché
rm -rf ~/.streamlit/

# Reiniciar aplicación
pkill -f streamlit
./deploy_web.sh local
```

### **Enlaces útiles:**
- 📚 [Documentación de Streamlit](https://docs.streamlit.io/)
- 🌐 [Streamlit Cloud](https://share.streamlit.io/)
- 🚀 [Heroku](https://devcenter.heroku.com/)
- 🔗 [Ngrok](https://ngrok.com/docs)

---

## 🎯 **Recomendación Final**

**Para pruebas rápidas:** Usa **Ngrok**
**Para aplicaciones públicas:** Usa **Streamlit Cloud**
**Para aplicaciones empresariales:** Usa **Heroku**

¡Tu aplicación está lista para ser compartida con el mundo! 🌍 