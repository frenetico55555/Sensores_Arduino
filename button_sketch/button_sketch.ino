/*
 * Button Sensor Sketch
 * Lee un botón en el pin D2 y envía el estado por serial
 * Formato: BUTTON,0 o BUTTON,1
 */

const int BUTTON_PIN = 2;
const int BAUD_RATE = 9600;
const int READ_INTERVAL = 100; // ms

int lastButtonState = -1;
unsigned long lastReadTime = 0;

void setup() {
  Serial.begin(BAUD_RATE);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  
  // Esperar a que Serial esté listo (importante para algunos Arduinos)
  delay(2000);
  
  Serial.println("BUTTON_READY");
}

void loop() {
  unsigned long currentTime = millis();
  
  if (currentTime - lastReadTime >= READ_INTERVAL) {
    lastReadTime = currentTime;
    
    // Leer el botón (LOW = presionado, HIGH = suelto)
    int buttonState = digitalRead(BUTTON_PIN);
    
    // Enviar solo si cambió o es la primera lectura
    if (buttonState != lastButtonState) {
      lastButtonState = buttonState;
      
      // Convertir: LOW (presionado) = 1, HIGH (suelto) = 0
      int state = (buttonState == LOW) ? 1 : 0;
      Serial.print("BUTTON,");
      Serial.println(state);
    }
  }
}
