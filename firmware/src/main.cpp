#include <Arduino.h>
#include <WiFiManager.h>

#include "config.h"
#include "camera_handler.h"
#include "web_server_handler.h"

void saveConfigCallback() {
    Serial.println("Should save config");
}

void setup() {
    Serial.begin(115200);
    Serial.println("\nSystem starting...");

    WiFiManager wm;

    WiFiManagerParameter custom_server_url("server", "Django Server URL", DJANGO_SERVER_URL, 100);
    wm.addParameter(&custom_server_url);

    wm.setSaveConfigCallback(saveConfigCallback);

    bool res = wm.autoConnect("ESP-MONITOR-SETUP"); 

    if (!res) {
        Serial.println("Failed to connect and hit timeout");
        ESP.restart();
    }

    strcpy(DJANGO_SERVER_URL, custom_server_url.getValue());
    Serial.print("Django Server URL is now: ");
    Serial.println(DJANGO_SERVER_URL);

    if (!initCamera()) {
        Serial.println("Halting due to camera failure.");
        while (true) { delay(1000); }
    }
        
    initServer();
}

void loop() {
    handleServerClient();
}