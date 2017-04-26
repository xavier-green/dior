# coding=utf-8

import subprocess, csv, socket

class query(object):


	def __init__ (self, table, columns, top_distinct =''):

		self.selected_tables = [table]
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
				self.selected_tables.append(table_asked)
			elif c == "count(*)" or c == "*":
				objectif.append(c)
			# format "sumCOLUMNNAME"
			elif "sum" in c:
				column_asked = c[3:]
				objectif.append("SUM("+table.alias+'.'+table.prefix+c[3:]+")")
			# Sinon, on vérifie que c'est une colonne de la première table
			elif c in table.columns:
				objectif.append(table.alias + '.' + table.prefix + c)
			# Si ce n'est pas un des trois cas précédent, la requête est invalide
			else:
				assert False, "Il semblerait que les colonnes demandées n'appartiennent à aucune table"

		# Ecrit le début de la requête
		self.request = "SELECT " + top_distinct + " " + ', '.join(objectif) + " FROM " + table.name + " AS " + table.alias + "\n"

		# Stock les tables utilisées dans la requête, et le nombre de where
		self.joined_tables = [table]
		self.wcount = []

	# Pour faire une jointure entre deux tables sous la condition t1.join1 = t2.join2
	# Attention à l'ordre des join, ils doivent correspondrent à leurs tables respectives
	def join(self, table1, table2, join1, join2):
		assert table1 or table2 in self.joined_tables, "Erreur : Aucune des deux tables n'est déjà présente dans la requête."
		assert join1 in table1.columns, "La table " + table1.name + " ne contient pas d'attribut " + table1.prefix + join1
		assert join2 in table2.columns, "La table " + table2.name + " ne contient pas d'attribut " + table2.prefix + join2

		self.joined_tables.append(table2)
		jointure1 = table1.alias + "." + table1.prefix + join1
		jointure2 = table2.alias + "." + table2.prefix + join2
		self.request += "JOIN " + table2.name + " AS " + table2.alias + " ON "  + jointure1 + " = " + jointure2 + "\n"

	# Pour faire une jointure avec des requêtes imbriquées
	# Comme c'est fait spécifiquement pour la table sale,
	def join_custom(self, table1, request_table, original_table, join1, join2):
		assert join1 in table1.columns, "La table " + table1.name + " ne contient pas d'attribut " + table1.prefix + join1

		self.joined_tables.append(original_table)
		jointure1 = table1.alias + "." + table1.prefix + join1
		jointure2 = original_table.alias + "." + original_table.prefix + join2
		self.request += "JOIN (\n" + request_table + ") AS " + original_table.alias + " ON "  + jointure1 + " = " + jointure2 + "\n"

	# à faire pour une vraie BDD : mettre end = time.strftime("%Y%m%d") pour avoir le current_date
	def wheredate(self, table, column, start="20170225", end="20170304"):
		assert table in self.joined_tables, "Vous faites appel à la table " + table.name + " absente de la requête, utilisez JOIN pour l'ajouter"
		assert column in table.columns, "La table " + table.name + " ne possède pas d'attribut " + table.prefix + column

		table_date = table.alias + '.' + table.prefix + column
		where = "WHERE " if len(self.wcount) == 0 else "AND "
		self.wcount.append(table.alias + column)

		self.request += where + table_date + ' >= ' + start + '\nAND ' + table_date + ' <= ' + end + '\n'
		
	def whereNotJDAandOTH(self):
		
		where = "WHERE " if len(self.wcount) == 0 else "AND "
		self.wcount.append("ZO.ZONE_Code")
		
		self.request += where + "ZO.ZONE_Code NOT IN ('JDA', 'OTH')\n"


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

		self.request += where_and_or + table.alias + '.' + table.prefix + column + " LIKE '%" + description + "%'\n"

	def groupby(self, table, column):
		assert table in self.joined_tables,  "Vous faites appel à la table " + table.name + " absente de la requête, utilisez JOIN pour l'ajouter"
		assert column in table.columns, "La table " + table.name + " ne possède pas d'attribut " + table.prefix + column
		self.request += "GROUP BY " + table.alias + '.' + table.prefix + column + "\n"

	def orderby(self, column, desc=""):

		self.request += "ORDER BY " + column + desc + '\n'


	def write(self):
		# Vérification que les colonnes SELECTed sont bien JOINed
		assert set(self.selected_tables) < set(self.joined_tables), "Erreur : Vous avez SELECT un élément d'une table que vous n'avez pas JOIN"
		
		sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		sock.connect('/tmp/request.sock')
		sock.sendall(bytes(self.request, 'utf-8'))
		out = sock.recv(8192).decode('utf-8').splitlines()[:-2]
		out.pop(1)
		return("\n".join(out))
