import subprocess
import random
import string
import re
import os
import platform
from pathlib import Path

# Constants
PI_MODEL_PATH = '/proc/device-tree/model'
PI_CPUINFO_PATH = '/proc/cpuinfo'

def is_raspberry_pi():
    """Check if the current device is a Raspberry Pi"""
    try:
        # On Raspberry Pi, the model information is in /proc/device-tree/model
        if os.path.exists(PI_MODEL_PATH):
            with open(PI_MODEL_PATH, 'r') as f:
                model = f.read()
                return 'raspberry pi' in model.lower()
        
        # Alternative check using platform information
        return platform.system() == 'Linux' and platform.machine().startswith('arm')
    except Exception:
        return False

def is_raspberry_pi_zero():
    """Check if the current device is a Raspberry Pi Zero"""
    try:
        # Check if it's a Raspberry Pi first
        if not is_raspberry_pi():
            return False
            
        # On Raspberry Pi Zero, the model information contains "Zero"
        if os.path.exists(PI_MODEL_PATH):
            with open(PI_MODEL_PATH, 'r') as f:
                model = f.read()
                return 'zero' in model.lower()
        
        # Alternative check using CPU info for Pi Zero
        with open(PI_CPUINFO_PATH, 'r') as f:
            cpuinfo = f.read()
            # Pi Zero has a single-core ARMv6 processor
            return 'ARMv6' in cpuinfo and cpuinfo.count('processor') == 1
    except Exception:
        return False

def check_wifi_connected():
    """Check if the Raspberry Pi is connected to WiFi"""
    try:
        result = subprocess.run(['iwgetid', '-r'], capture_output=True, text=True)
        return bool(result.stdout.strip())
    except Exception:
        return False

def resolve_mac_from_ip(ip_address):
    """Resolve MAC address from IP address using ARP table"""
    try:
        # On Raspberry Pi we would use:
        result = subprocess.run(['arp', '-a', ip_address], capture_output=True, text=True)
        mac_match = re.search(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', result.stdout)
        
        return mac_match.group(0) if mac_match else None
    except Exception as e:
        print(f"Error resolving MAC address: {e}")
        return None

def get_client_ip(request):
    """Get client IP address from FastAPI request"""
    # In production on Raspberry Pi, use:
    # return request.client.host
    
    # For development/testing:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    return request.client.host

def get_client_mac(request):
    """Get client MAC address from FastAPI request by resolving IP"""
    ip = get_client_ip(request)
    print(f"Client IP: {ip}")
    return resolve_mac_from_ip(ip)

def generate_strong_password(length=20):
    """Generate a strong random password"""
    chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    return ''.join(random.choice(chars) for _ in range(length))

def setup_ap_mode(ssid="PiDeviceManager"):
    """Setup Access Point mode on the Raspberry Pi"""
    # Generate a strong password for the AP
    password = generate_strong_password()
    
    # Use a cross-platform temp directory path
    temp_dir = Path(os.path.join(os.path.expanduser("~"), "wsmd_temp"))
    temp_dir.mkdir(exist_ok=True)
    password_file = temp_dir / "ap_password.txt"
    password_file.write_text(password)
    
    # Production configuration for Raspberry Pi
    if is_raspberry_pi():
        try:
            # Install required packages if not already installed
            subprocess.run(['apt-get', 'update'], check=True)
            subprocess.run(['apt-get', 'install', '-y', 'hostapd', 'dnsmasq'], check=True)
            
            # Stop services if running
            subprocess.run(['systemctl', 'stop', 'hostapd'], check=False)
            subprocess.run(['systemctl', 'stop', 'dnsmasq'], check=False)
            
            # Configure static IP for wlan0
            with open('/etc/dhcpcd.conf', 'a') as f:
                f.write('\n# WSMD AP Mode Configuration\n')
                f.write('interface wlan0\n')
                f.write('    static ip_address=192.168.4.1/24\n')
                f.write('    nohook wpa_supplicant\n')
            
            # Configure hostapd
            hostapd_conf = """
# WSMD hostapd configuration
interface=wlan0
driver=nl80211
ssid={}
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
""".format(ssid, password)
            
            with open('/etc/hostapd/hostapd.conf', 'w') as f:
                f.write(hostapd_conf)
            
            # Configure hostapd to use this config file
            with open('/etc/default/hostapd', 'w') as f:
                f.write('DAEMON_CONF="/etc/hostapd/hostapd.conf"\n')
            
            # Configure dnsmasq for DHCP server
            dnsmasq_conf = """
# WSMD dnsmasq configuration
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
domain=wlan
address=/wsmd.local/192.168.4.1
"""
            with open('/etc/dnsmasq.conf', 'w') as f:
                f.write(dnsmasq_conf)
            
            # Enable IP forwarding
            with open('/etc/sysctl.conf', 'a') as f:
                f.write('\n# WSMD IP forwarding\n')
                f.write('net.ipv4.ip_forward=1\n')
            
            # Apply sysctl changes
            subprocess.run(['sysctl', '-p'], check=True)
            
            # Restart networking
            subprocess.run(['systemctl', 'restart', 'dhcpcd'], check=True)
            
            # Enable and start services
            subprocess.run(['systemctl', 'unmask', 'hostapd'], check=True)
            subprocess.run(['systemctl', 'enable', 'hostapd'], check=True)
            subprocess.run(['systemctl', 'enable', 'dnsmasq'], check=True)
            subprocess.run(['systemctl', 'start', 'hostapd'], check=True)
            subprocess.run(['systemctl', 'start', 'dnsmasq'], check=True)
            
            print(f"""
=================================
ACCESS POINT MODE ACTIVATED
SSID: {ssid}
Password: {password}
IP Address: 192.168.4.1
=================================
            """)
        except Exception as e:
            print(f"Error configuring AP mode: {e}")
            # Fall back to simulated mode if configuration fails
            print(f"""
=================================
SIMULATED ACCESS POINT MODE
SSID: {ssid}
Password: {password}
=================================
            """)
    else:
        # Simulation mode for non-Raspberry Pi systems
        print(f"""
=================================
SIMULATED ACCESS POINT MODE
SSID: {ssid}
Password: {password}
=================================
        """)
    
    return password

def next_available_order(db_session):
    """Find the next available order number from the database"""
    from app.models.database import Device
    
    # Get the highest order currently in use
    highest_order = db_session.query(Device).order_by(Device.order.desc()).first()
    
    if highest_order is None or highest_order.order == 0:
        return 1
    
    return highest_order.order + 1
