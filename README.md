-------------------------------------------
    Plateforme HapTGP
    ===================================

 Ce programme sert au contrôle de la plateforme HapTGP. Celle-ci permet la mesure de la température,
 de l'humidité, de la pression et de la luminosité. Il y a 2 bouton de contrôle (A et B) sur le dessus de la platforme et
 la protection autour de l'écran est rotatif. Ces rotation sont détecter à l'aide d'une capteur de champ magnétique.

 Auteur:  Déryck Brais
 Fichier: firmWare_HapTGP
 Date:    29 novembre 2024
-------------------------------------------
 Instructions:

 Chargez les modules xxxxxxxxx

 Pour fonctionnement dans Thonny:
 Connecter la carte protoTphys avec ESP32

    NOTE: faire Ctrl-C pour terminer le programme et revenir au REPL de Thonny

 Pour fonctionnement avec alimentation externe:
 	L'affichage de base est sur le menu principale (lumière des DEL bleu)
	-Tourner le bouton principale pour déplacer le curseur de gauche
	-Appuyer sur le bouton A pour entrer des le l'option indiquer par le cuseur
	-Appuyer sur le bouton B pour retourner au menu principale

 Couleur des différent menu :
	Menu principale : Bleu
	BME280 : Blanc
	VEML7700 : Rouge
	Enregistrement sur micro uSD : Vert

-----------------------------------------------------------------------------------
To do
-Corriger bug navigation menu (amélioré la fluidité)
-Ajout fonction sauvegarde de donner sur SD card à tous les 30 secondes
-Implémenter un rafraîchissement de l'écran automatique (update des données affiché)
-----------------------------------------------------------------------------------