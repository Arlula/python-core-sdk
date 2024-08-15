'''
    Custom Exception Classes
'''

import requests

class ArlulaSessionError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

class ArlulaAPIException(Exception):
    def __init__(self, response: requests.Response):
        self.value = f"{response.status_code}: {response.text}"
        self.response = response

    def __str__(self):
        return self.value