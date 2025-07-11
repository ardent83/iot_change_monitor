#ifndef CAMERA_HANDLER_H
#define CAMERA_HANDLER_H

#include "esp_camera.h"

/**
 * @brief Initializes the camera module.
 * @return true if initialization is successful, false otherwise.
 */
bool initCamera();

/**
 * @brief Captures an image using the camera.
 * @return A pointer to the frame buffer (camera_fb_t) on success, nullptr on failure.
 */
camera_fb_t* captureImage();

/**
 * @brief Initializes the flash module.
 * This function sets up the GPIO pin for the flash if enabled.
 */
void initFlash();

/**
 * @brief Deinitializes the flash module.
 */
void deinitFlash();

/**
 * @brief Flushes the camera buffer by returning all frames.
 */
void flushCameraBuffer();

#endif
