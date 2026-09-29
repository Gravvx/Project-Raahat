# 🚁 Project RAAHAT
> **Rapid Aerial AI for Hazard Assessment & Tracking**  
> *Developed by Team Sutra for the Smart India Hackathon*

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-ARES--C2-FF4B4B?logo=streamlit)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Edge--AI-00FFFF)
![Webots](https://img.shields.io/badge/Webots-SITL-202020)
![Jetson](https://img.shields.io/badge/NVIDIA-Jetson%20Orin%20Nano-76B900?logo=nvidia)
![LoRa](https://img.shields.io/badge/LoRa-868MHz-orange)

Project RAAHAT is an Edge-AI powered autonomous UAV reconnaissance system designed for rapid disaster search-and-rescue (SAR) operations. 

Built for the Smart India Hackathon, the platform utilizes a **Software-in-the-Loop (SITL)** architecture to simulate drone flight physics, perform entirely offline on-device AI inference, and mathematically map 2D video pixel detections into precise 3D real-world GPS coordinates for emergency responders — backed by a validated custom hardware payload designed for real-world deployment.

---

## 📑 Table of Contents
- [System Architecture](#-system-architecture)
- [Hardware Architecture](#-hardware-architecture)
- [Directory Structure](#-directory-structure)
- [Mathematical Core: Pixel-to-GPS](#-mathematical-core-pixel-to-gps)
- [Installation & Prerequisites](#-installation--prerequisites)
- [Operational Guide (Usage)](#-operational-guide-usage)
- [Dashboard Features (ARES-C2)](#-dashboard-features-ares-c2)

---

## 🏗️ System Architecture

To ensure safety, rapid iteration, and hardware-readiness, Project RAAHAT is built on **4 foundational pillars**:

1. **SITL Simulation (Webots):** Simulates a DJI Mavic 2 Pro with physically accurate IMU, GPS, and optical sensors. The Python-based controller acts as the flight computer, running Boustrophedon (lawnmower) autonomous search patterns via PID stabilization.
2. **Edge-AI Computer Vision:** Utilizes YOLOv8n optimized for edge GPUs alongside ByteTrack. This ensures real-time victim detection while preventing duplicate counting of the same survivor across consecutive video frames.
3. **Hardware Payload & Power System:** A custom-designed carrier PCB integrating the compute, sensing, and communication stack onto the physical airframe.
4. **ARES-C2 Ground Control Station:** A monolithic, Python-native Streamlit dashboard styled to MIL-STD-1472H defense ergonomics. It provides responders with live telemetry, offline map rendering, and geo-triage audit logs.

---

## 🔧 Hardware Architecture

Project RAAHAT's hardware stack is engineered so all AI inference happens onboard, ensuring functionality even when network connectivity is entirely unavailable at a disaster site.

### Compute & Sensing

| Component | Role |
| :--- | :--- |
| **NVIDIA Jetson Orin Nano** | Edge AI compute — runs YOLOv8n inference locally (CUDA-accelerated) |
| **RGB Camera** | Visual-spectrum survivor and hazard detection |
| **Thermal Camera (LWIR)** | Heat-signature detection for survivors under debris / low-visibility conditions |
| **Pixhawk / STM32** | Real-time flight stabilization, independent of the AI compute layer |
| **NEO-M8N GPS Module** | Positioning data for geo-tagging detections |
| **IMU + Barometer** | Orientation and altitude sensing, feeds flight controller |
| **SX1276 LoRa Transceiver** | Long-range, low-bandwidth telemetry link to ground station (868 MHz) |

### Power System

| Component | Spec |
| :--- | :--- |
| **Main Battery** | 4S / 6S LiPo |
| **Buck Converter (Compute Rail)** | 19V / 5A → Jetson Orin Nano |
| **Buck Converter (Avionics Rail)** | 5V / 4A → Flight controller, IMU, GPS |
| **Power Distribution Board (PDB)** | Routes raw battery voltage to ESCs/motors and both converted rails |

### Custom Carrier PCB & Physical Integration
* **KiCad Verification:** Fully designed project schematic verified with zero Electrical Rules Check (ERC) errors.
* **RF Optimization:** Includes a Pi-filter LC matching network for optimal LoRa RF output on 868 MHz.
* **Physical Assembly:** Sourced accurate `.STEP` CAD files for the airframe, Jetson Orin Nano, and FPV camera module to verify 30.5 × 30.5 mm standoff mounting feasibility and dual payload bay clearance.

### Data Flow (Hardware → Software Bridge)

```text
[RGB + Thermal Cameras] ──▶ Jetson Orin Nano (YOLOv8 Inference)
                                      │
[Pixhawk GPS/IMU] ─────────▶ MAVLink  │
                             Telemetry│
                                      ▼
                        [Compact JSON Alert] 
                                      │
                                    (UART)
                                      │
                                      ▼
                          [LoRa Transmitter (SX1276)]
                                      │
                                (868 MHz RF)
                                      │
                                      ▼
                          [Ground Base Station]
                                      │
                                      ▼
                             [ARES-C2 Dashboard]

SIH_DRONE_PROJECT/
├── webots/                     # SITL Simulation Environment
│   ├── controllers/
│   │   └── autonomous_patrol/
│   │       ├── autonomous_patrol.py  # Drone Flight Controller & PID Logic
│   │       ├── telemetry.json        # Live data bridge to GCS
│   │       └── yolov8n.pt            # Edge AI Model weights
│   ├── mavic2pro/              # UAV Physical Models & Protocols
│   └── worlds/                 # Simulated Disaster Environments
├── hardware/                   # Physical Hardware Design Assets
│   ├── pcb/
│   │   ├── DRONE_SIH.kicad_sch  # Schematic
│   │   └── DRONE_SIH.kicad_pcb  # Board layout (Edge.Cuts verified)
│   ├── cad/
│   │   ├── airframe.step             # Drone airframe STEP file
│   │   ├── jetson_orin_nano.step     # Compute module STEP file
│   │   └── fpv_camera.step           # Camera module STEP file
│   └── renders/                      # KiCad 3D raytraced board renders
├── dashboard.py                # ARES-C2 Tactical Ground Control UI
├── test_ai.py                  # Standalone YOLO inference testing script
└── yolov8n.pt                  # Root AI weights for local dashboard video testing
