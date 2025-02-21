#include <ESP32Servo.h>
Servo testServo1;
Servo testServo2;

void setup() {
    Serial.begin(115200);

    testServo1.attach(19);
    testServo1.write(200); // Move to 90 degrees
    testServo2.attach(18);
    testServo2.write(10); // Move to 90 degrees
}

void loop() {}
