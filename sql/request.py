# coding=utf-8

class write_request(object):
    def __init__ (self, value, table):
        self.table = table
        self.value = value
        self.request = "SELECT TOP 3 " + value + " FROM " + table + "\n"
        self.file = open("example.sql", "w")
        self.file.write(self.request)

test = write_request('*', 'ITEM_ITEM')
test.file.write("GO")
test.file.close()