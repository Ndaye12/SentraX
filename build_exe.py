"""
build_exe.py - Create EXE for SENTRAX with embedded API and templates
"""

import os
import sys
import shutil
import subprocess

print("="*60)
print("SENTRAX - CREATE EXE (avec dashboard intégré)")
print("="*60)

print("\n[1/4] Cleaning...")
for d in ["build", "dist"]:
    if os.path.exists(d):
        shutil.rmtree(d)

# Chemin de l'icone
icon_path = "assets/icons/sentrax.ico"
has_icon = os.path.exists(icon_path)

print("\n[2/4] Creating executable with embedded web files...")

cmd = [
    "pyinstaller",
    "--onefile",
    "--windowed",
    "--clean",
    "--noconfirm",
    "--name", "SENTRAX",
    "--add-data", "src;src",
    "--add-data", "web/templates;web/templates",
    "--add-data", "web/static;web/static",
    "--add-data", "web/api.py;web",
    "--collect-submodules", "src.scanners",
    "--collect-submodules", "src.plugins",
    "--hidden-import", "concurrent",
    "--hidden-import", "concurrent.futures",
    "--hidden-import", "sqlite3",
    "--hidden-import", "dns",
    "--hidden-import", "dns.resolver",
    "--hidden-import", "socket",
    "--hidden-import", "threading",
    "--hidden-import", "tkinter",
    "--hidden-import", "importlib",
    "--hidden-import", "json",
    "--hidden-import", "datetime",
    "--hidden-import", "random",
    "--hidden-import", "time",
    "--hidden-import", "math",
    "--hidden-import", "re",
    "--hidden-import", "ipaddress",
    "--hidden-import", "subprocess",
    "--hidden-import", "ssl",
    "--hidden-import", "hashlib",
    "--hidden-import", "uuid",
    "--hidden-import", "flask",
    "--hidden-import", "flask_cors",
    "--hidden-import", "requests",
    "--hidden-import", "jwt",
    "--hidden-import", "bcrypt",
    "--hidden-import", "pyotp",
    "--hidden-import", "qrcode",
    "--hidden-import", "reportlab",
    "launcher.py"
]

if has_icon:
    cmd.insert(6, "--icon")
    cmd.insert(7, icon_path)
    print(f"Icône trouvée: {icon_path}")
else:
    print("Icône par défaut")

try:
    subprocess.run(cmd, check=True)
    print("EXE created successfully!")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

print("\n[3/4] Verification...")
exe_path = "dist/SENTRAX.exe"
if os.path.exists(exe_path):
    size = os.path.getsize(exe_path) / (1024 * 1024)
    print(f"EXE created: {exe_path} ({size:.1f} MB)")
else:
    print("EXE not found")

print("\n" + "="*60)
print("BUILD COMPLETE!")
print("="*60)
print("\nExecutable is in 'dist/' folder")
print("Launch: double-click SENTRAX.exe")
print("\n✅ Dashboard est intégré dans l'EXE sur le port 8080 !")