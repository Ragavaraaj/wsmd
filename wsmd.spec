"""
PyInstaller spec file for the WSMD application
"""
import os
from pathlib import Path

# Define paths
root_dir = os.path.abspath(os.path.dirname(SPECPATH))
app_dir = os.path.join(root_dir, 'app')

# Define data files to include
datas = [
    # Include static files
    (os.path.join(app_dir, 'static'), 'app/static'),
    # Include template files
    (os.path.join(app_dir, 'templates'), 'app/templates'),
]

a = Analysis(
    ['app/main.py'],
    pathex=[root_dir],
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
