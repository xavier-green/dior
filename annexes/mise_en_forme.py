"""
Fonctions auxiliaires pour mettre en forme les donnees comme il faut
pour que ce soit joli a l'affichage
"""

import datetime

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
	elif ',' in montant:
		somme, centimes = montant.split(",")
	else:
		somme, centimes = [montant, "0"]
	n = len(somme) % 3
	en_tete = somme[0:n] if n > 0 else ""
	espace = " " if len(somme) > 3 else ""
	milliers = [somme[i+n:i+3+n] for i in range(0, len(somme)-n, 3)]
	centimes = "," + centimes[0:2] if (len(centimes) >= 2 and centimes != "00") else ""
	return en_tete + espace + " ".join(milliers) + centimes +' €'

def affichage_date(date):
	"""
	Permet de passer d'un affichage en AAAAMMJJ
	à un affichage en JJ/MM/AAAA
	affichage_date("20170304")
	>> "04/03/2017"
	"""
	assert type(date) is str, "Expected a string, but %r is a %r" %(date, type(date))
	assert len(date) == 8, "Expected 8 caracters, %s has %i caracters" %(date, len(date))
	annee = date[0:4]
	mois = date[4:6]
	jour = date[6:8]
	input_date = jour + '/' + mois + '/' + annee
	return affichage_jour(input_date) + input_date

def affichage_jour(input_date):
	"""
	A partir d'une date au format DD/MM/AAAA,
	affiche le jour de la semaine
	"""
	assert type(input_date) is str, "Expected a string, but %r is a %r" %(input_date, type(input_date))
	assert len(input_date) == 10, "Expected 10 caracters, %s has %i caracters" %(input_date, len(input_date))
	assert len(input_date.split('/')) == 3, "Expected 2 '/', %s has %i '/'" %(input_date, len(input_date.split('/'))-1)

	weekday_dict = {
		'0':'lundi ',
		'1':'mardi ',
		'2':'mercredi ',
		'3':'jeudi ',
		'4':'vendredi ',
		'5':'samedi ',
		'6':'dimanche '
	}

	jour, mois, annee = input_date.split('/')
	datetime_date = datetime.date(int(annee), int(mois), int(jour))
	weekday = datetime_date.weekday()
	
	return weekday_dict[str(weekday)]



