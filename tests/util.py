import arlulacore
import arlulacore
import os

def create_test_session() -> arlulacore.Session:
    return arlulacore.Session(os.getenv("API_KEY"), os.getenv("API_SECRET"), url=os.getenv("API_HOST"))