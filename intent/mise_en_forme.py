"""
Fonctions auxiliaires pour mettre en forme les donnees comme il faut
pour que ce soit joli a l'affichage
"""

def affichage_euros(montant):
	"""
	Permet un bel affichage d'un montant en euros.
	affichage_euros("3456.12")
	>> "3 456,12 &euro"
	affichage_euros("12000000.00")
	>> "12 000 000 &euro"
	"""
	montant = str(montant)
	if "." in montant:
		somme, centimes = montant.split(".")
	else:
		somme, centimes = [montant, "0"]
	n = len(somme) % 3
	milliers = [somme[i+n:i+3+n] for i in range(0, len(somme)-n, 3)]
	centimes = "" if (centimes == "00" or centimes == "0") else "," + centimes
	return somme[0:n] + " " + " ".join(milliers) + centimes +'&euro'
