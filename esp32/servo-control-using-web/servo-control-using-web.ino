#include <ESP32Servo.h>
#include <WiFi.h>
#include <WebServer.h>

// Servo setup
Servo servo1;
int servo1Pin = 18; // Pin connected to the servo signal wire

// WiFi credentials
const char* ssid = "vivo V21e 5G";
const char* password = "12345678";

// Create web server instance
WebServer server(80);

void setup() {
  Serial.begin(115200);

  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  // Attach the servo
  servo1.attach(servo1Pin);

  // Define the `/control_servo` route
  server.on("/control_servo", handleServoControl);

  // Start the server
  server.begin();
  Serial.println("Server started");
}

void loop() {
  server.handleClient(); // Handle incoming client requests
}

void handleServoControl() {
  if (server.hasArg("status")) {
    String status = server.arg("status");

    if (status == "open") {
      // Move the servo to 180 degrees
      servo1.write(180);
      delay(5000); // Keep the servo open for 5 seconds

      // Move the servo back to 0 degrees
      servo1.write(0);

      server.send(200, "text/plain", "Servo moved to 180 and back to 0");
    } else {
      server.send(400, "text/plain", "Invalid status parameter");
    }
  } else {
    server.send(400, "text/plain", "Missing status parameter");
  }
}
