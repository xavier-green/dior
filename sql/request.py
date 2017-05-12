# coding=utf-8


import subprocess, csv
import time
from intent.gestion_dates import last_monday, today

class query(object):

	# A partir d'une table et de colonnes, renvoit un string de toutes les colonnes bien écrites
	# ex : proprify_columns(sale, ['Style', (staff, 'Name'), (None, 'count(*)'), ('sum', sale, 'RG_Quantity', sale, 'MD_Quantity')])
	# >> 'SA.SALE_Style, ST.STAFF_Name, count(*), sum(SA.SALE_RG_Quantity + SA.SALE_MD_Quantity)'
	def proprify_columns(self, table, columns, max_columns = 0):
		response = []
		for c in columns:
			# Cas spéciaux
			if c == '*' or c == 'count(*)' or (table == None and isinstance(c, str)):
				response.append(c)
			# Si la colonne appartient à la table de base
			elif table != None and c in table.columns:
				response.append(table.alias + '.' + table.prefix + c)
			# Pour les colonnes n'appartenant pas à la table initiale : (table, 'colonne')
			elif isinstance(c, tuple) and len(c) == 2:
				table_asked = c[0]
				if table_asked == None:
					response.append(c[1])
				else:
					column_asked = c[1]
					assert column_asked in table_asked.columns, "La table " + table_asked.name + " ne contient pas d'attribut " + table_asked.prefix + column_asked
					response.append(table_asked.alias + '.' + table_asked.prefix + column_asked)
			# Appliquer une méthode à une ou plusieurs colonnes, par exemple sum(a + b)
			elif isinstance(c, tuple) and len(c) > 2:
				if len(c)%2 == 1:
					method = c[0]
					method_columns = []
					for i in range(1, len(c), 2):
						method_table = c[i]
						method_column = c[i+1]
						method_columns.append(method_table.alias + '.' + method_table.prefix + method_column)
					response.append(method + '(' + ' + '.join(method_columns) + ')')
				else:
					method_columns = []
					for i in range(len(c), 2):
						method_table = c[i]
						method_column = c[i+1]
						method_columns.append(method_table.alias + '.' + method_table.prefix + method_column)
					response.append(' + '.join(method_columns))
			else:
				assert False, "Il semblerait que les colonnes demandées n'appartiennent à aucune table"
		# Pour les requêtes comme ORDER BY et GROUP BY qui demandent uniquement une colonne
		if max_columns > 0:
			response = response[0:max_columns]
		return ', '.join(response)

	def __init__ (self, table, columns, top_distinct =''):
		print(table.name, columns)
		self.selected_tables = [table]
		colonnes = self.proprify_columns(table, columns)

		# Ecrit le début de la requête
		self.request = "SELECT " + top_distinct +  " " + colonnes + " FROM " + table.name + " AS " + table.alias + "\n"

		# Stock les tables utilisées dans la requête, et le nombre de where
		self.joined_tables = [None, table]
		self.wcount = []
		self.grouped_by = False

	# Pour faire une jointure entre deux tables sous la condition t1.join1 = t2.join2
	# Attention à l'ordre des join, ils doivent correspondrent à leurs tables respectives
	def join(self, table1, table2, join1, join2):
		assert table1 or table2 in self.joined_tables, "Erreur : Aucune des deux tables n'est déjà présente dans la requête."
		assert join1 in table1.columns, "La table " + table1.name + " ne contient pas d'attribut " + table1.prefix + join1
		assert join2 in table2.columns, "La table " + table2.name + " ne contient pas d'attribut " + table2.prefix + join2

		self.joined_tables.append(table2)
		jointure1 = self.proprify_columns(table1, [join1], 1)
		jointure2 = self.proprify_columns(table2, [join2], 1)
		self.request += "JOIN " + table2.name + " AS " + table2.alias + " ON "  + jointure1 + " = " + jointure2 + "\n"

	# Pour faire une jointure avec des requêtes imbriquées
	# original_table doit contenir la table principale de cette jointure imbriquée, généralement la table sale
	def join_custom(self, table1, request_table, original_table, join1, join2):
		assert join1 in table1.columns, "La table " + table1.name + " ne contient pas d'attribut " + table1.prefix + join1

		self.joined_tables.append(original_table)
		jointure1 = self.proprify_columns(table1, [join1], 1)
		jointure2 = self.proprify_columns(original_table, [join2], 1)
		self.request += "JOIN (\n" + request_table + ") AS " + original_table.alias + " ON "  + jointure1 + " = " + jointure2 + "\n"

	# TODO pour la vraie BDD : mettre end = time.strftime("%Y%m%d") pour avoir le current_date
	# Default week-to-date
	def wheredate(self, table, column, start=last_monday(), end=today()):
		assert table in self.joined_tables, "Vous faites appel à la table " + table.name + " absente de la requête, utilisez JOIN pour l'ajouter"
		assert column in table.columns, "La table " + table.name + " ne possède pas d'attribut " + table.prefix + column

		table_date = self.proprify_columns(table, [column], 1)
		where = "WHERE " if len(self.wcount) == 0 else "AND "
		self.wcount.append(table.alias + column)


		self.request += where + table_date + ' >= ' + start + '\nAND ' + table_date + ' < ' + end + '\n'

	def whereNotJDAandOTH(self):

		where = "WHERE " if len(self.wcount) == 0 else "AND "
		self.wcount.append("ZO.ZONE_Code")

		self.request += where + "ZO.ZONE_Code NOT IN ('JDA', 'OTH')\n"

	# whereComparaison(sale, prix, ">", 35000)
	def whereComparaison(self, table, column, comparaison, description):
		assert table in self.joined_tables, "Vous faites appel à la table " + table.name + " absente de la requête, utilisez JOIN pour l'ajouter"
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

		self.request += where_and_or + self.proprify_columns(table, [column], 1) + " " + comparaison + " " + description + "\n"


	def where(self, table, column, description):
		assert table in self.joined_tables, "Vous faites appel à la table " + table.name + " absente de la requête, utilisez JOIN pour l'ajouter"
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

		self.request += where_and_or + self.proprify_columns(table, [column], 1) + " LIKE '%" + description + "%'\n"

	def groupby(self, table, column):
		assert table in self.joined_tables,  "Vous faites appel à la table " + table.name + " absente de la requête, utilisez JOIN pour l'ajouter"
		assert column in table.columns, "La table " + table.name + " ne possède pas d'attribut " + table.prefix + column
		if self.grouped_by:
			self.request += ","+self.proprify_columns(table, [column], 1) +'\n'
		else:
			self.request += "GROUP BY " + self.proprify_columns(table, [column], 1) + '\n'
			self.grouped_by = True


	def orderby(self, table, column, desc=""):
		if table:
			assert table in self.joined_tables,  "Vous faites appel à la table " + table.name + " absente de la requête, utilisez JOIN pour l'ajouter"
			assert column in table.columns, "La table " + table.name + " ne possède pas d'attribut " + table.prefix + column
		self.request += "ORDER BY " + self.proprify_columns(table, [column], 1) + ' ' + desc + '\n'

	def write(self):
		print('REQUETE', self.request, '\n')
		p = subprocess.run('sqlcmd -l 10 -S 10.148.102.166\DEV2012 -U REP_SQL_CHATBOT -P ChatBoT1984! -d Reporting_CDS -W -w 999 -s # -Q'.split() + [self.request], stdout=subprocess.PIPE, universal_newlines=True)
		print('STDOUT:', p.stdout)
		if "Error" in p.stdout:
			raise Exception("Error during SQL query : \n"+p.stdout)
		out = p.stdout.splitlines()[:-2]
		out.pop(1)
		return("\n".join(out))

"""
test = query(sale, ['Style', ('sum', sale, 'RG_Quantity')])
test.join(sale, item, 'Style', 'Code')
test.join(sale, zone, 'Location', 'Code')
test.wheredate(sale, 'Style')
test.orderby(None, 'count(*)')
test.groupby(zone, 'Description')
print(test.request)
#print(test.proprify_columns(sale, ['Style', (staff, 'Name'), (None, 'count(*)'), ('sum', sale, 'RG_Quantity', sale, 'MD_Quantity')]))
"""
