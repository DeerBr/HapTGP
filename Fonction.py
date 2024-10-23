import BME280
import VEML7700
import os
import DS3231
import GC9A01
import time
from machine import Pin, PWM, SoftI2C, SoftSPI, SPI, SDCard
import vga2_bold_16x32 as font

i2c_sda = 21
i2c_scl = 22
i2c_baudrate = 100000
# uSD
uSD_cs = Pin(5, Pin.OUT)
spi_baudrate = 100000
spi_polarity = 0
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
spi = SoftSPI(baudrate=spi_baudrate, polarity=spi_polarity, phase=spi_phase, sck=Pin(spi_sck), mosi=Pin(spi_mosi), miso=Pin(spi_miso))
ecran_spi = SoftSPI(-1, miso=Pin(spi_miso), mosi=Pin(spi_mosi), sck=Pin(spi_sck))

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
    def __init__(self, uSD_cs):
        self.sd = SDCard(slot=2, width=8, cs=uSD_cs)
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
    
    def setDate(self, YY, MM, mday, hh, mm, ss, wday, yday):
        dateManuel = [int(YY), int(MM), int(mday), int(hh), int(mm), int(ss), int(wday), int(yday)]
        self.date = self.moduleRtc.set_time(dateManuel)
        
class Ecran:
    def __init__(self, ecran_spi, dc, ecran_cs, reset, backlight, rotation):
        self.ecran = GC9A01.GC9A01(ecran_spi, dc, ecran_cs, reset, backlight, rotation)
    def test(self):
        self.ecran.fill(GC9A01.color565(0, 0, 255))  # Remplir l'écran en bleu
        self.ecran.text(font,"GC9A01 Test", 30, 110,GC9A01.color565(255, 255, 255))
        time.sleep(5)
        self.ecran.fill(GC9A01.color565(0, 0, 0))  # Efface l'écran
    
        