#include "web_server_handler.h"
#include "camera_handler.h"
#include "ai_handler.h"
#include <WebServer.h>

const char HTML_PROGMEM[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">
    <title>ESP32-CAM Interface</title>
    <style>
        body {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #f2f7f5, #e6f0ff);
            color: #2e2e2e;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
        }

        .container {
            background-color: #ffffff;
            padding: 2.5rem;
            border-radius: 20px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
            text-align: center;
            max-width: 90%;
            width: 480px;
            border: 1px solid #dfe6ec;
        }

        h1 {
            color: #3366cc;
            font-size: 1.8rem;
            margin-bottom: 1.5rem;
        }

        .controls {
            display: flex;
            flex-direction: column;
            gap: 1.2rem;
            align-items: center;
        }

        button {
            background: linear-gradient(to right, #4f83cc, #4178c0);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.2s, transform 0.2s;
        }

        button:hover {
            background-color: #345f9b;
            transform: scale(1.05);
        }

        #status {
            margin-top: 1.2rem;
            font-style: italic;
            color: #6b6b6b;
        }

        #live-view {
            border: 2px solid #c9d8e8;
            border-radius: 10px;
            max-width: 100%;
            height: auto;
            margin-bottom: 1rem;
            background-color: #f4f7fa;
        }


        .input-group {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        label {
            font-weight: 600;
            color: #3c3c3c;
        }

        input[type="number"] {
            padding: 0.5rem 0.75rem;
            border: 1px solid #ccd5e0;
            border-radius: 6px;
            font-size: 1rem;
            width: 80px;
            background-color: #f7f9fb;
            color: #333;
        }
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
    }, 1000);

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