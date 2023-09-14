#!/usr/bin/python3

##########################################################################
############      Designed and tested by Alexander Semenov  ##############
############       email: vj0r.awful@gmail.com              ##############
##########################################################################

from novaclient.client import Client
from cinderclient.v3 import client
import configparser
import sys
import logging
import time
import re


config = configparser.ConfigParser()
config.read("/etc/evacuate_engine/settings.ini")
log_path = config["log"]["path"]

username = config["auth"]["username"]
password = config["auth"]["password"]
project_id = config["auth"]["project_id"]
auth_url = config["auth"]["auth_url"]
user_domain_name = config["auth"]["user_domain_name"]
project_domain_name = config["auth"]["project_domain_name"]
project_name = config["auth"]["project_name"]

logging.basicConfig(
    level=logging.INFO,
    filename = log_path,
    format = '%(asctime)s %(levelname)s - %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S",
)

try:
    cinder = client.Client(username, password, project_id, auth_url)
    cinder.authenticate()
except:
    logging.error('authentication failed')
    sys.exit(1)

try:
    nova_client = Client('2', username=username,
                     password=password,
                     auth_url=auth_url,
                     user_domain_name=user_domain_name,
                     project_domain_name=project_domain_name,
                     project_name=project_name)
except:
    logging.error('authentication failed')
    sys.exit(1)

logging.info("Start evacuate servers success!")

def check_type_volume(dic):

    tmp_id_volume = []
    flag = False
    for v in dic:
            
        id_volume = v['id']
        volume = cinder.volumes.get(volume_id=id_volume)
        volume_type = volume.volume_type

        if re.search(r'ceph', volume_type, re.I):
            tmp_id_volume.append(id_volume)
            
        else:
            flag = True
            break
    
    if flag:
        return False
    else:
        return(tmp_id_volume)


def reset_volume(id_volume):
    try:
        cinder.volumes.reset_state(volume=id_volume, state="available", attach_status="detached")
        logging.info("Reset status volume id=%s. Success!" % id_volume)
        return True
    except:
        logging.info("Reset status volume id=%s failed" % id_volume)
        return False


def evacuate_vm(id_vm):
    try:
        nova_client.servers.evacuate(id_vm)
        logging.info("evacuate vm id_vm=%s. Success!\n" % id_vm)
    except:
        logging.error("evacuate failed vm id_vm=%s\n" % id_vm)



while True:

    down_hypervisor_hostname = ""
    

    for i in nova_client.hypervisors.list():
        if (i.state=="down"):
            down_hypervisor_hostname = i.hypervisor_hostname

            mass_servers = {}
            for j in nova_client.servers.list():
                if (j.__getattribute__('OS-EXT-SRV-ATTR:hypervisor_hostname') == down_hypervisor_hostname):
                    mass_servers[j.id]=j.__getattribute__('os-extended-volumes:volumes_attached')

            
            for id_server in mass_servers:
                
                fl = False
                id_volume = check_type_volume(mass_servers[id_server])
                if id_volume:
                    for v_id in id_volume:
                        if not (reset_volume(v_id)):
                            fl = True
                       

                    if not (fl):
                        evacuate_vm(id_server)        
                       


    time.sleep(60)

