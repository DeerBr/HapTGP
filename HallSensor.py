from machine import I2C

# TMAG5273B1 default address.
I2C_ADDR = 0x22

# TMAG5273B1 registers.
TMAG5273B1_MAG_X_MSB = 0x00 # Register for X-axis magnetic field (Most Significant Byte)
TMAG5273B1_MAG_Y_MSB = 0x02 # Register for Y-axis magnetic field (MSB)
TMAG5273B1_MAG_Z_MSB = 0x04 # Register for Z-axis magnetic field (MSB)
TMAG5273B1_TEMP_MSB = 0x06 # Register for temperature (MSB)

class TMAG5273B1:
    
    def __init__(self, i2c=None):
        #Création du périphérique I2C
        if i2c is None:
            raise ValueError('Un objet i2c est neccessaire.')
        else:
            self.i2c = i2c
        self.address = I2C_ADDR
        self.init_sensor()
        
    def write_register(self, reg, data):
        self.I2C.writeto_mem(self.address, reg, bytes([data]))
        
    def read_register(self, reg, length=1):
        return self.I2C.readfrom_mem(self.address, reg, length)
    def init_sensor(self):
        #Exemple: set-up différente configuration de registre
        #Peut être développer pour paramétrer différent mode d'alimentation/veille ou le magnetic range
        pass
        
    def _convert_16bit(self, msb, lsb):
        value = (msb << 8) | lsb
        if value & 0x8000: #Permet de gérer les nombre négatif
            value -= 65536
        return value
    
    #Lis le champ magnétique de l'axe X
    def read_x(self):
        msb = self.read_register(TMAG5273B1_MAG_X_MSB)[0]
        lsb = self.read_register(TMAG5273B1_MAG_X_MSB + 1)[0]
        return _convert_16bit(msb, lsb)
    
    #Lis le champ magnétique de l'axe Y
    def read_y(self):
        msb = self.read_register(TMAG5273B1_MAG_Y_MSB)[0]
        lsb = self.read_register(TMAG5273B1_MAG_Y_MSB + 1)[0]
        return _convert_16bit(msb, lsb)
    
    #Lis le champ magnétique de l'axe Z
    def read_z(self):
        msb = self.read_register(TMAG5273B1_MAG_Z_MSB)[0]
        lsb = self.read_register(TMAG5273B1_MAG_Z_MSB + 1)[0]
        return _convert_16bit(msb, lsb)
    
    def read_temperature(self):
        msb = self.read_register(TMAG5273B1_TEMP_MSB)[0]
        lsb = self.read_register(TMAG5273B1_TEMP_MSB + 1)[0]
        temp_raw = self._convert_16bit(msb, lsb)
        temperature = (temp_raw * 0.1)  # Conversion basé sur la datasheet, ajuster au besoin
        return temperature
    
    #Lis tous les axes du champ magnétique
    def read_all_magnetic_axes(self):
        x = self.read_x()
        y = self.read_y()
        z = self.read_z()
        return x, y, z
    