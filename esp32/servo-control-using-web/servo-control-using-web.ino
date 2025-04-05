#include <WiFi.h>
#include <WebServer.h>

#define motor_pin 14
int ir = 13;  // IR sensor pin

// WiFi credentials
const char* ssid = "Prathish";
const char* password = "Prathish1";

// Create web server instance
WebServer server(80);

void setup() {
  Serial.begin(115200);
  pinMode(ir, INPUT);
  pinMode(motor_pin, OUTPUT);
  digitalWrite(motor_pin, HIGH);  // Set motor OFF initially

  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  // Define the `/control_servo` route
  server.on("/control_servo", handleServoControl);
  server.begin();
  Serial.println("Server started");
}

void loop() {
  server.handleClient(); // Handle incoming client requests
}

void handleServoControl() {
  if (server.hasArg("status")) {
    String status = server.arg("status");

    // Enable CORS
    server.sendHeader("Access-Control-Allow-Origin", "*");
    server.sendHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS"); 
    server.sendHeader("Access-Control-Allow-Headers", "*");

    if (status == "open") {
      Serial.println("Motor ON");
      digitalWrite(motor_pin, LOW);  // Activate motor (LOW if relay is active LOW)
      delay(1700);
      digitalWrite(motor_pin, HIGH); // Turn motor OFF
      Serial.println("Motor OFF");

      // Wait for IR sensor to detect an object (Non-blocking)
      unsigned long startTime = millis();
      bool objectDetected = false;

      while (millis() - startTime < 5000) {  // Wait max 5 seconds
        if (digitalRead(ir) == LOW) {  // IR detects object
          Serial.println("LOW - Object Detected");
          objectDetected = true;
          break;
        }
        delay(100);
      }

      if (objectDetected) {
        server.send(200, "text/plain", "Plate dispensed");
      } else {
        server.send(408, "text/plain", "No object detected within 5 seconds");
      }

    } else {
      server.send(400, "text/plain", "Invalid status parameter");
    }
  } else {
    server.send(400, "text/plain", "Missing status parameter");
  }
}
