"""
-------------------------------------------
    Plateforme HapTGP
    ===================================

 Ce programme sert au contrôle de la plateforme HapTGP. Celle-ci permet la mesure de la température,
 de l'humidité, de la pression et de la luminosité. Il y a 2 bouton de contrôle (A et B) sur le dessus de la platforme et
 la protection autour de l'écran est rotatif. Ces rotation sont détecter à l'aide d'une capteur de champ magnétique.

 Auteur:  Déryck Brais
 Fichier: firmWare_HapTGP
 Date:    29 novembre 2024
-------------------------------------------
 Instructions:

 Chargez les modules xxxxxxxxx

 Pour fonctionnement dans Thonny:
 Connecter la carte protoTphys avec ESP32

    NOTE: faire Ctrl-C pour terminer le programme et revenir au REPL de Thonny

 Pour fonctionnement avec alimentation externe:
 	L'affichage de base est sur le menu principale (lumière des DEL bleu)
	-Tourner le bouton principale pour déplacer le curseur de gauche
	-Appuyer sur le bouton A pour entrer des le l'option indiquer par le cuseur
	-Appuyer sur le bouton B pour retourner au menu principale

 Couleur des différent menu :
	Menu principale : Bleu
	BME280 : Blanc
	VEML7700 : Rouge
	Enregistrement sur micro uSD : Vert

-----------------------------------------------------------------------------------
To do
-Corriger bug navigation menu (amélioré la fluidité)
-Ajout fonction sauvegarde de donner sur SD card à tous les 30 secondes
-Implémenter un rafraîchissement de l'écran automatique (update des données affiché)
-----------------------------------------------------------------------------------
"""
# **********************************************
# Importation des librairies
# **********************************************
from machine import Pin, PWM, SoftI2C, SoftSPI, SPI
from sys import exit
import Fonction as fonc
import array as arr
import buzzer, neopixel, utime

# **********************************************
# Variable global et variable de configuration
# **********************************************

# i2c
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
# DEL
Del = Pin(25, Pin.OUT)
# Minuterie et paramètre sauvegarde uSD
savingTimer = 0
savingDelay = 5000
etatSave = 0

# *******************************************
# Configuration pour le moteur
# *******************************************
PIN_GBM_EN = 13
PIN_GBM_IN1 = 14
PIN_GBM_IN2 = 27
PIN_GBM_IN3 = 26
PWM_FREQ = 30000	#Hz ... 11 bit de resolutions
coupleMot = 15		#Pour 20% après division par 100

pwm_in1 = PWM(Pin(PIN_GBM_IN1), freq=PWM_FREQ, duty=0)
pwm_in2 = PWM(Pin(PIN_GBM_IN2), freq=PWM_FREQ, duty=0)
pwm_in3 = PWM(Pin(PIN_GBM_IN3), freq=PWM_FREQ, duty=0)

#print(pwm_in1)
#print(pwm_in2)
#print(pwm_in3)

pwmSin = arr.array('I', [127, 110, 94, 78, 64, 50, 37, 26, 17, 10,
                         4, 1, 0, 1, 4, 10, 17, 26, 37, 50, 64, 78,
                         94, 110, 127, 144, 160, 176, 191, 204, 217,
                         228, 237, 244, 250, 253, 254, 255, 250, 244,
                         237, 228, 217, 204, 191, 176, 160, 144])
#print(pwmSin)
N = len(pwmSin)
#print(N)

elecPos = 0

pasActuel_IN1 = 0
pasActuel_IN2 = 16
pasActuel_IN3 = 32

gbm_en =  Pin(PIN_GBM_EN, Pin.OUT)
gbm_en.value(1)	#Driver activé au départ

# ********************************************
# Fonction pour faire bouger le moteur
# Auteur originel (crédit) : Richard Milette
# ********************************************
def gbmMove() :
   global elecPos
   global dirChampB
   global pasActuel_IN1
   global pasActuel_IN2
   global pasActuel_IN3
   global gbmDC
   
   elecPos = 1#Pour créer 7 "notchs" puisque nous avons 7 Pôles
   #elecPos = elecPos + 1	#Pour faire tourner le moteur
      
   OFFSET = 2
   
   pasActuel_IN1 = elecPos + OFFSET
   pasActuel_IN2 = pasActuel_IN1 + 16	#Déphasage de 120 degrés par rapport à la phase 1
   pasActuel_IN3 = pasActuel_IN1 + 32	#Déphasage de 240 degrés par rapport à la phase 1
   
   pasActuel_IN1 = pasActuel_IN1 % N	#Ramène la valeur entre 0 et 47 (Nombre de valeurs dans le tableau)
   pasActuel_IN2 = pasActuel_IN2 % N	#Ramène la valeur entre 0 et 47 (Nombre de valeurs dans le tableau)
   pasActuel_IN3 = pasActuel_IN3 % N	#Ramène la valeur entre 0 et 47 (Nombre de valeurs dans le tableau)
   
   pwm_in1.duty(int(((pwmSin[pasActuel_IN1]*1023)/255)*coupleMot/100))	#Map les valeurs du tableau de 0 à 255 à 0 à 1023 pour correspondre au Duty Cycle accepté
   pwm_in2.duty(int(((pwmSin[pasActuel_IN2]*1023)/255)*coupleMot/100))	#Map les valeurs du tableau de 0 à 255 à 0 à 1023 pour correspondre au Duty Cycle accepté
   pwm_in3.duty(int(((pwmSin[pasActuel_IN3]*1023)/255)*coupleMot/100))	#Map les valeurs du tableau de 0 à 255 à 0 à 1023 pour correspondre au Duty Cycle accepté
   
#    Permet de changer de direction en inversant la phase 1 avec la phase 3
#    pwm_in1.duty(int(((pwmSin[pasActuel_IN3]*1023)/255)*coupleMot/100))
#    pwm_in2.duty(int(((pwmSin[pasActuel_IN2]*1023)/255)*coupleMot/100))
#    pwm_in3.duty(int(((pwmSin[pasActuel_IN1]*1023)/255)*coupleMot/100))

# Configuration des différents port de communications
i2c = SoftI2C(scl=Pin(i2c_scl), sda=Pin(i2c_sda), freq=i2c_baudrate)
ecran_spi = SoftSPI(-1, miso=Pin(spi_miso), mosi=Pin(spi_mosi), sck=Pin(spi_sck))
spi = SoftSPI(baudrate=spi_baudrate, polarity=spi_polarity, phase=spi_phase, sck=Pin(spi_sck), mosi=Pin(spi_mosi), miso=Pin(spi_miso))

# Déclaration des objets
date = fonc.ds3231(i2c)
uSD = fonc.uSD(spi ,uSD_cs)
bme = fonc.bme280(i2c)
veml = fonc.veml7700(i2c)
ecran = fonc.Ecran(ecran_spi, dc, ecran_cs, reset, backlight, 0)
internet = fonc.wifi_connection('Deer', 'Deerdeer')
hall = fonc.hall_effect(i2c)
led = fonc.LED()
speaker = buzzer.BUZZER()

# ************************************
# Configuration pour le buzzer
# ************************************
tones = {
        "B0": 31, "C1": 33, "CS1": 35, "D1": 37, "DS1": 39, "E1": 41, "F1": 44, "FS1": 46, "G1": 49, "GS1": 52, "A1": 55, "S1": 58,
        "B1": 62, "C2": 65, "CS2": 69, "D2": 73, "DS2": 78, "E2": 82, "F2": 87, "FS2": 93, "G2": 98, "GS2": 104, "A2": 110, "AS2": 117,
        "B2": 123, "C3": 131, "CS3": 139, "D3": 147, "DS3": 156, "E3": 165, "F3": 175, "FS3": 185, "G3": 196, "GS3": 208,
        "A3": 220, "AS3": 233, "B3": 247, "C4": 262, "CS4": 277, "D4": 294, "DS4": 311, "E4": 330, "F4": 349, "FS4": 370,
        "G4": 392, "GS4": 415, "A4": 440, "AS4": 466, "B4": 494, "C5": 523, "CS5": 554, "D5": 587, "DS5": 622, "E5": 659,
        "F5": 698, "FS5": 740, "G5": 784, "GS5": 831, "A5": 880, "AS5": 932, "B5": 988, "C6": 1047, "CS6": 1109, "D6": 1175,
        "DS6": 1245, "E6": 1319, "F6": 1397, "FS6": 1480, "G6": 1568, "GS6": 1661, "A6": 1760, "AS6": 1865, "B6": 1976, "C7": 2093,
        "CS7": 2217, "D7": 2349, "DS7": 2489, "E7": 2637, "F7": 2794, "FS7": 2960, "G7": 3136, "GS7": 3322, "A7": 3520, "AS7": 3729,
        "B7": 3951, "C8": 4186, "CS8": 4435, "D8": 4699, "DS8": 4978
        }

save_song = ["B4","A5","P"]

# ************************************
# Première initialisation
# ************************************
ecran.menu(i2c) # Premier affichage de l'écran
date.setDate_ntp()
led.blue()
menu_pointer = 90
ecran.pointeur(menu_pointer)
prev_menu_pointer = 90
etatMenu = 0
savePointeur = 90
prev_savePointeur = 90

# ************************************
# Boucle infinie, code principal
# ************************************
try:
    while True:
        gbmMove()
        prev_angle = hall.read()
        
# -------Sélection du menu-------------------------
        
        if etatMenu == 0:
            if hall.read() > (prev_angle + 10):
                menu_pointer += 20
                if menu_pointer == 150:
                    menu_pointer = 90
            
            elif hall.read() < (prev_angle - 10):
                menu_pointer -= 20
                if menu_pointer == 70:
                    menu_pointer = 130
            
            if prev_menu_pointer != menu_pointer:
                prev_menu_pointer = menu_pointer
                ecran.menu(i2c)
                ecran.pointeur(menu_pointer)
        
# -------Logique de sélection menu-----------------        
        
        if not boutonA.value():
            if menu_pointer == 90:
                ecran.print_BME(i2c)
                led.white()
                etatMenu = 1
            elif menu_pointer == 110:
                ecran.print_VEML(i2c)
                led.red()
                etatMenu = 1
            elif menu_pointer == 130:
                ecran.print_uSD(i2c)
                led.green()
                speaker.playsong(save_song)
                data = {
                    "Temperature" : bme.temp(),
                    "Humidity" : bme.hum(),
                    "Pression" : bme.pres(),
                    "Luminositer" : veml.lux(),
                    "Date" : date.getDate()
                    }
                uSD.ecrire(data)
                ecran.menu(i2c)
                led.blue()
                ecran.pointeur(menu_pointer)

# -------Retour au menu principal-------------------

        if not boutonB.value():
            ecran.menu(i2c)
            led.blue()
            ecran.pointeur(menu_pointer)
            etatMenu = 0
            etatSave = 0
        
except KeyboardInterrupt:                   # trap Ctrl-C input
    print('Stop')                   
    exit()
