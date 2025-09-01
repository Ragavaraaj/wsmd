/*
  WSMD ESP8266 Sensor
  
  This sketch connects an ESP8266 to a WiFi network and communicates with the WSMD server.
  It registers the device during setup and sends a hit notification when an interrupt occurs.
  
  Hardware:
  - ESP8266 board (NodeMCU, Wemos D1 Mini, etc.)
  - Sensor connected to interrupt pin (D1/GPIO5)
  
  Created: Sept 1, 2025
*/

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>

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

// Device information
int deviceOrder = 0;
int hitCounter = 0;
int maxHits = 0;

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
  
  // Initialize interrupt pin
  pinMode(interruptPin, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(interruptPin), handleInterrupt, FALLING);
  
  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("\nWiFi connected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  
  // Register device with server
  registerDevice();
}

void loop() {
  // Check if an interrupt has occurred
  if (interruptOccurred) {
    Serial.println("Interrupt detected!");
    sendHitNotification();
    interruptOccurred = false;
  }
  
  // Add any other loop functionality here
  delay(100);
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
    
    // Send POST request
    int httpResponseCode = http.POST("{}");
    
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.print("HTTP Response code: ");
      Serial.println(httpResponseCode);
      Serial.print("Response: ");
      Serial.println(response);
      
      // Parse the JSON response
      // In a real implementation, use ArduinoJson library for robust parsing
      // This is a simple string-based parsing for demonstration
      if (response.indexOf("order") >= 0) {
        int startPos = response.indexOf("order") + 7;  // "order": 
        int endPos = response.indexOf(",", startPos);
        if (endPos < 0) {
          endPos = response.indexOf("}", startPos);
        }
        
        if (startPos >= 0 && endPos >= 0) {
          String orderStr = response.substring(startPos, endPos);
          deviceOrder = orderStr.toInt();
          Serial.print("Device registered with order: ");
          Serial.println(deviceOrder);
        }
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
    
    // Send POST request
    int httpResponseCode = http.POST("{}");
    
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.print("HTTP Response code: ");
      Serial.println(httpResponseCode);
      Serial.print("Response: ");
      Serial.println(response);
      
      // Parse the JSON response
      // In a real implementation, use ArduinoJson library for robust parsing
      // This is a simple string-based parsing for demonstration
      if (response.indexOf("counter") >= 0) {
        int startPos = response.indexOf("counter") + 9;  // "counter": 
        int endPos = response.indexOf(",", startPos);
        
        if (startPos >= 0 && endPos >= 0) {
          String counterStr = response.substring(startPos, endPos);
          hitCounter = counterStr.toInt();
          Serial.print("Hit counter: ");
          Serial.println(hitCounter);
        }
        
        // Parse max_hits
        startPos = response.indexOf("max_hits") + 10;  // "max_hits": 
        endPos = response.indexOf(",", startPos);
        
        if (startPos >= 0 && endPos >= 0) {
          String maxHitsStr = response.substring(startPos, endPos);
          maxHits = maxHitsStr.toInt();
          Serial.print("Max hits: ");
          Serial.println(maxHits);
        }
        
        // Parse order
        startPos = response.indexOf("order") + 7;  // "order": 
        endPos = response.indexOf("}", startPos);
        
        if (startPos >= 0 && endPos >= 0) {
          String orderStr = response.substring(startPos, endPos);
          deviceOrder = orderStr.toInt();
          Serial.print("Device order: ");
          Serial.println(deviceOrder);
        }
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
