#!/usr/bin/python3



##########################################################################
############      Designed and tested by Alexander Semenov  ##############
############       email: vj0r.awful@gmail.com              ##############
##########################################################################


import subprocess
import configparser
import logging
import time

config = configparser.ConfigParser()
config.read("/etc/process_list/settings.ini")

command = config["systemd"]["daemons"]
log_path = config["log"]["path"]
sleep_interval = int(config["interval"]["check"])

logging.basicConfig(
    level=logging.INFO,
    filename = log_path,
    format = '%(asctime)s %(levelname)s - %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S",
)

mass_command = command.split(',')

while True:
    for i in mass_command:
        
        mass_chack = ["systemctl", "status"]
        mass_run = ["systemctl", "restart"]
        mass_chack.append(i)
        
        if subprocess.call(mass_chack, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False):
            mass_run.append(i)
            try:
                if not subprocess.call(mass_run, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False):
                    logging.info("restart daemon %s" % (i))
                else:
                    logging.error("restart daemon %s failed" % (i))    
            except:
                logging.error("restart daemon %s failed" % (i))

    time.sleep(sleep_interval)
