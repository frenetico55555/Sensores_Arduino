# Arduino Sensor Monitor

GUI en Python para visualizar señales de sensores conectados a Arduino en tiempo real.

## Sensores soportados

- **LM35**: Temperatura ambiente (gráfico en tiempo real)
- **DHT22**: Temperatura y humedad relativa (gráficos en tiempo real)
- **Sensor de humedad de suelo**: Medidor circular
- **LDR (Fotoresistor)**: Indicador de brillo visual
- **Sensor de llama**: Indicador digital (verde/rojo)
- **Tilt Switch**: Indicador digital (verde/rojo)
- **Botón táctil**: Indicador digital (verde/rojo)
- **Joystick XY**: Visualización de posición con cruz
- **Potenciómetro**: Aguja rotatoria
- **Teclado 4x4**: Visualización de teclas presionadas

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

## Ejecución

### Modo simulado (datos ficticios)
```bash
python3 src/main.py
```

## Estructura del proyecto

```
Sensores_Arduino/
├── src/
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── widgets.py         # Widgets personalizados para cada sensor
│   │   └── main_window.py     # Ventana principal
│   ├── sensors/
│   │   ├── __init__.py
│   │   └── sensor_data.py     # Simulador de sensores
│   └── main.py               # Punto de entrada
├── requirements.txt
├── .gitignore
└── README.md
```

## Características

- ✅ Gráficos en tiempo real con escala de colores
- ✅ Medidores circulares para porcentajes
- ✅ Indicadores digitales (ON/OFF)
- ✅ Visualización de joystick XY
- ✅ Potenciómetro con aguja rotatoria
- ✅ Teclado 4x4 interactivo
- ✅ Interfaz responsiva y atractiva

## Próximos pasos

1. Conectar con Arduino vía puerto serial
2. Implementar lectura real de sensores
3. Agregar grabación de datos históricos
4. Agregar configuración de alertas por sensor

## Dependencias

- PyQt5: Interfaz gráfica
- PyQtGraph: Gráficos en tiempo real
- PySerial: Comunicación con Arduino
- NumPy: Cálculos numéricos

## Notas

- Todo el código está self-contained en esta carpeta
- El entorno virtual `venv/` no contamina el sistema
- Compatible con macOS, Linux y Windows
