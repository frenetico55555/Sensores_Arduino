/*
 * Multi-Sensor Sketch
 * Lee sensores y envía datos por serial
 * Formato: SENSOR,valor
 */

// Pines
const int BUTTON_PIN = 2;
const int POT_PIN = A0;
const int LDR_PIN = A1;

// Configuración
const int BAUD_RATE = 9600;
const int READ_INTERVAL = 100; // ms

// Estados previos
int lastButtonState = -1;
int lastPotValue = -1;
int lastLdrValue = -1;
unsigned long lastReadTime = 0;

void setup() {
  Serial.begin(BAUD_RATE);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(POT_PIN, INPUT);
  
  // Esperar a que Serial esté listo
  delay(2000);
  
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
  }
}
