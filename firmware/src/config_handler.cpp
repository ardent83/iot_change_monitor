#include "config_handler.h"
#include "config.h"
#include <Arduino.h>
#include <ArduinoJson.h>
#include <SPIFFS.h>
#include <WiFiManager.h>

const char* configFilePath = "/config.json";

void loadConfiguration() {
    if (!SPIFFS.begin(true)) {
        Serial.println("An Error has occurred while mounting SPIFFS");
        return;
    }

    if (SPIFFS.exists(configFilePath)) {
        File configFile = SPIFFS.open(configFilePath, "r");
        if (configFile) {
            JsonDocument doc;
            DeserializationError error = deserializeJson(doc, configFile);
            if (error) {
                Serial.println("Failed to read file, using default configuration");
            } else {
                Serial.println("Loading configuration from SPIFFS...");
                strlcpy(DJANGO_BASE_URL, doc["server_url"] | "http://192.168.1.100:8000", sizeof(DJANGO_BASE_URL));
                strlcpy(API_KEY, doc["api_key"] | "YOUR_DEFAULT_KEY", sizeof(API_KEY));
            }
            configFile.close();
        }
    } else {
        Serial.println("Config file not found, using default values.");
    }
}

void saveConfiguration() {
    Serial.println("Saving configuration to SPIFFS...");
    File configFile = SPIFFS.open(configFilePath, "w");
    if (!configFile) {
        Serial.println("Failed to create config file");
        return;
    }

    JsonDocument doc;
    doc["server_url"] = DJANGO_BASE_URL;
    doc["api_key"] = API_KEY;

    if (serializeJson(doc, configFile) == 0) {
        Serial.println("Failed to write to config file");
    }
    configFile.close();
    Serial.println("Configuration saved successfully.");
}

void checkFactoryReset() {
    pinMode(RESET_BUTTON_PIN, INPUT_PULLUP);
    Serial.println("Checking for factory reset command (hold button for 3s)...");
    delay(100);

    if (digitalRead(RESET_BUTTON_PIN) == LOW) {
        Serial.println("Reset button is pressed. Confirming...");
        
        #ifdef BUILTIN_LED
        pinMode(BUILTIN_LED, OUTPUT);
        digitalWrite(BUILTIN_LED, HIGH);
        #endif

        delay(3000);

        if (digitalRead(RESET_BUTTON_PIN) == LOW) {
            Serial.println("Factory reset confirmed. Clearing all settings...");
            
            WiFiManager wm;
            wm.resetSettings();
            
            if (SPIFFS.begin(true)) {
                if (SPIFFS.exists("/config.json")) {
                    SPIFFS.remove("/config.json");
                    Serial.println("Custom config file deleted.");
                }
            }
            
            Serial.println("Settings cleared. Restarting device...");
            delay(1000);
            ESP.restart();
        } else {
            Serial.println("Reset cancelled.");
            #ifdef BUILTIN_LED
            digitalWrite(BUILTIN_LED, LOW);
            #endif
        }
    } else {
        Serial.println("No reset command detected.");
    }
}
