# 🌐 Guía Rápida para Compartir tu Aplicación Web

## 🚀 **Opción 1: LocalTunnel (Más Fácil - Sin Registro)**

### **Paso 1: Instalar LocalTunnel**
```bash
npm install -g localtunnel
```

### **Paso 2: Compartir la Aplicación**
```bash
# Opción A: Usar el script automático
./share_app.sh

# Opción B: Manual
# 1. Asegúrate de que la aplicación esté corriendo
source venv/bin/activate
python start_robust.py

# 2. En otra terminal, crear el túnel
lt --port 8501
```

### **Resultado:**
- URL local: `http://localhost:8501`
- URL pública: `https://abc123.loca.lt` (se muestra en la terminal)

---

## 🔧 **Opción 2: Ngrok (Requiere Registro)**

### **Paso 1: Registrarse en Ngrok**
1. Ve a: https://dashboard.ngrok.com/signup
2. Regístrate (gratis)
3. Obtén tu authtoken

### **Paso 2: Configurar Ngrok**
```bash
ngrok config add-authtoken TU_TOKEN_AQUI
```

### **Paso 3: Compartir**
```bash
ngrok http 8501
```

---

## ☁️ **Opción 3: Streamlit Cloud (Permanente)**

### **Paso 1: Preparar el Código**
```bash
# Crear requirements.txt
cat > requirements.txt << EOF
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.15.0
altair>=5.0.0
pyodbc>=4.0.39
sqlalchemy>=2.0.0
openpyxl>=3.1.0
xlrd>=2.0.1
EOF
```

### **Paso 2: Subir a GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git push -u origin main
```

### **Paso 3: Desplegar en Streamlit Cloud**
1. Ve a: https://share.streamlit.io
2. Conecta tu repositorio de GitHub
3. Configura el archivo principal: `web_interface_robust.py`
4. ¡Listo! Tu app estará disponible en `https://tu-app.streamlit.app`

---

## 📋 **Comandos Útiles**

### **Verificar si la aplicación está corriendo:**
```bash
ps aux | grep streamlit
```

### **Detener la aplicación:**
```bash
pkill -f streamlit
```

### **Ver logs de la aplicación:**
```bash
tail -f streamlit.log
```

### **Probar la URL pública:**
```bash
curl -I https://tu-url-publica.loca.lt
```

---

## ⚠️ **Consideraciones de Seguridad**

### **Para Túneles Temporales (LocalTunnel/Ngrok):**
- ✅ Perfecto para demostraciones
- ✅ No compartas archivos sensibles
- ✅ Cierra el túnel cuando termines
- ⚠️ Cualquier persona con el enlace puede acceder

### **Para Despliegues Permanentes (Streamlit Cloud):**
- ✅ Más seguro para uso público
- ✅ Control de acceso configurable
- ✅ Siempre disponible
- ⚠️ Requiere gestión de archivos sensibles

---

## 🎯 **Recomendación**

**Para uso temporal/demostraciones:** Usa LocalTunnel
**Para uso permanente/público:** Usa Streamlit Cloud 