import os, time
from ampapi.modules.ADS import ADS
from ampapi.apimodules.ADSModule import Instance
from dotenv import load_dotenv  
from models.amp import ADSInstanceData
from cogs.amp.exceptions import *

load_dotenv()

API : ADS = None

def login() -> bool:
    global API
    site = os.getenv('AMP_SITE')
    username = os.getenv('AMP_BOT_NAME')
    password = os.getenv('AMP_BOT_PASSWORD')
    API = ADS(site, username, password)
    retries = 3
    while retries > 0:
        try:
            API.Login()
            break
        except Exception as e:
            print(f'Failed to login to AMP API: {e}')
            retries -= 1
            time.sleep(1)
    return retries > 0

async def get_server_list() -> (ADSInstanceData|None):
    global API
    if not API and not login():
        return None
    retries = 5
    while retries > 0:
        try:
            instances = API.ADSModule.GetInstances()
            instance = instances[0]
            return ADSInstanceData(instance)
        except Exception as e:
            print(f'Failed to get server list: {e}')
            retries -= 1
            time.sleep(1)
    return None

async def start_server(server : str):
    global API
    if not API and not login():
        raise FailedToLogin()
    
    server_list = await get_server_list()
    if not server_list:
        raise NoServer()
    
    server = server.lower().replace(' ','')
    server_to_start = server_list.get_server(server)

    if not server_to_start:
        raise NoServer()
    
    if server_to_start.Running:
        raise ServerAlreadyRunning()
    
    return API.ADSModule.StartInstance(server_list.get_instance(server))

async def stop_server(server : str):
    global API
    if not API and not login():
        raise FailedToLogin()
    
    server_list = await get_server_list()
    if not server_list:
        raise NoServer()
    
    server = server.lower().replace(' ','')
    server_to_stop = server_list.get_server(server)

    if not server_to_stop:
        raise NoServer()
    
    if not server_to_stop.Running:
        raise ServerAlreadyStopped()
    
    return API.ADSModule.StopInstance(server_list.get_instance(server))

async def restart_server(server : str):
    global API
    if not API and not login():
        raise FailedToLogin()
    
    server_list = await get_server_list()
    if not server_list:
        raise NoServer()
    
    server = server.lower().replace(' ','')
    server_to_stop = server_list.get_server(server)

    if not server_to_stop:
        raise NoServer()
    
    if not server_to_stop.Running:
        raise ServerAlreadyStopped()
    
    return API.ADSModule.RestartInstance(server_list.get_instance(server))