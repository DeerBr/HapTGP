from machine import Pin, SPI, SoftSPI
import vga2_bold_16x32 as font
import GC9A01
import time

# Configuration SPI
spi = SoftSPI(-1, miso=Pin(19), mosi=Pin(23), sck=Pin(18))
affichage = GC9A01.GC9A01(spi, dc=Pin(16, Pin.OUT), cs=Pin(32, Pin.OUT), reset=Pin(4, Pin.OUT), backlight=Pin(2, Pin.OUT), rotation=0)

# Test de l'affichage
affichage.fill(GC9A01.color565(0, 0, 255))  # Remplir l'écran en bleu
affichage.text(font,"GC9A01 Test", 30, 110,GC9A01.color565(255, 255, 255))
time.sleep(5)
affichage.fill(GC9A01.color565(0, 0, 0))  # Efface l'écran
