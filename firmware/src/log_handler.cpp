#include "log_handler.h"
#include "config.h"
#include <HTTPClient.h>
#include <Arduino_JSON.h>
#include <WiFi.h>

void sendLogToServer(const String& message) {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.printf("Log failed (No WiFi): %s\n", message.c_str());
        return;
    }

    String full_log_url = String(DJANGO_BASE_URL) + String(LOG_ENDPOINT);

    HTTPClient http;
    http.begin(full_log_url);
    http.addHeader("Content-Type", "application/json");
    http.setTimeout(5000);

    JSONVar jsonPayload;
    jsonPayload["message"] = message;
    String payload = JSON.stringify(jsonPayload);

    int httpResponseCode = http.POST(payload);
    
    if (httpResponseCode != 204) {
        Serial.printf("Failed to send log. HTTP Code: %d\n", httpResponseCode);
    }

    http.end();
}