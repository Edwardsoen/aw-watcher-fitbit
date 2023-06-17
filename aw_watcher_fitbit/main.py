import requests
from datetime import datetime, timedelta, timezone
import pytz
from time import sleep
import logging
from activity_tracker import SleepTracker, AuthorizationTokenExpire
from aw_core.models import Event
from aw_client import ActivityWatchClient


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
        LOGGER.warning("Error trying to refresh access token " + str(r.status_code) + " " + r.text)


def insert_heartbeat_by_duration(client:ActivityWatchClient, start_time: datetime, data:dict ,duration_seconds:int, bucket_id:str): 
    event = Event(timestamp = start_time, data = data)
    secondEvent = Event(timestamp = start_time + timedelta(seconds = duration_seconds), data = data)
    client.heartbeat(bucket_id, event, pulsetime=duration_seconds+10)
    client.heartbeat(bucket_id, secondEvent, pulsetime=duration_seconds+10)
 

if __name__ == "__main__":
    config = load_config()
    access_token = config[APP_NAME]["access_token"]
    poll_time = config[APP_NAME]["poll_time"]
    user_id = config[APP_NAME]["user_id"]
    sleep_tracker = SleepTracker(access_token=access_token, user_id=user_id)
    client = ActivityWatchClient(APP_NAME, testing=True)
    bucket_id = "{}_{}".format(APP_NAME, client.client_hostname)
    client.create_bucket(bucket_id, event_type= "Current Activity")
    now = datetime.now()
    yesterday = now- timedelta(days=1)
    while(True): 
        try: 
            data = sleep_tracker.get_sleep_data(yesterday, now)
            for i in data: 
                date = i.timestamp
                date = date.astimezone(pytz.timezone("Asia/Shanghai"))
                last_event = client.get_events(bucket_id=bucket_id, limit=1)
                if len(last_event) == 0: 
                    insert_heartbeat_by_duration(client=client, start_time= date, data = i.data, duration_seconds = i.duration, bucket_id=bucket_id)
                    continue
                last_event_timestamp = last_event[0]['timestamp']
                last_event_timestamp.astimezone(pytz.timezone("Asia/Shanghai"))
                if(date > last_event_timestamp): 
                    insert_heartbeat_by_duration(client=client, start_time= date, data = i.data, duration_seconds = i.duration, bucket_id=bucket_id)
        except AuthorizationTokenExpire: 
            refresh_access_token(config[APP_NAME]["client_id"], 
                                 config[APP_NAME]["refresh_token"] )
            continue
        sleep(poll_time)
        
