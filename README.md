# Wireless Sensor and Monitoring Device (WSMD) Management System

A comprehensive wireless sensor management system built with a Python backend, web-based admin panel, Tkinter dashboard, and ESP8266 Arduino devices.

## Features

- WiFi Access Point (AP) mode when no WiFi connection is detected
- MAC address auto-detection for device management
- Role-based access control with admin privileges
- Web-based admin panel for device configuration
- Fullscreen Tkinter dashboard for monitoring
- Automatic key user bootstrapping on first run
- ESP8266 Arduino integration for sensor data collection
- JSON-based communication between devices and server
- Cross-platform support (Windows and Raspberry Pi)

## Installation

This section explains how to install and set up the WSMD application on different platforms.

### Windows Installation

#### Automatic Installation

1. Download the installation script:

   - [Download install.bat](https://github.com/Ragavaraaj/wsmd/raw/main/scripts/install.bat)

2. Run the script:
   - Right-click on `install.bat` and select "Run as administrator"
   - The script will:
     - Download the latest WSMD server and dashboard executables
     - Create shortcuts on your desktop
     - Guide you through the installation process

#### Manual Installation

1. Go to the [Releases page](https://github.com/Ragavaraaj/wsmd/releases) on GitHub
2. Download the latest `wsmd.exe` and `wsmd_dashboard.exe` files
3. Place them in a folder of your choice
4. Run `wsmd.exe` to start the server
5. Run `wsmd_dashboard.exe` to start the dashboard application

### Raspberry Pi Installation

#### Automatic Installation

1. Open a terminal and run:

```bash
curl -sSL https://github.com/Ragavaraaj/wsmd/raw/main/scripts/install.sh | bash
```

2. The script will:
   - Download the appropriate ARM executables for Raspberry Pi
   - Make them executable
   - Create startup scripts

#### Manual Installation

1. Go to the [Releases page](https://github.com/Ragavaraaj/wsmd/releases) on GitHub
2. Download the latest `wsmd-arm` and `wsmd_dashboard-arm` files
3. Make them executable: `chmod +x wsmd-arm wsmd_dashboard-arm`
4. Run `./wsmd-arm` to start the server
5. Run `./wsmd_dashboard-arm` to start the dashboard application

### Installation from Source

#### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

#### Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/Ragavaraaj/wsmd.git
   cd wsmd
   ```

2. Set up a virtual environment (recommended):

   ```bash
   # Install venv if not already installed
   sudo apt-get install python3-venv

   # Create a virtual environment
   python -m venv venv

   # Activate the virtual environment
   # On Linux/Raspberry Pi:
   source venv/bin/activate
   # On Windows:
   # venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Project Structure

```
wsmd/
├── app/
│   ├── models/
│   │   └── database.py         # Database models and session management
│   ├── routers/
│   │   ├── admin.py            # Admin API endpoints
│   │   ├── auth.py             # Authentication endpoints
│   │   └── device.py           # Device-facing endpoints
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css      # Styles for web interface
│   │   └── js/
│   │       ├── dashboard.js    # Dashboard JavaScript
│   │       └── login.js        # Login JavaScript
│   ├── templates/
│   │   ├── dashboard.html      # Dashboard HTML template
│   │   └── login.html          # Login HTML template
│   ├── utils/
│   │   ├── auth.py             # Authentication utilities
│   │   └── network.py          # Network utilities
│   └── main.py                 # FastAPI application entry point
├── arduino/
│   └── wsmd_esp8266/
│       ├── wsmd_esp8266.ino           # Basic ESP8266 Arduino sketch
│       └── wsmd_esp8266_with_json.ino # ESP8266 sketch with JSON communication
├── dashboard/
│   └── main.py                 # Tkinter fullscreen dashboard
├── scripts/
│   ├── install.sh              # Installation script for Linux/Raspberry Pi
│   └── install.bat             # Installation script for Windows
└── requirements.txt            # Project dependencies
```

## Usage

### Starting the FastAPI Server

```bash
# Make sure the virtual environment is activated
# On Linux/Raspberry Pi:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Run the server
cd wsmd
python -m app.main
```

On first run, you'll be prompted to create a key user account.

### Starting the Tkinter Dashboard

```bash
# Make sure the virtual environment is activated
# On Linux/Raspberry Pi:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Run the dashboard
cd wsmd
python -m dashboard.main
```

Press `Esc` to exit the dashboard.

### First-time Setup

1. After starting the server, navigate to http://localhost:8000 in your web browser
2. Log in with the credentials as given while installing the software
3. It's strongly recommended to change the default password immediately after login

## ESP8266 Arduino Setup

1. Open the Arduino IDE and load one of the sketches from the `arduino/wsmd_esp8266/` directory:

   - `wsmd_esp8266.ino` - Basic sketch for sensor data collection
   - `wsmd_esp8266_with_json.ino` - Advanced sketch with JSON communication

2. Configure the sketch with your WiFi credentials and server information.

3. Upload the sketch to your ESP8266 device.

4. The device will automatically connect to your WiFi network and begin sending data to the server.

## API Endpoints

### Device-Facing Endpoints

- `PUT /hit` - Increment hit counter for device
- `POST /channel` - Request a channel for device

### Admin Endpoints (Authentication Required)

- `POST /admin/channel` - Update device channel
- `POST /admin/max-hit` - Set max hit count for device
- `POST /admin/user` - Create new user (key user only)
- `POST /admin/user/password` - Update user password (key user only)
- `GET /admin/devices` - Get list of all devices
- `GET /admin/users` - Get list of all users (key user only)

### Authentication

- `POST /token` - Obtain authentication token

## Running in Production

For production use, consider the following:

1. Update the `SECRET_KEY` in `app/utils/auth.py` with a secure random key
2. Set up a service to start the application automatically on boot
3. Use a proper reverse proxy like Nginx for production deployment

### Setting up as a Service

To run the application as a service on Raspberry Pi (using systemd):

1. Create a service file for the FastAPI server:

```bash
sudo nano /etc/systemd/system/wsmd-server.service
```

2. Add the following content (adjust paths as needed):

```
[Unit]
Description=Raspberry Pi Zero Device Manager Server
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/wsmd
ExecStart=/home/pi/wsmd/venv/bin/python -m app.main
Restart=always
RestartSec=5
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=wsmd-server

[Install]
WantedBy=multi-user.target
```

3. Create a service file for the Tkinter dashboard (if needed):

```bash
sudo nano /etc/systemd/system/wsmd-dashboard.service
```

4. Add the following content:

```
[Unit]
Description=Raspberry Pi Zero Device Manager Dashboard
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/wsmd
Environment="DISPLAY=:0"
ExecStart=/home/pi/wsmd/venv/bin/python -m dashboard.main
Restart=always
RestartSec=5
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=wsmd-dashboard

[Install]
WantedBy=multi-user.target
```

5. Enable and start the services:

```bash
sudo systemctl daemon-reload
sudo systemctl enable wsmd-server.service
sudo systemctl start wsmd-server.service
sudo systemctl enable wsmd-dashboard.service
sudo systemctl start wsmd-dashboard.service
```

## Windows-Specific Setup Notes

When running this application on Windows (for development/testing), there are a few considerations:

1. The application creates a temporary directory at `~/wsmd_temp` to store the AP password file
2. The WiFi connection check will be simulated on Windows since `iwgetid` is not available
3. MAC address resolution is simulated on Windows using a deterministic algorithm based on IP address

If you encounter the error `FileNotFoundError: [Errno 2] No such file or directory: '\tmp\ap_password.txt'`, make sure you're using the latest version which uses a cross-platform temp directory path.

## Troubleshooting

### Common Issues

- **Database errors**: Make sure the wsmd.db file is in the same directory as the executable or in the parent directory
- **Port conflicts**: If port 8000 is already in use, modify the code to use a different port
- **Dashboard not connecting**: Ensure the server is running and the database is accessible
- **ESP8266 Connection Problems**: Make sure your WiFi credentials are correct and the server is running on the expected IP address
- **Database Errors**: If you encounter database errors, try deleting the `wsmd.db` file and restarting the application to recreate the database schema
- **API Connectivity**: Ensure that the ESP8266 device can reach the server on the correct port

## Development

### Requirements

- Python 3.10+
- FastAPI
- SQLAlchemy
- Tkinter (for dashboard)
- Arduino IDE (for ESP8266 sketches)

### Database Schema

The application uses SQLite with the following main tables:

- Users - For authentication and role-based access
- Devices - For tracking connected ESP8266 devices
- SensorData - For storing data received from devices

### Contribution

Contributions are welcome! Please feel free to submit a Pull Request.

## Additional Resources

- [View the source code on GitHub](https://github.com/Ragavaraaj/wsmd)
- [Report issues or request features](https://github.com/Ragavaraaj/wsmd/issues)

## License

MIT

## Acknowledgments

- FastAPI framework
- Arduino community
- ESP8266 developers
