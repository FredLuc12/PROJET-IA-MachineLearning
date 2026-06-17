/*
 * Système d'irrigation intelligente — H3 Hitema M2 IoT
 * ESP32 + DHT11 + Capteur sol capacitif V2.0.0
 *
 * Bibliothèques requises (Arduino IDE → Gestionnaire de bibliothèques) :
 *   - DHT sensor library  (par Adafruit)
 *   - Adafruit Unified Sensor
 *   - ArduinoJson          (par Benoit Blanchon)
 *
 * Carte : "ESP32 Dev Module"  (Tools → Board → esp32 → ESP32 Dev Module)
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

// ─── Configuration WiFi ───────────────────────────────────────────────────────
const char* WIFI_SSID     = "Ansumdine";        
const char* WIFI_PASSWORD = "1234567890"; 

// ─── Configuration API ────────────────────────────────────────────────────────
// Mets l'IP locale de ton PC (ipconfig / ip addr)
const char* API_URL = "http://10.105.82.223:8000/mesures";
const int   CAPTEUR_ID = 1;

// ─── Pins ─────────────────────────────────────────────────────────────────────
#define DHTPIN        23    // GPIO23 → DATA du DHT11
#define DHTTYPE       DHT11
#define SOL_PIN       34    // GPIO34 → AOUT du capteur sol (entrée analogique)

// ─── Calibration capteur sol ──────────────────────────────────────────────────
// Mesure ces valeurs avec ton capteur :
//   → Dans l'air (sec)  : note la valeur ADC  → SOL_AIR
//   → Dans l'eau        : note la valeur ADC  → SOL_EAU
// Le capteur capacitif est INVERSÉ : plus c'est mouillé, plus la valeur est basse
#define SOL_AIR       3057     // valeur ADC capteur dans l'air  (~sec)
#define SOL_EAU       1500   // valeur ADC capteur dans l'eau  (~humide)

// ─── Intervalle d'envoi ───────────────────────────────────────────────────────
#define INTERVALLE_MS 10000  // 10 secondes entre chaque mesure

// ─── Objets ───────────────────────────────────────────────────────────────────
DHT dht(DHTPIN, DHTTYPE);

// ─── Fonctions utilitaires ────────────────────────────────────────────────────

/**
 * Convertit la valeur ADC brute du capteur sol en pourcentage (0-100%).
 * Capteur capacitif inversé : SOL_AIR = 0%, SOL_EAU = 100%
 */
float lireHumiditeSol() {
  // Moyenne sur 5 lectures pour stabiliser
  long somme = 0;
  for (int i = 0; i < 5; i++) {
    somme += analogRead(SOL_PIN);
    delay(10);
  }
  int adc = somme / 5;

  // Conversion en pourcentage (inversé)
  float pct = map(adc, SOL_AIR, SOL_EAU, 0, 100);
  pct = constrain(pct, 0.0, 100.0);

  Serial.print("[SOL] ADC brut = ");
  Serial.print(adc);
  Serial.print("  →  ");
  Serial.print(pct, 1);
  Serial.println("%");

  return pct;
}

/**
 * Retourne l'état du sol sous forme de texte.
 */
String etatSol(float humidite) {
  if (humidite < 30.0) return "sec";
  if (humidite > 70.0) return "humide";
  return "normal";
}

/**
 * Connexion WiFi avec timeout.
 */
void connecterWifi() {
  Serial.print("[WiFi] Connexion à ");
  Serial.print(WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int tentatives = 0;
  while (WiFi.status() != WL_CONNECTED && tentatives < 20) {
    delay(500);
    Serial.print(".");
    tentatives++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[WiFi] Connecté !");
    Serial.print("[WiFi] IP : ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n[WiFi] Échec connexion — mode console seulement");
  }
}

/**
 * Envoie les données à FastAPI via HTTP POST JSON.
 * Retourne true si HTTP 201.
 */
bool envoyerMesure(float humSol, float temp, float humAir) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[HTTP] WiFi non connecté — envoi annulé");
    return false;
  }

  // Construction du JSON
  StaticJsonDocument<256> doc;
  doc["id_capteur"]   = CAPTEUR_ID;
  doc["humidite_sol"] = round(humSol * 10) / 10.0;
  doc["temperature"]  = round(temp  * 10) / 10.0;
  doc["humidite_air"] = round(humAir * 10) / 10.0;

  String body;
  serializeJson(doc, body);

  Serial.print("[HTTP] POST → ");
  Serial.println(API_URL);
  Serial.print("[HTTP] Body : ");
  Serial.println(body);

  HTTPClient http;
  http.begin(API_URL);
  http.addHeader("Content-Type", "application/json");

  int code = http.POST(body);

  if (code == 201) {
    Serial.println("[HTTP] ✓ 201 Created");
    http.end();
    return true;
  } else if (code > 0) {
    Serial.print("[HTTP] ✗ Code : ");
    Serial.println(code);
    Serial.print("[HTTP] Réponse : ");
    Serial.println(http.getString());
  } else {
    Serial.print("[HTTP] ✗ Erreur réseau : ");
    Serial.println(http.errorToString(code));
  }

  http.end();
  return false;
}

// ─── Setup ────────────────────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("========================================");
  Serial.println("  ESP32 — Irrigation intelligente");
  Serial.println("  DHT11 + Sol capacitif V2.0.0");
  Serial.println("========================================");

  // Init DHT11
  pinMode(DHTPIN, INPUT_PULLUP);
  dht.begin();
  Serial.println("[DHT11] Initialisé sur GPIO23");

  // GPIO34 = entrée analogique uniquement (pas besoin de pinMode)
  analogReadResolution(12);  // 12 bits → 0 à 4095
  Serial.println("[SOL]   Capteur sol sur GPIO34 (12 bits ADC)");

  // WiFi
  connecterWifi();

  Serial.println("[SYS]  Démarrage des mesures...\n");
}

// ─── Loop ─────────────────────────────────────────────────────────────────────
void loop() {
  Serial.println("─────────────────────────────────────────");

  // ── Lecture DHT11 ──────────────────────────────────────
  float humAir = dht.readHumidity();
  float temp   = dht.readTemperature();  // °C

  if (isnan(humAir) || isnan(temp)) {
    Serial.println("[DHT11] ✗ Lecture échouée — capteur déconnecté ?");
    Serial.println("         Vérifier GPIO23 et résistance pull-up 10kΩ");
    delay(INTERVALLE_MS);
    return;
  }

  Serial.print("[DHT11] Temp     = ");
  Serial.print(temp, 1);
  Serial.println(" °C");
  Serial.print("[DHT11] Hum air  = ");
  Serial.print(humAir, 1);
  Serial.println(" %");

  // ── Lecture capteur sol ────────────────────────────────
  float humSol = lireHumiditeSol();
  String etat  = etatSol(humSol);

  Serial.print("[SOL]   Hum sol  = ");
  Serial.print(humSol, 1);
  Serial.print(" %  (");
  Serial.print(etat);
  Serial.println(")");

  // ── Décision pompe (GPIO34 input only → juste log ici) ─
  if (etat == "sec") {
    Serial.println("[POMPE] ⚠ Sol sec → irrigation recommandée");
  } else if (etat == "humide") {
    Serial.println("[POMPE] ✓ Sol humide → pas d'irrigation");
  } else {
    Serial.println("[POMPE] ● Sol normal → surveillance continue");
  }

  // ── Envoi HTTP ─────────────────────────────────────────
  bool ok = envoyerMesure(humSol, temp, humAir);
  if (!ok) {
    Serial.println("[SYS]  Mesure gardée en local (pas d'envoi)");
  }

  Serial.println();
  delay(INTERVALLE_MS);
}
