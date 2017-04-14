# coding=utf-8

from sql.tables import *

class query(object):
    def __init__ (self, table, columns, number):
        # Vérifie que toutes les colonnes demandées appartiennent à la table indiquée
        Bool = True
        for c in columns :
            if c not in table.columns:
                Bool = False
        assert Bool or columns[0] == '*', "La table " + table.name + " ne possède pas un des attributs demandés parmi " + ', '.join(columns)

        # Met en forme les colonnes demandées
        if columns[0] != "*" :
            objectif = table.alias + '.' + table.prefix + columns[0]
            for i in range(1, len(columns)):
                objectif += ', ' + table.alias + '.' + table.prefix + columns[i]
        else :
            objectif = "*"
            
        # Met en forme un éventuel TOP i éléments
        top = '' if number == 0 else 'TOP %i ' % (number)
        
        # Ecrit le début de la requête
        self.request = "SELECT " + top + objectif + " FROM " + table.name + " AS " + table.alias + "\n"
        
        # Stock les tables utilisées dans la requête, et le nombre de where
        self.joints = [table]
        self.wcount = 0
        
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
        
        und = 'WHERE ' if self.wcount == 0 else 'AND '
        self.wcount += 1
        
        self.request += und + table.alias + '.' + table.prefix + column + " LIKE '%" + description + "%'\n"
    
    def groupby(self, table, column):
        assert table in self.joints,  "Vous faites appel à la table " + table.name + " absente de la requête, utilisez JOIN pour l'ajouter"
        assert column in table.columns, "La table " + table.name + " ne possède pas d'attribut " + table.prefix + column
        
        self.request += "GROUP BY " + table.alias + '.' + table.prefix + column + "\n"
        
    def write(self):
        self.request += "GO\n"
        self.request += "QUIT"
        self.file = open("example.sql", "w")
        self.file.write(self.request)
        self.file.close()