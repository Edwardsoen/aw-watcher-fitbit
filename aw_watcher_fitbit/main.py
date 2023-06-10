import requests
from datetime import datetime, timedelta, timezone
from time import sleep
import logging


APP_NAME = "aw-watcher-fitbit"
LOGGER = logging.getLogger()

def get_toml_config_string(app_name:str = "", access_token:str = "" , refresh_token:str = "", user_id:str = "", client_id:str = "" ,poll_time:float = 5.0) -> str: 
    return   f"""
[{app_name}]
access_token = "{access_token}"
refresh_token = "{refresh_token}"
user_id = "{user_id}"
client_id = "{client_id}"
poll_time = {poll_time}
"""

def load_config() -> dict : 
    from aw_core.config import load_config_toml as _load_config
    return _load_config(APP_NAME, get_toml_config_string(APP_NAME))

def write_access_token(new_access_token:str): 
    from aw_core.config import save_config_toml as _save_config 
    data = load_config()[APP_NAME]
    new_config = get_toml_config_string(APP_NAME, new_access_token, data["refresh_token"], data["user_id"], data["poll_time"])
    return _save_config(APP_NAME, new_config)

def refresh_access_token(client_id:str, refresh_token:str): 
    end_point = "https://api.fitbit.com/oauth2/token"
    data =  { 
        "grant_type":"refresh_token", 
        "client_id":client_id, 
        "refresh_token":refresh_token
    }
    r = requests.post(url= end_point, data=data)
    if r.status_code == 200: 
        new_access_token = r.json()["access_token"] 
        write_access_token(new_access_token=new_access_token)
    else: 
        LOGGER.warning("Error trying to refresh access token " + r.status_code + " " + r.text)

def get_sleep_by_date(access_token:str): 
    end_point = f"https://api.fitbit.com/1.2/user/-/sleep/date/2023-06-09.json"
    header = {"authorization": f"Bearer {access_token}"}
    response = requests.get(end_point, headers=header)    
    print(response.status_code)

if __name__ == "__main__":
    config = load_config()
    # access_token = config[APP_NAME]["access_token"]
    # refresh_access_token("",config[APP_NAME]["refresh_token"] )
    get_sleep_by_date(access_token = access_token)
