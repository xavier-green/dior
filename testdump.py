import subprocess

cmd1='sqlcmd -l 10 -S 10.148.102.166\DEV2012 -U REP_SQL_CHATBOT -P ChatBoT1984! -d Reporting_CDS -W -w 999 -f 65001 -s # -Q "SELECT distinct('
cmd2='_description) from '

tables=[ 'LOCA_location', 'COLO_color', 'COUN_country', 'DEPT_department', 'DIVI_division' , 'FAMI_family', 'GROU_group', 'MATE_material', 'ITEM_item', 'SHAP_shape', 'STAT_state', 'SZONE_sub_zone', 'THEM_theme', 'UZONE_zone', 'ZONE_zone' ]
files=['Boutiques', 'color', 'country', 'Departements', 'Divisions', 'family', 'Groupe', 'material', 'products', 'shape', 'state', 'szone', 'Themes', 'uzone', 'zone']

for index, x in enumerate(tables):
    m = x[:x.find('_')]
    if x == "SZONE_sub_zone":
        m = "SZON"
    tot = cmd1+m+cmd2+x+'"'

    if x == 'COUN_country':
        tot = cmd1 + m + '_Description_FR) from '+x+'"'

    with open('d:/dior/data/'+files[index]+'.csv', 'w', encoding='utf-8') as f:
            p = subprocess.Popen(tot, shell=True, encoding='utf-8', stdout=subprocess.PIPE)
            f.write("".join(p.stdout.readlines()[2:-1]))
            print('Dumped', x) 
