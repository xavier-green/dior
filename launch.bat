REM Ce fichier doit �tre inscrit dans le Task Scheduler de Windows / Crontab de *NIX. 
REM Le configurer pour �tre lanc� � chaque d�marrage de la machine
@echo off
chcp 65001
CD /D D:/dior
D:/Anaconda/python.exe D:/dior/start.py