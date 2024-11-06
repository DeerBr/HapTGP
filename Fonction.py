import BME280, VEML7700, os, DS3231, GC9A01, time, network, ntptime, SDCard
from machine import Pin, PWM, SoftI2C, SoftSPI, SPI
import vga1_8x8 as font

class bme280:
    def __init__(self,i2c):
        self.bme = BME280.BME280(i2c=i2c) #déclare le bme avec les broches du i2c
    def temp(self): #lis la température et renvoie la donné (string)
        temp = self.bme.temperature
        return temp
    def hum(self): #lis l'humidité et renvoie la donné (string)
        hum = self.bme.humidity
        return hum
    def pres(self): #lis la pression et renvoie la donné (string)
        pres = self.bme.pressure
        return pres
    
class veml7700:
    def __init__(self,i2c):
        self.veml = VEML7700.VEML7700(i2c=i2c)
    def lux(self): #lis la luminosité et renvoie la donné (int)
        try:
            lux = f"{self.veml.read_lux()}lux"
            return lux
        except Exception as e:
            print("Erreur lors de la lecture du VEML7700:", e)
    
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
        data_string = f"Temperature: {data['Temperature']}, Humidity: {data['Humidity']}, Pression: {data['Pression']}, Luminositer: {data['Luminositer']}, Date: {data['Date']}\n"
        try:
            # Ouvre le fichier en mode ajout et écrit la string data_string
            with open('/sd/data.txt', 'a') as file:
                file.write(data_string)
        except Exception as e:
            print("Erreur lors de l'ecriture sur la carte uSD:", e)
            
class ds3231:
    def __init__(self, i2c):
        self.moduleRtc = DS3231.DS3231(i2c=i2c)
        
    def getDate(self):
        
        buffer = bytearray(7)
        
        time_data = self.moduleRtc.get_time(buffer)

        print(f"Time data received: {time_data}")

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
        ntptime.host = 'ca.pool.ntp.org'
        ntptime.settime()
        ntp = time.gmtime(ntptime.time())
        print(ntp)
        self.moduleRtc.set_time(ntptime.time())
        
class Ecran:
    def __init__(self, ecran_spi, dc, ecran_cs, reset, backlight, rotation):
        self.ecran = GC9A01.GC9A01(ecran_spi, dc, ecran_cs, reset, backlight, rotation)
    def clear(self):
        self.ecran.fill(GC9A01.color565(0, 0, 0))  # Efface l'écran
    def menu(self):
        blanc = GC9A01.WHITE
        self.ecran.fill(GC9A01.BLACK)
        self.ecran.text(font, "MENU", 110, 50, blanc)
        self.ecran.text(font, "1- BME280", 35, 70, blanc)
        self.ecran.text(font, "2- VEML7700", 35, 90, blanc)
        self.ecran.text(font, "3- uSD", 35, 110, blanc)
        
class wifi_connection:
    def __init__(self, ssid, key):
        self.station = network.WLAN(network.STA_IF)
        self.station.active(True)
        if not self.station.active():
            print("erreur lors de l'activation du wifi")
            raise RuntimeError("erreur lors de l'activation du wifi")
        self.station.connect(ssid, key)
        try:
            self.station.isconnected()
        except Exception as e:
            print("Erreur lors de la connection internet:", e)
    def verif_connect(self):
        self.station.isconnected()
        