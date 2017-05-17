REM Ce fichier doit être inscrit dans le Task Scheduler de Windows / Crontab de *NIX. 
REM Le configurer pour être lancé à chaque démarrage de la machine
@echo off
chcp 65001
CD /D D:/dior
D:/Anaconda/python.exe D:/dior/start.py