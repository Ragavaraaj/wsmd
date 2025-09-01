"""
PyInstaller spec file for the WSMD application
"""
import os
import sys
from pathlib import Path

# Define paths - use relative paths to work in any environment
base_dir = os.path.dirname(SPECPATH)
print(f"Initial base directory: {base_dir}")

# In GitHub Actions, the repository is checked out to a subfolder with its name
if os.path.exists(os.path.join(base_dir, 'wsmd')):
    # For GitHub Actions environment
    base_dir = os.path.join(base_dir, 'wsmd')
    print(f"Updated base directory for GitHub Actions: {base_dir}")

app_dir = os.path.join(base_dir, 'app')

# Debug info to help troubleshoot
print(f"Base directory: {base_dir}")
print(f"App directory: {app_dir}")
print(f"Static directory exists: {os.path.exists(os.path.join(app_dir, 'static'))}")
print(f"Templates directory exists: {os.path.exists(os.path.join(app_dir, 'templates'))}")

# Define data files to include - with path validation
static_path = os.path.join(app_dir, 'static')
templates_path = os.path.join(app_dir, 'templates')

datas = []
# Add paths only if they exist
if os.path.exists(static_path):
    datas.append((static_path, 'app/static'))
else:
    print(f"WARNING: Static directory not found at {static_path}")
    
if os.path.exists(templates_path):
    datas.append((templates_path, 'app/templates'))
else:
    print(f"WARNING: Templates directory not found at {templates_path}")

# List directory contents to aid debugging
print("Contents of base directory:")
for item in os.listdir(base_dir):
    print(f"  {item}")

if os.path.exists(app_dir):
    print("Contents of app directory:")
    for item in os.listdir(app_dir):
        print(f"  {item}")
else:
    print(f"App directory not found: {app_dir}")

a = Analysis(
    ['app/main.py'],
    pathex=[base_dir],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'uvicorn.lifespan.off',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.protocols.websockets.wsproto_implementations',
        'uvicorn.protocols.websockets.websockets_implementations',
        'email.mime.image'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='wsmd',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
