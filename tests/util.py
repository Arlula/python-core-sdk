import arlulacore
import arlulacore
import os

def create_test_client() -> arlulacore.Session:
    return arlulacore.Session(os.getenv("API_KEY"), os.getenv("API_SECRET"))