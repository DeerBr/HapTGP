"""
Module permettant d'établir la communication avec l'entrée USB de la carte ESP32
et de capturer une ligne (string) terminée par un caractère LF ('\n' = '\0xA') 
ref: https://www.digi.com/resources/documentation/digidocs/90002219/container/cont_access_uart.htm?tocpath=Access%20the%20primary%20UART%7C_____0

Une fois initialisé (__init__) et démarré (start()), ce module établit une communication série
à 115200 baud par le lien USB de la carte ESP32 et recueille les caractères reçus de façon périodique.

À l'aide de la fonction getLineBuffer(), on obtient la dernière string enregistrée se terminant par LF.

Jude Levasseur
25 août 2023

"""
from machine import Timer     # Importation du module Timer pour la périodicité de communication
from sys import stdin, stdout # Importation des modules de communication pour USB-UART
import uselect                # Importation du module incluant le polling

class UsbSerialPeriodic :
    """Definir un lien de communication série par USB."""
    # Constructeur
    def __init__(self, Echo=True, inBuffersize=128):
        """Initialise du module."""
        self.bufferSize = inBuffersize              # Dimension du buffer circulaire
        self.buffer = [' '] * self.bufferSize       # Initiatilisation du buffer circulaire avec des espaces
        self.bufferEcho = Echo                      # Flag pour valider l'écho des caractères reçus (True/False) 
        self.bufferNextIn, self.bufferNextOut = 0,0 # Pointeurs pour les caractères entrant (In) et sortant (Out) du buffer circulaire
        self.terminatePeriodic = False              # Flag pour bloquer la scrutation du port USB par la fonction 'bufferSTDIN' (True/False)
        
        self.spoll = uselect.poll()
        self.spoll.register(stdin, uselect.POLLIN)  # Permet le fonctionnement du stdin (port USB-Serie principal) en structation
        self.tim = Timer(0)                         # Permet l'utilisation d'un Timer pour la période de structation du stdin. Il faut un arg pour le ESP32

    
    #
    # bufferSTDIN() fonction pour la scrutation périodique du port USB (stdin)
    #
    def bufferSTDIN(self, timer):
        """Boucle periodique pour la communication."""
        if self.terminatePeriodic == False:                # si requis par le prg appelant ...
            _data = (stdin.read(1) if self.spoll.poll(0) else "")   # Scrutation du USB
            if _data:                                               # Si byte reçu ...
                self.buffer[self.bufferNextIn] = _data              # Enregistre le byte dans le buffer
                if self.bufferEcho:                                 # Si l'écho est requis ...
                    stdout.write(self.buffer[self.bufferNextIn])
                self.bufferNextIn += 1                              # Ajuste le pointeur d'entrée
                if self.bufferNextIn == self.bufferSize:            # ... et wrap, si nécessaire
                    self.bufferNextIn = 0
        

    #
    # start() Démarrage de la structation périodique du USB
    #         par l'entremise de la fonction bufferSTDIN()
    #
    def start(self):
        """Démarre la communication."""
        self.terminatePeriodic = False           # signaler à 'bufferSTDIN' de terminer (True/False)
        self.tim.init(period = 5, mode = Timer.PERIODIC, callback = self.bufferSTDIN) # Ajustement de la périodicité 

    #
    # stop() fonction pour stopper le processus
    #
    def stop(self):
        """Arrete la communication."""
        self.terminatePeriodic = True           # signaler à 'bufferSTDIN' de terminer (True/False)

    #
    # getByteBuffer() fonction pour vérifier si un byte est disponible dans le buffer et le retourner
    #
    def getByteBuffer(self):
        """Renvoie le dernier caractère du buffer."""
        if self.bufferNextOut == self.bufferNextIn: # si aucun nouveau byte ...
            return ''                               # ... retourne string vide
        n = self.bufferNextOut                      # sauvegarde pointeur courant de sortie
        self.bufferNextOut += 1                     # ajuste le pointeur de sortie
        if self.bufferNextOut == self.bufferSize:   # ... et wrap, si nécessaire
            self.bufferNextOut = 0
        return (self.buffer[n])                     # retourne le byte du buffer

    #
    # getLineBuffer() fonction pour vérifier si une ligne est disponible dans le buffer et la retourner
    #                 sinon, retourne une ligne vide
    #
    # NOTE 1: une ligne correspond à une suite d'un ou plusieurs bytes terminée par un LF (line feed, \x0a correspondant à '\n')
    #      2: une line contenant seulement un simple byte LF retourne aussi une line vide
    #
    def getLineBuffer(self):
        """Renvoie la ligne complete du buffer."""
        if self.bufferNextOut == self.bufferNextIn:    # si le buffer est vide ...
            return ''                                  # ... retourne une ligne vide

        n = self.bufferNextOut                         # recherche d'un LF
        while n != self.bufferNextIn:
            _strBuffer= str(self.buffer[n])
            if  (self.buffer[n]) == '\x0a':            # si un LF ...
                break                                  # termine la boucle 
            
            else:
                n = n + 1                              # ajuste le pointeur de recherche
                if n == self.bufferSize:               #  ... wrap, si nécessaire
                    n = 0
        
        if n == self.bufferNextIn:                     # si aucune LF trouvé ...
            return ''                                  # ... retourne une ligne vide

        line = ''                                      # Si LF trouvé dans la suite de bytes non déjà réclamés 
        n = n + 1                                      # ajuste le pointeur au byte suivant le LF
        if n == self.bufferSize:                       #    ... wrap, si nécessaire
            n = 0                                      

        while self.bufferNextOut != n:                      # Boucle pour construire la ligne à retourner (jusqu'au LF)
            if (self.buffer[self.bufferNextOut]) == '\x0d': # Si caractere CR (équivalent à '\r')
                self.bufferNextOut = self.bufferNextOut + 1 # augmente le pointeur de sortie pour ignorer ce CR
                if self.bufferNextOut == self.bufferSize:   #    ... wrap, si nécessaire
                    self.bufferNextOut = 0
                continue                                    # continuer en ignorant (strip) les CR (\x0d) bytes
            
            if (self.buffer[self.bufferNextOut]) == '\x0a': # Si le byte courant est LF ...
                self.bufferNextOut += 1                     # ajuste le ponteur de sortie
                if self.bufferNextOut == self.bufferSize:   #    ... wrap, si nécessiare
                    self.bufferNextOut = 0
                break                                       # et termine la boucle en ignorant ce LF byte

            line = line + str(self.buffer[self.bufferNextOut])    # ajooute du caractère à la ligne
            self.bufferNextOut += 1                         # ajuste le ponteur de sortie
            if self.bufferNextOut == self.bufferSize:       #    ... wrap, si nécessiare
                self.bufferNextOut = 0

        return line                                 # Retourne la ligne demandée 

    
    
    