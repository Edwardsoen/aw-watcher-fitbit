from datetime import datetime
import requests


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
        self._requests_data(start_date=start_date, end_date=end_date)
        pass

    def _parse_data(self, data:dict) -> list:
        sleep_time_stamp = []
        sleep_data_by_date = data["sleep"]
        for i in sleep_data_by_date: 
            sleep_data = i["levels"]["data"]
            sleep_time_stamp += sleep_data
        return sleep_time_stamp

    def _requests_data(self, start_date:datetime, end_date:datetime) -> dict:
        end_point = self.get_end_point(start_date=start_date, end_date=end_date)
        header = {"authorization": f"Bearer {self.access_token}"}
        response = requests.get(end_point, headers=header)    
        if(response.status_code == 401): 
            raise AuthorizationTokenExpire
        else:
            self._parse_data(response.json())
        pass


if __name__ == "__main__": 
    from datetime import datetime, timedelta
    now = datetime.now()
    yesterday = now- timedelta(days=1)
    #   test.get_sleep_data(yesterday, now)
    pass