"""
Módulo para lectura de sensores reales desde Arduino vía serial
"""

import serial
import serial.tools.list_ports
import threading
import time
from dataclasses import dataclass
from typing import Optional, Callable, Union

@dataclass
class SensorReading:
    """Lectura de un sensor"""
    name: str
    value: Union[int, float]
    units: str = ""
    timestamp: float = 0.0


class ArduinoSerial:
    """Gestiona comunicación serial con Arduino"""
    
    def __init__(self, baudrate: int = 9600):
        self.baudrate = baudrate
        self.port = None
        self.ser = None
        self.running = False
        self.thread = None
        self.callback = None
        
    def find_arduino_port(self) -> Optional[str]:
        """Busca puerto USB del Arduino"""
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if 'usbserial' in port.device.lower() or 'CH340' in port.description:
                return port.device
        return None
    
    def connect(self, callback: Callable[[SensorReading], None] = None) -> bool:
        """Conecta a Arduino y inicia lectura en thread"""
        self.port = self.find_arduino_port()
        if not self.port:
            print("❌ Arduino no encontrado")
            return False
        
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=2)
            time.sleep(2)  # Esperar reinicio del Arduino
            self.callback = callback
            self.running = True
            self.thread = threading.Thread(target=self._read_loop, daemon=True)
            self.thread.start()
            print(f"✅ Conectado a Arduino en {self.port}")
            return True
        except Exception as e:
            print(f"❌ Error conectando: {e}")
            return False
    
    def _read_loop(self):
        """Loop de lectura (corre en thread separado)"""
        while self.running and self.ser:
            try:
                if self.ser.in_waiting > 0:
                    line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    if line and not line.endswith("_READY"):
                        self._parse_and_callback(line)
            except Exception as e:
                print(f"Error leyendo: {e}")
                self.running = False
    
    def _parse_and_callback(self, line: str):
        """Parsea línea y ejecuta callback"""
        try:
            parts = line.split(',')
            if len(parts) >= 2:
                sensor_name = parts[0]
                value = float(parts[1])
                
                reading = SensorReading(
                    name=sensor_name,
                    value=int(value) if sensor_name == "BUTTON" else value,
                    units="%" if sensor_name == "POT" else "",
                    timestamp=time.time()
                )
                
                if self.callback:
                    self.callback(reading)
        except Exception as e:
            print(f"Error parseando: {line} - {e}")
    
    def disconnect(self):
        """Desconecta de Arduino"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        if self.ser:
            self.ser.close()
        print("✅ Desconectado")
