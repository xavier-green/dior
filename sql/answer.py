# coding=utf-8

from sql.tables import table, country, nationality, customer, department, division, family, retail, color_size, item
from sql.request import query

class answer(object):
    
    def produit(self, product):
        demande = query(item, ['Description'], 50)
        demande.where(item, 'Description', product)
        demande.groupby(item, 'Description')
        demande.write()
        print(demande.request)
    
    def make(self, data):
        cities = data['cities']
        countries = data['countries']
        nationalities = data['nationalities']
        dates = data['dates']
        intent = data['intent']
        items = data['items']
        
        if intent == "produit":
            for product in items:
                print("\nVoici la liste des produits contenant " + product)
                self.produit(product)

data = {
        'cities' : '',
        'countries' : '',
        'nationalities' : '',
        'dates' : '',
        'intent' : 'produit',
        'items' : ('rose des vents', 'pantalon')
        }
test = answer()
test.make(data)
            
    