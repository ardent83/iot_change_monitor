#include <Arduino.h>
#include <WiFiManager.h>

#include "config.h"
#include "camera_handler.h"
#include "web_server_handler.h"
#include "log_handler.h"
#include "server_handler.h"

void saveConfigCallback() {
    sendLogToServer("Configuration saved via WiFiManager.");
    Serial.println("Should save config");
}

void setup() {
    Serial.begin(115200);
    Serial.println("\nSystem starting...");

    WiFiManager wm;

    WiFiManagerParameter custom_server_url("server", "Django Server Base URL", DJANGO_BASE_URL, 100);
    wm.addParameter(&custom_server_url);
    wm.setSaveConfigCallback(saveConfigCallback);

    bool res = wm.autoConnect("ESP-MONITOR-SETUP"); 

    if (!res) {
        Serial.println("Failed to connect and hit timeout");
        ESP.restart();
    }

    strcpy(DJANGO_BASE_URL, custom_server_url.getValue());
    Serial.print("Django Server URL is now: ");
    Serial.println(DJANGO_BASE_URL);

    String ip = WiFi.localIP().toString();
    sendLogToServer("WiFi Connected Successfully.");
    sendLogToServer("Device IP Address: " + ip);
    sendLogToServer("Confirmed connection to server: " + String(DJANGO_BASE_URL));
    
    Serial.println("WiFi Connected!");
    Serial.print("Device IP: ");
    Serial.println(ip);

    if (!initCamera()) {
        sendLogToServer("CRITICAL: Halting due to camera failure.");
        Serial.println("Halting due to camera failure.");
        while (true) { delay(1000); }
    }
    
    initServer();
}

void loop() {
    handleServerClient();
}