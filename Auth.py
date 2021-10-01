from secrets import *
import base64
import requests

class Auth:
    def __init__(self):
        self.client_id = get_clientID()
        self.client_secret = get_clientSecret()

    def encode_credentials(self):
        message = f"{self.client_id}:{self.client_secret}"
        message_bytes = message.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        base64_encoded = base64_bytes.decode('ascii')
        return base64_encoded

    def get_access_token(self):
        auth_url = "https://accounts.spotify.com/api/token"
        auth_headers = {'Authorization': 'Basic ' + self.encode_credentials()}
        auth_data = {'grant_type': 'client_credentials'}
        res = requests.post(auth_url, headers = auth_headers, data = auth_data)
        responseObject = res.json()
        return responseObject['access_token']



#if __name__ == '__main__':
    #auth1 = Auth()
    #print(auth1.get_access_token())
