# GitHub Workflows for WSMD

This directory contains GitHub Actions workflow configurations for building standalone executables of the WSMD application.

## Available Workflows

### 1. Build Executable (`build_executable.yml`)

This workflow builds the main WSMD server application with the following features:

- Creates a single-file executable for Windows
- Includes all static files and templates
- Runs on each push to the main branch, on pull requests, or can be triggered manually

The executable will be available as an artifact named `wsmd-executable-[commit-sha]` and can be downloaded from the GitHub Actions page.

### 2. Build Dashboard (`build_dashboard.yml`)

This workflow builds the WSMD Dashboard application with the following features:

- Creates a single-file executable for Windows
- Builds as a windowed application (no console)
- Runs on each push to the main branch, on pull requests, or can be triggered manually

The executable will be available as an artifact named `wsmd-dashboard-executable-[commit-sha]` and can be downloaded from the GitHub Actions page.

## How to Use

### Running the Workflows

1. Push to the main branch or create a pull request to trigger builds automatically
2. Alternatively, navigate to the "Actions" tab in your GitHub repository
3. Select the workflow you want to run
4. Click "Run workflow" and select the branch to build from

### Downloading Artifacts

1. Navigate to the "Actions" tab in your GitHub repository
2. Select the completed workflow run
3. Scroll down to the "Artifacts" section
4. Click on the artifact you want to download (either `wsmd-executable-[commit-sha]` or `wsmd-dashboard-executable-[commit-sha]`)

### Using the Executables

1. Extract the downloaded ZIP file
2. For the main WSMD application:

   - Run `wsmd.exe` to start the server
   - The server will run on port 8000 by default
   - Access the web interface at http://localhost:8000

3. For the Dashboard application:
   - Make sure the database file (`wsmd.db`) is in the same directory as the executable or in the parent directory
   - Run `wsmd_dashboard.exe` to start the dashboard
   - The dashboard will automatically update with device data from the database

## Notes

- Artifacts are available for 30 days after the workflow run
- Each build is tagged with the commit SHA for easy identification
