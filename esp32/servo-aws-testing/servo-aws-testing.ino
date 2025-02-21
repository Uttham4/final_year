#include <WiFi.h>
#include <WebServer.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <ESP32Servo.h>

// WiFi credentials
const char* ssid = "mm";
const char* password = "solo1234";

// Server endpoint
const char* sendDataServer = "http://18.218.182.119:5000/send_data";

// Server for receiving requests
WebServer server(80);

// Servo control pin
const int servoPin = 18;

// Servo object
Servo servo;

// Current servo position
int servoDegree = 90;

void setup() {
    Serial.begin(115200);

    // Connect to WiFi
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }
    Serial.println("Connected to WiFi");

    // Print the local IP address
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());

    // Attach servo to its pin
    servo.attach(servoPin);
    Serial.println("Servo attached successfully.");
    servo.write(90); // Move servo to 90 degrees

    // Define HTTP route for updating servo
    server.on("/update_servo", HTTP_POST, handleServoUpdate);

    // Start HTTP server
    server.begin();
    Serial.println("HTTP server started");
}

void loop() {
    // Handle incoming HTTP requests
    server.handleClient();
}

// Function to move the servo
void moveServo(int degree) {
    servo.write(degree); // Set servo position
    delay(500);          // Allow servo to stabilize
}

// Handle incoming HTTP POST request to update servo position
void handleServoUpdate() {
    if (server.hasArg("plain")) { // Check if a JSON payload is received
        String body = server.arg("plain");

        // Parse JSON payload
        DynamicJsonDocument doc(256);
        DeserializationError error = deserializeJson(doc, body);

        if (error) {
            Serial.printf("JSON Parsing Error: %s\n", error.c_str());
            server.send(400, "application/json", "{\"status\":\"error\",\"message\":\"Invalid JSON\"}");
            return;
        }

        // Extract servo degree from the JSON payload
        int newServoDegree = doc["servo_degree"];

        // Move the servo to the new position
        moveServo(newServoDegree);

        // Send updated data to the Flask server
        sendData(servoPin, newServoDegree, (newServoDegree == 0 ? "0" : "180"));

        // Send success response
        server.send(200, "application/json", "{\"status\":\"success\"}");
    } else {
        server.send(400, "application/json", "{\"status\":\"error\",\"message\":\"Invalid request\"}");
    }
}

// Function to send servo data to Flask server
void sendData(int pinOut, int degree, String position) {
    HTTPClient http;
    http.begin(sendDataServer);
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");

    String data = "PIN_OUT=" + String(pinOut) + "&DEGREE=" + String(degree) + "&POSITION=" + position;

    int httpResponseCode = http.POST(data);

    if (httpResponseCode > 0) {
        Serial.printf("Data sent. HTTP Response code: %d\n", httpResponseCode);
    } else {
        Serial.printf("Failed to send data. Error: %s\n", http.errorToString(httpResponseCode).c_str());
    }

    http.end();
}
