"""
Fonctions auxiliaires pour mettre en forme les données comme il faut
pour que ce soit joli à l'affichage
"""

def affichage_euros(montant):
	"""
	Permet un bel affichage d'un montant en euros.
	affichage_euros("3456.12")
	>> "3 456,12€"
	affichage_euros("12000000.00")
	>> "12 000 000€"
	"""
	somme, centimes = montant.split(".")
	n = len(somme) % 3
	milliers = [somme[i+n:i+3+n] for i in range(0, len(somme)-n, 3)]
	centimes = "" if centimes == "00" else "," + centimes
	return somme[0:n] + " " + " ".join(milliers) + centimes +'€'