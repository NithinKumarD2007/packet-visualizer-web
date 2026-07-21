Packet Visualizer
Project Description

Packet Visualizer is a real-time network monitoring and analysis application that captures live network traffic, stores packet information in a PostgreSQL database, analyzes the collected data, and presents it through an interactive web dashboard.

The application uses Scapy to capture packets from the network interface, FastAPI as the backend framework, PostgreSQL (Neon) for persistent packet storage, and WebSockets to deliver live updates to the frontend.
The interface provides network administrators and users with real-time insights into network activity, protocol usage, connected devices, traffic patterns, and potential security threats.

The project is designed to demonstrate concepts in network packet analysis, backend API development, real-time communication, database management, and data visualization through a modern web application.

Key Features
📡 Real-time packet capture using Scapy
⚡ Live dashboard with continuously updating statistics
📊 Interactive protocol distribution charts
🖥 Device monitoring and capture management
🔍 Packet search and protocol filtering
🌐 Top source and destination IP analysis
🚨 Basic threat detection with threat level and reason
🤖 AI-powered network assistant using Gemini API
📄 Network report generation
📥 CSV and PDF export support
🔄 WebSocket-based live updates
💾 PostgreSQL database integration


Technology Stack

Backend	-          FastAPI, Python|
Packet Capture	-  Scapy|
Database	    -    PostgreSQL (Neon)|
Frontend	     -   HTML, CSS, JavaScript|
Charts	        -  Chart.js|
AI	             - Google Gemini API|
Communication	    - WebSockets

Project Workflow 

Network Traffic
       │
       ▼
Scapy Packet Capture
       │
       ▼
Packet Processing
       │
       ▼
PostgreSQL Database
       │
       ▼
FastAPI REST APIs
       │
       ▼
WebSocket Updates
       │
       ▼
Interactive Dashboard
