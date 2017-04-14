# coding=utf-8

from tables import item

class query(object):
    def __init__ (self, table, columns):
        Bool = True
        for c in columns :
            if c not in table.columns:
                Bool = False
        assert Bool or columns[0] == '*', "La table " + table.name + " ne possède pas un des attributs demandés parmi " + ', '.join(columns)

        if columns[0] != "*" :
            objectif = table.alias + '.' + table.prefix + columns[0]
            for i in range(1, len(columns)):
                objectif += ', ' + table.alias + '.' + table.prefix + columns[i]
        else :
            objectif = "*"
        
        self.request = "SELECT TOP 3 " + objectif + " FROM " + table.name + " AS " + table.alias + "\n"
        self.joints = [table]
        
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
        
        self.request += "WHERE " + table.alias + '.' + table.prefix + column + " LIKE '%" + description + "%'\n"
    
    def groupby(self, table, column):
        assert table in self.joints,  "Vous faites appel à la table " + table.name + " absente de la requête, utilisez JOIN pour l'ajouter"
        
    def write_query(self):
        self.request += "GO\n"
        self.request += "QUIT"
        self.file = open("example.sql", "w")
        self.file.write(self.request)
        self.file.close()

test = query(item, ['*'])
test.join(item, color_size, "Code", "Code")
test.where(item, 'Description', 'bustier')
test.write_query()

test20 = query(color_size, ['Color'])
test20.join(color_size, item, 'Code', 'Code')
test20.where(item, 'Description', 'rose des vents')
test20.write_query()

#print(test20.request)