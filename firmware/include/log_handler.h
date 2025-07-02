#ifndef LOG_HANDLER_H
#define LOG_HANDLER_H

#include <Arduino.h>

/**
 *  @brief send log to server to display real-time logs
 */
void sendLogToServer(const String& message);

#endif