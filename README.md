# Arduino Sensor Monitor

GUI en Python/PyQt5 para visualizar señales de sensores conectados a Arduino en tiempo real.

## Sensores soportados

### Sensores analógicos
- **LM35**: Temperatura ambiente (°C) - Gráfico de línea en tiempo real con gradiente de color
- **DHT22**: Temperatura (°C) y humedad relativa (%) - Gráficos de línea en tiempo real
- **Sensor de humedad de suelo**: Barra vertical (0-100%)
- **LDR (Fotoresistor)**: Barra vertical de brillo (0-100%)
- **Potenciómetro**: Barra vertical (0-100%)

### Sensores digitales
- **Sensor de llama**: Indicador visual (verde/rojo)
- **Tilt Switch**: Indicador visual (verde/rojo)
- **Botón táctil**: Indicador visual (verde/rojo) ✅ **FUNCIONANDO CON HARDWARE REAL**

### Controles de entrada
- **Joystick XY**: Visualización de posición con ejes y punto móvil
- **Teclado 4x4**: Matriz de teclas con resaltado de última tecla presionada

## Instalación

### 1. Crear entorno virtual
```bash
cd Sensores_Arduino
python3 -m venv venv
source venv/bin/activate  # En macOS/Linux
# venv\Scripts\activate    # En Windows
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Instalar Arduino-CLI (para cargar sketches)
```bash
# macOS
curl -L -o /tmp/arduino-cli.tar.gz https://github.com/arduino/arduino-cli/releases/download/v1.4.1/arduino-cli_1.4.1_macOS_64bit.tar.gz
tar xzf /tmp/arduino-cli.tar.gz -C /tmp
sudo mv /tmp/arduino-cli /usr/local/bin/

# Linux / WSL
curl -L -o arduino-cli.tar.gz https://github.com/arduino/arduino-cli/releases/download/v1.4.1/arduino-cli_1.4.1_Linux_64bit.tar.gz
tar xzf arduino-cli.tar.gz
sudo mv arduino-cli /usr/local/bin/
```

## Ejecución

### Modo con hardware real (si Arduino está conectado)
La app intenta conectar automáticamente a Arduino al iniciar:
- Si **encuentra Arduino**: usa datos reales del botón (D2) en tiempo real ✅
- Si **no lo encuentra**: fallback a simulador para todos los sensores

```bash
python3 src/main.py
```

### Prueba del botón en tiempo real
Para verificar que Arduino-Button está enviando datos correctamente:
```bash
python3 test_button.py
```

## Hardware

### Wiring (conexiones)
```
Arduino Uno
├─ D2: Botón (digital input con PULLUP interno)
│  ├─ Botón cable rojo → D2
│  └─ Botón cable negro → GND
└─ GND: Tierra común
```

### Carga del sketch
```bash
# Instalar board package para Arduino Uno
arduino-cli core install arduino:avr

# Compilar y cargar sketch
./upload_sketch.sh
```

El sketch se carga automáticamente en `/button_sketch/button_sketch.ino`

## Estructura del proyecto

```
Sensores_Arduino/
├── src/
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── widgets.py           # Widgets personalizados para cada sensor
│   │   └── main_window.py       # Ventana principal + Arduino integration
│   ├── sensors/
│   │   ├── __init__.py
│   │   ├── sensor_data.py       # Simulador de sensores
│   │   └── arduino_serial.py    # Comunicación serial con Arduino ✅ NUEVO
│   └── main.py                 # Punto de entrada
├── button_sketch/
│   └── button_sketch.ino        # Código Arduino para botón ✅ NUEVO
├── test_button.py              # Script de prueba interactivo ✅ NUEVO
├── test_serial.py              # Script de prueba serial directo ✅ NUEVO
├── check_firmata.py            # Script para detectar Firmata
├── upload_sketch.sh            # Script para compilar/cargar ✅ NUEVO
├── requirements.txt
├── .gitignore
└── README.md
```

## Características

- ✅ **GUI en PyQt5**: Interfaz profesional sin scroll
- ✅ **Gráficos en tiempo real**: Escala de colores (gradiente azul-verde-rojo)
- ✅ **Barras verticales**: Para mediciones analógicas
- ✅ **Indicadores digitales**: Visualización ON/OFF
- ✅ **Joystick XY**: Visualización con ejes de referencia
- ✅ **Teclado 4x4**: Interactivo con resaltado visual
- ✅ **Hardware real**: Comunicación serial Arduino vía PySerial
- ✅ **Fallback inteligente**: Modo simulador si no hay hardware
- ✅ **Threading**: Lectura no-bloqueante de puerto serial
- ✅ **Valores ergonómicos**: °C, %

## Comunicación Arduino

### Método: PySerial directo (sin Firmata)
- **Baudrate**: 9600
- **Formato**: Texto separado por comas
  - Ejemplo: `BUTTON,1` (presionado), `BUTTON,0` (suelto)
- **Threading**: Lectura en hilo separado para no bloquear UI

### Flujo de datos
```
Arduino sketch (button_sketch.ino)
    ↓ (serial @9600)
ArduinoSerial.py (thread de lectura)
    ↓ (callback)
MainWindow.on_arduino_data()
    ↓
button_sensor.update_state()
    ↓
GUI actualiza en tiempo real
```

## Visualizaciones

### Gráficos de línea
Sensores de temperatura y humedad muestran gráficos con colores dinámicos:
- **Azul**: valores bajos
- **Verde**: valores medios  
- **Rojo**: valores altos

### Barras verticales
Humedad de suelo, luz ambiental y potenciómetro con mismo esquema de colores.

### Indicadores digitales
Sensores binarios: **rojo** (OFF) ↔ **verde** (ON)

### Joystick
Plano XY con cruz de referencia y punto que cambia de color al presionar.

### Teclado
Matriz 4x4 con resaltado en amarillo de última tecla presionada.

## Testing

```bash
# Prueba interactiva del botón
python3 test_button.py

# Prueba básica de serial
python3 test_serial.py

# Detectar si Firmata está instalado
python3 check_firmata.py
```

## Próximos sensores

Listos para integrar en orden de simplicidad:
1. Potenciómetro (pin A0)
2. LDR / Luz ambiental (pin A1)
3. Humedad de suelo (pin A2)
4. Temperatura LM35 (pin A3)
5. DHT22 (pin D3)
6. Joystick XY (pins A4, A5)
7. Teclado 4x4 (pines digitales)
8. Tilt switch (pin D4)
9. Sensor de llama (pin D5)

## Dependencias

Ver `requirements.txt`:
- PyQt5 ≥ 5.15.0
- PyQtGraph ≥ 0.13.0
- pyserial ≥ 3.5
- numpy ≥ 1.21.0


## Dependencias

- PyQt5: Interfaz gráfica
- PyQtGraph: Gráficos en tiempo real
- PySerial: Comunicación con Arduino
- NumPy: Cálculos numéricos

## Notas

- Todo el código está self-contained en esta carpeta
- El entorno virtual `venv/` no contamina el sistema
- Compatible con macOS, Linux y Windows
