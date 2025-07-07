#include <Arduino.h>
#include <WiFiManager.h>
#include <SPIFFS.h>
#include "config.h"
#include "config_handler.h"
#include "camera_handler.h"
#include "log_handler.h"
#include "ai_handler.h"
#include "web_server_handler.h"
#include "log_handler.h"

void saveConfigCallback() {
    sendLogToServer("Configuration saved via WiFiManager.");
    Serial.println("Should save config");
}

void setup() {
    Serial.begin(115200);
    Serial.println("\nSystem starting...");

    checkFactoryReset();

    loadConfiguration();

    WiFiManager wm;

    WiFiManagerParameter custom_server_url("server", "Django Server Base URL", DJANGO_BASE_URL, 100);
    WiFiManagerParameter custom_api_key("apikey", "Your API Key", API_KEY, 65);
    
    wm.addParameter(&custom_server_url);
    wm.addParameter(&custom_api_key);

    if (!wm.autoConnect("ESP-MONITOR-SETUP")) {
        Serial.println("Failed to connect and hit timeout. Restarting...");
        delay(3000);
        ESP.restart();
    }

    strcpy(DJANGO_BASE_URL, custom_server_url.getValue());
    strcpy(API_KEY, custom_api_key.getValue());

    saveConfiguration();

    Serial.println("\nWiFi Connected Successfully!");
    sendLogToServer("WiFi Connected Successfully.");

    String ip_message = "Device IP Address: " + WiFi.localIP().toString();
    Serial.println(ip_message);
    sendLogToServer(ip_message);

    String server_msg = "Server URL set to: " + String(DJANGO_BASE_URL);
    Serial.println(server_msg);
    sendLogToServer(server_msg);

    String key_message = "API Key configured, starting with: " + String(API_KEY).substring(0, 8);
    Serial.println(key_message);
    sendLogToServer(key_message);

    if (!initCamera()) {
        Serial.println("CRITICAL: Camera initialization failed. Halting.");
        sendLogToServer("CRITICAL: Camera initialization failed. Halting.");
        while (true) { delay(1000); }
    }
    
    Serial.println("Camera initialized successfully.");
    sendLogToServer("Camera initialized successfully.");

    initServer();
}

void loop() {
    handleServerClient();
}