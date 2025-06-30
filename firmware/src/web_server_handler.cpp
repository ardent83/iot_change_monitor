#include "web_server_handler.h"
#include "camera_handler.h"
#include "server_handler.h"
#include <WebServer.h>

const char HTML_PROGMEM[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESP32-CAM Interface</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #121212; color: #e0e0e0; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; margin: 0; }
        .container { background-color: #1e1e1e; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5); text-align: center; max-width: 90%; width: 500px; }
        h1 { color: #bb86fc; }
        #live-view { border: 2px solid #333; border-radius: 8px; max-width: 100%; height: auto; margin-bottom: 1rem; background-color: #000; }
        .controls { display: flex; flex-direction: column; gap: 1rem; align-items: center; }
        button { background-color: #bb86fc; color: #121212; border: none; padding: 0.75rem 1.5rem; border-radius: 4px; font-size: 1rem; font-weight: bold; cursor: pointer; transition: background-color 0.2s; }
        button:hover { background-color: #a362ea; }
        #status { margin-top: 1rem; font-style: italic; color: #888; }
        .input-group { margin-bottom: 1rem; }
    </style>
</head>
<body>
    <div class="container">
        <h1>ESP32-CAM AI Monitor</h1>
        <img id="live-view" src="/view" alt="Live Camera View">
        <div class="controls">
            <div class="input-group">
                <label for="delay">Delay (sec): </label>
                <input type="number" id="delay" value="10" min="1">
            </div>
            <button id="capture-btn">Analyze for Changes</button>
        </div>
        <p id="status">Status: Idle</p>
    </div>
    <script>
    const liveView = document.getElementById('live-view');
    const captureBtn = document.getElementById('capture-btn');
    const statusEl = document.getElementById('status');
    const delayInput = document.getElementById('delay');

    setInterval(() => {
        liveView.src = '/view?t=' + new Date().getTime();
    }, 2000);

    captureBtn.addEventListener('click', () => {
        const delay = delayInput.value;
        statusEl.textContent = 'Request sent. Please check Serial Monitor...';
        
        fetch(`/capture?delay=${delay}`)
            .then(response => response.text())
            .then(data => {
                console.log(data);
                statusEl.textContent = 'Analysis request sent. Check Serial Monitor for results.';
                setTimeout(() => { statusEl.textContent = 'Status: Idle'; }, 5000);
            })
            .catch(error => {
                console.error('Error:', error);
                statusEl.textContent = 'Error sending request.';
            });
    });
    </script>
</body>
</html>
)rawliteral";

WebServer server(80);

void handleRoot() {
    server.send_P(200, "text/html", HTML_PROGMEM);
}

void handleView() {
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
        server.send(500, "text/plain", "Failed to capture image");
        return;
    }
    server.send_P(200, "image/jpeg", (const char*)fb->buf, fb->len);
    esp_camera_fb_return(fb);
}

void handleCapture() {
    int delay_sec = 10;
    if (server.hasArg("delay")) {
        delay_sec = server.arg("delay").toInt();
    }
    
    server.send(200, "text/plain", "Request received. Check Serial Monitor for results.");
    sendImagesToServer(delay_sec);
}

void initServer() {
    server.on("/", HTTP_GET, handleRoot);
    server.on("/view", HTTP_GET, handleView);
    server.on("/capture", HTTP_GET, handleCapture);

    server.onNotFound([]() {
        server.send(404, "text/plain", "Not Found");
    });
    
    server.begin();
    Serial.println("HTTP server started. Access the IP address in a browser.");
}

void handleServerClient() {
    server.handleClient();
}