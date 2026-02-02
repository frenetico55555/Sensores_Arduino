#!/usr/bin/env python3
"""
Script para probar el botón en D2
Muestra en tiempo real: presionado / suelto
"""

import serial
import serial.tools.list_ports
import time
import sys

def find_arduino():
    """Busca puerto Arduino"""
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if 'usbserial' in port.device.lower():
            return port.device
    return None

def test_button():
    """Prueba el botón"""
    print("\n" + "="*50)
    print("PRUEBA DE BOTÓN - D2")
    print("="*50 + "\n")
    
    port = find_arduino()
    if not port:
        print("❌ Arduino no encontrado")
        return False
    
    print(f"✅ Arduino encontrado: {port}")
    print("🔗 Conectando...\n")
    
    try:
        ser = serial.Serial(port, 9600, timeout=2)
        time.sleep(2)  # Esperar reinicio
        
        # Limpiar buffer inicial
        while ser.in_waiting > 0:
            ser.readline()
        
        print("📡 ESCUCHANDO BOTÓN")
        print("-" * 50)
        print("Presiona y suelta el botón varias veces")
        print("Ctrl+C para salir\n")
        
        last_state = None
        count = 0
        
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                
                if line and line != "BUTTON_READY":
                    count += 1
                    timestamp = time.strftime("%H:%M:%S")
                    
                    if "BUTTON,1" in line:
                        state = "PRESIONADO"
                        emoji = "🔴"
                        if last_state != 1:
                            print(f"[{timestamp}] #{count} {emoji} BOTÓN PRESIONADO ← " + "↓"*3)
                            last_state = 1
                    elif "BUTTON,0" in line:
                        state = "SUELTO"
                        emoji = "⚪"
                        if last_state != 0:
                            print(f"[{timestamp}] #{count} {emoji} BOTÓN SUELTO ← " + "↑"*3)
                            last_state = 0
                    else:
                        print(f"[{timestamp}] Datos: {line}")
        
        ser.close()
    
    except KeyboardInterrupt:
        print("\n\n" + "="*50)
        print(f"✅ Prueba completada - {count} lecturas recibidas")
        print("="*50 + "\n")
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_button()
