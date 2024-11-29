import BME280, VEML7700, os, DS3231, GC9A01, time, network, ntptime, neopixel, SDCard
from machine import Pin, PWM, SoftI2C, SoftSPI, SPI
import vga1_8x8 as font

class bme280:
    def __init__(self,i2c):
        self.bme = BME280.BME280(i2c=i2c) #déclare le bme avec les broches du i2c
    def temp(self): #lis la température et renvoie la donné (string)
        tempBrute = self.bme.temperature
        temp = float(tempBrute.split('°')[0])
        temp = f"{(temp + 0.925):.2f} Celsius"
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
        self.blanc = GC9A01.WHITE
        self.noir = GC9A01.BLACK
    def clear(self):
        self.ecran.fill(GC9A01.color565(0, 0, 0))  # Efface l'écran
    def menu(self):
        self.ecran.fill(self.noir)
        self.ecran.text(font, "MENU", 110, 50, self.blanc)
        self.ecran.text(font, "1- BME280", 35, 70, self.blanc)
        self.ecran.text(font, "2- VEML7700", 35, 90, self.blanc)
        self.ecran.text(font, "3- uSD", 35, 110, self.blanc)
    def pointeur(self, point):
        self.ecran.text(font, ">", 25, int(point), self.blanc)
    def print_BME(self, i2c):
        self.ecran.fill(self.noir)
        self.ecran.text(font, "BME280", 110, 50, self.blanc)
        self.ecran.text(font, f"Température: " + bme280(i2c).temp(), 35, 70, self.blanc)
        self.ecran.text(font, "Humidité: " + bme280(i2c).hum(), 35, 90, self.blanc)
        self.ecran.text(font, "Pression: " + bme280(i2c).pres(), 35, 110, self.blanc)
    def print_VEML(self,i2c):
        self.ecran.fill(self.noir)
        self.ecran.text(font, "VEML7700", 110, 50, self.blanc)
        self.ecran.text(font, "Luminosité: " + veml7700(i2c).lux(), 35, 70, self.blanc)
    def print_uSD(self, spi, uSD_cs):
        self.ecran.fill(self.noir)
        self.ecran.text(font, "Enregistrement", 70, 130, self.blanc)
        
        
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
    
class LED:
    def __init__(self, n=4, p=25):
        self.led = neopixel.NeoPixel(Pin(p), n)
    def red(self):
        self.led[0] = (0,0,0)
        self.led[1] = (0,0,0)
        self.led[2] = (0,0,0)
        self.led[3] = (0,0,0)
        self.led.write()
        self.led[0] = (255,0,0)
        self.led[1] = (255,0,0)
        self.led[2] = (255,0,0)
        self.led[3] = (255,0,0)
        self.led.write()
    def green(self):
        self.led[0] = (0,0,0)
        self.led[1] = (0,0,0)
        self.led[2] = (0,0,0)
        self.led[3] = (0,0,0)
        self.led.write()
        self.led[0] = (0,255,0)
        self.led[1] = (0,255,0)
        self.led[2] = (0,255,0)
        self.led[3] = (0,255,0)
        self.led.write()
    def blue(self):
        self.led[0] = (0,0,0)
        self.led[1] = (0,0,0)
        self.led[2] = (0,0,0)
        self.led[3] = (0,0,0)
        self.led.write()
        self.led[0] = (0,0,255)
        self.led[1] = (0,0,255)
        self.led[2] = (0,0,255)
        self.led[3] = (0,0,255)
        self.led.write()
    def white(self):
        self.led[0] = (0,0,0)
        self.led[1] = (0,0,0)
        self.led[2] = (0,0,0)
        self.led[3] = (0,0,0)
        self.led.write()
        self.led[0] = (255,255,255)
        self.led[1] = (255,255,255)
        self.led[2] = (255,255,255)
        self.led[3] = (255,255,255)
        self.led.write()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        