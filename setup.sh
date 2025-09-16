#!/bin/bash

echo "🇭🇳 Configurando Dashboard de Ventas - Honduras"
echo "================================================"

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado. Por favor instala Python3 primero."
    exit 1
fi

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "🔧 Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
echo "🔄 Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ ¡Instalación completada!"
echo ""
echo "🚀 Para ejecutar el dashboard:"
echo "   1. Activar entorno: source venv/bin/activate"
echo "   2. Ejecutar dashboard: streamlit run dashboard_streamlit.py"
echo ""
echo "📂 Asegúrate de tener el archivo 'VENTAS 2025.CSV' en esta carpeta."