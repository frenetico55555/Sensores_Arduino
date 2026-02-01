import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass
class SensorData:
    """Estructura base para datos de sensores"""
    timestamp: float
    value: float
    unit: str


@dataclass
class DigitalSensorData:
    """Estructura para sensores digitales"""
    timestamp: float
    state: bool  # True = ON, False = OFF


@dataclass
class JoystickData:
    """Estructura para joystick"""
    timestamp: float
    x: float  # -100 a 100
    y: float  # -100 a 100
    button: bool


class SensorSimulator:
    """Genera datos simulados para pruebas de GUI"""
    
    def __init__(self):
        self.time_step = 0
    
    def get_temperature_lm35(self) -> SensorData:
        """Simula LM35: temperatura ambiente (20-30°C con variación suave)"""
        value = 25 + 3 * np.sin(self.time_step * 0.01) + np.random.normal(0, 0.5)
        value = np.clip(value, 15, 35)
        return SensorData(
            timestamp=self.time_step,
            value=value,
            unit="°C"
        )
    
    def get_dht_temperature(self) -> SensorData:
        """Simula DHT22 temperatura (18-28°C)"""
        value = 23 + 2 * np.sin(self.time_step * 0.008) + np.random.normal(0, 0.3)
        value = np.clip(value, 15, 32)
        return SensorData(
            timestamp=self.time_step,
            value=value,
            unit="°C"
        )
    
    def get_dht_humidity(self) -> SensorData:
        """Simula DHT22 humedad (40-80%)"""
        value = 60 + 15 * np.sin(self.time_step * 0.005) + np.random.normal(0, 2)
        value = np.clip(value, 30, 90)
        return SensorData(
            timestamp=self.time_step,
            value=value,
            unit="%"
        )
    
    def get_soil_humidity(self) -> SensorData:
        """Simula sensor de humedad de suelo (0-100%)"""
        value = 50 + 20 * np.sin(self.time_step * 0.003) + np.random.normal(0, 1)
        value = np.clip(value, 0, 100)
        return SensorData(
            timestamp=self.time_step,
            value=value,
            unit="%"
        )
    
    def get_light_ldr(self) -> SensorData:
        """Simula LDR luz (0-100%)"""
        value = 50 + 40 * np.sin(self.time_step * 0.002) + np.random.normal(0, 3)
        value = np.clip(value, 0, 100)
        return SensorData(
            timestamp=self.time_step,
            value=value,
            unit="%"
        )
    
    def get_flame_sensor(self) -> DigitalSensorData:
        """Simula sensor de llama (digital)"""
        state = bool(int(self.time_step / 50) % 3 == 0)  # Activaciones periódicas
        return DigitalSensorData(
            timestamp=self.time_step,
            state=state
        )
    
    def get_tilt_switch(self) -> DigitalSensorData:
        """Simula tilt switch (digital)"""
        state = bool(int(self.time_step / 80) % 2 == 0)
        return DigitalSensorData(
            timestamp=self.time_step,
            state=state
        )
    
    def get_button(self) -> DigitalSensorData:
        """Simula botón táctil (digital)"""
        state = bool(int(self.time_step / 30) % 4 < 1)
        return DigitalSensorData(
            timestamp=self.time_step,
            state=state
        )
    
    def get_potentiometer(self) -> SensorData:
        """Simula potenciómetro (0-100%)"""
        value = 50 + 45 * np.sin(self.time_step * 0.02) + np.random.normal(0, 2)
        value = np.clip(value, 0, 100)
        return SensorData(
            timestamp=self.time_step,
            value=value,
            unit="%"
        )
    
    def get_joystick(self) -> JoystickData:
        """Simula joystick XY"""
        x = 80 * np.sin(self.time_step * 0.015)
        y = 80 * np.cos(self.time_step * 0.01)
        button = bool(int(self.time_step / 100) % 2 == 0)
        return JoystickData(
            timestamp=self.time_step,
            x=x,
            y=y,
            button=button
        )
    
    def get_keyboard(self) -> Optional[str]:
        """Simula pulsaciones del teclado 4x4"""
        keys = ["1", "2", "3", "A", "4", "5", "6", "B", "7", "8", "9", "C", "*", "0", "#", "D"]
        # Emite una tecla cada 40 pasos
        if int(self.time_step) % 40 == 0 and self.time_step % 1 < 0.2:
            return keys[int(self.time_step / 40) % len(keys)]
        return None
    
    def update(self):
        """Avanza el tiempo de simulación"""
        self.time_step += 1
