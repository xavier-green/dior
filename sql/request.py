# coding=utf-8

import subprocess, csv

class query(object):

	def __init__ (self, table, columns, number=0):
		# Vérifie que toutes les colonnes demandées appartiennent à la table indiquée
		Bool = True
		for c in columns :
			if c not in table.columns:
				Bool = False
		
		assert Bool or columns[0] in ['*', 'count(*)'], "La table " + table.name + " ne possède pas un des attributs demandés parmi " + ', '.join(columns)

		# Met en forme les colonnes demandées
		if columns[0] not in ["*", 'count(*)'] :
			objectif = table.alias + '.' + table.prefix + columns[0]
			for i in range(1, len(columns)):
				objectif += ', ' + table.alias + '.' + table.prefix + columns[i]
		else :
			objectif = columns[0]

		# Met en forme un éventuel TOP i éléments
		top = '' if number == 0 else 'TOP %i ' % (number)
		
		# Ecrit le début de la requête
		self.request = "SELECT " + top + objectif + " FROM " + table.name + " AS " + table.alias + "\n"
		
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

	def write(self):
		self.request += "GO\n"
		# Database call
		p = subprocess.run('docker exec  mssql /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P D10R_password! -d Reporting -W -w 999 -s | -Q'.split() + [self.request], stdout=subprocess.PIPE, universal_newlines=True)
		# Delete last line '(n rows affected)'
		out = p.stdout.splitlines()[:-1]
		out.pop(1)
		return(csv.DictReader(out, delimiter='|'))