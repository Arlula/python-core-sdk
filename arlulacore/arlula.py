from .auth import Session
from .archive import ArchiveAPI
from .orders import OrdersAPI

class ArlulaAPI:
    '''
        Main class for Arlula API Calls. Contains an instance of the archive and orders APIs.
    '''

    def __init__(self, session: Session):
        self._archive = ArchiveAPI(session)
        self._orders = OrdersAPI(session)
    
    def archiveAPI(self) -> ArchiveAPI:
        '''
            Returns the archive api instance, used for searching and ordering imagery.
        '''
        return self._archive

    def ordersAPI(self) -> OrdersAPI:
        '''
            Returns the orders api instance, used for maintaining orders and getting resources.
        '''
        return self._orders
