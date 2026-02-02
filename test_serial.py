#!/usr/bin/env python3
"""
Script para probar comunicación serial directa con Arduino
(sin Firmata)
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

def test_serial_direct():
    """Intenta comunicación serial directa"""
    
    print("🔍 Buscando Arduino conectado...")
    port = find_arduino_port()
    
    if not port:
        print("❌ No se encontró Arduino conectado")
        print("   Verifica la conexión USB")
        return False
    
    print(f"✅ Arduino encontrado en: {port}")
    
    try:
        print("🔗 Conectando a 9600 baud...")
        ser = serial.Serial(port, 9600, timeout=2)
        time.sleep(2)  # Esperar a que Arduino se reinicie
        
        print("📡 Escuchando datos por 5 segundos...")
        print("-" * 40)
        
        start_time = time.time()
        data_received = False
        
        while time.time() - start_time < 5:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    print(f"Recibido: {line}")
                    data_received = True
        
        ser.close()
        
        print("-" * 40)
        
        if data_received:
            print("✅ DATOS RECIBIDOS - PySerial directo FUNCIONA")
            return True
        else:
            print("❌ SIN DATOS - Arduino no envía datos por serial")
            print("   Chequea que el código Arduino esté cargado")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Verificador PySerial Directo")
    print("=" * 50)
    print()
    
    result = test_serial_direct()
    
    print()
    print("=" * 50)
    if result:
        print("Resultado: PySerial FUNCIONA ✅")
        print("Podemos usar comunicación serial directa")
    else:
        print("Resultado: PySerial NO FUNCIONA ❌")
        print("Necesitamos Firmata o cargar código Arduino")
    print("=" * 50)
