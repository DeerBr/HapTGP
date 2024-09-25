#-------------------------------------------
#    Test_ESP32_USB_serial_periodic
#    ===================================
#
# Ce programme affiche le décodage d'une commande avec arguments par USB Série
# et contrôle les Dels rouge et verte de la carte protoTphys avec ESP32 devkit 
#
# Auteur:  Jude Levasseur
# Fichier: Test_ESP32_USB_serial_periodic.py
# Date:    25 août 2023
#-------------------------------------------
# Instructions:
#
# Chargez les modules ESP32_USB_serial_periodic_class.py et Decode_Commande_Arguments_class.py 
# dans la mémoire du ESP32.
#
# Pour fonctionnement dans Thonny:
# Connecter la carte protoTphys avec ESP32 et 
#  ... essayez en écrivant les commandes suivantes:
#      - DELR suivi d'un entier entre 0 et 100; pour duty circle Del rouge ex. "DELR 54";
#      - DELV suivi de ON ou OFF pour allumer/éteindre la Del Verte
#
#    NOTE: faire Ctrl-C pour terminer le programme et revenir au REPL de Thonny

# Pour fonctionnement avec un terminal externe (ex. Putty):
# Démarrez ce programme (quittez Thonny avec le programme en action) et ensuite
# démarrez un programme de terminal (ex. Putty) sur le PC et connectez au ESP32 ProtoTphys à 115200 baud.
#   ... essayez en écrivant les commandes suivantes:
#       - DELR suivi d'un entier entre 0 et 100; pour duty circle Del rouge ex. "DELR 54";
#       - DELV suivi de ON ou OFF pour allumer/éteindre la Del Verte
#
#    NOTE: faire Ctrl-C, Ctrl-C, Ctrl-D puis Ctrl-B sur le terminal du PC
#          pour terminer le programme MicroPython sur le ESP32. Vous pouvez revenir à Thonny.
#          

from machine import Pin, PWM, SoftI2C
from utime import sleep
from sys import exit
from ESP32_USB_serial_periodic_class import UsbSerialPeriodic
from Decode_Commande_Arguments_class import decodeur
import Fonction as fonc
import BME280


frequence = 1000                    # Fréquence du PWM Led Rouge= 1000Hz
LedRouge = PWM(Pin(4), frequence)   # PWM à D4 (Del rouge protoTphys)
LedRouge.duty(100)                  # Duty cycle initial, valide entre 0 à 1023
LedVerte = Pin(2, Pin.OUT)          # Broche 2 en sortie, Del verte du ESP32 (plaquette protoTPhys)
LedVerte.value(0)                   # Del verte initialement éteinte
# LedVerte_On_Off = True
i2c_sda = 21
i2c_scl = 22
i2c_baudrate = 100000

i2c = SoftI2C(scl=Pin(i2c_scl), sda=Pin(i2c_sda), freq=i2c_baudrate)

monserie = UsbSerialPeriodic(Echo=True, inBuffersize= 128) # Pour l'initialisation de l'objet de communication
monserie.start()                                           # Démarrage de la communication
 
mondecodeur = decodeur()            # Initialisation du décodeur de commande

ack = '*'
nak = '?'

# Mapping de valeur pour le retour d'un float
def map_float(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

# Mapping de valeur pour le retour d'un integer
def map_int(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

# Mapping de valeur pour le retour d'un integer avec limitation
def map_int_limit(x, i_m, i_M, o_m, o_M):
    return max(min(o_M, (x - i_m) * (o_M - o_m) // (i_M - i_m) + o_m), o_m)

date = fonc.ds3231(i2c)
uSD = fonc.uSD()
bme = fonc.bme280(i2c)
veml = fonc.veml7700(i2c)
try:
    while True:                             # Boucle infinie
        buffLine = monserie.getLineBuffer() # Obtenir une ligne de commande si présente
    
        # Affichage de la commande et des arguments
        if buffLine:
            Commande, NbArg, Arg = mondecodeur.decode(buffLine)
            print('Commande = ' + Commande)
            print('NbArg = ' + str(NbArg))
            if NbArg > 0:
                i=0
                for x in Arg:
                    print('Arg['+ str(i) +'] = ' + x)
                    i = i + 1
            
        # Contrôle des Dels rouge et verte
        if buffLine:                        
            Commande, NbArg, Arg = mondecodeur.decode(buffLine)
            
            if Commande == 'DELR' and NbArg >= 1:
                duty = map_int_limit(int(float(Arg[0])), 0, 100, 0, 1023)  # Mapping 0-100 à 0-1023
                LedRouge.duty(duty) # Change Duty cycle
                print(ack)
            
            elif Commande == 'DELV' and Arg[0] in ['ON', 'OFF']:
                if Arg[0] == 'ON':            
                   LedVerte.value(1)
                elif Arg[0] == 'OFF':
                   LedVerte.value(0)
                print(ack)
                
        # Contrôle des capteurs          
            elif Commande == 'BME' and NbArg >=1:
                if Arg[0] == 'Temp':
                    print("Temperature: ", bme.temp())
                    print(ack)
                elif Arg[0] == 'Hum':
                    print("Humidity: ", bme.hum())
                    print(ack)
                elif Arg[0] == 'Pres':
                    print("Pressure: ", bme.pres())
                    print(ack)
                else:
                    print(nak)
            elif Commande == 'VEML' and NbArg >=1:
                if Arg[0] == 'Lum':
                    print("Luminositer: ", veml.lux())
                    print(ack)
                else:
                    print(nak)
                    
        # Contrôle écriture carte uSD            
            elif Commande == 'Save':
                data = {
                    "Temperature" : bme.temp(),
                    "Humidity" : bme.hum(),
                    "Pression" : bme.pres(),
                    "Luminositer" : veml.lux()
                    }
                uSD.ecrire(data)
                print(ack)
            
        # Contrôle RTC
            elif Commande == 'Heure':
                print(date.Date())
                print(ack)                
            
            else:
                print(nak)

        sleep(1)
        
except KeyboardInterrupt:                   # trap Ctrl-C input
    print('Stop')
    monserie.stop()                   
    exit()
