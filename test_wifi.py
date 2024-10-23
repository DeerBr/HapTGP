import network
import time

station = network.WLAN(network.STA_IF)
station.active(True)

if not station.active():
    print("Erreur lors de l'activation du wifi")
    raise RuntimeError("Erreur lors de l'activation du wifi")

# Replace 'SSID' and 'PASSWORD' with your network credentials
station.connect('Deer', 'Deerdeer')

# Wait for the connection to establish
for _ in range(10):  # Wait 10 seconds
    if station.isconnected():
        print("Connexion WiFi réussie!")
        print(station.ifconfig())
        break
    time.sleep(1)
else:
    print("Connexion WiFi échouée.")