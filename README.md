# 🇭🇳 Dashboard de Inteligencia de Negocios - Honduras

Un dashboard web interactivo para analizar datos de ventas en Honduras, diseñado para ser usado por cualquier persona sin conocimientos técnicos.

## 🌟 Características

### 📊 **Dashboard Completo**
- **Métricas en tiempo real** en Lempiras hondureñas
- **Filtros interactivos** por fecha, cliente y categoría
- **5 pestañas especializadas** para diferentes análisis
- **Visualizaciones profesionales** con Plotly

### 🎯 **Pestañas Disponibles**
1. **📈 Tendencias** - Análisis temporal de ventas
2. **🏆 Top Productos** - Productos más vendidos por ingresos y cantidad
3. **👑 Top Clientes** - Clientes más valiosos y análisis de frecuencia
4. **📊 Categorías** - Distribución de ventas por categoría de producto
5. **🎯 Dashboard Ejecutivo** - Resumen consolidado con insights automáticos

### 🔧 **Filtros Inteligentes**
- **Selector de fechas** para análisis por período
- **Filtro de clientes** múltiple
- **Filtro de categorías** de productos
- **Controles deslizantes** para número de elementos a mostrar

### 💡 **Insights Automáticos**
- Identificación automática de mejores días, productos y clientes
- Recomendaciones estratégicas basadas en datos
- Métricas KPI calculadas automáticamente

## 🚀 Instalación Rápida

### Opción 1: Script Automático (Recomendado)
```bash
./setup.sh
```

### Opción 2: Instalación Manual
```bash
# 1. Crear entorno virtual
python3 -m venv venv

# 2. Activar entorno virtual
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt
```

## 🎮 Cómo Usar el Dashboard

### 1. **Preparar los Datos**
- Asegúrate de tener el archivo `VENTAS 2025.CSV` en la misma carpeta
- El dashboard maneja automáticamente diferentes codificaciones de texto

### 2. **Ejecutar el Dashboard**
```bash
# Activar entorno virtual (si no está activo)
source venv/bin/activate

# Ejecutar el dashboard
streamlit run dashboard_streamlit.py
```

### 3. **Abrir en el Navegador**
- El dashboard se abrirá automáticamente en tu navegador
- Si no se abre, ve a: `http://localhost:8501`

## 🎨 Guía de Uso

### **Sidebar (Panel Lateral)**
- **📅 Filtro de Fechas**: Selecciona el período a analizar
- **👥 Filtro de Clientes**: Elige clientes específicos (opcional)
- **🏷️ Filtro de Categorías**: Selecciona categorías de productos (opcional)

### **Métricas Principales**
- **💰 Ventas Totales**: Suma total en Lempiras del período seleccionado
- **🛒 Transacciones**: Número total de ventas
- **🎯 Ticket Promedio**: Valor promedio por transacción
- **👥 Clientes Únicos**: Número de clientes diferentes
- **📦 Productos Únicos**: Número de productos diferentes vendidos

### **Pestañas de Análisis**

#### 📈 **Tendencias**
- Gráfico de líneas de ventas diarias
- Ventas por día de la semana
- Mapa de calor para identificar patrones

#### 🏆 **Top Productos**
- Control deslizante para mostrar 5-20 productos
- Ranking por ingresos y por cantidad vendida
- Tabla detallada con métricas por producto

#### 👑 **Top Clientes**
- Control deslizante para mostrar 5-20 clientes
- Análisis de frecuencia vs valor
- Distribución de clientes por rango de valor

#### 📊 **Categorías**
- Gráfico de pastel y barras por categoría
- Tabla de resumen detallado
- Métricas por categoría de producto

#### 🎯 **Dashboard Ejecutivo**
- Vista consolidada con 4 gráficos principales
- Insights automáticos destacados
- Recomendaciones estratégicas

## 🛠️ Tecnologías Utilizadas

- **Streamlit**: Framework web para aplicaciones de datos
- **Plotly**: Visualizaciones interactivas
- **Pandas**: Manipulación y análisis de datos
- **NumPy**: Computación numérica

## 📋 Requisitos del Sistema

- Python 3.7 o superior
- 4GB de RAM mínimo (recomendado 8GB)
- Navegador web moderno (Chrome, Firefox, Safari, Edge)

## 🔧 Solución de Problemas

### **Error de codificación de archivo**
- El dashboard maneja automáticamente diferentes codificaciones
- Soporta: UTF-8, Latin-1, ISO-8859-1, CP1252

### **El dashboard no carga**
- Verifica que el archivo `VENTAS 2025.CSV` esté en la carpeta correcta
- Asegúrate de que el entorno virtual esté activado
- Verifica que todas las dependencias estén instaladas

### **Problemas de rendimiento**
- Para archivos muy grandes, considera filtrar por fecha
- Cierra otras aplicaciones para liberar memoria

## 🎯 Casos de Uso

### **Para Gerentes**
- Monitoreo diario de KPIs
- Identificación de tendencias de ventas
- Análisis de clientes VIP

### **Para Vendedores**
- Identificación de productos estrella
- Análisis de clientes por valor
- Planificación de visitas comerciales

### **Para Administradores**
- Análisis financiero por período
- Optimización de inventario
- Estrategias de crecimiento

## 📞 Soporte

Para soporte técnico o mejoras, contacta con el equipo de desarrollo.

## 🔄 Actualizaciones

El dashboard se actualiza automáticamente cuando cambias los filtros. Los datos se recargan automáticamente si modificas el archivo CSV.

---

**¡Disfruta analizando tus datos de ventas con este dashboard profesional! 🚀🇭🇳**