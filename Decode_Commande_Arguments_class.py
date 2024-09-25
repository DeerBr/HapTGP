"""
Module permettant de séparer les tokens d'une string
ayant un (ou des) espaces(s) comme séparateur.
ref: https://stackoverflow.com/questions/5749195/how-can-i-split-and-parse-a-string-in-python

Entrée:  decode(mystring)
         paramètre 'mystring' de type string incluant des tokens, exemple: " Xxx, 23, 45.6"
Sorties: getCommande() : premier token (Xxx)
         getNbArg()    : nombre d'argument (2)
         getArg(index) : ['23' , '45.6']

Jude Levasseur
24 juillet 2022

"""
class decodeur:
    """Décode une une ligne de caractères: une commande et des arguments"""
    # Constructeur
    def __init__(self):
        """Initialise le décodeur."""
        self.commande = ''
        self.nbArguments = 0
        self.arguments = []                            

    #
    # Fonction pour décode la commande et les arguments
    #
    def decode(self, mystring=""):
        """Décode une ligne."""
        _mystring=(' '.join(mystring.split())).split()  # Le premier split sert à joindre les esapces consécutifs
                                                        # et le second pour sépararer les tokens. 

        if _mystring :                              # Si _mystring est non vide                 
            self.commande = _mystring.pop(0)    # On retire le 1er item corespondant à la commande
            self.nbArguments = len(_mystring)   # Les éléments restant dans la liste sont des arguments
            self.arguments = _mystring                            
            # self.arguments = [float(item) for item in self.mystring]  #Convertir les arguments en float (Est-ce nécessaire?)
        else:
            self.commande = ''
            self.nbArguments = 0
            self.arguments = []                            
     
        # print("La commande   = ", self.commande)
        # print("Nb arguments  = ", self.nbArguments)
        # print("Les arguments = ", self.arguments)
        return self.commande, self.nbArguments, self.arguments
        
    #
    # Fonction pour retourner la commande, soit le premier token
    #
    def getCommande(self):
        """Renvoie la dernière commande décodée."""
        return self.commande
    #
    # Fonction pour retourner le nombre d'argument, soit le nombre de tokens suivants le premier
    #
    def getNbArg(self):
        """Renvoie le dernier nombre d'argument décodé."""
        return self.nbArguments

    #
    # Fonction pour retourner la liste d'arguments, soit les tokens suivants le premier
    #
    def getArg(self, indexArg):
        """Renvoie les derniers arguments décodés."""
        if indexArg >= 0 and indexArg < self.nbArguments:
            return self.arguments[indexArg]
        else:
            return ''
