REM Ce fichier doit être inscrit dans le Task Scheduler de Windows / Crontab de *NIX. 
REM Lancé 1-3 fois par semaines, il permet de mettre à jour les csv de data/ 
REM qui contiennent les noms des produits / familles / ...
chcp 65001
d:/Anaconda/python.exe d:/dior/testdump.py
pause