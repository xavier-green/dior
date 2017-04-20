# coding=utf-8

import subprocess, csv
from datetime import timedelta, date

class query(object):

	def __init__ (self, table, columns, number=0):
		
		self.used_tables = [table]
		# Vérifie que toutes les colonnes demandées appartiennent à la table indiquée
		objectif = []
		for c in columns:
			# Si c'est un couple (table, colonne), vérifier que la colonne existe dans la table
			# Puis vérifier plus tard (au write) qu'on va bien join cette table
			if isinstance(c, tuple) and len(c) == 2:
				column_asked = c[1]
				table_asked = c[0]
				assert column_asked in table_asked.columns, "La table " + table_asked.name + " ne contient pas d'attribut " + table_asked.prefix + column_asked
				objectif.append(table_asked.alias + '.' + table_asked.prefix + column_asked)
				self.used_tables.append(table_asked)
			# Sinon, si c'est un de ces strings là on accepte
			elif c == "count(*)" or c == "*":
				objectif.append(c)
			# Sinon, on vérifie que c'est une colonne de la première table
			elif c in table.columns:
				objectif.append(table.alias + '.' + table.prefix + c)
			# Si ce n'est pas un des trois cas précédent, la requête est invalide
			else:
				assert False, "Il semblerait que les colonnes demandées n'appartiennent à aucune table"

		# Met en forme un éventuel TOP i éléments
		top = '' if number == 0 else 'TOP %i ' % (number)
		
		# Ecrit le début de la requête
		self.request = "SELECT " + top + ', '.join(objectif) + " FROM " + table.name + " AS " + table.alias + "\n"
		
		# Stock les tables utilisées dans la requête, et le nombre de where
		self.joints = [table]
		self.wcount = []

	def join(self, table1, table2, join1, join2):
		assert table1 in self.joints, "Vous tentez de joindre deux tables absentes de la requête."
		assert join1 in table1.columns, "La table " + table1.name + " ne contient pas d'attribut " + table1.prefix + join1
		assert join2 in table2.columns, "La table " + table2.name + " ne contient pas d'attribut " + table2.prefix + join2

		self.joints.append(table2)
		jointure1 = table1.alias + "." + table1.prefix + join1
		jointure2 = table2.alias + "." + table2.prefix + join2
		self.request += "JOIN " + table2.name + " AS " + table2.alias + " ON "  + jointure1 + " = " + jointure2 + "\n"
		
	def join_custom(self, table1, request_table, original_table, join1, join2):
		assert join1 in table1.columns, "La table " + table1.name + " ne contient pas d'attribut " + table1.prefix + join1
		
		self.joints.append(original_table)
		jointure1 = table1.alias + "." + table1.prefix + join1
		jointure2 = original_table.alias + "." + original_table.prefix + join2
		self.request += "JOIN (\n" + request_table + ") AS " + original_table.alias + " ON "  + jointure1 + " = " + jointure2 + "\n"

	# à faire pour une vraie BDD : mettre end = time.strftime("%Y%m%d") pour avoir le current_date
	def wheredate(self, table, column, duration = "week", end="20170304"):
		assert table in self.joints, "Vous faites appel à la table " + table.name + " absente de la requête, utilisez JOIN pour l'ajouter"
		assert column in table.columns, "La table " + table.name + " ne possède pas d'attribut " + table.prefix + column
		
		end_time = date(int(end[0:4]), int(end[4:6]), int(end[6:8]))
		if duration == "week":
			duration_time = timedelta(weeks=1)
		elif duration == "month":
			duration_time = timedelta(months=1)
		elif duration == "day":
			duration_time = timedelta(days=1)
		
		start_time = end_time - duration_time
		start = str(start_time.year) + '0'*(2-len(str(start_time.month))) + str(start_time.month) + '0'*(2-len(str(start_time.day))) + str(start_time.day)
		
		table_date = table.alias + '.' + table.prefix + column
		where = "WHERE " if len(self.wcount) == 0 else "AND "
		self.wcount.append(table.alias + column)
		
		self.request += where + table_date + ' >= ' + start + '\nAND ' + table_date + ' <= ' + end + '\n'
		
		
	def where(self, table, column, description):
		assert table in self.joints, "Vous faites appel à la table " + table.name + " absente de la requête, utilisez JOIN pour l'ajouter"
		assert column in table.columns, "La table " + table.name + " ne possède pas d'attribut " + table.prefix + column

		# Choix d'utiliser WHERE, AND ou OR au début de la condition
		if len(self.wcount) == 0:
			where_and_or = "WHERE "
			self.wcount.append(table.alias + column)
		elif (table.alias + column) not in self.wcount:
			where_and_or = "AND "
			self.wcount.append(table.alias + column)
		else:
			where_and_or = "OR "
		
		self.request += where_and_or + table.alias + '.' + table.prefix + column + " LIKE '%" + description + "%'\n"

	def groupby(self, table, column):
		assert table in self.joints,  "Vous faites appel à la table " + table.name + " absente de la requête, utilisez JOIN pour l'ajouter"
		assert column in table.columns, "La table " + table.name + " ne possède pas d'attribut " + table.prefix + column
		
		self.request += "GROUP BY " + table.alias + '.' + table.prefix + column + "\n"
	
	def orderby(self, column, desc=""):
		
		self.request += "ORDER BY " + column + desc + '\n'
		

	def write(self):
		# On vérifie que toutes les tables demandées sont bien join
		used = set(self.used_tables)
		joined = set(self.joints)
		assert used.issubset(joined), "Some of the tables asked are not joined"
		
		# On termine la requête
		self.request += "GO\n"
		# Database call
		#p = subprocess.run('docker exec  mssql /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P D10R_password! -d Reporting -W -w 999 -s | -Q'.split() + [self.request], stdout=subprocess.PIPE, universal_newlines=True)
		# Delete last line '(n rows affected)'
		#out = p.stdout.splitlines()[:-1]
		#out.pop(1)
		#return(csv.DictReader(out, delimiter='|'))