from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QGridLayout, QLabel)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from src.gui.widgets import (
    LineGraphWidget, CircularGaugeWidget, BrightnessIndicatorWidget,
    DigitalIndicatorWidget, JoystickDisplayWidget, RotaryWidget,
    KeyboardDisplayWidget
)
from src.sensors.sensor_data import SensorSimulator


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Arduino Sensor Monitor - GUI")
        self.setGeometry(100, 100, 1400, 900)
        
        # Inicializar simulador
        self.simulator = SensorSimulator()
        
        # Crear contenedor principal
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(6)
        
        # Título
        title = QLabel("Monitor de Sensores Arduino")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Grid principal (sin scroll)
        grid_layout = QGridLayout()
        grid_layout.setSpacing(8)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        
        # ===== FILA 1: TEMPERATURAS Y HUMEDAD =====
        self.lm35_graph = LineGraphWidget("Temperatura LM35", min_val=15, max_val=35)
        grid_layout.addWidget(self.lm35_graph, 0, 0)
        
        self.dht_temp_graph = LineGraphWidget("Temperatura DHT22", min_val=15, max_val=32)
        grid_layout.addWidget(self.dht_temp_graph, 0, 1)
        
        self.dht_humidity_graph = LineGraphWidget("Humedad Relativa DHT22", min_val=30, max_val=90)
        grid_layout.addWidget(self.dht_humidity_graph, 0, 2)
        
        # ===== FILA 2: SENSORES ANALÓGICOS =====
        self.soil_humidity = CircularGaugeWidget("Humedad de Suelo")
        grid_layout.addWidget(self.soil_humidity, 1, 0)
        
        self.light_indicator = BrightnessIndicatorWidget("Luz Ambiental (LDR)")
        grid_layout.addWidget(self.light_indicator, 1, 1)
        
        self.potentiometer = RotaryWidget("Potenciómetro")
        grid_layout.addWidget(self.potentiometer, 1, 2)
        
        # ===== FILA 3: SENSORES DIGITALES =====
        self.flame_sensor = DigitalIndicatorWidget("Sensor de Llama")
        grid_layout.addWidget(self.flame_sensor, 2, 0)
        
        self.tilt_switch = DigitalIndicatorWidget("Tilt Switch")
        grid_layout.addWidget(self.tilt_switch, 2, 1)
        
        self.button_sensor = DigitalIndicatorWidget("Botón Táctil")
        grid_layout.addWidget(self.button_sensor, 2, 2)
        
        # ===== FILA 4: JOYSTICK =====
        self.joystick = JoystickDisplayWidget("Joystick XY")
        grid_layout.addWidget(self.joystick, 3, 0, 1, 2)
        
        # ===== FILA 4: TECLADO =====
        self.keyboard = KeyboardDisplayWidget("Teclado 4x4")
        grid_layout.addWidget(self.keyboard, 3, 2)
        
        main_layout.addLayout(grid_layout)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Timer para actualizar datos
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_sensors)
        self.timer.start(100)  # Actualizar cada 100ms
    
    def update_sensors(self):
        """Actualiza todos los sensores con datos simulados"""
        
        # Temperaturas
        lm35_data = self.simulator.get_temperature_lm35()
        self.lm35_graph.update_value(lm35_data.value)
        
        dht_temp_data = self.simulator.get_dht_temperature()
        self.dht_temp_graph.update_value(dht_temp_data.value)
        
        dht_humidity_data = self.simulator.get_dht_humidity()
        self.dht_humidity_graph.update_value(dht_humidity_data.value)
        
        # Sensores analógicos
        soil_data = self.simulator.get_soil_humidity()
        self.soil_humidity.update_value(soil_data.value)
        
        light_data = self.simulator.get_light_ldr()
        self.light_indicator.update_value(light_data.value)
        
        pot_data = self.simulator.get_potentiometer()
        self.potentiometer.update_value(pot_data.value)
        
        # Sensores digitales
        flame_data = self.simulator.get_flame_sensor()
        self.flame_sensor.update_state(flame_data.state)
        
        tilt_data = self.simulator.get_tilt_switch()
        self.tilt_switch.update_state(tilt_data.state)
        
        button_data = self.simulator.get_button()
        self.button_sensor.update_state(button_data.state)
        
        # Joystick
        joystick_data = self.simulator.get_joystick()
        self.joystick.update_values(joystick_data.x, joystick_data.y, joystick_data.button)
        
        # Teclado
        key = self.simulator.get_keyboard()
        if key:
            self.keyboard.show_key_pressed(key)
        
        # Avanzar simulación
        self.simulator.update()
