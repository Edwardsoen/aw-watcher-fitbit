import requests
from datetime import datetime, timedelta, timezone
from time import sleep
from aw_core.models import Event
import logging
from aw_client import ActivityWatchClient
from aw_core import dirs 
import traceback
import sys

APP_NAME = "aw-watcher-fitbit"




def get_toml_config_string(app_name:str = "", access_token:str = "" , refresh_token:str = "", user_id:str = "", poll_time:float = 5.0) -> str: 
    return   f"""
[{app_name}]
access_token = "{access_token}"
refresh_token = "{refresh_token}"
user_id = "{user_id}"
poll_time = {poll_time}
"""


def load_config() -> dict : 
    from aw_core.config import load_config_toml as _load_config
    return _load_config(APP_NAME, get_toml_config_string(APP_NAME))

def write_access_token(new_access_token): 
    from aw_core.config import save_config_toml as _save_config 
    data = load_config()[APP_NAME]
    print(data)
    new_config = get_toml_config_string(APP_NAME, new_access_token, data["refresh_token"], data["user_id"], data["poll_time"])
    return _save_config(APP_NAME, new_config)


def refresh_access_token(client_id = "", refresh_token = ""): 
    end_point = "https://api.fitbit.com/oauth2/token"
    data =  { 
        "grant_type":"refresh_token", 
        "client_id":"23QWTQ" , 
        "refresh_token":"c82fefe6c65ed363b9d5cf94993b02fa93fc101b690d29814eee99ef43bc74b1"
    }
    r = requests.post(url= end_point, data=data)
    if r.status_code == 200: 
        new_access_token = r.json()["access_token"] 
        write_access_token(new_access_token=new_access_token)
    else: 
        print("error")




if __name__ == "__main__":
    print(write_access_token("testi2ng"))

