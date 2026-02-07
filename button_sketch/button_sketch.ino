/*
 * Multi-Sensor Sketch
 * Lee sensores y envía datos por serial
 * Formato: SENSOR,valor
 */

// Pines
const int BUTTON_PIN = 2;
const int POT_PIN = A0;
const int LDR_PIN = A1;
const int LM35_PIN = A3;
const int JOYSTICK_X_PIN = A5;
const int JOYSTICK_Y_PIN = A4;
const int JOYSTICK_SW_PIN = 3;

// Configuración
const int BAUD_RATE = 9600;
const int READ_INTERVAL = 100; // ms

// Estados previos
int lastButtonState = -1;
int lastPotValue = -1;
int lastLdrValue = -1;
float lastLm35Value = -1000.0;
int lastJoystickX = -1;
int lastJoystickY = -1;
int lastJoystickSW = -1;

// Calibración del joystick
int joystickXOffset = 512;  // Centro teórico
int joystickYOffset = 512;  // Centro teórico
unsigned long lastReadTime = 0;

void setup() {
  Serial.begin(BAUD_RATE);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(JOYSTICK_SW_PIN, INPUT_PULLUP);
  pinMode(POT_PIN, INPUT);
  pinMode(JOYSTICK_X_PIN, INPUT);
  pinMode(JOYSTICK_Y_PIN, INPUT);
  
  // Esperar a que Serial esté listo
  delay(2000);
  
  // ===== CALIBRACIÓN DEL JOYSTICK =====
  // Tomar 50 muestras en reposo para encontrar el centro
  Serial.println("Calibrando joystick...");
  long sumX = 0, sumY = 0;
  for (int i = 0; i < 50; i++) {
    sumX += analogRead(JOYSTICK_X_PIN);
    sumY += analogRead(JOYSTICK_Y_PIN);
    delay(10);
  }
  joystickXOffset = sumX / 50;
  joystickYOffset = sumY / 50;
  Serial.print("Offset X: ");
  Serial.print(joystickXOffset);
  Serial.print(", Offset Y: ");
  Serial.println(joystickYOffset);
  
  Serial.println("SENSORS_READY");
}

void loop() {
  unsigned long currentTime = millis();
  
  if (currentTime - lastReadTime >= READ_INTERVAL) {
    lastReadTime = currentTime;
    
    // ===== BOTÓN DIGITAL =====
    int buttonState = digitalRead(BUTTON_PIN);
    if (buttonState != lastButtonState) {
      lastButtonState = buttonState;
      int state = (buttonState == LOW) ? 1 : 0;
      Serial.print("BUTTON,");
      Serial.println(state);
    }
    
    // ===== POTENCIÓMETRO ANALÓGICO =====
    int potValue = analogRead(POT_PIN);
    // Convertir de 0-1023 a 0-100 para porcentaje
    int potPercent = map(potValue, 0, 1023, 0, 100);
    
    // Enviar si cambió más de 2% (reducir ruido)
    if (abs(potPercent - lastPotValue) >= 2) {
      lastPotValue = potPercent;
      Serial.print("POT,");
      Serial.println(potPercent);
    }
    
    // ===== LDR ANALÓGICO (LUZ) =====
    int ldrValue = analogRead(LDR_PIN);
    // Convertir de 0-1023 a 0-100 para porcentaje de luz
    int ldrPercent = map(ldrValue, 0, 1023, 0, 100);
    
    // Enviar si cambió más de 2% (reducir ruido)
    if (abs(ldrPercent - lastLdrValue) >= 2) {
      lastLdrValue = ldrPercent;
      Serial.print("LDR,");
      Serial.println(ldrPercent);
    }

    // ===== LM35 TEMPERATURA =====
    int lm35Raw = analogRead(LM35_PIN);
    float voltage = lm35Raw * (5.0 / 1023.0);
    float temperatureC = voltage * 100.0; // 10 mV/°C

    // Enviar si cambió más de 0.5°C (reducir ruido)
    if (abs(temperatureC - lastLm35Value) >= 0.5) {
      lastLm35Value = temperatureC;
      Serial.print("LM35,");
      Serial.println(temperatureC, 1);
    }
    
    // ===== JOYSTICK ANALÓGICO =====
    int joystickX = analogRead(JOYSTICK_X_PIN) - joystickXOffset;
    int joystickY = analogRead(JOYSTICK_Y_PIN) - joystickYOffset;
    // Convertir de -512 a +512 a -100 a +100 (centrado en 0)
    int joystickXPercent = map(joystickX, -512, 512, -100, 100);
    int joystickYPercent = map(joystickY, -512, 512, -100, 100);
    
    // Enviar si cambió más de 3% (reducir ruido del joystick)
    if (abs(joystickXPercent - lastJoystickX) >= 3 || abs(joystickYPercent - lastJoystickY) >= 3) {
      lastJoystickX = joystickXPercent;
      lastJoystickY = joystickYPercent;
      Serial.print("JOYSTICK,");
      Serial.print(joystickXPercent);
      Serial.print(",");
      Serial.println(joystickYPercent);
    }
    
    // ===== JOYSTICK BOTÓN =====
    int joystickSW = digitalRead(JOYSTICK_SW_PIN);
    if (joystickSW != lastJoystickSW) {
      lastJoystickSW = joystickSW;
      int state = (joystickSW == LOW) ? 1 : 0;
      Serial.print("JOYSTICK_BTN,");
      Serial.println(state);
    }
  }
}
