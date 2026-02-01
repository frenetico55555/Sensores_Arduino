from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFrame
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QPainter, QPen, QBrush, QFont
import pyqtgraph as pg
from collections import deque
import numpy as np


class LineGraphWidget(QWidget):
    """Widget para gráfico de línea en tiempo real con escala de colores"""
    
    def __init__(self, title: str, min_val: float = 0, max_val: float = 100, parent=None):
        super().__init__(parent)
        self.title = title
        self.min_val = min_val
        self.max_val = max_val
        self.data_points = deque(maxlen=100)
        
        layout = QVBoxLayout()
        
        # Título
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title_label)
        
        # Gráfico PyQtGraph
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel('left', 'Valor')
        self.plot_widget.setLabel('bottom', 'Tiempo')
        self.plot_widget.setTitle(title)
        self.plot_widget.setBackground('w')
        self.plot_widget.setYRange(min_val, max_val)
        
        self.curve = self.plot_widget.plot(pen=pg.mkPen('b', width=2))
        layout.addWidget(self.plot_widget)
        
        # Label de valor actual
        self.value_label = QLabel("Valor: --")
        self.value_label.setFont(QFont("Arial", 11))
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)
        
        self.setLayout(layout)
    
    def update_value(self, value: float):
        """Actualiza con nuevo valor"""
        # Clip al rango
        value = max(self.min_val, min(self.max_val, value))
        self.data_points.append(value)
        
        # Color según valor (azul frío a rojo caliente)
        normalized = (value - self.min_val) / (self.max_val - self.min_val)
        normalized = max(0, min(1, normalized))
        
        # Gradiente azul -> verde -> rojo
        if normalized < 0.5:
            r = int(0 + normalized * 2 * 255)
            g = int(100 + normalized * 2 * 100)
            b = 255
        else:
            r = int((normalized - 0.5) * 2 * 255)
            g = int(200 - (normalized - 0.5) * 2 * 200)
            b = int(255 - (normalized - 0.5) * 2 * 255)
        
        # Usar tupla de color para PyQtGraph
        color_tuple = (r, g, b)
        self.curve.setPen(pg.mkPen(color_tuple, width=2))
        self.curve.setData(list(self.data_points))
        
        # Color para label en formato rgb()
        self.value_label.setText(f"Valor: {value:.2f}")
        self.value_label.setStyleSheet(f"color: rgb({r},{g},{b}); font-weight: bold;")


class CircularGaugeWidget(QWidget):
    """Widget medidor circular para humedad de suelo"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.value = 0
        
        layout = QVBoxLayout()
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title_label)
        
        self.gauge_widget = QWidget()
        self.gauge_widget.setMinimumSize(200, 200)
        layout.addWidget(self.gauge_widget)
        
        self.value_label = QLabel("0%")
        self.value_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)
        
        self.setLayout(layout)
    
    def update_value(self, value: float):
        """Actualiza valor del medidor (0-100)"""
        self.value = max(0, min(100, value))
        self.value_label.setText(f"{self.value:.0f}%")
        self.gauge_widget.update()
    
    def paintEvent(self, event):
        """Dibuja el medidor circular"""
        if self.sender() != self.gauge_widget:
            return
        
        painter = QPainter(self.gauge_widget)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.gauge_widget.width()
        h = self.gauge_widget.height()
        center_x = w // 2
        center_y = h // 2
        radius = min(w, h) // 2 - 10
        
        # Círculo de fondo
        painter.setBrush(QBrush(QColor(200, 200, 200)))
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
        
        # Círculo coloreado según valor
        normalized = self.value / 100
        if normalized < 0.5:
            r = int(normalized * 2 * 255)
            g = 200
            b = int(255 - normalized * 2 * 255)
        else:
            r = 255
            g = int(200 - (normalized - 0.5) * 2 * 200)
            b = 0
        
        painter.setBrush(QBrush(QColor(r, g, b)))
        angle = int(360 * (self.value / 100))
        painter.drawPie(center_x - radius, center_y - radius, radius * 2, radius * 2, 0, angle * 16)
        
        # Borde
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)


class BrightnessIndicatorWidget(QWidget):
    """Widget indicador de brillo para LDR"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.brightness = 0
        
        layout = QVBoxLayout()
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title_label)
        
        self.brightness_display = QWidget()
        self.brightness_display.setMinimumHeight(80)
        layout.addWidget(self.brightness_display)
        
        self.value_label = QLabel("Brillo: 0%")
        self.value_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)
        
        self.setLayout(layout)
    
    def update_value(self, value: float):
        """Actualiza brillo (0-1023 -> 0-100%)"""
        self.brightness = max(0, min(100, (value / 1023) * 100))
        self.value_label.setText(f"Brillo: {self.brightness:.0f}%")
        self.brightness_display.update()
    
    def paintEvent(self, event):
        """Dibuja indicador de brillo"""
        if self.sender() != self.brightness_display:
            return
        
        painter = QPainter(self.brightness_display)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.brightness_display.width()
        h = self.brightness_display.height()
        
        # Fondo oscuro
        painter.fillRect(0, 0, w, h, QColor(50, 50, 50))
        
        # Área de brillo
        bright_width = int(w * (self.brightness / 100))
        painter.fillRect(0, 0, bright_width, h, QColor(255, 255, 100))
        
        # Borde
        painter.setPen(QPen(QColor(200, 200, 200), 2))
        painter.drawRect(0, 0, w, h)


class DigitalIndicatorWidget(QWidget):
    """Widget para indicadores digitales (encendido/apagado)"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.state = False
        
        layout = QVBoxLayout()
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title_label)
        
        self.indicator = QFrame()
        self.indicator.setMinimumSize(100, 100)
        self.indicator.setStyleSheet("background-color: red; border: 3px solid darkred; border-radius: 10px;")
        layout.addWidget(self.indicator)
        
        self.state_label = QLabel("DESACTIVADO")
        self.state_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.state_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.state_label)
        
        self.setLayout(layout)
    
    def update_state(self, state: bool):
        """Actualiza estado (True = verde, False = rojo)"""
        self.state = state
        if state:
            self.indicator.setStyleSheet("background-color: green; border: 3px solid darkgreen; border-radius: 10px;")
            self.state_label.setText("ACTIVADO")
            self.state_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.indicator.setStyleSheet("background-color: red; border: 3px solid darkred; border-radius: 10px;")
            self.state_label.setText("DESACTIVADO")
            self.state_label.setStyleSheet("color: red; font-weight: bold;")


class JoystickDisplayWidget(QWidget):
    """Widget para visualizar posición del joystick XY"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.x = 0
        self.y = 0
        self.button_pressed = False
        
        layout = QVBoxLayout()
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title_label)
        
        self.joystick_display = QWidget()
        self.joystick_display.setMinimumSize(200, 200)
        self.joystick_display.setStyleSheet("background-color: white; border: 2px solid black;")
        layout.addWidget(self.joystick_display)
        
        self.values_label = QLabel("X: 0  Y: 0  Botón: --")
        self.values_label.setFont(QFont("Arial", 10))
        self.values_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.values_label)
        
        self.setLayout(layout)
    
    def update_values(self, x: float, y: float, button: bool = False):
        """Actualiza posición (x,y: -100 a 100)"""
        self.x = max(-100, min(100, x))
        self.y = max(-100, min(100, y))
        self.button_pressed = button
        
        button_text = "PRESIONADO" if button else "LIBRE"
        self.values_label.setText(f"X: {self.x:.0f}  Y: {self.y:.0f}  Botón: {button_text}")
        self.joystick_display.update()
    
    def paintEvent(self, event):
        """Dibuja la cruz y punto del joystick"""
        if self.sender() != self.joystick_display:
            return
        
        painter = QPainter(self.joystick_display)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.joystick_display.width()
        h = self.joystick_display.height()
        center_x = w // 2
        center_y = h // 2
        
        # Dibujar ejes
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.drawLine(0, center_y, w, center_y)  # Eje X
        painter.drawLine(center_x, 0, center_x, h)  # Eje Y
        
        # Escala
        painter.setPen(QPen(QColor(200, 200, 200), 0.5))
        for i in range(-100, 101, 20):
            pixel_x = center_x + (i / 100) * (w / 2)
            pixel_y = center_y - (i / 100) * (h / 2)
            painter.drawPoint(int(pixel_x), center_y)
            painter.drawPoint(center_x, int(pixel_y))
        
        # Posición del joystick
        pixel_x = center_x + (self.x / 100) * (w / 2 - 10)
        pixel_y = center_y - (self.y / 100) * (h / 2 - 10)
        
        # Color según botón
        color = QColor(0, 150, 255) if self.button_pressed else QColor(100, 100, 100)
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.drawEllipse(int(pixel_x) - 5, int(pixel_y) - 5, 10, 10)


class RotaryWidget(QWidget):
    """Widget para visualizar potenciómetro con aguja rotatoria"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.angle = 0
        
        layout = QVBoxLayout()
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title_label)
        
        self.rotary_display = QWidget()
        self.rotary_display.setMinimumSize(150, 150)
        layout.addWidget(self.rotary_display)
        
        self.value_label = QLabel("0%")
        self.value_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)
        
        self.setLayout(layout)
    
    def update_value(self, value: float):
        """Actualiza ángulo (0-255 -> 0-360°)"""
        normalized = max(0, min(1, value / 255))
        self.angle = normalized * 300 - 150  # -150° a 150°
        percentage = normalized * 100
        self.value_label.setText(f"{percentage:.0f}%")
        self.rotary_display.update()
    
    def paintEvent(self, event):
        """Dibuja el dial rotatorio"""
        if self.sender() != self.rotary_display:
            return
        
        painter = QPainter(self.rotary_display)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.rotary_display.width()
        h = self.rotary_display.height()
        center_x = w // 2
        center_y = h // 2
        radius = min(w, h) // 2 - 10
        
        # Círculo de fondo
        painter.setBrush(QBrush(QColor(220, 220, 220)))
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
        
        # Marcas de escala
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        for i in range(0, 7):
            angle = -150 + i * 50
            rad = np.radians(angle)
            x1 = center_x + (radius - 5) * np.cos(rad)
            y1 = center_y - (radius - 5) * np.sin(rad)
            x2 = center_x + radius * np.cos(rad)
            y2 = center_y - radius * np.sin(rad)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        
        # Aguja
        painter.setPen(QPen(QColor(255, 0, 0), 3))
        rad = np.radians(self.angle)
        needle_length = radius - 15
        x = center_x + needle_length * np.cos(rad)
        y = center_y - needle_length * np.sin(rad)
        painter.drawLine(center_x, center_y, int(x), int(y))
        
        # Centro
        painter.setBrush(QBrush(QColor(0, 0, 0)))
        painter.drawEllipse(center_x - 5, center_y - 5, 10, 10)


class KeyboardDisplayWidget(QWidget):
    """Widget para mostrar teclas presionadas del teclado 4x4"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.last_key = None
        
        layout = QVBoxLayout()
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title_label)
        
        # Matriz de botones 4x4
        keys = [["1", "2", "3", "A"],
                ["4", "5", "6", "B"],
                ["7", "8", "9", "C"],
                ["*", "0", "#", "D"]]
        
        self.key_buttons = {}
        keyboard_frame = QWidget()
        keyboard_layout = QVBoxLayout()
        
        for row in keys:
            row_layout = QVBoxLayout()
            for key in row:
                btn = QPushButton(key)
                btn.setMinimumSize(40, 40)
                btn.setFont(QFont("Arial", 10, QFont.Bold))
                btn.setStyleSheet("background-color: lightgray; border: 1px solid black;")
                row_layout.addWidget(btn)
                self.key_buttons[key] = btn
            keyboard_layout.addLayout(row_layout)
        
        keyboard_frame.setLayout(keyboard_layout)
        layout.addWidget(keyboard_frame)
        
        self.pressed_label = QLabel("Última tecla: --")
        self.pressed_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.pressed_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.pressed_label)
        
        self.setLayout(layout)
    
    def show_key_pressed(self, key: str):
        """Resalta tecla presionada"""
        # Resetear botón anterior
        if self.last_key and self.last_key in self.key_buttons:
            self.key_buttons[self.last_key].setStyleSheet("background-color: lightgray; border: 1px solid black;")
        
        # Resaltar nuevo
        if key in self.key_buttons:
            self.key_buttons[key].setStyleSheet("background-color: yellow; border: 2px solid orange; font-weight: bold;")
            self.last_key = key
            self.pressed_label.setText(f"Última tecla: {key}")
