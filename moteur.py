from machine import Pin, PWM
import array as arr
import utime

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

#********************************************
#Fonction pour faire bouger le moteur
#********************************************
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
   
   #Permet de changer de direction en inversant la phase 1 avec la phase 3
   #pwm_in1.duty(int(((pwmSin[pasActuel_IN3]*1023)/255)*coupleMot/100))
   #pwm_in2.duty(int(((pwmSin[pasActuel_IN2]*1023)/255)*coupleMot/100))
   #pwm_in3.duty(int(((pwmSin[pasActuel_IN1]*1023)/255)*coupleMot/100))
   
millisTimer = utime.ticks_ms()

#########################################################################################
# Programme principal - tourne en boucle
#########################################################################################
while True:
    millisNow = utime.ticks_ms()
    if(millisNow - millisTimer >= 50):
        millisTimer = millisNow
        gbmMove()
        