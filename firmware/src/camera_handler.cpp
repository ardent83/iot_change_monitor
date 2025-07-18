#include "camera_handler.h"
#include "config.h"
#include <Arduino.h>

bool initCamera() {
    if (ENABLE_FLASH) {
        pinMode(FLASH_GPIO_PIN, OUTPUT);
        digitalWrite(FLASH_GPIO_PIN, LOW);
    }

    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;
    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_pclk = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;
    config.pin_sccb_sda = SIOD_GPIO_NUM;
    config.pin_sccb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_JPEG;
    config.frame_size = FRAMESIZE_VGA;
    config.jpeg_quality = 12;
    config.fb_count = 2;

    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("Camera init failed with error 0x%x\n", err);
        return false;
    }
    return true;
}

camera_fb_t* captureImage() {
    if (ENABLE_FLASH) {
        digitalWrite(FLASH_GPIO_PIN, HIGH);
        delay(100);
    }

    flushCameraBuffer();

    camera_fb_t* fb = esp_camera_fb_get();

    if (ENABLE_FLASH) {
        deinitFlash();
    }

    if (!fb) {
        Serial.println("Failed to capture image!");
        return nullptr;
    }
    return fb;
}

void initFlash() {
    pinMode(FLASH_GPIO_PIN, OUTPUT);
    digitalWrite(FLASH_GPIO_PIN, LOW);
}

void deinitFlash() {
    digitalWrite(FLASH_GPIO_PIN, LOW);
}

void flushCameraBuffer() {
    for (int i = 0; i < 2; ++i) {
        camera_fb_t* fb_flush = esp_camera_fb_get();
        if (fb_flush) {
            esp_camera_fb_return(fb_flush);
        }
    }
}
