/*
  WSMD ESP8266 Sensor with ArduinoJson
  
  This sketch connects an ESP8266 to a WiFi network and communicates with the WSMD server.
  It registers the device during setup and sends a hit notification when an interrupt occurs.
  
  This version uses the ArduinoJson library for proper JSON parsing.
  
  Hardware:
  - ESP8266 board (NodeMCU, Wemos D1 Mini, etc.)
  - Sensor connected to interrupt pin (D1/GPIO5)
  
  Required Libraries:
  - ESP8266WiFi
  - ESP8266HTTPClient
  - ArduinoJson (version 6.x)
  
  Created: Sept 1, 2025
*/

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <ArduinoJson.h>

// WiFi settings - replace with your network credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Server settings
const char* serverIP = "192.168.1.100";  // Replace with your server IP address
const int serverPort = 8000;             // Replace with your server port
const String baseUrl = "http://" + String(serverIP) + ":" + String(serverPort);

// Interrupt pin configuration
const int interruptPin = 5;  // D1 on NodeMCU/Wemos D1 Mini (GPIO5)
volatile bool interruptOccurred = false;
unsigned long lastInterruptTime = 0;
const unsigned long debounceTime = 200;  // Debounce time in milliseconds

// LED indicator
const int ledPin = LED_BUILTIN;  // Built-in LED for status indication

// Device information
int deviceOrder = 0;
int hitCounter = 0;
int maxHits = 0;

// Status indicators
bool isRegistered = false;
unsigned long lastConnectionAttempt = 0;
const unsigned long reconnectInterval = 30000;  // Try to reconnect every 30 seconds

void ICACHE_RAM_ATTR handleInterrupt() {
  unsigned long currentTime = millis();
  if (currentTime - lastInterruptTime > debounceTime) {
    interruptOccurred = true;
    lastInterruptTime = currentTime;
  }
}

void setup() {
  // Initialize Serial
  Serial.begin(115200);
  Serial.println("\n\nWSMD ESP8266 Sensor Starting...");
  
  // Initialize pins
  pinMode(interruptPin, INPUT_PULLUP);
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, HIGH);  // LED off (ESP8266 built-in LED is active LOW)
  
  // Set up interrupt
  attachInterrupt(digitalPinToInterrupt(interruptPin), handleInterrupt, FALLING);
  
  // Connect to WiFi
  connectToWiFi();
  
  // Register device with server
  if (WiFi.status() == WL_CONNECTED) {
    registerDevice();
  }
}

void loop() {
  // Check WiFi connection and reconnect if needed
  if (WiFi.status() != WL_CONNECTED) {
    unsigned long currentTime = millis();
    if (currentTime - lastConnectionAttempt > reconnectInterval) {
      Serial.println("WiFi disconnected. Attempting to reconnect...");
      connectToWiFi();
      if (WiFi.status() == WL_CONNECTED && !isRegistered) {
        registerDevice();
      }
    }
  }
  
  // Check if an interrupt has occurred and we're connected
  if (interruptOccurred && WiFi.status() == WL_CONNECTED) {
    Serial.println("Interrupt detected!");
    
    // Visual indicator - blink LED
    digitalWrite(ledPin, LOW);  // LED on
    
    sendHitNotification();
    interruptOccurred = false;
    
    digitalWrite(ledPin, HIGH);  // LED off
  }
  
  // Add any other loop functionality here
  delay(100);
}

void connectToWiFi() {
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  
  // Try to connect for about 20 seconds
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 40) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  lastConnectionAttempt = millis();
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nFailed to connect to WiFi");
  }
}

void registerDevice() {
  // Check WiFi connection
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client;
    HTTPClient http;
    
    String url = baseUrl + "/device/register";
    Serial.print("Registering device at: ");
    Serial.println(url);
    
    http.begin(client, url);
    http.addHeader("Content-Type", "application/json");
    
    // Create empty JSON document for the request
    StaticJsonDocument<64> requestDoc;
    String requestBody;
    serializeJson(requestDoc, requestBody);
    
    // Send POST request
    int httpResponseCode = http.POST(requestBody);
    
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.print("HTTP Response code: ");
      Serial.println(httpResponseCode);
      Serial.print("Response: ");
      Serial.println(response);
      
      // Parse the JSON response
      StaticJsonDocument<256> responseDoc;
      DeserializationError error = deserializeJson(responseDoc, response);
      
      if (!error) {
        deviceOrder = responseDoc["order"];
        Serial.print("Device registered with order: ");
        Serial.println(deviceOrder);
        isRegistered = true;
        
        // Success indicator - quick double blink
        for (int i = 0; i < 2; i++) {
          digitalWrite(ledPin, LOW);  // LED on
          delay(100);
          digitalWrite(ledPin, HIGH);  // LED off
          delay(100);
        }
      } else {
        Serial.print("JSON parsing error: ");
        Serial.println(error.c_str());
      }
    } else {
      Serial.print("Error on registration. Error code: ");
      Serial.println(httpResponseCode);
    }
    
    http.end();
  } else {
    Serial.println("WiFi not connected");
  }
}

void sendHitNotification() {
  // Check WiFi connection
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client;
    HTTPClient http;
    
    String url = baseUrl + "/device/hit";
    Serial.print("Sending hit notification to: ");
    Serial.println(url);
    
    http.begin(client, url);
    http.addHeader("Content-Type", "application/json");
    
    // Create empty JSON document for the request
    StaticJsonDocument<64> requestDoc;
    String requestBody;
    serializeJson(requestDoc, requestBody);
    
    // Send POST request
    int httpResponseCode = http.POST(requestBody);
    
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.print("HTTP Response code: ");
      Serial.println(httpResponseCode);
      Serial.print("Response: ");
      Serial.println(response);
      
      // Parse the JSON response
      StaticJsonDocument<256> responseDoc;
      DeserializationError error = deserializeJson(responseDoc, response);
      
      if (!error) {
        hitCounter = responseDoc["counter"];
        maxHits = responseDoc["max_hits"];
        deviceOrder = responseDoc["order"];
        
        Serial.print("Hit counter: ");
        Serial.println(hitCounter);
        Serial.print("Max hits: ");
        Serial.println(maxHits);
        Serial.print("Device order: ");
        Serial.println(deviceOrder);
      } else {
        Serial.print("JSON parsing error: ");
        Serial.println(error.c_str());
      }
    } else {
      Serial.print("Error on sending hit. Error code: ");
      Serial.println(httpResponseCode);
    }
    
    http.end();
  } else {
    Serial.println("WiFi not connected");
  }
}
