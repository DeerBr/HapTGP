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

from machine import Pin, PWM, SoftI2C, SoftSPI, SPI
from utime import sleep
from sys import exit
from ESP32_USB_serial_periodic_class import UsbSerialPeriodic
from Decode_Commande_Arguments_class import decodeur
import vga2_bold_16x32 as font
import Fonction as fonc
import BME280

i2c_sda = 21
i2c_scl = 22
i2c_baudrate = 100000
# uSD
uSD_cs = Pin(5, Pin.OUT)
spi_baudrate = 100000
spi_polarity = 1
spi_phase = 0
# Ecran
spi_sck = 18
spi_mosi = 23
spi_miso = 19
dc = Pin(16, Pin.OUT)
ecran_cs = Pin(32, Pin.OUT)
reset = Pin(4, Pin.OUT)
backlight = Pin(2, Pin.OUT)
rotation = 0

i2c = SoftI2C(scl=Pin(i2c_scl), sda=Pin(i2c_sda), freq=i2c_baudrate)
ecran_spi = SoftSPI(-1, miso=Pin(spi_miso), mosi=Pin(spi_mosi), sck=Pin(spi_sck))
spi = SoftSPI(baudrate=spi_baudrate, polarity=spi_polarity, phase=spi_phase, sck=Pin(spi_sck), mosi=Pin(spi_mosi), miso=Pin(spi_miso))

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
uSD = fonc.uSD(uSD_cs)
bme = fonc.bme280(i2c)
veml = fonc.veml7700(i2c)
ecran = fonc.Ecran(ecran_spi, dc, ecran_cs, reset, backlight, 0)
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
                
        # Contrôle des capteurs          
            if Commande == 'BME' and NbArg >=1:
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
            elif Commande == 'Save' and NbArg ==0:
                uSD_cs.value(0)
                ecran_cs.value(1)
                data = {
                    "Temperature" : bme.temp(),
                    "Humidity" : bme.hum(),
                    "Pression" : bme.pres(),
                    "Luminositer" : veml.lux(),
                    "Date" : date.getDate()
                    }
                uSD.ecrire(data)
                print(ack)
            
        # Contrôle RTC
            elif Commande == 'Heure' and NbArg >=1:
                if Arg[0] == "get":
                    print(date.getDate())
                    print(ack)
                elif Arg[0] == "set":
                    YY, MM, mday, hh, mm, ss, wday, yday = Arg[1], Arg[2], Arg[3], Arg[4], Arg[5], Arg[6], Arg[7], Arg[8]
                    print(date.setDate(YY, MM, mday, hh, mm, ss, wday, yday))
                    print(ack)
                else:
                    print(nak)

        # Contrôle Ecran
            elif Commande == "Ecran" and NbArg >=1:
                if Arg[0] == "test":
                    uSD_cs.value(1)
                    ecran_cs.value(0)
                    ecran.test() 
                    print(ack)
                else:
                    print(nak)
        
        sleep(1)
        
except KeyboardInterrupt:                   # trap Ctrl-C input
    print('Stop')
    monserie.stop()                   
    exit()
