# coding=utf-8

class table(object):
    def __init__(self, name, prefix, alias, columns):
        self.name = name
        self.prefix = prefix
        self.alias = alias
        self.columns = columns

country = table("COUN_COUNTRY", "COUN_", "CO", ["Description", "Zone", "Currency", "Sub_Zone", "Description_FR"])
item = table("ITEM_ITEM", "ITEM_", "IT", ["Code", "Description"])
color_size = table("ITEM_COLOR_SIZE", "ITEM_", "CS", ["Code", "Color", "Size"])