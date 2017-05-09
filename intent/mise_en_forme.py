"""
Fonctions auxiliaires pour mettre en forme les donnees comme il faut
pour que ce soit joli a l'affichage
"""

def affichage_euros(montant):
	"""
	Permet un bel affichage d'un montant en euros.
	affichage_euros("3456.12")
	>> "3 456,12 €"
	affichage_euros("12000000.00")
	>> "12 000 000 €"
	"""
	montant = str(montant)
	if "." in montant:
		somme, centimes = montant.split(".")
	else:
		somme, centimes = [montant, "0"]
	n = len(somme) % 3
	milliers = [somme[i+n:i+3+n] for i in range(0, len(somme)-n, 3)]
	centimes = "" if (centimes == "00" or centimes == "0") else "," + centimes
	return somme[0:n] + " " + " ".join(milliers) + centimes +' €'

def affichage_date(date):
	"""
	Permet de passer d'un affichage en AAAAMMJJ
	à un affichage en JJ/MM/AAAAMMJJ
	affichage_date("20170304")
	>> "04/03/2017"
	"""
	assert type(date) is str, "Expected a string, but %r is a %r" %(date, type(date))
	assert len(date) == 8, "Expected 8 caracters, %s has %i caracters" %(date, len(date))
	annee = date[0:4]
	mois = date[4:6]
	jour = date[6:8]
	return jour + '/' + mois + '/' + annee
