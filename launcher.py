import subprocess
import webbrowser
import time

# Lancer l'API Flask
process = subprocess.Popen(["python", "web/api.py"])

# Attendre que le serveur démarre
time.sleep(3)

# Ouvrir le dashboard
webbrowser.open("http://localhost:5000/dashboard")

process.wait()