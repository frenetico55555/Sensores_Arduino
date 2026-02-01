# Arduino Sensor Monitor

GUI en Python para visualizar señales de sensores conectados a Arduino en tiempo real.

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
- **Botón táctil**: Indicador visual (verde/rojo)

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

- ✅ Gráficos en tiempo real con escala de colores (gradiente azul-verde-rojo)
- ✅ Barras verticales para mediciones analógicas
- ✅ Indicadores digitales visuales (ON/OFF)
- ✅ Visualización de joystick XY con ejes de referencia
- ✅ Teclado 4x4 interactivo con resaltado visual
- ✅ Interfaz compacta sin scroll (todo visible de un vistazo)
- ✅ Valores ergonómicos para humanos (°C, %)
- ✅ Simulación de datos para pruebas sin hardware

## Visualizaciones

### Gráficos de línea
Los sensores de temperatura (LM35, DHT22) y humedad relativa muestran gráficos en tiempo real que cambian de color según el valor:
- **Azul**: valores bajos
- **Verde**: valores medios  
- **Rojo**: valores altos

### Barras verticales
Humedad de suelo, luz ambiental y potenciómetro usan barras que se llenan progresivamente con el mismo esquema de colores.

### Indicadores digitales
Los sensores binarios (llama, tilt, botón) muestran cuadros grandes que cambian de **rojo** (desactivado) a **verde** (activado).

### Joystick
Visualización de plano XY con cruz de referencia y punto móvil que cambia de color cuando se presiona el botón.

### Teclado
Matriz 4x4 que resalta en amarillo la última tecla presionada.

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
