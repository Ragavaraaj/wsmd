#!/bin/bash

# WSMD Installation Script
# This script downloads and installs the appropriate WSMD executable 
# from the GitHub releases page at https://github.com/Ragavaraaj/wsmd

set -e  # Exit immediately if a command exits with a non-zero status

OWNER="Ragavaraaj"
REPO="wsmd"
VERSION="$1"  # Optional, if not provided will download latest

echo "======================================"
echo "WSMD Installation Script"
echo "======================================"
echo "Repository: https://github.com/$OWNER/$REPO"
echo ""

# Create installation directory
INSTALL_DIR="$HOME/wsmd"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Determine system type
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
  if [[ $(uname -m) == "armv"* || $(uname -m) == "aarch"* ]]; then
    SYSTEM="raspberry-pi"
    SERVER_FILE="wsmd-arm"
    DASHBOARD_FILE="wsmd_dashboard-arm"
  else
    echo "This script currently only supports Raspberry Pi installations on Linux."
    echo "For other Linux systems, please build from source."
    exit 1
  fi
elif [[ "$OSTYPE" == "msys"* || "$OSTYPE" == "win"* || "$OSTYPE" == "cygwin"* ]]; then
  SYSTEM="windows"
  SERVER_FILE="wsmd.exe"
  DASHBOARD_FILE="wsmd_dashboard.exe"
else
  echo "Unsupported operating system: $OSTYPE"
  echo "This script supports Windows and Raspberry Pi installations only."
  exit 1
fi

echo "Detected system: $SYSTEM"
echo "Installing to: $INSTALL_DIR"

# Determine the download URL
if [[ -z "$VERSION" || "$VERSION" == "latest" ]]; then
  echo "Looking for latest release..."
  VERSION=$(curl -s "https://api.github.com/repos/$OWNER/$REPO/releases/latest" | grep -Po '"tag_name": "\K.*?(?=")')
  if [[ -z "$VERSION" ]]; then
    echo "Error: Could not determine latest version"
    exit 1
  fi
fi

echo "Using version: $VERSION"
echo "Fetching release information..."

# Get the release assets
RELEASE_INFO=$(curl -s "https://api.github.com/repos/$OWNER/$REPO/releases/tags/$VERSION")
SERVER_URL=$(echo "$RELEASE_INFO" | grep -Po '"browser_download_url": "\K[^"]*' | grep "$SERVER_FILE" | head -n 1)
DASHBOARD_URL=$(echo "$RELEASE_INFO" | grep -Po '"browser_download_url": "\K[^"]*' | grep "$DASHBOARD_FILE" | head -n 1)

if [[ -z "$SERVER_URL" || -z "$DASHBOARD_URL" ]]; then
  echo "Error: Could not find the required files in the release."
  echo "Make sure version $VERSION has builds for $SYSTEM."
  exit 1
fi

# Download server
echo "Downloading WSMD Server..."
curl -L -o "$SERVER_FILE" "$SERVER_URL"
chmod +x "$SERVER_FILE"
echo "✅ Downloaded server: $SERVER_FILE"

# Download dashboard
echo "Downloading WSMD Dashboard..."
curl -L -o "$DASHBOARD_FILE" "$DASHBOARD_URL"
chmod +x "$DASHBOARD_FILE"
echo "✅ Downloaded dashboard: $DASHBOARD_FILE"

# Create startup scripts
if [[ "$SYSTEM" == "raspberry-pi" ]]; then
  # Create server startup script
  cat > start-server.sh << EOF
#!/bin/bash
cd "$INSTALL_DIR"
./wsmd-arm
EOF
  chmod +x start-server.sh

  # Create dashboard startup script
  cat > start-dashboard.sh << EOF
#!/bin/bash
cd "$INSTALL_DIR"
./wsmd_dashboard-arm
EOF
  chmod +x start-dashboard.sh

  echo "Created startup scripts:"
  echo "- start-server.sh"
  echo "- start-dashboard.sh"
fi

echo ""
echo "======================================"
echo "Installation complete!"
echo "======================================"
echo ""
echo "WSMD Server and Dashboard have been installed to: $INSTALL_DIR"
echo ""
if [[ "$SYSTEM" == "raspberry-pi" ]]; then
  echo "To start the server:"
  echo "  $INSTALL_DIR/start-server.sh"
  echo ""
  echo "To start the dashboard:"
  echo "  $INSTALL_DIR/start-dashboard.sh"
else
  echo "To start the server:"
  echo "  Navigate to $INSTALL_DIR and run wsmd.exe"
  echo ""
  echo "To start the dashboard:"
  echo "  Navigate to $INSTALL_DIR and run wsmd_dashboard.exe"
fi
echo ""
echo "Note: The server runs on port 8000 by default"
echo "Access the web interface at: http://localhost:8000"
echo ""