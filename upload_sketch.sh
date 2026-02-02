#!/bin/bash
# Script para compilar y cargar sketch en Arduino usando Arduino-CLI

set -e

PROJECT_DIR="/Users/rodrigofigueroa/Documents/Coding/Sensores_Arduino"
SKETCH_PATH="$PROJECT_DIR/button_sketch"
FQBN="arduino:avr:uno"  # Arduino Uno

echo "=========================================="
echo "Arduino Sketch Uploader"
echo "=========================================="
echo

# 1. Buscar Arduino conectado
echo "🔍 Buscando Arduino conectado..."
PORT=$(ls /dev/cu.usbserial-* 2>/dev/null | head -1)

if [ -z "$PORT" ]; then
    echo "❌ No se encontró Arduino conectado"
    exit 1
fi
echo "✅ Arduino encontrado en: $PORT"
echo

# 2. Compilar sketch
echo "🔨 Compilando sketch..."
arduino-cli compile --fqbn $FQBN "$SKETCH_PATH" 2>/dev/null || {
    echo "❌ Error en compilación"
    exit 1
}
echo "✅ Compilación exitosa"
echo

# 3. Cargar en Arduino
echo "📤 Cargando sketch en Arduino..."
arduino-cli upload -p "$PORT" --fqbn $FQBN "$SKETCH_PATH" 2>/dev/null || {
    echo "❌ Error al cargar"
    exit 1
}
echo "✅ Sketch cargado exitosamente"
echo

# 4. Verificar conexión serial
echo "📡 Esperando conexión serial..."
sleep 2

echo "Presiona Ctrl+C para salir"
python3 -c "
import serial
import time

port = '$PORT'
ser = serial.Serial(port, 9600, timeout=2)
time.sleep(1)

try:
    for i in range(10):
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8', errors='ignore').strip()
            print(f'Recibido: {data}')
except KeyboardInterrupt:
    pass
finally:
    ser.close()
"
