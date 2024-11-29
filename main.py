#-------------------------------------------
#    Plateforme HapTGP
#    ===================================
#
# Ce programme sert au contrôle de la plateforme HapTGP. Celle-ci permet la mesure de la température,
# de l'humidité, de la pression et de la luminosité. Il y a 2 bouton de contrôle (A et B) sur le dessus de la platforme et
# la protection autour de l'écran est rotatif. Ces rotation sont détecter à l'aide d'une capteur de champ magnétique.
#
# Auteur:  Déryck Brais
# Fichier: xxxxxxxxx
# Date:    29 novembre 2024
#-------------------------------------------
# Instructions:
#
# Chargez les modules xxxxxxxxx
#
# Pour fonctionnement dans Thonny:
# Connecter la carte protoTphys avec ESP32
#
#    NOTE: faire Ctrl-C pour terminer le programme et revenir au REPL de Thonny

# Pour fonctionnement avec alimentation externe:
# 	L'affichage de base est sur le menu principale (lumière des DEL bleu)
#	-Tourner le bouton principale pour déplacer le curseur de gauche
#	-Appuyer sur le bouton A pour entrer des le l'option indiquer par le cuseur
#	-Appuyer sur le bouton B pour retourner au menu principale
#
#Couleur des différent menu :
#	Menu principale : Bleu
#	BME280 : Blanc
#	VEML7700 : Rouge
#	Enregistrement sur micro uSD : Vert
#          

from machine import Pin, PWM, SoftI2C, SoftSPI, SPI
from utime import sleep
from sys import exit
import Fonction as fonc
import neopixel

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
# Bouton
boutonA = Pin(35, Pin.IN)
boutonB = Pin(34, Pin.IN)
#DEL
Del = Pin(25, Pin.OUT)

i2c = SoftI2C(scl=Pin(i2c_scl), sda=Pin(i2c_sda), freq=i2c_baudrate)
ecran_spi = SoftSPI(-1, miso=Pin(spi_miso), mosi=Pin(spi_mosi), sck=Pin(spi_sck))
spi = SoftSPI(baudrate=spi_baudrate, polarity=spi_polarity, phase=spi_phase, sck=Pin(spi_sck), mosi=Pin(spi_mosi), miso=Pin(spi_miso))

date = fonc.ds3231(i2c)
uSD = fonc.uSD(spi ,uSD_cs)
bme = fonc.bme280(i2c)
veml = fonc.veml7700(i2c)
ecran = fonc.Ecran(ecran_spi, dc, ecran_cs, reset, backlight, 0)
internet = fonc.wifi_connection('CAL-Techno', 'technophys123')
hall = fonc.hall_effect(i2c)
led = fonc.LED()

ecran.menu() # Premier affichage de l'écran
led.blue()
menu_pointer = 70
ecran.pointeur(menu_pointer)
prev_menu_pointer = 70
try:
    while True:                             # Boucle infinie
        prev_angle = hall.read()
        
        if hall.read() > (prev_angle + 10):
            menu_pointer += 20
            if menu_pointer == 130:
                menu_pointer = 70
        
        elif hall.read() < (prev_angle - 10):
            menu_pointer -= 20
            if menu_pointer == 50:
                menu_pointer = 110
        
        if prev_menu_pointer != menu_pointer:
            prev_menu_pointer = menu_pointer
            ecran.menu()
            ecran.pointeur(menu_pointer)
        
        if not boutonA.value():
            if menu_pointer == 70:
                ecran.print_BME(i2c)
                led.white()
            elif menu_pointer == 90:
                ecran.print_VEML(i2c)
                led.red()
            elif menu_pointer == 110:
                led.green()
                ecran.print_uSD(spi ,uSD_cs)
                data = {
                    "Temperature" : bme.temp(),
                    "Humidity" : bme.hum(),
                    "Pression" : bme.pres(),
                    "Luminositer" : veml.lux(),
                    "Date" : date.getDate()
                    }
                uSD.ecrire(data)
                ecran.menu()
                led.blue()
                ecran.pointeur(menu_pointer)
                
        if not boutonB.value():
            ecran.menu()
            led.blue()
            ecran.pointeur(menu_pointer)
        
except KeyboardInterrupt:                   # trap Ctrl-C input
    print('Stop')                   
    exit()
