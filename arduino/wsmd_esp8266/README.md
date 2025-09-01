# WSMD ESP8266 Sketches

This directory contains Arduino sketches for ESP8266 devices to work with the WSMD (Wireless Sensor and Motion Detector) system.

## Available Sketches

1. **wsmd_esp8266.ino** - Basic implementation with simple string-based JSON parsing
2. **wsmd_esp8266_with_json.ino** - Advanced implementation using the ArduinoJson library

## Hardware Requirements

- ESP8266 board (NodeMCU, Wemos D1 Mini, or similar)
- Sensor with digital output (PIR motion sensor, reed switch, etc.)
- Jumper wires
- Optional: breadboard for prototyping

## Wiring Instructions

Connect your sensor to the ESP8266 as follows:

- Sensor signal pin → D1 (GPIO5) on ESP8266
- Sensor VCC → 3.3V on ESP8266
- Sensor GND → GND on ESP8266

## Setup Instructions

1. Install the Arduino IDE from [arduino.cc](https://www.arduino.cc/en/software)
2. Install ESP8266 board support:

   - Open Arduino IDE
   - Go to File → Preferences
   - Add `http://arduino.esp8266.com/stable/package_esp8266com_index.json` to Additional Boards Manager URLs
   - Go to Tools → Board → Boards Manager
   - Search for "esp8266" and install the package

3. For the JSON version, install the ArduinoJson library:

   - Go to Tools → Manage Libraries
   - Search for "ArduinoJson" by Benoit Blanchon
   - Install version 6.x (not version 5.x)

4. Open the desired sketch and configure:

   - Set your WiFi SSID and password
   - Set the correct IP address and port of your WSMD server
   - Modify pin assignments if needed for your hardware

5. Upload the sketch to your ESP8266 board:
   - Select the correct board from Tools → Board menu (e.g., "NodeMCU 1.0 (ESP-12E Module)")
   - Select the correct port from Tools → Port menu
   - Click the Upload button

## Troubleshooting

- **Device doesn't connect to WiFi**: Check your SSID and password
- **Can't register with server**: Make sure server IP and port are correct
- **Interrupt not detected**: Check wiring and verify the sensor is connected to the correct pin
- **JSON parsing errors**: Try the advanced sketch with ArduinoJson library

## Serial Monitor

Open the Arduino IDE Serial Monitor (Tools → Serial Monitor) and set the baud rate to 115200 to view debug messages from the ESP8266.

## Adding Additional Sensors

To add multiple sensors to a single ESP8266:

1. Define additional interrupt pins
2. Set up additional interrupt handlers
3. Modify the hit notification to include sensor ID information

Example for multiple sensors (pseudo-code):

```arduino
const int interruptPin1 = 5;  // D1
const int interruptPin2 = 4;  // D2

volatile bool interruptOccurred1 = false;
volatile bool interruptOccurred2 = false;

void setup() {
  // ... existing code ...

  pinMode(interruptPin1, INPUT_PULLUP);
  pinMode(interruptPin2, INPUT_PULLUP);

  attachInterrupt(digitalPinToInterrupt(interruptPin1), handleInterrupt1, FALLING);
  attachInterrupt(digitalPinToInterrupt(interruptPin2), handleInterrupt2, FALLING);
}

void loop() {
  // ... existing code ...

  if (interruptOccurred1) {
    sendHitNotification(1);
    interruptOccurred1 = false;
  }

  if (interruptOccurred2) {
    sendHitNotification(2);
    interruptOccurred2 = false;
  }
}
```
