# coding=utf-8

from sql.tables import table, country, nationality, customer, department, division, family, retail, color_size, item
from sql.request import query

class answer(object):
    
    # Cette fonction a été déplacée dans ../intent/produit.py
    def produit(self, product):
        demande = query(item, ['Description'], 50)
        demande.where(item, 'Description', product)
        demande.groupby(item, 'Description')
        demande.write()
        return demande.request
    
    def make(self, data):
        cities = data['cities']
        countries = data['countries']
        nationalities = data['nationalities']
        dates = data['dates']
        intent = data['intent']
        items = data['items']
        
        string = ""
        
        if intent == "produit":
            for product in items:
                string += "\nVoici la liste des produits contenant " + product + "\n"
                string += self.produit(product)
                
        return string