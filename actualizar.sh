#!/bin/bash

# Evitar que el script falle silenciosamente
set -e

echo "=================================================="
echo "       INICIANDO ACTUALIZACIÓN DE ALGEBRAX        "
echo "=================================================="
echo ""

# 1. Obtener cambios del repositorio
echo "➡️ [1/3] Obteniendo los últimos cambios de GitHub..."
git pull
echo "✅ Cambios descargados correctamente."
echo ""

# 2. Actualizar y Compilar el Frontend
echo "➡️ [2/3] Instalando dependencias y compilando Frontend..."
cd frontend

# Ejecutar npm install por si hay nuevas dependencias
npm install

# Compilar para producción
npm run build
cd ..
echo "✅ Frontend compilado exitosamente en 'frontend/dist'."
echo ""

# 3. Actualizar dependencias del Backend (opcional/preventivo)
echo "➡️ [3/3] Verificando dependencias del Backend..."
if [ -d "backend/venv" ]; then
    # Activar entorno virtual de Linux
    source backend/venv/bin/activate
    pip install -r backend/requirements.txt
    deactivate
    echo "✅ Entorno virtual actualizado."
elif [ -d "backend/env" ]; then
    source backend/env/bin/activate
    pip install -r backend/requirements.txt
    deactivate
    echo "✅ Entorno virtual actualizado."
else
    echo "⚠️ No se detectó entorno virtual en backend/venv o backend/env. Si usas uno global, asegúrate de tener al día las dependencias."
fi

echo ""
echo "=================================================="
echo "   ¡PROCESO DE ACTUALIZACIÓN COMPLETADO CON ÉXITO! "
echo "=================================================="
echo "Nota: Si usas PM2 o algún servicio de sistema (systemd)"
echo "para correr FastAPI o Node, recuerda reiniciarlo si"
echo "hiciste cambios en el código de backend o de servicio."
echo "=================================================="
