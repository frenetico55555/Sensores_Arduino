from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFrame, QGridLayout
from PyQt5.QtCore import Qt
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
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)
        
        # Título
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(title_label)
        
        # Gráfico PyQtGraph
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel('left', 'Valor')
        self.plot_widget.setLabel('bottom', 'Tiempo')
        self.plot_widget.setTitle(title)
        self.plot_widget.setBackground('w')
        self.plot_widget.setYRange(min_val, max_val)
        self.plot_widget.setMinimumHeight(140)
        
        self.curve = self.plot_widget.plot(pen=pg.mkPen('b', width=2))
        layout.addWidget(self.plot_widget)
        
        # Label de valor actual
        self.value_label = QLabel("Valor: --")
        self.value_label.setFont(QFont("Arial", 9))
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


class SoilBarWidget(QWidget):
    """Widget interno para pintar la barra de humedad"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(80, 140)

    def paintEvent(self, event):
        parent = self.parent()
        value = getattr(parent, "value", 0)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        padding = 6
        bar_width = max(20, w - padding * 2)
        bar_height = max(40, h - padding * 2)
        bar_x = (w - bar_width) // 2
        bar_y = (h - bar_height) // 2

        # Fondo del contenedor
        painter.setBrush(QBrush(QColor(230, 230, 230)))
        painter.setPen(QPen(QColor(150, 150, 150), 1))
        painter.drawRoundedRect(bar_x, bar_y, bar_width, bar_height, 6, 6)

        # Barra de nivel
        fill_height = int(bar_height * (value / 100))
        fill_y = bar_y + (bar_height - fill_height)

        normalized = value / 100
        if normalized < 0.5:
            r = int(normalized * 2 * 255)
            g = 200
            b = int(255 - normalized * 2 * 255)
        else:
            r = 255
            g = int(200 - (normalized - 0.5) * 2 * 200)
            b = 0

        painter.setBrush(QBrush(QColor(r, g, b)))
        painter.setPen(Qt.NoPen)
        if fill_height > 0:
            painter.drawRoundedRect(bar_x + 2, fill_y + 2, bar_width - 4, fill_height - 4, 4, 4)

        # Borde
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(bar_x, bar_y, bar_width, bar_height, 6, 6)


class CircularGaugeWidget(QWidget):
    """Widget medidor de barra para humedad de suelo"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.value = 0
        
        layout = QVBoxLayout()
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(title_label)
        
        self.bar_widget = SoilBarWidget(self)
        layout.addWidget(self.bar_widget, alignment=Qt.AlignCenter)
        
        self.value_label = QLabel("0%")
        self.value_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)
        
        self.setLayout(layout)
    
    def update_value(self, value: float):
        """Actualiza valor del medidor (0-100)"""
        self.value = max(0, min(100, value))
        self.value_label.setText(f"{self.value:.0f}%")
        self.bar_widget.update()
    
    def paintEvent(self, event):
        """Sin pintura directa: la barra se dibuja en SoilBarWidget"""
        super().paintEvent(event)


class VerticalBarWidget(QWidget):
    """Widget interno para pintar una barra vertical"""

    def __init__(self, parent=None, min_value: float = 0, max_value: float = 100):
        super().__init__(parent)
        self.min_value = min_value
        self.max_value = max_value
        self.setMinimumSize(80, 140)

    def paintEvent(self, event):
        parent = self.parent()
        value = getattr(parent, "value", 0)
        value = max(self.min_value, min(self.max_value, value))

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        padding = 6
        bar_width = max(20, w - padding * 2)
        bar_height = max(40, h - padding * 2)
        bar_x = (w - bar_width) // 2
        bar_y = (h - bar_height) // 2

        # Fondo del contenedor
        painter.setBrush(QBrush(QColor(230, 230, 230)))
        painter.setPen(QPen(QColor(150, 150, 150), 1))
        painter.drawRoundedRect(bar_x, bar_y, bar_width, bar_height, 6, 6)

        # Barra de nivel
        normalized = 0 if self.max_value == self.min_value else (value - self.min_value) / (self.max_value - self.min_value)
        normalized = max(0, min(1, normalized))
        fill_height = int(bar_height * normalized)
        fill_y = bar_y + (bar_height - fill_height)

        if normalized < 0.5:
            r = int(normalized * 2 * 255)
            g = 200
            b = int(255 - normalized * 2 * 255)
        else:
            r = 255
            g = int(200 - (normalized - 0.5) * 2 * 200)
            b = 0

        painter.setBrush(QBrush(QColor(r, g, b)))
        painter.setPen(Qt.NoPen)
        if fill_height > 0:
            painter.drawRoundedRect(bar_x + 2, fill_y + 2, bar_width - 4, fill_height - 4, 4, 4)

        # Borde
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(bar_x, bar_y, bar_width, bar_height, 6, 6)


class BrightnessIndicatorWidget(QWidget):
    """Widget indicador de brillo para LDR"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.value = 0
        self.min_value = 0
        self.max_value = 100
        
        layout = QVBoxLayout()
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(title_label)
        
        self.brightness_display = VerticalBarWidget(self, self.min_value, self.max_value)
        layout.addWidget(self.brightness_display, alignment=Qt.AlignCenter)
        
        self.value_label = QLabel("Brillo: 0%")
        self.value_label.setFont(QFont("Arial", 9, QFont.Bold))
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)
        
        self.setLayout(layout)
    
    def update_value(self, value: float):
        """Actualiza brillo (0-100%)"""
        self.value = max(self.min_value, min(self.max_value, value))
        self.value_label.setText(f"Brillo: {self.value:.0f}%")
        self.brightness_display.update()


class DigitalIndicatorWidget(QWidget):
    """Widget para indicadores digitales (encendido/apagado)"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.state = False
        
        layout = QVBoxLayout()
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(title_label)
        
        self.indicator = QFrame()
        self.indicator.setMinimumSize(70, 70)
        self.indicator.setStyleSheet("background-color: red; border: 3px solid darkred; border-radius: 10px;")
        layout.addWidget(self.indicator)
        
        self.state_label = QLabel("DESACTIVADO")
        self.state_label.setFont(QFont("Arial", 9, QFont.Bold))
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


class JoystickCanvasWidget(QWidget):
    """Widget interno para pintar el joystick"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(160, 160)
        self.setStyleSheet("background-color: white; border: 2px solid black;")

    def paintEvent(self, event):
        parent = self.parent()
        x = getattr(parent, "x", 0)
        y = getattr(parent, "y", 0)
        button_pressed = getattr(parent, "button_pressed", False)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
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
        pixel_x = center_x + (x / 100) * (w / 2 - 10)
        pixel_y = center_y - (y / 100) * (h / 2 - 10)

        # Color según botón
        color = QColor(0, 150, 255) if button_pressed else QColor(100, 100, 100)
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.drawEllipse(int(pixel_x) - 5, int(pixel_y) - 5, 10, 10)


class JoystickDisplayWidget(QWidget):
    """Widget para visualizar posición del joystick XY"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.x = 0
        self.y = 0
        self.button_pressed = False
        
        layout = QVBoxLayout()
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(title_label)
        
        self.joystick_display = JoystickCanvasWidget(self)
        layout.addWidget(self.joystick_display)
        
        self.values_label = QLabel("X: 0  Y: 0  Botón: --")
        self.values_label.setFont(QFont("Arial", 9))
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


class RotaryWidget(QWidget):
    """Widget para visualizar potenciómetro con barra vertical"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.value = 0
        self.min_value = 0
        self.max_value = 100
        
        layout = QVBoxLayout()
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(title_label)
        
        self.rotary_display = VerticalBarWidget(self, self.min_value, self.max_value)
        layout.addWidget(self.rotary_display, alignment=Qt.AlignCenter)
        
        self.value_label = QLabel("0%")
        self.value_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)
        
        self.setLayout(layout)
    
    def update_value(self, value: float):
        """Actualiza valor (0-100%)"""
        self.value = max(self.min_value, min(self.max_value, value))
        self.value_label.setText(f"{self.value:.0f}%")
        self.rotary_display.update()


class KeyboardDisplayWidget(QWidget):
    """Widget para mostrar teclas presionadas del teclado 4x4"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.last_key = None
        
        layout = QVBoxLayout()
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(title_label)
        
        # Matriz de botones 4x4
        keys = [["1", "2", "3", "A"],
                ["4", "5", "6", "B"],
                ["7", "8", "9", "C"],
                ["*", "0", "#", "D"]]
        
        self.key_buttons = {}
        keyboard_frame = QWidget()
        keyboard_layout = QGridLayout()
        keyboard_layout.setSpacing(3)
        
        for row_idx, row in enumerate(keys):
            for col_idx, key in enumerate(row):
                btn = QPushButton(key)
                btn.setMinimumSize(28, 28)
                btn.setFont(QFont("Arial", 8, QFont.Bold))
                btn.setStyleSheet("background-color: lightgray; border: 1px solid black;")
                keyboard_layout.addWidget(btn, row_idx, col_idx)
                self.key_buttons[key] = btn
        
        keyboard_frame.setLayout(keyboard_layout)
        layout.addWidget(keyboard_frame)
        
        self.pressed_label = QLabel("Última tecla: --")
        self.pressed_label.setFont(QFont("Arial", 9, QFont.Bold))
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
