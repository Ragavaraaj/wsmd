# Raspberry Pi Zero Device Manager

A comprehensive device management system for Raspberry Pi Zero with AP/LAN mode switching, role-based admin panel, and a Tkinter dashboard.

## Features

- WiFi Access Point (AP) mode when no WiFi connection is detected
- MAC address auto-detection for device management
- Role-based access control
- Web-based admin panel
- Fullscreen Tkinter dashboard
- Automatic key user bootstrapping on first run

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
├── dashboard/
│   └── tkinter_dashboard.py    # Tkinter fullscreen dashboard
└── requirements.txt            # Project dependencies
```

## Installation

1. Clone the repository to your Raspberry Pi Zero:

```bash
git clone https://github.com/yourusername/wsmd.git
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

3. Install the dependencies:

```bash
pip install -r requirements.txt
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

### Windows-Specific Setup Notes

When running this application on Windows (for development/testing), there are a few considerations:

1. The application creates a temporary directory at `~/wsmd_temp` to store the AP password file
2. The WiFi connection check will be simulated on Windows since `iwgetid` is not available
3. MAC address resolution is simulated on Windows using a deterministic algorithm based on IP address

If you encounter the error `FileNotFoundError: [Errno 2] No such file or directory: '\tmp\ap_password.txt'`, make sure you're using the latest version which uses a cross-platform temp directory path.

### Starting the Tkinter Dashboard

```bash
# Make sure the virtual environment is activated
# On Linux/Raspberry Pi:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Run the dashboard
cd wsmd
python -m dashboard.tkinter_dashboard
```

Press `Esc` to exit the dashboard.

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
ExecStart=/home/pi/wsmd/venv/bin/python -m dashboard.tkinter_dashboard
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

## License

MIT
