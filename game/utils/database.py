import requests




class Database:
    def __init__(self):
        self.login_url = (
            f'http://127.0.0.1:5000/login'
        )
    
    def login_or_register(self, username, password):        
        try:
            response = requests.get(f'{self.login_url}?username={username}&password={password}')
            if response.status_code != 200:
                raise Exception(f"Failed to fetch level from API: {response.status_code}")
            data = response.json()
            return data['success'], data['result']
        except Exception as e:
            print("Error, check utils/database.py")
        
        
        
        
        