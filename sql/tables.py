# coding=utf-8

class table(object):
    def __init__(self, name, prefix, alias, columns):
        self.name = name
        self.prefix = prefix
        self.alias = alias
        self.columns = columns

country = table("COUN_COUNTRY", "COUN_", "CO", ["Code", "Description", "Zone", "Currency", "Sub_Zone", "Description_FR"])
nationality = table("CRM_Country_Nationality", "CRM_", "CN", ["Code_ISO", "Country_Desc_FR", "Country_Desc_EN", "Nationality_Desc_FR", "Nationality_Desc_EN", "Zone", "Sub_Zone"])
customer = table("CUST_CUSTOMER", "CUST_", "CU", [""])
department = table("DEPT_Department", "DEPT_", "DE", ["Code", "Description", "Division"])
division = table("DIVI_Division", "DIVI_", "DI", ["Code", "Description"])
family = table("FAMI_family", "FAMI_", "FA", ["Code, Description", "Line", "Division", "Departement"])
retail = table("grou_group", "GROU_", "GR", ["Code", "Description"])
color_size = table("ITEM_COLOR_SIZE", "ITEM_", "CS", ["Code", "Color", "Size"])
item = table("ITEM_ITEM", "ITEM_", "IT", ["Code", "Description", "Year", "Collection", "Division", "Line", "Family", "Sub_Family", "Theme", "Department", "Group", "Vendor", "Series", "RS_Style", "Segment", "Material", "Price_Cat", "Model"])
boutique = table("loca_location", "LOCA_", "BT", ["Code", "Description", "Country", "City", "Zone", "Type", "Category", "Currency", "State", "Sub_Zone"])
model = table("mod_model", "MOD_", "MD", ["Code", "Description"])
sale = table("sale_sales", "SALE_", "SA", ["Location", "Date", "Style", "Color", "Size", "Country"])
sub_family = table("SFAM_sub_Family", "SFAM_", "SF", [""])
staff = table("STAFF_staff", "STAFF_", "STF", [""])
state = table("STAT_STATE", "STAT_", "STT", [""])
stock_daily = table("stoc_stocks_Daily", "STOC_", "DA", [""])
stock_weekly = table("stoc_stocks_week", "STOC_", "WE", [""])
sub_zone = table("SZONE_Sub_Zone", "SZONE_", "SZ", [""])
theme = table("THEM_Theme", "THEM_", "TH", [""])
uzone = table("UZONE_Zone", "UZONE_", "UZ", [""])
zone = table("ZONE_Zone", "ZONE_", "ZO", [""])



#sale_sales_Random
#stoc_stocks_Daily
#stoc_stocks_week
#sysdiagrams