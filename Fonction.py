import BME280
import VEML7700
import os
import DS3231
from machine import Pin, PWM, SoftI2C, SoftSPI, SDCard

i2c_sda = 21
i2c_scl = 22
i2c_baudrate = 100000
spi_baudrate = 100000
spi_polarity = 1
spi_phase = 0
spi_sck = 18
spi_mosi = 23
spi_miso = 19

i2c = SoftI2C(scl=Pin(i2c_scl), sda=Pin(i2c_sda), freq=i2c_baudrate)
spi = SoftSPI(baudrate=spi_baudrate, polarity=spi_polarity, phase=spi_phase, sck=Pin(spi_sck), mosi=Pin(spi_mosi), miso=Pin(spi_miso))

class bme280:
    def __init__(self,i2c):
        self.bme = BME280.BME280(i2c=i2c) #déclare le bme avec les broches du i2c
    def temp(self): #lie la température et renvoie la donné (string)
        temp = self.bme.temperature
        return temp
    def hum(self): #lie l'humidité et renvoie la donné (string)
        hum = self.bme.humidity
        return hum
    def pres(self): #lie la pression et renvoie la donné (string)
        pres = self.bme.pressure
        return pres
    
class veml7700:
    def __init__(self,i2c):
        self.veml = VEML7700.VEML7700(i2c=i2c)
    def lux(self): #lie la luminosité et renvoie la donné (int)
        lux = f"{self.veml.read_lux()}lux"
        return lux
    
class uSD:
    def __init__(self):
        self.sd = SDCard(slot=2, width=8)

        self.vfs = os.VfsFat(self.sd)
        os.mount(self.vfs, "/sd")
    def ecrire(self, data):
        data_string = f"Temperature: {data['Temperature']}, Humidity: {data['Humidity']}, Pression: {data['Pression']}, Luminositer: {data['Luminositer']}, Date: {data['Date']}\n"
        with open('/sd/data.txt', 'a') as file:  # Ouvre le fichier en mode append
            file.write(data_string)  # Écrit la string dans le fichier
            file.close()
            
class ds3231:
    def __init__(self, i2c):
        self.moduleRtc = DS3231.DS3231(i2c=i2c)
        
    def getDate(self):
        annee = self.moduleRtc.get_time([0])
        mois = self.moduleRtc.get_time([1])
        jour = self.moduleRtc.get_time([2])
        heure = self.moduleRtc.get_time([3])
        minute = self.moduleRtc.get_time([4])
        seconde = self.moduleRtc.get_time([5])
        jourSemaine = self.moduleRtc.get_time([6])
        if jourSemaine == 1:
            jourSemaine = "Lundi"
        elif jourSemaine == 2:
            jourSemaine = "Mardi"
        elif jourSemaine == 3:
            jourSemaine = "Mercredi"
        elif jourSemaine == 4:
            jourSemaine = "Jeudi"
        elif jourSemaine == 5:
            jourSemaine = "Vendredi"
        elif jourSemaine == 6:
            jourSemaine = "Samedi"
        elif jourSemaine == 7:
            jourSemaine = "Dimanche"
        else:
            pass
        self.date = f"Date: {jourSemaine, jour, mois, annee}, Heure: {heure, minute, seconde}\n"
        return self.date
    
    def setDate(self, YY, MM, mday, hh, mm, ss, wday, yday):
        dateManuel = [int(YY), int(MM), int(mday), int(hh), int(mm), int(ss), int(wday), int(yday)]
        self.date = self.moduleRtc.set_time(dateManuel)
        