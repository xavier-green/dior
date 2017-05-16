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
	year_delta = datetime.timedelta(weeks=52)
	start_date = monday_from_last_week() - year_delta
	end_date = start_date + datetime.timedelta(days=6)
	start = start_date.strftime("%Y%m%d")
	end = end_date.strftime("%Y%m%d")
	return start, end

def last_week():
	start_date = monday_from_last_week()
	end_date = start_date + datetime.timedelta(days=6)
	start = start_date.strftime("%Y%m%d")
	end = end_date.strftime("%Y%m%d")
	return start, end
	