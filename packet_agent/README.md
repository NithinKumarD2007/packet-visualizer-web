# Packet Agent

## Overview

Packet Agent is a lightweight client application that runs on the user's computer and enables live network packet capture for the Packet Visualizer web application.

The agent captures packets using Scapy, communicates with the deployed FastAPI server, sends heartbeat messages, and starts or stops packet capture based on commands received from the server.

---

## Requirements

- Python 3.10 or later
- Windows Operating System
- Internet Connection

---

## Installation

### 1. Download the Packet Agent

Download `agent_download.zip` from the GitHub Releases page.

Extract the ZIP file.

---

### 2. Install Dependencies

Open Command Prompt or PowerShell inside the extracted folder.

Run:

```bash
pip install -r requirements.txt
```

---

### 3. Configure the Server

Open `config.py`.

Ensure the backend URL points to the deployed Render server.

Example:

```python
BASE_URL = "https://your-render-backend.onrender.com"
```

---

### 4. Start the Agent

Run:

```bash
python main.py
```

If everything is configured correctly, you should see messages similar to:

```
Packet Agent Started
Connected to Server
Heartbeat Sent
Waiting for Capture...
```

---

## Using the Agent

1. Start the Packet Agent.
2. Open the Packet Visualizer website.
3. Your computer should appear under **Connected Devices**.
4. Select your device.
5. Click **Start Capture**.
6. View live packets on the dashboard.

---

## Folder Structure

```
packet_agent/
│
├── main.py
├── client.py
├── agent_capture.py
├── config.py
├── requirements.txt
└── README.md
```

---

## Troubleshooting

### Device is not displayed

- Verify the agent is running.
- Check your internet connection.
- Ensure the backend URL in `config.py` is correct.

### Unable to install packages

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Then run:

```bash
pip install -r requirements.txt
```

### Connection Failed

- Verify the Render backend is online.
- Ensure there are no firewall restrictions.
- Confirm the server URL is correct.

---

## Author

**Nithin Kumar D**

AI & Data Science

Sri Shakthi Institute of Engineering and Technology