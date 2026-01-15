# Server Monitor Portable

A lightweight, standalone server monitoring tool featuring a web-based dashboard. Designed for portability, this application allows users to monitor real-time system metrics without requiring a Python environment installation.

![Project Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.x-blue.svg)
![Flask](https://img.shields.io/badge/flask-backend-orange.svg)

## 📋 Overview

**Server Monitor Portable** is a system utility that initializes a local web server to display critical system metrics (CPU, RAM, Disk usage) via a visual dashboard. 

Packaged as a single executable (`.exe`), this tool is designed for immediate deployment on Windows environments, eliminating the need for dependency management or Python configuration on the target machine.

## 🚀 Key Features

* **Real-time Monitoring**: Instant visualization of system resource usage.
* **Web-Based Dashboard**: Clean, responsive interface built with HTML/CSS.
* **Zero Dependency**: Runs entirely from the executable; no Python installation required on the client machine.
* **Portable Deployment**: Single-file distribution using PyInstaller.

## 🛠️ Tech Stack

* **Language**: Python 3
* **Backend Framework**: Flask (Werkzeug)
* **Frontend**: HTML, CSS, JavaScript
* **System Metrics**: `psutil` (Library for retrieving system utilization data)
* **Build Tool**: PyInstaller

## 📦 Installation & Usage

### For End Users (Executable)
1.  Download `Server_Monitor_Portable.exe` from the **Releases** section.
2.  Run the `.exe` file as Administrator (required to access full system metrics).
3.  Open your web browser and navigate to the address displayed in the terminal (default: `http://127.0.0.1:5000`).

### For Developers (Source Code)
To run or modify the source code locally:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/server-monitor-portable.git](https://github.com/your-username/server-monitor-portable.git)
    cd server-monitor-portable
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    python app.py
    ```

## ⚙️ Build Instructions

To recompile the application into a single executable after modifying the source code:

```bash
pyinstaller --noconfirm --onefile --windowed --add-data "templates;templates" --add-data "static;static" app.py
