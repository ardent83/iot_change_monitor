#ifndef WEB_SERVER_HANDLER_H
#define WEB_SERVER_HANDLER_H

/**
 * @brief Initializes the web server and its routes.
 */
void initServer();

/**
 * @brief Handles incoming client requests. Must be called in the main loop.
 */
void handleServerClient();

#endif
