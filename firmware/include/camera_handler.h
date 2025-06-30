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

#endif
