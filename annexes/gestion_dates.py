"""
Pour gérer les demandes sur un format particulier de dates
"""

import datetime
import time

def last_monday():
	today = datetime.date.today()
	weekday = today.weekday()
	week_delta = datetime.timedelta(days=weekday) if weekday != 0 else datetime.timedelta(days=weekday, weeks=1)
	start_date = today - week_delta
	start = start_date.strftime("%Y%m%d")
	return start

def today():
	return time.strftime("%Y%m%d")

def monday_from_last_week():
	today = datetime.date.today()
	weekday = today.weekday()
	week_delta = datetime.timedelta(days=weekday, weeks=1)
	start_date = today - week_delta
	return start_date

def same_week_last_year():
	today = monday_from_last_week
