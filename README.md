Code pour le projet du cours de prototypage.
Fonctionnalité :

Utilisations du décodeur de commande série :
  Entrer une commande et un argument avec un espace entre les deux, voici les commandes disponnibles.
  Commande : "BME" Accède au capteur BME280.
    Arguments : "Temp" Renvoie la température capter par le BME280.
                "Hum" Renvoie l'humidité capter par le BME280.
                "Pres" Renvoie la pression capter par le BME280.
                
  Commande : "VEML" Accède au capteur VEML7700.
    Arguments : "Lux" Renvoie la luminosité capter par le VEML7700.
    
  Commande : "Save" Enregistre les données actuel des capteurs BME280 et VEML7700 sur la carte microSD.
  
  Commande : "Heure" Renvoie l'heure actuel du module RTC.
