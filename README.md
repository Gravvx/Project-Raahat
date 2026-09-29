# 🚁 Project SUTRA (System for Unmanned Tactical Reconnaissance & Assistance)

[![Smart India Hackathon](https://img.shields.io/badge/SIH-2026-orange.svg)](#)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit App](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](#)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Edge_Inference-00FFFF.svg)](#)
[![Webots](https://img.shields.io/badge/Webots-SITL_Simulation-red.svg)](#)

**Project SUTRA** is an Edge-AI powered autonomous UAV (Unmanned Aerial Vehicle) reconnaissance system designed for rapid disaster search-and-rescue (SAR) operations. 

Built for the **Smart India Hackathon**, this project utilizes a **Software-in-the-Loop (SITL)** architecture to simulate drone flight physics, perform entirely offline on-device AI inference, and mathematically map 2D video pixel detections into precise 3D real-world GPS coordinates for emergency responders.

---

## 📑 Table of Contents
- [System Architecture](#-system-architecture)
- [Directory Structure](#-directory-structure)
- [Mathematical Core: Pixel-to-GPS](#-mathematical-core-pixel-to-gps)
- [Installation & Prerequisites](#-installation--prerequisites)
- [Operational Guide (Usage)](#-operational-guide)
- [Dashboard Features (ARES-C2)](#-dashboard-features-ares-c2)

---

## 🏗️ System Architecture

To ensure safety, rapid iteration, and hardware-readiness, SUTRA is built on 3 foundational pillars:

1. **SITL Simulation (Webots):** Simulates a DJI Mavic 2 Pro with physically accurate IMU, GPS, and optical sensors. The Python-based controller acts as the flight computer, running Boustrophedon (lawnmower) autonomous search patterns via PID stabilization.
2. **Edge-AI Computer Vision:** Utilizes `YOLOv8n` optimized for edge GPUs alongside `ByteTrack`. This ensures real-time victim detection while preventing duplicate counting of the same survivor across consecutive video frames.
3. **ARES-C2 Ground Control Station:** A monolithic, Python-native Streamlit dashboard styled to MIL-STD-1472H defense ergonomics. It provides responders with live telemetry, offline map rendering, and geo-triage audit logs.

---

## 📂 Directory Structure

```text
SIH_DRONE_PROJECT/
├── webots/                     # SITL Simulation Environment
│   ├── controllers/
│   │   └── autonomous_patrol/
│   │       ├── autonomous_patrol.py  # Drone Flight Controller & PID Logic
│   │       ├── telemetry.json        # Live data bridge to GCS
│   │       └── yolov8n.pt            # Edge AI Model weights
│   ├── mavic2pro/              # UAV Physical Models & Protocols
│   └── worlds/                 # Simulated Disaster Environments
├── dashboard.py                # ARES-C2 Tactical Ground Control UI
├── test_ai.py                  # Standalone YOLO inference testing script
└── yolov8n.pt                  # Root AI weights for local dashboard video testing
