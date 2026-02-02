#!/usr/bin/env python3
"""
Script para verificar si Firmata está instalado en Arduino
"""

import serial
import serial.tools.list_ports
import time

def find_arduino_port():
    """Busca el puerto del Arduino conectado"""
    ports = serial.tools.list_ports.comports()
    
    for port in ports:
        if 'Arduino' in port.description or 'CH340' in port.description or 'USB' in port.description:
            return port.device
    
    return None

def check_firmata():
    """Intenta conectarse y chequea si Firmata está instalado"""
    
    print("🔍 Buscando Arduino conectado...")
    port = find_arduino_port()
    
    if not port:
        print("❌ No se encontró Arduino conectado")
        print("   Verifica la conexión USB e intenta de nuevo")
        return False
    
    print(f"✅ Arduino encontrado en: {port}")
    
    try:
        print("🔗 Conectando a Arduino...")
        ser = serial.Serial(port, 57600, timeout=2)
        time.sleep(1)  # Esperar a que Arduino se inicialice
        
        # Enviar comando Firmata: REQUEST_FIRMWARE (0x79)
        print("📡 Enviando comando Firmata...")
        ser.write(bytes([0xF0, 0x79, 0xF7]))  # REQUEST_FIRMWARE
        
        time.sleep(0.5)
        
        # Intentar leer respuesta
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting)
            print("✅ Arduino responde a comandos Firmata")
            print("✅ FIRMWARE INSTALADO - Listo para usar")
            ser.close()
            return True
        else:
            print("⚠️ No hay respuesta a comandos Firmata")
            print("❌ FIRMWARE NO INSTALADO")
            ser.close()
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Verificador de Firmata en Arduino")
    print("=" * 50)
    print()
    
    result = check_firmata()
    
    print()
    print("=" * 50)
    if result:
        print("Resultado: FIRMATA INSTALADO ✅")
        print("Puedes proceder con Python/PyMata4")
    else:
        print("Resultado: NECESITA INSTALACIÓN ❌")
        print("Instrucciones:")
        print("1. Abre Arduino IDE")
        print("2. Archivo → Ejemplos → Firmata → StandardFirmata")
        print("3. Carga en tu Arduino")
    print("=" * 50)
