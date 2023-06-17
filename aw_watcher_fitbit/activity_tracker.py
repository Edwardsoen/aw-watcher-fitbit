from datetime import datetime
import requests


class ActivityData(): 
    def __init__(self, timestamp:datetime, data:dict,  duration:int) -> None:
        self.timestamp = timestamp
        self.data = data 
        self.duration = duration


def sort_activity_data(data:list[ActivityData]): 
    data.sort(key=lambda x: x.timestamp)
    

class AuthorizationTokenExpire(Exception):
    def __init__(self, message="Authorization Token Expired"):
        self.message = message
        super().__init__(self.message)


class SleepTracker(): 
    def __init__(self, access_token:str, user_id:str = "-") -> None:
        self.access_token = access_token
        self.user_id = user_id

    def get_end_point(self, start_date:datetime, end_date:datetime) -> str:
        return f"https://api.fitbit.com/1.2/user/{self.user_id}/sleep/date/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}.json"

    def get_sleep_data(self, start_date, end_date): 
        return self._requests_data(start_date=start_date, end_date=end_date)
        
    def _parse_data(self, data:dict) -> list[ActivityData]:
        sleep_data_by_timestamp = []
        sleep_data_by_date = data["sleep"]
        for i in sleep_data_by_date: 
            sleep_data = i["levels"]["data"]
            for ii in sleep_data:
                date = datetime.strptime(ii["dateTime"], '%Y-%m-%dT%H:%M:%S.%f')
                data = {"Activity": 
                        "Sleep", 
                        "Level": ii["level"]}
                duration = ii["seconds"] 
                sleep_data = ActivityData(
                    data=data, 
                    timestamp=date, 
                    duration=int(duration)
                )
                sleep_data_by_timestamp.append(sleep_data)
        sort_activity_data(sleep_data_by_timestamp)
        return sleep_data_by_timestamp
    

    def _requests_data(self, start_date:datetime, end_date:datetime) -> dict:
        end_point = self.get_end_point(start_date=start_date, end_date=end_date)
        header = {"authorization": f"Bearer {self.access_token}"}
        response = requests.get(end_point, headers=header)    
        data = {}
        if(response.status_code == 401): 
            raise AuthorizationTokenExpire
        else:
            data = self._parse_data(response.json())
        return data


if __name__ == "__main__": 
    from datetime import datetime, timedelta
    test = SleepTracker("")
    now = datetime.now()
    yesterday = now- timedelta(days=1)
    data = test.get_sleep_data(yesterday, now)
    breakpoint()
    pass