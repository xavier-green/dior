"""
Pour gérer les demandes sur un format particulier de dates
"""

import datetime
import time

def last_monday():
	"""
	Renvoit la date du dernier lundi, au format AAAAMMJJ
	Si on est lundi, renvoit le lundi d'avant
	"""
	today = datetime.date.today()
	weekday = today.weekday()
	week_delta = datetime.timedelta(days=weekday) if weekday != 0 else datetime.timedelta(days=weekday, weeks=1)
	start_date = today - week_delta
	start = start_date.strftime("%Y%m%d")
	return start

def today():
	"""
	Renvoit la date d'aujourd'hui, au format AAAAMMJJ
	"""
	return time.strftime("%Y%m%d")

def monday_from_last_week():
	"""
	Renvoit le lundi de la semaine d'avant, au format datetime
	"""
	today = datetime.date.today()
	weekday = today.weekday()
	week_delta = datetime.timedelta(days=weekday, weeks=1)
	start_date = today - week_delta
	return start_date

def same_week_last_year():
	"""
	Renvoit le lundi et dimanche d'il y a 52 semaines, au format AAAAMMJJ
	"""
	year_delta = datetime.timedelta(weeks=52)
	start_date = monday_from_last_week() - year_delta
	end_date = start_date + datetime.timedelta(weeks=1)
	start = start_date.strftime("%Y%m%d")
	end = end_date.strftime("%Y%m%d")
	return start, end

def last_week():
	"""
	Renvoit le lundi et dimanche de la semaine dernière, au format AAAAMMJJ
	"""
	start_date = monday_from_last_week()
	end_date = start_date + datetime.timedelta(weeks=1)
	start = start_date.strftime("%Y%m%d")
	end = end_date.strftime("%Y%m%d")
	return start, end
