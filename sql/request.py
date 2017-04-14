# coding=utf-8

from tables import item

class query(object):
    def __init__ (self, table, columns):
        self.columns = columns
        self.table = table
        self.request = "SELECT TOP 3 " + self.columns + " FROM " + self.table.name + " AS " + table.alias + "\n"
        self.joints = [self.table]
        
    def add_joint(self, table1, table2, join1, join2):
        assert table1 in self.joints, "Vous tentez de joindre deux tables absentes de la requête."
        assert join1 in table1.columns, "La table " + table1.name + " ne contient pas d'attribut " + table1.prefix + join1
        assert join2 in table2.columns, "La table " + table2.name + " ne contient pas d'attribut " + table2.prefix + join2
               
        self.joints.append(table2)
        jointure1 = table1.alias + "." + table1.prefix + join1
        jointure2 = table2.alias + "." + table2.prefix + join2
        self.request += "JOIN " + table2.name + " AS " + table2.alias + " ON "  + jointure1 + " = " + jointure2 + "\n"
        
    def add_country(self, country):
        # A modifier suivant la table
        self.request += "WHERE " + self.table.prefix + "country LIKE '%" + country + "%'\n"
        
    def add_description(self, description):
        if "Description" in self.table.columns :
            self.request += "WHERE " + self.table.alias + '.' + self.table.prefix + "Description LIKE '%" + description + "%'\n"
        else:
            print("Cette table ne possède pas d'attribut 'Description'")
        
    def write_query(self):
        self.request += "GO\n"
        self.request += "QUIT"
        self.file = open("example.sql", "w")
        self.file.write(self.request)
        self.file.close()

test = query(item, '*')
test.add_joint(item, color_size, "Code", "Code")
test.add_description('bustier')
test.write_query()
print(test.request)