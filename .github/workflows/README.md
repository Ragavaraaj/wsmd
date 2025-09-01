# GitHub Workflows for WSMD

This directory contains GitHub Actions workflow configurations for building standalone executables of the WSMD application.

## Available Workflows

### WSMD Build and Release (`wsmd_build_and_release.yml`)

This combined workflow handles the entire process of building and releasing WSMD executables with the following features:

- **Job 1: Build Main Executable**

  - Creates a single-file executable for the WSMD server application
  - Includes all static files and templates
  - Uploads the executable as an artifact

- **Job 2: Build Dashboard Executable**

  - Creates a single-file executable for the WSMD Dashboard application
  - Builds as a windowed application (no console)
  - Uploads the executable as an artifact

- **Job 3: Build Raspberry Pi Executable**

  - Creates an executable for the WSMD server application that runs on Raspberry Pi Zero
  - Uses ARM-compatible build environment
  - Uploads the executable as an artifact

- **Job 4: Build Raspberry Pi Dashboard**

  - Creates an executable for the WSMD dashboard application that runs on Raspberry Pi Zero
  - Uses ARM-compatible build environment with Tkinter support
  - Uploads the executable as an artifact

- **Job 5: Create GitHub Release**
  - Automatically runs after both build jobs complete successfully
  - Only runs on the main branch, not on pull requests
  - Creates a GitHub release containing both executables
  - Adds detailed release notes

The workflow runs on each push to the main branch, on pull requests, or can be triggered manually.

## How to Use

### Running the Workflow

1. Push to the main branch or create a pull request to trigger the workflow automatically
2. Alternatively, navigate to the "Actions" tab in your GitHub repository
3. Select the "WSMD Build and Release" workflow
4. Click "Run workflow" and select the branch to build from

### Downloading Artifacts

1. Navigate to the "Actions" tab in your GitHub repository
2. Select the completed workflow run
3. Scroll down to the "Artifacts" section
4. Click on the artifact you want to download (`wsmd-executable` or `wsmd-dashboard-executable`)

### Accessing Releases

1. Navigate to the "Releases" section of your GitHub repository
2. Download the assets from the latest release
3. Each release contains four executables:
   - `wsmd.exe` (Windows server application)
   - `wsmd_dashboard.exe` (Windows dashboard application)
   - `wsmd-arm` (Raspberry Pi server application)
   - `wsmd_dashboard-arm` (Raspberry Pi dashboard application)

### Using the Executables

1. Extract the downloaded ZIP file

2. For the Windows main WSMD application:

   - Run `wsmd.exe` to start the server
   - The server will run on port 8000 by default
   - Access the web interface at http://localhost:8000

3. For the Windows Dashboard application:

   - Make sure the database file (`wsmd.db`) is in the same directory as the executable or in the parent directory
   - Run `wsmd_dashboard.exe` to start the dashboard
   - The dashboard will automatically update with device data from the database

4. For the Raspberry Pi WSMD application:

   - Transfer `wsmd-arm` to your Raspberry Pi Zero
   - Make it executable: `chmod +x wsmd-arm`
   - Run it: `./wsmd-arm`
   - The server will run on port 8000 by default
   - Access the web interface at http://[raspberry-pi-ip]:8000

5. For the Raspberry Pi Dashboard application:
   - Transfer `wsmd_dashboard-arm` to your Raspberry Pi Zero
   - Make it executable: `chmod +x wsmd_dashboard-arm`
   - Run it: `./wsmd_dashboard-arm`
   - The dashboard will display device data from the local database

## Notes

- Build artifacts are available for 30 days after the workflow run
- GitHub releases are permanent and provide a more stable way to distribute executables
- Each release includes a timestamp-based version number (e.g., v2025.09.02-123456)
- Releases are only created for pushes to the main branch, not for pull requests
- The workflow automatically prevents creating duplicate releases within a short time period
