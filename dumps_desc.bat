REM Ce fichier doit �tre inscrit dans le Task Scheduler de Windows / Crontab de *NIX. 
REM Lanc� 1-3 fois par semaines, il permet de mettre � jour les csv de data/ 
REM qui contiennent les noms des produits / familles / ...
chcp 65001
d:/Anaconda/python.exe d:/dior/testdump.py
pause