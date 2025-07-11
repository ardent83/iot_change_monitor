# IoT AI Visual Monitoring Platform

A full-stack, scalable platform for visual environment monitoring, featuring AI-powered change detection and real-time reporting. The system leverages an ESP32-CAM for image capture and a Django backend for processing, analysis, and user interaction.

---

## Core Features

- **Secure Multi-Tenancy:** A robust multi-user architecture where each user manages their own isolated set of devices and data.
- **Dual Authentication Scheme:**
  - **Session Authentication:** Secures the web dashboard for users.
  - **API Keys:** Provides secure, stateless authentication for IoT devices, with each device having a unique, revocable key.
- **LLM-based Vision Analysis:** Compares sequential images to detect and describe tangible changes using advanced vision-capable Large Language Models.
- **Per-Device Dynamic Configuration:** Each registered device (via its API key) has its own unique configuration (AI model, custom prompt, hardware settings) manageable through the dashboard.
- **Real-time Logging via WebSockets:** A live log stream from devices to the dashboard, implemented with Django Channels and Redis for stable, real-time communication.
- **Zero-Config Device Onboarding:** Utilizes `WiFiManager` on the ESP32, allowing end-users to set up WiFi credentials, server URL, and API Key through a web portal without flashing new firmware.
- **Secure Media Serving:** Protects user privacy by serving analysis images through a protected Django view that verifies ownership before granting access.
- **Hardware Factory Reset:** A physical button on the ESP32 allows for a hard reset, clearing all stored configurations and returning the device to setup mode.

---

## Tech Stack

### **Backend**
- **Language:** Python 3.12
- **Framework:** Django
- **API:** Django REST Framework
- **Real-time:** Django Channels & Redis
- **ASGI Server:** Daphne
- **Database:** PostgreSQL
- **Device Auth:** Django REST Framework API Key
- **API Docs:** drf-spectacular (Swagger UI)

### **Firmware**
- **Hardware:** ESP32-CAM
- **Framework:** Arduino
- **IDE:** PlatformIO
- **Key Libraries:**
  - `WiFiManager`: For network configuration.
  - `ArduinoJson`: For data serialization.

---

## Setup & Installation

The project is divided into two main components: `backend` and `firmware`.

### **Backend Setup**

1.  **Prerequisites:**
    - Python 3.10+
    - PostgreSQL
    - Redis

2.  **Installation Steps:**
    ```bash
    # 1. Navigate to the backend directory
    cd backend

    # 2. Create and activate a virtual environment
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    # source venv/bin/activate

    # 3. Install dependencies
    pip install -r requirements.txt

    # 4. Create a .env file based on .env.example and fill in your DB credentials

    # 5. Run the Redis server

    # 6. Apply database migrations
    python manage.py migrate

    # 7. Create a superuser for the admin panel
    python manage.py createsuperuser

    # 8. Run the Daphne ASGI server
    daphne -b 0.0.0.0 -p 8000 core.asgi:application
    or
    .\run_dev_server.bat
    ```

### **Firmware Setup**

1.  **Prerequisites:**
    - VS Code with the PlatformIO IDE extension.

2.  **Installation Steps:**
    ```bash
    # 1. Open the `firmware` directory in VS Code
    
    # 2. PlatformIO will automatically detect platformio.ini and install the required libraries
    
    # 3. Build and upload the firmware to your ESP32-CAM board
    ```

3.  **Initial Device Configuration:**
    - On its first boot, the device will create a Wi-Fi Access Point named `ESP-MONITOR-SETUP`.
    - Connect to this network with your phone or laptop. A captive portal should open automatically.
    - Configure your local Wi-Fi credentials, the Django server URL (e.g., `http://192.168.1.104:8000`), and the API Key generated from the dashboard.

---

## API Documentation

Full, interactive API documentation is available via Swagger UI at the following endpoint after running the server:
- `http://127.0.0.1:8000/api/schema/swagger-ui/`
