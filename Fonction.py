# **********************************************
# Importation des librairies
# **********************************************
import BME280, VEML7700, os, DS3231, GC9A01, time, network, ntptime, neopixel, SDCard, utime
from machine import Pin, PWM, SoftI2C, SoftSPI, SPI, PWM
import vga1_8x8 as font

# **********************************************
# Fonction bme280
# Argument nécessaire :
# - Paramètre pour communication i2c contenant la broche d'horloge, celle de data ainsi que le fréquence
# Module inclue:
# - temp : lecture de la température ambiante en °C avec 2 décimale
# - hum : lecture de l'humidité ambiante en % avec 2 décimale
# - pres : lecture de la pression en hectoPascal avec 2 décimale
# Fonctionnalité supplémentaire intrinsèque :
# **********************************************
class bme280:
    def __init__(self,i2c):
        self.bme = BME280.BME280(i2c=i2c) #déclare le bme avec les broches du i2c
    def temp(self): #lis la température et renvoie la donné (string)
        tempBrute = self.bme.temperature
        temp = float(tempBrute.split('°')[0])
        print(temp)
        temp = f"{(temp + 1.1):.2f} Celsius"
        return temp
    def hum(self): #lis l'humidité et renvoie la donné (string)
        hum = self.bme.humidity
        return hum
    def pres(self): #lis la pression et renvoie la donné (string)
        pres = self.bme.pressure
        return pres

# **********************************************
# Fonction : veml7700
# Argument nécessaire :
# - Paramètre pour communication i2c contenant la broche d'horloge, celle de data ainsi que le fréquence
# Module inclue:
# - lux : lecture de la luminosité en lux en nombre entier
# Fonctionnalité supplémentaire intrinsèque :
# - Détection d'erreur automatique (inclue dans la librairie du veml7700)
# **********************************************
class veml7700:
    def __init__(self,i2c):
        self.veml = VEML7700.VEML7700(i2c=i2c)
    def lux(self): #lis la luminosité et renvoie la donné (int)
        try:
            donneBrute = (6.5453 * self.veml.read_lux())
            lux = f"{donneBrute}lux"
            return lux
        except Exception as e:
            errorCode = f"Erreur lors de la lecture du VEML7700: {e}"
            print(errorCode)
            return errorCode
        
# **********************************************
# Fonction : uSD
# Argument nécessaire :
# - Paramètre pour communication spi contenant baudrate, polarité, phase, clock, miso et mosi
# - Chip select
# Module inclue :
# - ecrire : Écrit dans un fichier texte les données capté par les différent module ainsi que la date
# 	Argument : data (dictionnaire)
# Fonctionnalité supplémentaire intrinsèque :
# - Détection d'erreur lors de l'initialisation de la carte et/ou de l'écriture sur celle-ci
# **********************************************
class uSD:
    def __init__(self, spi, uSD_cs):
        self.sd = SDCard.SDCard(spi, cs=uSD_cs)
         # Try mounting the SD card filesystem
        try:
            os.mount(self.sd, "/sd")
            print("Cart uSD monter avec succes")
        except Exception as e:
            print("Erreur lors du montage de la carte uSD:", e)
    def ecrire(self, data):
        data_string = f"Temperature, {data['Temperature']}, Humidity, {data['Humidity']}, Pression, {data['Pression']}, Luminositer, {data['Luminositer']}, Date, {data['Date']}\n"
        try:
            # Ouvre le fichier en mode ajout et écrit la string data_string
            with open('/sd/data.txt', 'a') as file:
                file.write(data_string)
        except Exception as e:
            print("Erreur lors de l'ecriture sur la carte uSD:", e)        

# **********************************************
# Fonction : ds3231
# Argument nécessaire :
# - Paramètre pour communication i2c contenant la broche d'horloge, celle de data ainsi que le fréquence
# Module inclue :
# - getDate : Va chercher l'heure et la date dans le module RTC et le traduit en format humain jourDeLaSemaine, jour/mois/année, heure:minute:seconde
# - setDate_manual : Permet de donner manuellement l'heure au module RTC,
# 	Argument d'entré : année, mois, jour, heure, minute, seconde, jourDeLaSemaine, # du jour dans l'année
# - setDate_ntp : Permet de donner la date et l'heure au module RTC via un serveur ntp (serveur en question : pool.ntp.org )
# - format_ecran1 : Formatte la date afin de pouvoir l'inscrire sur l'écran de la plateforme HapTGP ( jourSemaine , année/mois/jour )
# - format_ecran2 : Formatte l'heure afin de pouvoir l'inscrire sur la plateforme HapTGP ( hh:min )
# Fonctionnalité supplémentaire intrinsèque :
# - Tente la connexion et l'obtention de la date et l'heure sur le serveur ntp à 3 reprise, indique le code d'erreur si une tentative échoue
# (non bloquant, sortie automatique de la fonction après le nombre d'essaie donnée (variable "nbEssaie" dans module "setDate_ntp"))
# **********************************************
class ds3231:
    def __init__(self, i2c):
        self.moduleRtc = DS3231.DS3231(i2c=i2c)
        
    def getDate(self):
        
        buffer = bytearray(7)
        
        time_data = self.moduleRtc.get_time(buffer)

        #print(f"Time data received: {time_data}")

        annee = time_data[0]
        mois = time_data[1]
        jour = time_data[2]
        heure = time_data[3]
        minute = time_data[4]
        seconde = time_data[5]
        jourSemaine = time_data[6]
        
        joursSemaine = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
 
        jourSemaine = joursSemaine[jourSemaine]

        # Formatage de la date et de l'heure
        self.date = f"{jourSemaine}, {jour}/{mois}/{annee}, Heure: {heure}:{minute}:{seconde}"
        return self.date
    
    def setDate_manual(self, YY, MM, mday, hh, mm, ss, wday, yday):
        dateManuel = [int(YY), int(MM), int(mday), int(hh), int(mm), int(ss), int(wday), int(yday)]
        self.date = self.moduleRtc.set_time(dateManuel)
    
    def setDate_ntp(self):
        ntptime.host = 'pool.ntp.org'
        nbEssaie = 3
        for essaie in range(nbEssaie):
            try:
                ntptime.settime()
                ntp = utime.gmtime(ntptime.time() + (-5*3600))
                print("NTP Time Synchronized:", ntp)
                self.moduleRtc.set_time(ntp)
                break
            except OSError as e:
                print(f"Essaie {essaie + 1} failed: {e}")
                if essaie + 1 == nbEssaie:
                    print("synchronisation NTP échouer après les essaies")
                else:
                    utime.sleep(5)  # Delay before retrying
    def format_ecran1(self):
        buffer = bytearray(7)
        
        time_data = self.moduleRtc.get_time(buffer)

        #print(f"Time data received: {time_data}")

        annee = time_data[0]
        mois = time_data[1]
        jour = time_data[2]
        heure = time_data[3]
        minute = time_data[4]
        seconde = time_data[5]
        jourSemaine = time_data[6]
        
        joursSemaine = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
 
        jourSemaine = joursSemaine[jourSemaine]
        
        self.infoJour = f"{jourSemaine}, {jour}/{mois}/{annee}"
        
        return self.infoJour
        
    def format_ecran2(self):
        buffer = bytearray(7)
        
        time_data = self.moduleRtc.get_time(buffer)

        #print(f"Time data received: {time_data}")

        annee = time_data[0]
        mois = time_data[1]
        jour = time_data[2]
        heure = time_data[3]
        minute = time_data[4]
        seconde = time_data[5]
        jourSemaine = time_data[6]
        
        self.infoHeure = f"{heure}:{minute}"
        
        return self.infoHeure

# **********************************************
# Fonction : Ecran
# Argument nécessaire :
# - Paramètre pour communication spi contenant le mode, miso, mosi et clock
# - Broche de data (pour écran TFT)
# - Chip select
# - Broche de reset
# - Broche du backlight
# - valeur de rotation de l'écran (pour tourner l'affichage)
# Module inclue :
# clear : Efface tous l'écran en remplissant l'affichage de noir
# - menu : Affiche le menu principale, fond noir écriture blanche
# 	Argument : Paramètre pour communication i2c (pour DS3231)
# - pointeur : Gère l'affichage du pointeur (module indépendant pour réutilisation dans de future sous-menu / option)
# - print_BME : Affiche sur l'écran les lecture du BME280, soit température, humidité et pression, fond noir écriture blanche
# 	Argument : Paramètre pour communication i2c (pour DS3231, BME280)
# - print_VEML : Affiche sur l'écran les lecture du VEML7700, soit la luminosité, fond noir écriture blanche
# 	Argument : Paramètre pour communication i2c (pour DS3231, VEML7700)
# - print_uSD : Affiche sur l'écran l'état de l'enregistrement sur la carte micro-SD
# 	Argument : Paramètre pour communication i2c (pour DS3231)
# Fonctionnalité supplémentaire intrinsèque :
# - Fonctionnalité intrinsèque au Fonction appeler : ds3231/bme280/veml7700
# **********************************************
class Ecran:
    def __init__(self, ecran_spi, dc, ecran_cs, reset, backlight, rotation):
        self.ecran = GC9A01.GC9A01(ecran_spi, dc, ecran_cs, reset, backlight, rotation)
        self.blanc = GC9A01.WHITE
        self.noir = GC9A01.BLACK
    def clear(self):
        self.ecran.fill(GC9A01.color565(0, 0, 0))  # Efface l'écran
    def menu(self, i2c):
        self.ecran.fill(self.noir)
        self.ecran.text(font, ds3231(i2c).format_ecran1(), 50, 30, self.blanc)
        self.ecran.text(font, ds3231(i2c).format_ecran2(), 50, 50, self.blanc)
        self.ecran.text(font, "MENU", 110, 70, self.blanc)
        self.ecran.text(font, "1- BME280", 35, 90, self.blanc)
        self.ecran.text(font, "2- VEML7700", 35, 110, self.blanc)
        self.ecran.text(font, "3- Sauvegarde", 35, 130, self.blanc)
    def pointeur(self, point):
        self.ecran.text(font, ">", 25, int(point), self.blanc)
    def print_BME(self, i2c):
        self.ecran.fill(self.noir)
        self.ecran.text(font, ds3231(i2c).format_ecran1(), 50, 30, self.blanc)
        self.ecran.text(font, ds3231(i2c).format_ecran2(), 50, 50, self.blanc)
        self.ecran.text(font, "BME280", 110, 70, self.blanc)
        self.ecran.text(font, f"Température: " + bme280(i2c).temp(), 35, 90, self.blanc)
        self.ecran.text(font, "Humidité: " + bme280(i2c).hum(), 35, 110, self.blanc)
        self.ecran.text(font, "Pression: " + bme280(i2c).pres(), 35, 130, self.blanc)
    def print_VEML(self,i2c):
        self.ecran.fill(self.noir)
        self.ecran.text(font, ds3231(i2c).format_ecran1(), 50, 30, self.blanc)
        self.ecran.text(font, ds3231(i2c).format_ecran2(), 50, 50, self.blanc)
        self.ecran.text(font, "VEML7700", 110, 70, self.blanc)
        self.ecran.text(font, "Luminosité: " + veml7700(i2c).lux(), 35, 90, self.blanc)
    def print_uSD(self, i2c):
        self.ecran.fill(self.noir)
        self.ecran.text(font, ds3231(i2c).format_ecran1(), 50, 30, self.blanc)
        self.ecran.text(font, ds3231(i2c).format_ecran2(), 50, 50, self.blanc)
        self.ecran.text(font, "Sauvegarde", 110, 70, self.blanc)
# ---------Affichage pour option d'eregistrement automatique (à implémenter)----------
#         self.ecran.text(font, "Activer", 35, 90, self.blanc)
#         self.ecran.text(font, "Désactiver", 35, 110, self.blanc)
# ------------------------------------------------------------------------------------
        
# **********************************************
# Fonction : wifi_connection
# Argument nécessaire :
# - Nom du réseau wifi à connecter
# - Mot de passe du réseau (None par défaut)
# Module inclue :
# - verif_connect : Permet de vérifier la connxion internet
# Fonctionnalité supplémentaire intrinsèque :
# - Vérification de la connexion lors de celle-ci et impression du code d'erreur dans le moniteur série s'il y a lieu
# **********************************************

class wifi_connection:
    def __init__(self, ssid, key=None):
        self.station = network.WLAN(network.STA_IF)
        self.station.active(True)
        if not self.station.active():
            print("erreur lors de l'activation du wifi")
            raise RuntimeError("erreur lors de l'activation du wifi")
        self.station.connect(ssid, key)
        try:
            if self.station.isconnected():
                print("Connexion internet établie")
        except Exception as e:
            print("Erreur lors de la connection internet:", e)
    def verif_connect(self):
        try:
            if self.station.isconnected():
                print("Connexion internet établie")
        except Exception as e:
            print("Erreur lors de la connection internet:", e)
        
# **********************************************
# Fonction : hall_effect
# Argument nécessaire : Paramètre pour communication i2c
# Module inclue :
# read : Lecture de l'état des indicateur MSB et LSB du capteur effet Hall et calcul de l'angle résultant
# Fonctionnalité supplémentaire intrinsèque :
# Auteur originel (crédit): Richard Milette
# **********************************************
class hall_effect:
    def __init__(self, i2c):
        self.i2c = i2c
        
        # Adresse du capteur
        self.adresse = 0x22

        # Configuration des registres du capteur
        self.i2c.writeto_mem(self.adresse, 0x00, bytes([0x14]))  # Configuration initiale
        self.i2c.writeto_mem(self.adresse, 0x02, bytes([0x79]))  
        self.i2c.writeto_mem(self.adresse, 0x08, bytes([0xA6]))  
        self.i2c.writeto_mem(self.adresse, 0x01, bytes([0x22])) 
        self.i2c.writeto_mem(self.adresse, 0x03, bytes([0x04])) 
        
    def read(self):
        self.msb = self.i2c.readfrom_mem(self.adresse, 0x19, 1)[0]  # Lire MSB
        self.lsb = self.i2c.readfrom_mem(self.adresse, 0x1A, 1)[0]  # Lire LSB
    
        # Calcul de l'angle 
        self.angle_entier = ((self.msb & 0x1F) << 4) | ((self.lsb & 0xF0) >> 4)
        self.angle_frac = (self.lsb & 0x0F) / 16.0
        angle = self.angle_entier + self.angle_frac
        
        return angle

# **********************************************
# Fonction : LED
# Argument nécessaire : aucun
# Module inclue :
# - red : Éteint les 4 DEL puis les allume en rouge a faible puissance (25 sur 255)
# - green : Éteint les 4 DEL puis les allume en vert a la moitié de la puissance (127 sur 255)
# - blue : Éteint les 4 DEL puis les allume en bleu a la moitié de la puissance (127 sur 255)
# - white : Éteint les 4 DEL puis les allume en blanc a la moitié de la puissance (127 sur 255)
# - off : Éteint les 4 DEL
# Fonctionnalité supplémentaire intrinsèque :
# **********************************************
class LED:
    def __init__(self, n=4, p=25):
        self.led = neopixel.NeoPixel(Pin(p), n)
    def red(self):
        self.led[0] = (0,0,0)
        self.led[1] = (0,0,0)
        self.led[2] = (0,0,0)
        self.led[3] = (0,0,0)
        self.led.write()
        self.led[0] = (25,0,0)
        self.led[1] = (25,0,0)
        self.led[2] = (25,0,0)
        self.led[3] = (25,0,0)
        self.led.write()
    def green(self):
        self.led[0] = (0,0,0)
        self.led[1] = (0,0,0)
        self.led[2] = (0,0,0)
        self.led[3] = (0,0,0)
        self.led.write()
        self.led[0] = (0,127,0)
        self.led[1] = (0,127,0)
        self.led[2] = (0,127,0)
        self.led[3] = (0,127,0)
        self.led.write()
    def blue(self):
        self.led[0] = (0,0,0)
        self.led[1] = (0,0,0)
        self.led[2] = (0,0,0)
        self.led[3] = (0,0,0)
        self.led.write()
        self.led[0] = (0,0,127)
        self.led[1] = (0,0,127)
        self.led[2] = (0,0,127)
        self.led[3] = (0,0,127)
        self.led.write()
    def white(self):
        self.led[0] = (0,0,0)
        self.led[1] = (0,0,0)
        self.led[2] = (0,0,0)
        self.led[3] = (0,0,0)
        self.led.write()
        self.led[0] = (127,127,127)
        self.led[1] = (127,127,127)
        self.led[2] = (127,127,127)
        self.led[3] = (127,127,127)
        self.led.write()
    def off(self):
        self.led[0] = (0,0,0)
        self.led[1] = (0,0,0)
        self.led[2] = (0,0,0)
        self.led[3] = (0,0,0)
        self.led.write()

# **********************************************
# Fonction : BUZZER
# Argument nécessaire : aucun
# Module inclue :
# - playtone : envoie une puissance PWM ainsi qu'une fréquence à émettre sur la broche contrôlant le buzzer
# 	Argument : fréquence
# - bequiet : envoie une puissance PWM sur la broche contrôlant le buzzer afin d'éliminer les bruit parasite lorsque celui-ci n'est pas en fonction
# - playsong : joue les différente fréquence (en utilisant "playtone") selon les notes demander, reconnait la lettre "P" et déclanche "bequiet" lors
# 			   l'interprétation de "P"
# 	Argument : Musicalité à jouer (List)
# Fonctionnalité supplémentaire intrinsèque :
# Auteur originel (crédit) : Richard Milette
# **********************************************
class BUZZER:
    def __init__(self):
        self.buzzer = PWM(Pin(17))

        self.tones = {
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

        self.save_song = ["B4","A5"]
        
    def playtone(self,frequency):
        self.buzzer.duty_u16(5000)
        self.buzzer.freq(frequency)

    def bequiet(self):
#         self.buzzer.duty_u16(0)
        self.buzzer.duty_u16(65534) # Permet d'éliminer le bruit quand le buzzer est désactivé. Ne pas écrire 65535 !!

    def playsong(self,mysong):
        for i in range(len(mysong)):
            if (mysong[i] == "P"):
                self.bequiet()
            else:
                self.playtone(tones[mysong[i]])
            utime.sleep_ms(300)
        self.bequiet()
        
        