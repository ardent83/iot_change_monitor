#include "server_handler.h"
#include "config.h"
#include "camera_handler.h"
#include <WiFiClient.h>
#include <WiFiClientSecure.h>

struct ServerInfo {
    String host;
    int port;
    String path;
};

bool parseUrl(const char* url_str, ServerInfo &info);
String generateBoundary();

void sendImagesToServer(int delaySeconds) {
    camera_fb_t* fb1 = captureImage();
    if (!fb1) {
        Serial.println("Failed to capture first image.");
        return;
    }
    
    delay(delaySeconds * 1000);

    camera_fb_t* fb2 = captureImage();
    if (!fb2) {
        esp_camera_fb_return(fb1);
        Serial.println("Failed to capture second image.");
        return;
    }

    ServerInfo server;
    if (!parseUrl(DJANGO_SERVER_URL, server)) {
        Serial.println("Failed to parse server URL.");
        esp_camera_fb_return(fb1);
        esp_camera_fb_return(fb2);
        return;
    }
    
    Client* client;
    WiFiClient httpClient;
    WiFiClientSecure httpsClient;

    if (server.port == 443) {
        httpsClient.setInsecure();
        client = &httpsClient;
    } else {
        client = &httpClient;
    }
    
    Serial.printf("Connecting to host: %s, port: %d\n", server.host.c_str(), server.port);

    if (!client->connect(server.host.c_str(), server.port)) {
        Serial.println("Connection failed!");
        esp_camera_fb_return(fb1);
        esp_camera_fb_return(fb2);
        return;
    }

    String boundary = generateBoundary();
    String head_part1 = "--" + boundary + "\r\nContent-Disposition: form-data; name=\"image1\"; filename=\"image1.jpg\"\r\nContent-Type: image/jpeg\r\n\r\n";
    String head_part2 = "\r\n--" + boundary + "\r\nContent-Disposition: form-data; name=\"image2\"; filename=\"image2.jpg\"\r\nContent-Type: image/jpeg\r\n\r\n";
    String tail_part = "\r\n--" + boundary + "--\r\n";
    
    uint32_t total_len = head_part1.length() + fb1->len + head_part2.length() + fb2->len + tail_part.length();
    
    client->printf("POST %s HTTP/1.1\r\n", server.path.c_str());
    client->printf("Host: %s\r\n", server.host.c_str());
    client->println("Connection: close");
    client->printf("Content-Length: %u\r\n", total_len);
    client->printf("Content-Type: multipart/form-data; boundary=%s\r\n", boundary.c_str());
    client->println();

    client->print(head_part1);
    client->write(fb1->buf, fb1->len);
    client->print(head_part2);
    client->write(fb2->buf, fb2->len);
    client->print(tail_part);

    Serial.println("Request sent. Waiting for response...");

    unsigned long timeout = millis();
    while (client->available() == 0) {
        if (millis() - timeout > 10000) {
            Serial.println(">>> Client Timeout !");
            client->stop();
            break;
        }
    }
    
    Serial.println("Server Response:");
    while(client->available()) {
        Serial.write(client->read());
    }

    client->stop();
    esp_camera_fb_return(fb1);
    esp_camera_fb_return(fb2);
}

bool parseUrl(const char* url_str, ServerInfo &info) {
    String url = String(url_str);

    if (url.startsWith("https://")) {
        info.port = 443;
    } else if (url.startsWith("http://")) {
        info.port = 80;
    } else {
        Serial.println("Invalid URL: Protocol (http:// or https://) is missing.");
        return false;
    }

    int protocol_end_index = url.indexOf("://") + 3;
    int host_end_index = url.indexOf('/', protocol_end_index);
    if (host_end_index == -1) {
        info.host = url.substring(protocol_end_index);
        info.path = "/";
    } else {
        info.host = url.substring(protocol_end_index, host_end_index);
        info.path = url.substring(host_end_index);
    }

    int port_index = info.host.indexOf(':');
    if (port_index != -1) {
        info.port = info.host.substring(port_index + 1).toInt();
        info.host = info.host.substring(0, port_index);
    }
    return true;
}

String generateBoundary() {
  String boundary = "----WebKitFormBoundary";
  const char* charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
  for (int i = 0; i < 16; i++) {
    boundary += charset[random(0, strlen(charset) - 1)];
  }
  return boundary;
}
