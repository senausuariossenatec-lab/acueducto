/*
 * ============================================================
 * SISTEMA IoT MULTI-SENSOR - Wokwi + ThingSpeak
 * Sensores: DHT22 + 5 Potenciómetros
 * Proyecto: Monitoreo de Acueducto
 * ============================================================
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>

// ============================================================
// CONFIGURACIÓN DE RED (Wokwi usa red gratuita)
// ============================================================
const char* ssid = "Wokwi-GUEST";
const char* password = "";

// ============================================================
// ️ THINGSPEAK - REEMPLAZAR CON TUS DATOS
// ============================================================
const char* THINGSPEAK_WRITE_KEY = "XXXXXXXXXXXXXXXX";
const int CHANNEL_ID = 1234567;

// ============================================================
// ️ PINES DE SENSORES
// ============================================================
#define DHTPIN 4
#define DHTTYPE DHT22
#define PIN_CAUDAL 34
#define PIN_CLORO 35
#define PIN_NIVEL 32
#define PIN_ALTURA 33
#define PIN_PRESION 25

DHT dht(DHTPIN, DHTTYPE);

unsigned long lastTime = 0;
const unsigned long intervalo = 15000; // 15 segundos

// ============================================================
// ️ SETUP
// ============================================================
void setup() {
  Serial.begin(115200);
  dht.begin();

  Serial.println("Conectando a WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi conectado: " + WiFi.localIP().toString());
}

// ============================================================
// ️ FUNCIONES AUXILIARES
// ============================================================
float leerPotenciometro(int pin, float minVal, float maxVal) {
  int raw = analogRead(pin);
  return map(raw, 0, 4095, minVal * 100, maxVal * 100) / 100.0;
}

// ============================================================
// ️ LOOP PRINCIPAL
// ============================================================
void loop() {
  if (millis() - lastTime >= intervalo) {
    lastTime = millis();

    // Leer DHT22
    float temp = dht.readTemperature();
    float hum = dht.readHumidity();

    // Leer potenciómetros (escalados)
    float caudal = leerPotenciometro(PIN_CAUDAL, 0, 50);
    float cloro = leerPotenciometro(PIN_CLORO, 0, 5);
    float nivel = leerPotenciometro(PIN_NIVEL, 0, 100);
    float altura = leerPotenciometro(PIN_ALTURA, 0, 50);
    float presion = leerPotenciometro(PIN_PRESION, 0, 10);

    // Validar DHT22
    if (isnan(temp) || isnan(hum)) {
      Serial.println("Error leyendo DHT22");
      return;
    }

    // Construir URL de ThingSpeak (8 campos)
    HTTPClient http;
    String url = "http://api.thingspeak.com/update?api_key=";
    url += THINGSPEAK_WRITE_KEY;
    url += "&field1=" + String(temp, 2);
    url += "&field2=" + String(hum, 2);
    url += "&field3=" + String(caudal, 2);
    url += "&field4=" + String(cloro, 2);
    url += "&field5=" + String(nivel, 2);
    url += "&field6=" + String(altura, 2);
    url += "&field7=" + String(presion, 2);
    url += "&field8=1"; // Sistema activo

    http.begin(url);
    int code = http.GET();

    Serial.println("--- Envío #" + String(lastTime/1000));
    Serial.println("Temp: " + String(temp) + "°C | Hum: " + String(hum) + "%");
    Serial.println("Caudal: " + String(caudal) + " L/min");
    Serial.println("Cloro: " + String(cloro) + " ppm");
    Serial.println("Nivel: " + String(nivel) + "%");
    Serial.println("Altura: " + String(altura) + " m");
    Serial.println("Presión: " + String(presion) + " bar");
    Serial.println("HTTP: " + String(code));

    http.end();
  }
}
