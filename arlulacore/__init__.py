from .auth import *
from .archive import *
from .orders import *

class Arlula:
    '''
        Main class for Arlula API Calls. Contains an instance of the archive and orders APIs.
    '''

    def __init__(self, session: Session):
        self._archive = Archive(session)
        self._orders = Orders(session)
    
    def archive(self) -> Archive:
        return self._archive

    def orders(self) -> Orders:
        return self._orders