import os, time
from ampapi.modules.ADS import ADS
from ampapi.apimodules.ADSModule import ADSModule
from dotenv import load_dotenv  
from models.amp import ADSInstanceData

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